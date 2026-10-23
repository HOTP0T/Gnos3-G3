<script lang="ts">
	import { getContext, onDestroy } from 'svelte';
	import { toast } from 'svelte-sonner';

	import ExternalLink from '@lucide/svelte/icons/external-link';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Check from '@lucide/svelte/icons/check';
	import Maximize2 from '@lucide/svelte/icons/maximize-2';
	import Minimize2 from '@lucide/svelte/icons/minimize-2';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';

	import {
		updateBusinessCard,
		reprocessBusinessCard,
		syncBusinessCardFromK4mi,
		markBusinessCardReviewed,
		getBusinessCardPreviewUrl,
		type BusinessCard
	} from '$lib/apis/business-cards';
	import { k4miDocHref } from '$lib/apis/k4mi';
	import { fetchAsBlobUrl, revokeBlobUrl } from '$lib/utils/blobPreview';

	import * as Sheet from '$lib/components/ui/sheet/index.js';
	import * as Collapsible from '$lib/components/ui/collapsible/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';
	import { cn } from '$lib/utils/shadcn.js';

	const i18n: any = getContext('i18n');

	let {
		card: cardProp,
		onclose,
		onupdated,
		ondeleterequest
	}: {
		card: BusinessCard;
		onclose: () => void;
		onupdated: (card: BusinessCard) => void;
		ondeleterequest: (card: BusinessCard) => void;
	} = $props();

	// Local copy: "mark reviewed" saves pending edits first and works on the saved row.
	let card = $state<BusinessCard>(cardProp);
	$effect(() => {
		card = cardProp;
	});

	let open = $state(true);
	let draft = $state<Partial<BusinessCard>>({});
	let saving = $state(false);
	let syncing = $state(false);
	let reprocessing = $state(false);
	let marking = $state(false);
	let confirmDiscard = $state(false);

	const dirty = $derived(Object.keys(draft).length > 0);

	type Field = { key: keyof BusinessCard; label: string; type?: 'text' | 'textarea'; full?: boolean };

	const MAIN_SECTIONS: Array<{ title: string; fields: Field[] }> = [
		{
			title: 'Identity',
			fields: [
				{ key: 'full_name', label: 'Full name' },
				{ key: 'job_title', label: 'Job title' },
				{ key: 'company_name', label: 'Company' }
			]
		},
		{
			title: 'Contact',
			fields: [
				{ key: 'email', label: 'Email' },
				{ key: 'email_secondary', label: 'Email (secondary)' },
				{ key: 'phone', label: 'Phone' },
				{ key: 'mobile', label: 'Mobile' },
				{ key: 'fax', label: 'Fax' }
			]
		}
	];
	const MORE_SECTIONS: Array<{ title: string; fields: Field[] }> = [
		{
			title: 'Online & address',
			fields: [
				{ key: 'website', label: 'Website' },
				{ key: 'linkedin', label: 'LinkedIn' },
				{ key: 'address', label: 'Address', type: 'textarea', full: true }
			]
		},
		{
			title: 'Notes',
			fields: [{ key: 'notes', label: 'Card notes', type: 'textarea', full: true }]
		}
	];

	const fieldValue = (key: keyof BusinessCard): string => {
		const v = key in draft ? (draft as any)[key] : (card as any)[key];
		return v == null ? '' : String(v);
	};

	const onChange = (key: keyof BusinessCard, value: string) => {
		const normalized = value.trim() === '' ? null : value;
		const original = (card as any)[key] ?? null;
		const isSame =
			normalized === original || (normalized == null && (original == null || original === ''));
		const next = { ...draft } as Record<string, unknown>;
		if (isSame) delete next[key as string];
		else next[key as string] = normalized;
		draft = next as Partial<BusinessCard>;
	};

	const close = () => {
		open = false;
		onclose();
	};

	// Escape, the overlay and the close button all come here: unsaved edits ask first.
	const requestClose = () => {
		if (dirty) confirmDiscard = true;
		else close();
	};

	const handleSave = async () => {
		if (!dirty) return;
		saving = true;
		try {
			const updated = await updateBusinessCard(localStorage.token, card.id, draft);
			toast.success($i18n.t('Saved'));
			draft = {};
			onupdated(updated);
		} catch (err) {
			toast.error(`${err}`);
		} finally {
			saving = false;
		}
	};

	const handleSync = async () => {
		if (!card.k4mi_document_id) return;
		syncing = true;
		try {
			await syncBusinessCardFromK4mi(localStorage.token, card.id);
			toast.success($i18n.t('Syncing from K4mi…'));
			setTimeout(close, 600);
		} catch (err) {
			toast.error(`${err}`);
		} finally {
			syncing = false;
		}
	};

	const handleMarkReviewed = async () => {
		marking = true;
		try {
			// Save any pending edits first so "reviewed" reflects what's on screen.
			if (dirty) {
				const saved = await updateBusinessCard(localStorage.token, card.id, draft);
				draft = {};
				card = saved;
			}
			const updated = await markBusinessCardReviewed(localStorage.token, card.id);
			toast.success($i18n.t('Marked as reviewed'));
			onupdated(updated);
		} catch (err) {
			toast.error(`${err}`);
		} finally {
			marking = false;
		}
	};

	const handleReprocess = async () => {
		if (!card.k4mi_document_id) return;
		reprocessing = true;
		try {
			await reprocessBusinessCard(localStorage.token, card.id);
			toast.success($i18n.t('Re-extraction queued'));
			setTimeout(close, 600);
		} catch (err) {
			toast.error(`${err}`);
		} finally {
			reprocessing = false;
		}
	};

	const formatK4miNotes = (notes: unknown): Array<{ text: string; created: string }> => {
		if (!Array.isArray(notes)) return [];
		return notes
			.map((n) => {
				if (typeof n === 'string') return { text: n, created: '' };
				if (n && typeof n === 'object') {
					const obj = n as { text?: unknown; created?: unknown };
					return { text: String(obj.text ?? ''), created: String(obj.created ?? '') };
				}
				return { text: '', created: '' };
			})
			.filter((n) => n.text);
	};

	const k4miNotes = $derived(formatK4miNotes(card.k4mi_notes));
	const status = $derived(
		card.processing_status === 'processing' || card.processing_status === 'pending'
			? card.processing_status
			: card.processing_status === 'failed'
				? 'failed'
				: card.needs_review
					? 'needs_review'
					: 'ok'
	);

	// Iframes / <img> can't send `Authorization: Bearer …` and /api/business-cards/* needs it:
	// fetch the preview with the header and show a blob URL.
	let previewUrl = $state<string | null>(null);
	let previewMode = $state<'image' | 'iframe'>('image');
	let previewError = $state(false);
	let previewExpanded = $state(false);
	let lastFetchedFor: number | null = null;

	const loadPreview = async (cardId: number | null, hasDoc: boolean) => {
		if (cardId === lastFetchedFor) return;
		if (previewUrl) {
			revokeBlobUrl(previewUrl);
			previewUrl = null;
		}
		previewMode = 'image';
		previewError = false;
		previewExpanded = false;
		lastFetchedFor = cardId;
		if (!cardId || !hasDoc) return;
		const token = typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null;
		const result = await fetchAsBlobUrl(getBusinessCardPreviewUrl(cardId), token);
		if (result && lastFetchedFor === cardId) {
			previewUrl = result.url;
			// Pick the mode from the content type so PDFs skip the <img> → onerror → <iframe> step.
			if (!result.contentType.startsWith('image/')) previewMode = 'iframe';
		} else if (lastFetchedFor === cardId) {
			previewError = true;
		}
	};

	$effect(() => {
		loadPreview(card?.id ?? null, !!card?.k4mi_document_id);
	});

	onDestroy(() => revokeBlobUrl(previewUrl));

	const handleKeydown = (e: KeyboardEvent) => {
		if ((e.metaKey || e.ctrlKey) && e.key === 's') {
			e.preventDefault();
			if (dirty) handleSave();
		}
	};
