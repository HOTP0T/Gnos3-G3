<script lang="ts">
	import { getContext, onDestroy } from 'svelte';
	import dayjs from 'dayjs';
	import { toast } from 'svelte-sonner';

	import ExternalLink from '@lucide/svelte/icons/external-link';
	import FileWarning from '@lucide/svelte/icons/file-warning';

	import { updateInvoice } from '$lib/apis/invoices';
	import { k4miDocHref } from '$lib/apis/k4mi';
	import { INVOICE_API_BASE_URL } from '$lib/constants';
	import { fetchAsBlobUrl, revokeBlobUrl } from '$lib/utils/blobPreview';

	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';

	const i18n: any = getContext('i18n');

	export let show = false;
	export let invoice: any = null;
	export let onUpdate: (updated: any) => void = () => {};

	const INVOICE_API_BASE = INVOICE_API_BASE_URL;

	// Iframes can't send `Authorization: Bearer …`, and Phase 1 RBAC added a
	// router-level auth dep on `/api/invoices/*`. So fetch the PDF ourselves
	// (where we control headers) and use a blob URL for the iframe src.
	let previewUrl = '';
	let previewError = false;
	let lastFetchedFor: number | null = null;

	const loadPreview = async (id: number | null) => {
		if (id === lastFetchedFor) return;
		if (previewUrl) {
			revokeBlobUrl(previewUrl);
			previewUrl = '';
		}
		previewError = false;
		lastFetchedFor = id;
		if (!id) return;
		const token = typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null;
		const result = await fetchAsBlobUrl(`${INVOICE_API_BASE}/api/invoices/${id}/preview`, token);
		if (result && lastFetchedFor === id) {
			previewUrl = result.url;
		} else if (lastFetchedFor === id) {
			previewError = true;
		}
	};

	// Only fetch when the modal is open AND has an invoice — avoids loading
	// every previously-rendered invoice in the table.
	$: if (show && invoice?.id) {
		loadPreview(invoice.id);
	} else if (!show) {
		loadPreview(null);
	}

	onDestroy(() => revokeBlobUrl(previewUrl));

	// Editable field definitions
	const EDITABLE_FIELDS = [
		{ key: 'vendor_name', label: 'Vendor', type: 'text', section: 'info' },
		{ key: 'invoice_number', label: 'Invoice #', type: 'text', section: 'info' },
		{ key: 'invoice_date', label: 'Date', type: 'date', section: 'info' },
		{ key: 'due_date', label: 'Due Date', type: 'date', section: 'info' },
		{ key: 'client_name', label: 'Client', type: 'text', section: 'info' },
		{ key: 'subtotal', label: 'Subtotal', type: 'number', section: 'money' },
		{ key: 'tax_amount', label: 'Tax', type: 'number', section: 'money' },
		{ key: 'total_amount', label: 'Total', type: 'number', section: 'money', bold: true },
		// Paid / Balance Due deliberately absent — see InvoiceTable. They are accounting
		// state, never extracted from the document; payment status lives in Accounting.
		{ key: 'payment_terms', label: 'Payment Terms', type: 'text', section: 'details' },
		{ key: 'po_number', label: 'PO #', type: 'text', section: 'details' },
		{ key: 'description', label: 'Description', type: 'text', section: 'details' }
	];

	// Edit state
	let editingField: string | null = null;
	let editValue = '';

	function startEdit(field: (typeof EDITABLE_FIELDS)[0]) {
		if (!invoice) return;
		editingField = field.key;
		const val = invoice[field.key];
		if (field.type === 'date' && val) {
			editValue = dayjs(val).format('YYYY-MM-DD');
		} else if (field.type === 'number' && val !== null && val !== undefined) {
			editValue = String(parseFloat(val));
		} else {
			editValue = val ?? '';
		}
	}

	function cancelEdit() {
		editingField = null;
	}

	async function saveEdit() {
		if (!editingField || !invoice) return;

		const field = EDITABLE_FIELDS.find((f) => f.key === editingField);
		if (!field) return;

		let updateVal: any = editValue;
		if (field.type === 'number') {
			updateVal = editValue === '' ? null : parseFloat(editValue);
		} else if (field.type === 'date') {
			updateVal = editValue === '' ? null : editValue;
		} else {
			updateVal = editValue === '' ? null : editValue;
		}

		// Skip if unchanged
		const oldVal = invoice[field.key];
		const oldStr = oldVal === null || oldVal === undefined ? '' : String(oldVal);
		const newStr = updateVal === null ? '' : String(updateVal);
		if (
			oldStr === newStr ||
			(field.type === 'date' && dayjs(oldStr).format('YYYY-MM-DD') === newStr)
		) {
			editingField = null;
			return;
		}

		try {
			const res = await updateInvoice(localStorage.token, invoice.id, {
				[field.key]: updateVal
			});
			if (res) {
				invoice = res;
				onUpdate(res);
				toast.success($i18n.t('Updated'));
			}
		} catch (err) {
			toast.error(`${err}`);
		}

		editingField = null;
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') {
			e.preventDefault();
			saveEdit();
		} else if (e.key === 'Escape') {
			cancelEdit();
		}
	}

	function formatMoney(val: any, currency: string): string {
		if (val === null || val === undefined || val === '') return '—';
		const n = parseFloat(val);
		if (!isFinite(n)) return '—';
		const amount = n.toLocaleString(undefined, {
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		});
		return currency ? `${currency} ${amount}` : amount;
	}

	function formatDate(val: any): string {
		if (!val) return '—';
		return dayjs(val).format('YYYY-MM-DD');
	}

	function displayValue(field: (typeof EDITABLE_FIELDS)[0]): string {
		const val = invoice?.[field.key];
		if (field.type === 'date') return formatDate(val);
		if (field.type === 'number') return formatMoney(val, invoice?.currency ?? '');
		return val === null || val === undefined || val === '' ? '—' : String(val);
	}

	const SECTIONS = [
		{ key: 'info', label: 'Invoice' },
		{ key: 'money', label: 'Amounts' },
		{ key: 'details', label: 'Details' }
	];

	$: confidence =
		invoice?.confidence_score !== null && invoice?.confidence_score !== undefined
			? Math.round(parseFloat(invoice.confidence_score) * 100)
			: null;
	$: subtitle = invoice
		? [
				invoice.invoice_number,
				invoice.vendor_name,
				invoice.extraction_model
					? $i18n.t('extracted by {{model}}', { model: invoice.extraction_model })
					: ''
			]
				.filter(Boolean)
				.join(' · ')
		: '';
