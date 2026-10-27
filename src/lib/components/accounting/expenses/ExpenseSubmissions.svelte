<script lang="ts">
	import { onMount, onDestroy, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import Eye from '@lucide/svelte/icons/eye';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Check from '@lucide/svelte/icons/check';
	import X from '@lucide/svelte/icons/x';
	import Luggage from '@lucide/svelte/icons/luggage';
	import CreditCard from '@lucide/svelte/icons/credit-card';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import Inbox from '@lucide/svelte/icons/inbox';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';
	import FilePlus from '@lucide/svelte/icons/file-plus';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import Info from '@lucide/svelte/icons/info';
	import FileDown from '@lucide/svelte/icons/file-down';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { badgeVariants, Badge } from '$lib/components/ui/badge/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as ToggleGroup from '$lib/components/ui/toggle-group/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';
	import {
		listCompanyExpenses,
		approveExpense,
		rejectExpense,
		markReimbursed,
		fetchReceipt,
		updateExpense,
		getCategories,
		type ExpenseItem,
		type ExpenseCategory
	} from '$lib/apis/expenses';
	import { createExpenseSheetFromItems } from '$lib/apis/accounting';

	const i18n: any = getContext('i18n');
	export let companyId: number;
	// Called after anything that changes what awaits review (the page's badge).
	export let onChanged: () => void = () => {};
	// Called when the server answers 403: the user is not an approver here.
	export let onForbidden: () => void = () => {};

	let rawItems: ExpenseItem[] = [];
	let loading = true;
	let loadError = '';
	let busyId: number | null = null;

	// An approved expense either goes on a reimbursement sheet (the employee paid)
	// or is simply closed (company card / record only: nothing is owed).
	const bundlable = (i: ExpenseItem) =>
		i.status === 'approved' && !i.expense_sheet_id && i.reimbursable;
	const closable = (i: ExpenseItem) =>
		i.status === 'approved' && !i.expense_sheet_id && !i.reimbursable;

	type View = {
		key: string;
		label: string;
		status: string;
		keep?: (i: ExpenseItem) => boolean;
	};
	const VIEWS: View[] = [
		{ key: 'submitted', label: 'To review', status: 'submitted' },
		{
			key: 'approved',
			label: 'To reimburse',
			status: 'approved',
			keep: (i) => i.reimbursable || !!i.expense_sheet_id
		},
		{ key: 'to_close', label: 'To close', status: 'approved', keep: closable },
		{ key: 'reimbursed', label: 'Reimbursed', status: 'reimbursed' },
		{ key: 'rejected', label: 'Rejected', status: 'rejected' },
		{ key: 'all', label: 'All', status: '' }
	];
	const viewOf = (key: string) => VIEWS.find((v) => v.key === key) ?? VIEWS[0];
	let viewKey = 'submitted';
	$: view = viewOf(viewKey);
	$: items = view.keep ? rawItems.filter(view.keep) : rawItems;
	// In "To reimburse": how many approved expenses wait in "To close" instead.
	$: toCloseCount = viewKey === 'approved' ? rawItems.filter(closable).length : 0;

	// Bundling (only in the "To reimburse" view): select approved, un-bundled,
	// reimbursable items for a single employee and create a reimbursement sheet.
	let selected = new Set<number>();
	let bundling = false;

	$: selectableItems = items.filter(bundlable);
	$: selectedItems = items.filter((i) => selected.has(i.id));
	$: selectedEmployeeId = selectedItems.length ? selectedItems[0].employee_id : null;
	$: mixedEmployees = new Set(selectedItems.map((i) => i.employee_id)).size > 1;

	function toggle(id: number) {
		const next = new Set(selected);
		next.has(id) ? next.delete(id) : next.add(id);
		selected = next;
	}

	// One-click: select every selectable item in the same trip (same employee).
	function selectTrip(item: ExpenseItem) {
		if (!item.report_title) return;
		const next = new Set(selected);
		for (const i of selectableItems) {
			if (i.report_title === item.report_title && i.employee_id === item.employee_id) {
				next.add(i.id);
			}
		}
		selected = next;
	}

	async function bundle() {
		if (!selectedItems.length) return;
		if (mixedEmployees) {
			toast.error($i18n.t('Select expenses for a single employee to bundle'));
			return;
		}
		bundling = true;
		try {
			const sheet = await createExpenseSheetFromItems(companyId, {
				employee_id: selectedEmployeeId as number,
				expense_item_ids: selectedItems.map((i) => i.id)
			});
			toast.success(
				$i18n.t('Reimbursement sheet {{reference}} created', { reference: sheet.reference })
			);
			onChanged();
			goto(`/accounting/company/${companyId}/expenses/${sheet.id}`);
		} catch (e: any) {
			toast.error(e?.detail ?? e?.message ?? $i18n.t('Could not bundle'));
		} finally {
			bundling = false;
		}
	}

	// Receipt preview modal. What it can show follows the type the server sent
	// (a phone's HEIC photo can't be shown by most browsers: offer a download).
	let preview: { url: string; type: string; filename: string } | null = null;
	const SHOWABLE_IMAGES = [
		'image/jpeg',
		'image/png',
		'image/gif',
		'image/webp',
		'image/avif',
		'image/bmp'
	];
	const kindOf = (type: string, filename: string): 'pdf' | 'image' | 'other' => {
		if (type === 'application/pdf') return 'pdf';
		if (SHOWABLE_IMAGES.includes(type)) return 'image';
		// No useful type from the server: fall back on the file name.
		if (!type || type === 'application/octet-stream') {
			const ext = filename.toLowerCase().split('.').pop() ?? '';
			if (ext === 'pdf') return 'pdf';
			if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'avif', 'bmp'].includes(ext)) return 'image';
		}
		return 'other';
	};
	$: previewKind = preview ? kindOf(preview.type, preview.filename) : null;

	// ── Finance correction ──────────────────────────────────────────────
	// Reviewers fix employee mistakes (wrong category, amount, tax, currency)
	// without bouncing the claim back. Mirrors the backend rule: editable until
	// the money moves. The server additionally rejects edits once the parent
	// sheet's journal entry is built — surfaced via its 409 message.
	const EDITABLE_STATUSES = ['draft', 'submitted', 'approved'];
	let categories: ExpenseCategory[] = [];
	let editing: ExpenseItem | null = null;
	let saving = false;
	let form = {
		expense_date: '',
		merchant: '',
		description: '',
		category_id: '' as string,
		currency: '',
		amount: '',
		tax_amount: '',
		payment_method: 'personal',
		reimbursable: true
	};

	function canEdit(item: ExpenseItem): boolean {
		return EDITABLE_STATUSES.includes(item.status);
	}

	async function openEdit(item: ExpenseItem) {
		editing = item;
		form = {
			expense_date: item.expense_date ?? '',
			merchant: item.merchant ?? '',
			description: item.description ?? '',
			category_id: item.category_id != null ? String(item.category_id) : '',
			currency: item.currency ?? '',
			amount: item.amount ?? '',
			tax_amount: item.tax_amount ?? '',
			payment_method: item.payment_method ?? 'personal',
			reimbursable: item.reimbursable
		};
		if (!categories.length) {
			try {
				categories = await getCategories(companyId);
			} catch {
				/* non-fatal — the category dropdown just stays empty */
			}
		}
	}

	function closeEdit() {
		editing = null;
	}

	async function saveEdit() {
		if (!editing) return;
		saving = true;
		try {
			// Send only what actually changed so a PATCH never clobbers a field
			// the reviewer didn't touch.
			const before = editing;
			const payload: Record<string, any> = {};
			if (form.expense_date && form.expense_date !== before.expense_date)
				payload.expense_date = form.expense_date;
			if (form.merchant.trim() && form.merchant !== before.merchant)
				payload.merchant = form.merchant.trim();
			if (form.description !== before.description) payload.description = form.description;
			const catId = form.category_id === '' ? null : Number(form.category_id);
			if (catId !== (before.category_id ?? null) && catId !== null) payload.category_id = catId;
			if (form.currency && form.currency.toUpperCase() !== before.currency)
				payload.currency = form.currency.toUpperCase();
			if (form.amount !== '' && form.amount !== before.amount) payload.amount = form.amount;
			if (form.tax_amount !== (before.tax_amount ?? '')) payload.tax_amount = form.tax_amount || 0;
			if (form.payment_method !== before.payment_method)
				payload.payment_method = form.payment_method;
			if (form.reimbursable !== before.reimbursable) payload.reimbursable = form.reimbursable;

			if (!Object.keys(payload).length) {
				closeEdit();
				return;
			}
			await updateExpense(editing.id, payload as any);
			toast.success($i18n.t('Expense updated'));
			closeEdit();
			await load();
			onChanged();
		} catch (e: any) {
			toast.error(e?.detail ?? e?.message ?? $i18n.t('Could not save changes'));
		} finally {
			saving = false;
		}
	}

	// The view is a single-choice toggle group; clicking the pressed item would
	// clear it, so an empty value snaps back to the current view.
	let filterValue = 'submitted';
	$: if (!filterValue) filterValue = viewKey;

	function fmtMoney(amount: string, currency: string): string {
		const n = Number(amount);
		return `${currency} ${isNaN(n) ? amount : n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
	}

	// Switching views quickly can leave an older request to answer last: only
	// the latest one is applied.
	let loadSeq = 0;
	async function load() {
		const seq = ++loadSeq;
		loading = true;
		loadError = '';
		try {
			// viewOf(viewKey), not `view`: setView() calls this before `$:` reruns.
			const res = await listCompanyExpenses(companyId, {
				status: viewOf(viewKey).status || undefined
			});
			if (seq !== loadSeq) return;
			rawItems = res.items;
			// Drop selections that are no longer selectable (bundled/paid elsewhere).
			selected = new Set(
				[...selected].filter((id) => rawItems.some((i) => i.id === id && bundlable(i)))
			);
		} catch (e: any) {
			if (seq !== loadSeq) return;
			if (e?.status === 403) onForbidden();
			loadError = e?.message ?? $i18n.t('Failed to load submissions');
			toast.error(loadError);
		} finally {
			if (seq === loadSeq) loading = false;
		}
	}

	async function viewReceipt(item: ExpenseItem) {
		try {
			const { url, type } = await fetchReceipt(item.id);
			closePreview();
			preview = { url, type, filename: item.receipt_filename || 'receipt' };
		} catch (e: any) {
			toast.error(e?.message ?? $i18n.t('Could not load receipt'));
		}
	}

	function closePreview() {
		if (preview) URL.revokeObjectURL(preview.url);
		preview = null;
	}

	async function doApprove(item: ExpenseItem) {
		busyId = item.id;
		try {
			await approveExpense(item.id);
			toast.success($i18n.t('Expense approved'));
			await load();
			onChanged();
		} catch (e: any) {
			toast.error(e?.message ?? $i18n.t('Could not approve'));
		} finally {
			busyId = null;
		}
	}

	// Close: an approved expense that owes the employee nothing (company card or
	// record only). It moves to Reimbursed without a journal entry.
	let closeTarget: ExpenseItem | null = null;
	let showCloseConfirm = false;

	function askClose(item: ExpenseItem) {
		closeTarget = item;
		showCloseConfirm = true;
	}

	async function confirmClose() {
		const item = closeTarget;
		if (!item) return;
		busyId = item.id;
		try {
			await markReimbursed(item.id);
			toast.success($i18n.t('Expense closed'));
			await load();
			onChanged();
		} catch (e: any) {
			toast.error(e?.message ?? $i18n.t('Could not close the expense'));
		} finally {
			busyId = null;
		}
	}

	// Reject asks for a reason first (a dialog; the reason is required).
	let rejectTarget: ExpenseItem | null = null;
	let rejectReason = '';

	function doReject(item: ExpenseItem) {
		rejectTarget = item;
		rejectReason = '';
	}

	async function confirmReject() {
		const item = rejectTarget;
		const reason = rejectReason.trim();
		if (!item || !reason) return;
		busyId = item.id;
		try {
			await rejectExpense(item.id, reason);
			toast.success($i18n.t('Expense rejected'));
			rejectTarget = null;
			await load();
			onChanged();
		} catch (e: any) {
			toast.error(e?.message ?? $i18n.t('Could not reject'));
		} finally {
			busyId = null;
		}
	}

	function setView(key: string) {
		const sameRequest = viewOf(key).status === viewOf(viewKey).status;
		viewKey = key;
		filterValue = key;
		selected = new Set();
		// "To reimburse" and "To close" read the same list: no need to fetch again.
		if (!sameRequest || loadError) load();
	}

	onMount(load);
	onDestroy(() => {
		if (preview) URL.revokeObjectURL(preview.url);
	});
</script>

<div class="flex flex-col gap-4">
	<!-- Status filter -->
	<div class="flex flex-wrap items-center gap-2">
		<ToggleGroup.Root
			type="single"
			variant="outline"
			size="sm"
			class="max-w-full overflow-x-auto"
			bind:value={filterValue}
			onValueChange={(v) => {
				if (v) setView(v);
			}}
			aria-label={$i18n.t('Status')}
		>
			{#each VIEWS as v}
				<ToggleGroup.Item value={v.key} class="px-3">{$i18n.t(v.label)}</ToggleGroup.Item>
			{/each}
		</ToggleGroup.Root>
	</div>

	{#if viewKey === 'approved'}
		<p class="text-sm text-muted-foreground">
			{$i18n.t(
				"Select approved expenses for one employee and bundle them into a reimbursement sheet — that sheet posts the journal entry when it's approved & paid."
			)}
		</p>
		{#if toCloseCount > 0 && !loading}
			<Alert.Root>
				<Info />
				<Alert.Description>
					<p>
						{$i18n.t(
							'{{count}} approved expense(s) owe the employee nothing (company card or record only). They are closed, not reimbursed.',
							{ count: toCloseCount }
						)}
					</p>
					<Button variant="outline" size="xs" class="mt-1" onclick={() => setView('to_close')}>
						{$i18n.t('To close')}<ArrowRight />
					</Button>
				</Alert.Description>
			</Alert.Root>
		{/if}
	{:else if viewKey === 'to_close'}
		<p class="text-sm text-muted-foreground">
			{$i18n.t(
				'Approved expenses paid with a company card or kept for the record: nothing is owed to the employee. Closing one moves it to Reimbursed, without a journal entry.'
			)}
		</p>
	{/if}

	{#if loadError && !loading}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Could not load the submissions.')}</Alert.Title>
			<Alert.Description>
				<p>{loadError}</p>
				<Button variant="outline" size="sm" class="mt-2" onclick={load}>
					<RefreshCw />{$i18n.t('Retry')}
				</Button>
			</Alert.Description>
		</Alert.Root>
	{:else if loading}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(5) as _}<Skeleton class="h-9 w-full" />{/each}
		</div>
	{:else if items.length === 0}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><Inbox /></Empty.Media>
				<Empty.Title>
					{viewKey === 'submitted'
						? $i18n.t('Nothing awaiting review.')
						: $i18n.t('No expenses here.')}
				</Empty.Title>
			</Empty.Header>
		</Empty.Root>
	{:else}
		<div class="overflow-hidden rounded-md border">
			<Table.Root>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						{#if viewKey === 'approved'}
							<Table.Head class="w-10"><span class="sr-only">{$i18n.t('Select')}</span></Table.Head>
						{/if}
						<Table.Head>{$i18n.t('Employee')}</Table.Head>
						<Table.Head>{$i18n.t('Date')}</Table.Head>
						<Table.Head>{$i18n.t('Merchant')}</Table.Head>
						<Table.Head>{$i18n.t('Category')}</Table.Head>
						<Table.Head class="text-right">{$i18n.t('Amount')}</Table.Head>
						<Table.Head>{$i18n.t('Status')}</Table.Head>
						<Table.Head class="text-right"
							><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head
						>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each items as item (item.id)}
						{@const selectable = bundlable(item)}
						<Table.Row data-state={selected.has(item.id) ? 'selected' : undefined}>
							{#if viewKey === 'approved'}
								<Table.Cell>
									{#if selectable}
										<Checkbox
											checked={selected.has(item.id)}
											onCheckedChange={() => toggle(item.id)}
											aria-label="{$i18n.t('Select')} {item.merchant}"
										/>
									{/if}
								</Table.Cell>
							{/if}
							<Table.Cell>{item.employee_name ?? '—'}</Table.Cell>
							<Table.Cell class="text-muted-foreground tabular-nums">{item.expense_date}</Table.Cell
							>
							<Table.Cell class="max-w-[18rem] whitespace-normal">
								<div class="truncate font-medium">{item.merchant}</div>
								{#if item.description}
									<div class="truncate text-[13px] text-muted-foreground">{item.description}</div>
								{/if}
								{#if !item.has_receipt && item.mileage_distance}
									<div class="text-[13px] text-muted-foreground">
										{$i18n.t('Mileage')}: {item.mileage_distance} km{item.mileage_rate
											? ` × ${item.mileage_rate}`
											: ''}
									</div>
								{:else if !item.has_receipt && item.no_receipt_reason}
									<div class="text-[13px] text-muted-foreground">
										{$i18n.t('No receipt because')}: {item.no_receipt_reason}
									</div>
								{/if}
								{#if item.report_title}
									{#if viewKey === 'approved' && selectable}
										<button
											type="button"
											class="{badgeVariants({
												variant: 'secondary'
											})} mt-1 max-w-full cursor-pointer hover:bg-secondary/80"
											title={$i18n.t('Select all in this trip')}
											on:click={() => selectTrip(item)}
										>
											<Luggage /><span class="truncate">{item.report_title}</span>
										</button>
									{:else}
										<Badge variant="secondary" class="mt-1 max-w-full">
											<Luggage /><span class="truncate">{item.report_title}</span>
										</Badge>
									{/if}
								{/if}
							</Table.Cell>
							<Table.Cell class="text-muted-foreground">{item.category_label ?? '—'}</Table.Cell>
							<Table.Cell class="text-right">
								<div class="font-medium tabular-nums">{fmtMoney(item.amount, item.currency)}</div>
								{#if item.payment_method === 'company_card'}
									<div class="inline-flex items-center gap-1 text-[13px] text-muted-foreground">
										<CreditCard class="size-3.5" />{$i18n.t('company card')}
									</div>
								{:else if !item.reimbursable}
									<div class="text-[13px] text-muted-foreground">{$i18n.t('record only')}</div>
								{/if}
							</Table.Cell>
							<Table.Cell>
								<StatusBadge kind="expense" status={item.status} />
							</Table.Cell>
							<Table.Cell>
								<div class="flex items-center justify-end gap-1">
									{#if item.has_receipt}
										<Tip content={$i18n.t('Receipt')}>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label={$i18n.t('Receipt')}
												onclick={() => viewReceipt(item)}
											>
												<Eye />
											</Button>
										</Tip>
									{:else}
										<span
											class="inline-flex items-center gap-1 px-1 text-[13px] whitespace-nowrap text-muted-foreground"
										>
											<TriangleAlert class="size-3.5 text-warning" />{$i18n.t('no receipt')}
										</span>
									{/if}
									{#if canEdit(item)}
										<Tip content={$i18n.t('Correct this claim')}>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label={$i18n.t('Correct this claim')}
												onclick={() => openEdit(item)}
											>
												<Pencil />
											</Button>
										</Tip>
									{/if}
									{#if item.status === 'submitted'}
										<Button
											variant="outline"
											size="xs"
											disabled={busyId === item.id}
											onclick={() => doReject(item)}
										>
											<X />{$i18n.t('Reject')}
										</Button>
										<Button
											variant="outline"
											size="xs"
											disabled={busyId === item.id}
											onclick={() => doApprove(item)}
										>
											{#if busyId === item.id}<Spinner />{:else}<Check />{/if}{$i18n.t('Approve')}
										</Button>
									{:else if closable(item)}
										<Button
											variant="outline"
											size="xs"
											disabled={busyId === item.id}
											onclick={() => askClose(item)}
										>
											{#if busyId === item.id}<Spinner />{:else}<CircleCheck />{/if}{$i18n.t(
												'Close',
												{ context: 'expense' }
											)}
										</Button>
									{:else if item.status === 'approved' && item.expense_sheet_id}
										<Button
											variant="ghost"
											size="xs"
											class="text-link"
											href={`/accounting/company/${companyId}/expenses/${item.expense_sheet_id}`}
										>
											{$i18n.t('On sheet')}<ArrowRight />
										</Button>
									{/if}
								</div>
							</Table.Cell>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</div>
	{/if}

	<!-- Bulk bar: bundle the selected expenses -->
	{#if selected.size > 0}
		<div
			class="sticky bottom-4 z-10 mx-auto flex w-fit max-w-full flex-wrap items-center gap-2 rounded-lg border bg-card py-1.5 pr-1.5 pl-3 text-sm shadow-md"
		>
			<span>
				<span class="font-semibold tabular-nums">{selected.size}</span>
				{$i18n.t('selected')}
				{#if mixedEmployees}
					<span class="ml-1 inline-flex items-center gap-1 text-destructive">
						<CircleAlert class="size-3.5" />{$i18n.t('select one employee only')}
					</span>
				{:else if selectedItems.length}
					· {selectedItems[0].employee_name}
				{/if}
			</span>
			<Button size="xs" disabled={bundling || mixedEmployees} onclick={bundle}>
				{#if bundling}<Spinner />{:else}<FilePlus />{/if}
				{bundling ? $i18n.t('Bundling…') : $i18n.t('Bundle into reimbursement sheet')}
			</Button>
			<Tip content={$i18n.t('Clear')}>
				<Button
					variant="ghost"
					size="icon-xs"
					aria-label={$i18n.t('Clear')}
					onclick={() => (selected = new Set())}
				>
					<X />
				</Button>
			</Tip>
		</div>
	{/if}
</div>

<!-- Correct an expense -->
<Dialog.Root
	open={!!editing}
	onOpenChange={(v) => {
		if (!v) closeEdit();
	}}
>
	<Dialog.Content class="sm:max-w-lg">
		{#if editing}
			<Dialog.Header>
				<Dialog.Title>{$i18n.t('Correct expense')}</Dialog.Title>
				<Dialog.Description class="flex flex-wrap items-center gap-x-2 gap-y-1">
					<span>{editing.employee_name ?? $i18n.t('Employee')}</span>
					<StatusBadge kind="expense" status={editing.status} />
					{#if editing.expense_sheet_id}<span>{$i18n.t('on a reimbursement sheet')}</span>{/if}
				</Dialog.Description>
			</Dialog.Header>

			<div class="grid grid-cols-2 gap-4">
				<div class="grid gap-1.5">
					<Label for="exp-edit-date">{$i18n.t('Date')}</Label>
					<Input id="exp-edit-date" type="date" bind:value={form.expense_date} />
				</div>
				<div class="grid gap-1.5">
					<Label for="exp-edit-category">{$i18n.t('Category')}</Label>
					<NativeSelect.Root id="exp-edit-category" class="w-full" bind:value={form.category_id}>
						<NativeSelect.Option value="">— {$i18n.t('none')} —</NativeSelect.Option>
						{#each categories as c}
							<NativeSelect.Option value={String(c.id)}>{c.label}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
				<div class="col-span-2 grid gap-1.5">
					<Label for="exp-edit-merchant">{$i18n.t('Merchant')}</Label>
					<Input id="exp-edit-merchant" bind:value={form.merchant} />
				</div>
				<div class="col-span-2 grid gap-1.5">
					<Label for="exp-edit-desc">{$i18n.t('Description')}</Label>
					<Input id="exp-edit-desc" bind:value={form.description} />
				</div>
				<div class="grid gap-1.5">
					<Label for="exp-edit-currency">{$i18n.t('Currency')}</Label>
					<Input
						id="exp-edit-currency"
						class="uppercase"
						maxlength={3}
						bind:value={form.currency}
					/>
				</div>
				<div class="grid gap-1.5">
					<Label for="exp-edit-payment">{$i18n.t('Payment')}</Label>
					<NativeSelect.Root id="exp-edit-payment" class="w-full" bind:value={form.payment_method}>
						<NativeSelect.Option value="personal">{$i18n.t('Personal')}</NativeSelect.Option>
						<NativeSelect.Option value="company_card">{$i18n.t('Company card')}</NativeSelect.Option
						>
					</NativeSelect.Root>
				</div>
				<div class="grid gap-1.5">
					<Label for="exp-edit-amount">{$i18n.t('Total amount')}</Label>
					<Input
						id="exp-edit-amount"
						type="number"
						step="0.01"
						min="0"
						class="text-right tabular-nums"
						bind:value={form.amount}
					/>
				</div>
				<div class="grid gap-1.5">
					<Label for="exp-edit-tax">{$i18n.t('Tax amount')}</Label>
					<Input
						id="exp-edit-tax"
						type="number"
						step="0.01"
						min="0"
						class="text-right tabular-nums"
						bind:value={form.tax_amount}
					/>
				</div>
				<div class="col-span-2 flex items-center gap-2">
					<Checkbox
						id="exp-edit-reimbursable"
						checked={form.reimbursable}
						onCheckedChange={(v) => (form.reimbursable = v === true)}
					/>
					<Label for="exp-edit-reimbursable" class="font-normal">
						{$i18n.t('Reimbursable to the employee')}
					</Label>
				</div>
			</div>

			{#if editing.expense_sheet_id}
				<Alert.Root variant="warning">
					<TriangleAlert />
					<Alert.Description>
						{$i18n.t(
							"This expense is bundled on a reimbursement sheet — saving re-calculates that sheet's totals."
						)}
					</Alert.Description>
				</Alert.Root>
			{/if}

			<Dialog.Footer>
				<Button variant="outline" onclick={closeEdit}>{$i18n.t('Cancel')}</Button>
				<Button disabled={saving} onclick={saveEdit}>
					{#if saving}<Spinner />{/if}
					{saving ? $i18n.t('Saving…') : $i18n.t('Save changes')}
				</Button>
			</Dialog.Footer>
		{/if}
	</Dialog.Content>
</Dialog.Root>

<!-- Reject: a reason is required -->
<Dialog.Root
	open={!!rejectTarget}
	onOpenChange={(v) => {
		if (!v) rejectTarget = null;
	}}
>
	<Dialog.Content class="sm:max-w-lg">
		{#if rejectTarget}
			<Dialog.Header>
				<Dialog.Title>{$i18n.t('Reject this expense?')}</Dialog.Title>
				<Dialog.Description>
					{rejectTarget.merchant} · {fmtMoney(rejectTarget.amount, rejectTarget.currency)} · {rejectTarget.employee_name ??
						''}
				</Dialog.Description>
			</Dialog.Header>
			<div class="grid gap-1.5">
				<Label for="exp-reject-reason">{$i18n.t('Reason for rejection:')}</Label>
				<Textarea id="exp-reject-reason" rows={3} bind:value={rejectReason} />
			</div>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (rejectTarget = null)}>{$i18n.t('Cancel')}</Button>
				<Button
					disabled={!rejectReason.trim() || busyId === rejectTarget.id}
					onclick={confirmReject}
				>
					{#if busyId === rejectTarget.id}<Spinner />{/if}
					{$i18n.t('Reject')}
				</Button>
			</Dialog.Footer>
		{/if}
	</Dialog.Content>
</Dialog.Root>

<!-- Receipt preview -->
<Dialog.Root
	open={!!preview}
	onOpenChange={(v) => {
		if (!v) closePreview();
	}}
>
	<Dialog.Content class="max-h-[95vh] gap-3 sm:max-w-3xl">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Receipt')}</Dialog.Title>
			<Dialog.Description class="sr-only">{$i18n.t('Receipt preview')}</Dialog.Description>
		</Dialog.Header>
		{#if preview}
			{#if previewKind === 'pdf'}
				<iframe
					src={preview.url}
					title={$i18n.t('Receipt')}
					class="h-[80vh] w-full rounded-md border bg-muted"
				></iframe>
			{:else if previewKind === 'image'}
				<img
					src={preview.url}
					alt={$i18n.t('Receipt')}
					class="mx-auto max-h-[80vh] max-w-full rounded-md object-contain"
				/>
			{:else}
				<Empty.Root class="border border-dashed">
					<Empty.Header>
						<Empty.Media variant="icon"><FileDown /></Empty.Media>
						<Empty.Title>{$i18n.t("This file can't be shown here.")}</Empty.Title>
						<Empty.Description>{preview.filename}</Empty.Description>
					</Empty.Header>
					<Empty.Content>
						<Button variant="outline" size="sm" href={preview.url} download={preview.filename}>
							<FileDown />{$i18n.t('Download')}
						</Button>
					</Empty.Content>
				</Empty.Root>
			{/if}
		{/if}
	</Dialog.Content>
</Dialog.Root>

<ConfirmDialog
	bind:open={showCloseConfirm}
	title={$i18n.t('Close this expense?')}
	description={closeTarget
		? `${closeTarget.merchant} · ${fmtMoney(closeTarget.amount, closeTarget.currency)} — ${$i18n.t(
				'Nothing is owed to the employee. It moves to Reimbursed, without a journal entry.'
			)}`
		: ''}
	confirmLabel={$i18n.t('Close', { context: 'expense' })}
	onconfirm={confirmClose}
	oncancel={() => (closeTarget = null)}
/>