</script>

<svelte:window onkeydown={handleKeydown} />

{#snippet fieldGrid(fields: Field[])}
	<div class="grid grid-cols-[repeat(auto-fit,minmax(min(11rem,100%),1fr))] gap-3">
		{#each fields as f}
			<div class={cn('grid gap-1.5', f.full && 'col-span-full')}>
				<Label for="bc-{String(f.key)}" class="text-[13px]">{$i18n.t(f.label)}</Label>
				{#if f.type === 'textarea'}
					<Textarea
						id="bc-{String(f.key)}"
						rows={2}
						value={fieldValue(f.key)}
						oninput={(e) => onChange(f.key, e.currentTarget.value)}
					/>
				{:else}
					<Input
						id="bc-{String(f.key)}"
						class="h-8"
						value={fieldValue(f.key)}
						placeholder={$i18n.t('Not on the card')}
						oninput={(e) => onChange(f.key, e.currentTarget.value)}
					/>
				{/if}
			</div>
		{/each}
	</div>
{/snippet}

<!-- Function binding: the sheet's close button, Escape and the overlay all call the setter,
	 which asks before dropping unsaved edits; the sheet stays open until close() runs. -->
<Sheet.Root
	bind:open={
		() => open,
		(v) => {
			if (v) open = true;
			else requestClose();
		}
	}
>
	<Sheet.Content
		side="right"
		class={cn(
			'flex w-full flex-col gap-0 p-0',
			previewExpanded ? 'data-[side=right]:sm:max-w-3xl' : 'data-[side=right]:sm:max-w-[30rem]'
		)}
	>
		<Sheet.Header class="gap-1.5 p-4 pr-12">
			<div class="flex items-center gap-3">
				<span
					class="inline-flex size-10 shrink-0 items-center justify-center rounded-full bg-muted text-sm font-medium"
				>
					{(card.full_name || '?')
						.split(/\s+/)
						.filter(Boolean)
						.slice(0, 2)
						.map((p) => p[0]?.toUpperCase())
						.join('') || '?'}
				</span>
				<div class="min-w-0">
					<Sheet.Title class="truncate">{card.full_name || $i18n.t('Untitled card')}</Sheet.Title>
					{#if card.job_title || card.company_name}
						<Sheet.Description class="truncate">
							{[card.job_title, card.company_name].filter(Boolean).join(' · ')}
						</Sheet.Description>
					{/if}
				</div>
			</div>

			<div class="mt-1.5 flex flex-wrap items-center gap-1.5">
				<StatusBadge kind="extraction" {status} />
				{#if card.confidence_score != null}
					<Badge variant="outline" title={$i18n.t('Extraction confidence')}>
						{Math.round(Number(card.confidence_score) * 100)}% {$i18n.t('confidence')}
					</Badge>
				{/if}
				{#if card.user_corrected}
					<Badge variant="outline" title={$i18n.t('Manually edited — DB is authoritative')}>
						<Pencil />{$i18n.t('User-edited')}
					</Badge>
				{/if}
			</div>

			<div class="mt-1.5 flex flex-wrap items-center gap-1.5">
				{#if card.k4mi_document_id}
					<Button
						variant="outline"
						size="xs"
						href={k4miDocHref(card.k4mi_document_id)}
						target="_blank"
						rel="noopener noreferrer"
					>
						<ExternalLink />{$i18n.t('Open in K4mi')}
					</Button>
					<Button variant="outline" size="xs" onclick={handleSync} disabled={syncing}>
						{#if syncing}<Spinner />{:else}<RefreshCw />{/if}
						{$i18n.t('Sync from K4mi')}
					</Button>
					<Button variant="outline" size="xs" onclick={handleReprocess} disabled={reprocessing}>
						{#if reprocessing}<Spinner />{:else}<RotateCcw />{/if}
						{$i18n.t('Reprocess')}
					</Button>
				{/if}
				<Tip content={$i18n.t('Delete')}>
					<Button
						variant="ghost"
						size="icon-xs"
						class="text-destructive hover:bg-destructive/10 hover:text-destructive"
						aria-label={$i18n.t('Delete')}
						onclick={() => ondeleterequest(card)}
					>
						<Trash2 />
					</Button>
				</Tip>
			</div>
		</Sheet.Header>

		<div class="flex flex-1 flex-col gap-5 overflow-y-auto px-4 pb-4">
			<Separator />

			{#if previewUrl || previewError}
				<section class="grid gap-2">
					<div class="flex items-center justify-between">
						<h3 class="text-sm font-medium">{$i18n.t('Original document')}</h3>
						<div class="flex items-center gap-1">
							<Button
								variant="ghost"
								size="xs"
								onclick={() => (previewExpanded = !previewExpanded)}
							>
								{#if previewExpanded}<Minimize2 />{$i18n.t('Collapse')}{:else}<Maximize2 />{$i18n.t(
										'Expand'
									)}{/if}
							</Button>
						</div>
					</div>
					<div
						class={cn(
							'flex items-center justify-center overflow-hidden rounded-md border bg-muted',
							previewExpanded ? 'min-h-[60vh]' : 'h-[240px]'
						)}
					>
						{#if previewError}
							<div class="p-6 text-center text-sm text-muted-foreground">
								<p>{$i18n.t('Could not load the original document.')}</p>
								<p class="mt-1 text-xs">
									{$i18n.t('Check that bc-api can reach K4mi and that the document still exists.')}
								</p>
								{#if card.k4mi_document_id}
									<a
										class="mt-2 inline-block text-xs text-link underline-offset-4 hover:underline"
										href={k4miDocHref(card.k4mi_document_id)}
										target="_blank"
										rel="noopener noreferrer">{$i18n.t('Open in K4mi instead →')}</a
									>
								{/if}
							</div>
						{:else if previewMode === 'image'}
							<img
								src={previewUrl}
								alt={card.full_name || 'Business card'}
								class="max-h-full max-w-full object-contain"
								onerror={() => (previewMode = 'iframe')}
							/>
						{:else}
							<iframe
								src={previewUrl}
								class="h-full w-full"
								title={card.full_name || 'Business card preview'}
								onerror={() => (previewError = true)}
							></iframe>
						{/if}
					</div>
				</section>
			{/if}

			{#each MAIN_SECTIONS as section}
				<section class="grid gap-3">
					<h3 class="text-sm font-medium">{$i18n.t(section.title, { context: 'gnos3' })}</h3>
					{@render fieldGrid(section.fields)}
				</section>
			{/each}

			<Collapsible.Root class="grid gap-3">
				<Collapsible.Trigger
					class="group flex items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground"
				>
					<ChevronRight class="size-4 transition-transform group-data-[state=open]:rotate-90" />
					{$i18n.t('Online & address')} · {$i18n.t('Notes', { context: 'gnos3' })} · {$i18n.t('K4mi')} · {$i18n.t(
						'Extraction metadata'
					)}
				</Collapsible.Trigger>
				<Collapsible.Content class="grid gap-5">
					{#each MORE_SECTIONS as section}
						<section class="grid gap-3">
							<h3 class="text-sm font-medium">{$i18n.t(section.title, { context: 'gnos3' })}</h3>
							{@render fieldGrid(section.fields)}
						</section>
					{/each}

					<section class="grid gap-2">
						<h3 class="text-sm font-medium">{$i18n.t('K4mi document notes')}</h3>
						{#if k4miNotes.length === 0}
							<p class="text-sm text-muted-foreground">
								{$i18n.t(
									'No K4mi notes on this document yet. Add notes in K4mi and click "Sync from K4mi" above to pull them in.'
								)}
							</p>
						{:else}
							<ul class="grid gap-2">
								{#each k4miNotes as n}
									<li class="rounded-md border bg-muted/50 px-3 py-2 text-sm">
										<p class="whitespace-pre-wrap">{n.text}</p>
										{#if n.created}
											<p class="mt-1 text-xs text-muted-foreground">
												{new Date(n.created).toLocaleString()}
											</p>
										{/if}
									</li>
								{/each}
							</ul>
						{/if}
					</section>

					{#if Array.isArray(card.k4mi_tags) && card.k4mi_tags.length > 0}
						<section class="grid gap-2">
							<h3 class="text-sm font-medium">{$i18n.t('K4mi tags')}</h3>
							<div class="flex flex-wrap gap-1.5">
								{#each card.k4mi_tags as tag}
									<Badge variant="secondary">{tag}</Badge>
								{/each}
							</div>
						</section>
					{/if}

					{#if card.extraction_model}
						<section class="grid gap-2">
							<h3 class="text-sm font-medium">{$i18n.t('Extraction metadata')}</h3>
							<dl class="grid grid-cols-3 gap-x-3 gap-y-1.5 text-sm">
								<dt class="text-muted-foreground">{$i18n.t('Model')}</dt>
								<dd class="col-span-2 font-mono text-[13px] break-all">{card.extraction_model}</dd>
								{#if card.created_at}
									<dt class="text-muted-foreground">{$i18n.t('Created')}</dt>
									<dd class="col-span-2">{new Date(card.created_at).toLocaleString()}</dd>
								{/if}
								{#if card.updated_at}
									<dt class="text-muted-foreground">{$i18n.t('Updated')}</dt>
									<dd class="col-span-2">{new Date(card.updated_at).toLocaleString()}</dd>
								{/if}
							</dl>
						</section>
					{/if}
				</Collapsible.Content>
			</Collapsible.Root>
		</div>

		<Sheet.Footer class="mt-auto flex-row flex-wrap items-center gap-2 border-t p-4">
			<span class="mr-auto inline-flex items-center gap-1.5 text-sm text-muted-foreground">
				{#if dirty}
					<span class="size-1.5 rounded-full bg-warning"></span>{$i18n.t('Unsaved changes')}
				{:else}
					{$i18n.t('All changes saved')}
				{/if}
			</span>
			<Button variant="outline" size="sm" onclick={requestClose}>{$i18n.t('Close')}</Button>
			{#if card.needs_review}
				<Tip content={$i18n.t('Clear the needs-review flag and remove the tag in K4mi')}>
					<Button size="sm" onclick={handleMarkReviewed} disabled={marking || saving}>
						{#if marking}<Spinner />{:else}<Check />{/if}
						{dirty ? $i18n.t('Save & mark reviewed') : $i18n.t('Mark reviewed')}
					</Button>
				</Tip>
				{#if dirty}
					<Button variant="secondary" size="sm" onclick={handleSave} disabled={saving}>
						{saving ? $i18n.t('Saving…') : $i18n.t('Save')}
					</Button>
				{/if}
			{:else}
				<Tip content={$i18n.t('Cmd/Ctrl + S')}>
					<Button size="sm" onclick={handleSave} disabled={!dirty || saving}>
						{#if saving}<Spinner />{/if}
						{saving ? $i18n.t('Saving…') : $i18n.t('Save')}
					</Button>
				</Tip>
			{/if}
		</Sheet.Footer>
	</Sheet.Content>
</Sheet.Root>

<ConfirmDialog
	bind:open={confirmDiscard}
	title={$i18n.t('Discard unsaved changes?')}
	description={$i18n.t('Your edits to this card will be lost.')}
	confirmLabel={$i18n.t('Discard')}
	destructive
	onconfirm={() => {
		draft = {};
		close();
	}}
/>