</script>

<Dialog.Root bind:open={show}>
	<Dialog.Content class="max-h-[90vh] gap-5 overflow-y-auto sm:max-w-[60rem]">
		<Dialog.Header class="pr-8">
			<div class="flex flex-wrap items-center justify-between gap-2">
				<Dialog.Title>{$i18n.t('Document Preview')}</Dialog.Title>
				{#if invoice?.k4mi_document_id}
					<Button
						variant="outline"
						size="sm"
						href={k4miDocHref(invoice.k4mi_document_id)}
						target="_blank"
						rel="noopener noreferrer"
					>
						<ExternalLink />{$i18n.t('Open in K4mi')}
					</Button>
				{/if}
			</div>
			<Dialog.Description class={subtitle ? '' : 'sr-only'}>
				{subtitle || $i18n.t('Document Preview')}
			</Dialog.Description>
		</Dialog.Header>

		{#if invoice}
			<div class="grid gap-5 lg:grid-cols-[minmax(0,1fr)_20rem]">
				<!-- Document -->
				<div class="h-[70vh] min-w-0 overflow-hidden rounded-md border bg-muted">
					{#if previewUrl}
						<iframe src={previewUrl} title={$i18n.t('Invoice document')} class="h-full w-full border-0"
						></iframe>
					{:else if previewError}
						<div
							class="flex h-full flex-col items-center justify-center gap-2 p-6 text-center text-sm text-muted-foreground"
						>
							<FileWarning class="size-5" />
							<p>{$i18n.t('Could not load the original document.')}</p>
							{#if invoice.k4mi_document_id}
								<a
									class="text-link underline-offset-4 hover:underline"
									href={k4miDocHref(invoice.k4mi_document_id)}
									target="_blank"
									rel="noopener noreferrer">{$i18n.t('Open in K4mi instead →')}</a
								>
							{/if}
						</div>
					{:else}
						<Skeleton class="h-full w-full rounded-none" />
					{/if}
				</div>

				<!-- Extracted data (click a value to edit it) -->
				<div class="flex min-w-0 flex-col gap-4 lg:max-h-[70vh] lg:overflow-y-auto lg:pr-1">
					<div class="flex items-center justify-between gap-2">
						<span class="font-medium">{$i18n.t('Extracted Data')}</span>
						{#if confidence !== null}
							<StatusBadge
								kind="confidence"
								status={confidence}
								label={`${confidence}% ${$i18n.t('confidence')}`}
							/>
						{/if}
					</div>

					{#each SECTIONS as section, i}
						{#if i > 0}<Separator />{/if}
						<div>
							<div class="mb-2 text-xs font-medium text-muted-foreground">
								{$i18n.t(section.label)}
							</div>
							<dl
								class="grid grid-cols-[minmax(6rem,auto)_minmax(0,1fr)] items-center gap-x-4 gap-y-2 text-sm"
							>
								{#each EDITABLE_FIELDS.filter((f) => f.section === section.key) as field}
									<dt class="text-muted-foreground">{$i18n.t(field.label)}</dt>
									<dd class="min-w-0">
										{#if editingField === field.key}
											<input
												type={field.type === 'date'
													? 'date'
													: field.type === 'number'
														? 'number'
														: 'text'}
												step={field.type === 'number' ? '0.01' : undefined}
												aria-label={$i18n.t(field.label)}
												class="h-7 w-full min-w-0 rounded-md border border-input bg-transparent px-1.5 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 {field.type ===
												'number'
													? 'tabular-nums'
													: ''}"
												bind:value={editValue}
												on:keydown={handleKeydown}
												on:blur={saveEdit}
												autofocus
											/>
										{:else}
											<button
												type="button"
												class="-mx-1.5 block max-w-full cursor-text truncate rounded-sm px-1.5 py-0.5 text-left transition-colors hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none {field.type ===
												'number'
													? 'tabular-nums'
													: ''} {field.bold ? 'font-semibold' : ''} {field.key ===
													'invoice_number' || field.key === 'po_number'
													? 'font-mono text-[13px]'
													: ''} {displayValue(field) === '—' ? 'text-muted-foreground' : ''}"
												on:click={() => startEdit(field)}
												title={$i18n.t('Click to edit')}
											>
												{displayValue(field)}
											</button>
										{/if}
									</dd>
								{/each}
							</dl>
						</div>
					{/each}

					{#if invoice.k4mi_tags?.length}
						<Separator />
						<div>
							<div class="mb-2 text-xs font-medium text-muted-foreground">{$i18n.t('Tags')}</div>
							<div class="flex flex-wrap gap-1">
								{#each invoice.k4mi_tags as tag}
									<Badge variant="outline">{tag}</Badge>
								{/each}
							</div>
						</div>
					{/if}

					{#if invoice.k4mi_notes?.length}
						<Separator />
						<div>
							<div class="mb-2 text-xs font-medium text-muted-foreground">{$i18n.t('Notes', { context: 'gnos3' })}</div>
							<div class="grid gap-2">
								{#each invoice.k4mi_notes as note}
									<div class="rounded-md border bg-muted/50 px-3 py-2 text-sm whitespace-pre-wrap">
										{note.text || note.note || ''}
									</div>
								{/each}
							</div>
						</div>
					{/if}

					<p class="text-xs text-muted-foreground">{$i18n.t('Click a value to edit it.')}</p>
				</div>
			</div>
		{/if}
	</Dialog.Content>
</Dialog.Root>
