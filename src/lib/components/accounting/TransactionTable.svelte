<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import { page as pageStore } from '$app/stores';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import { browser } from '$app/environment';

	import Search from '@lucide/svelte/icons/search';
	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';
	import Ellipsis from '@lucide/svelte/icons/ellipsis';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Eye from '@lucide/svelte/icons/eye';
	import Check from '@lucide/svelte/icons/check';
	import Sparkles from '@lucide/svelte/icons/sparkles';
	import Ban from '@lucide/svelte/icons/ban';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Scale from '@lucide/svelte/icons/scale';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import NotebookPen from '@lucide/svelte/icons/notebook-pen';
	import RotateCw from '@lucide/svelte/icons/rotate-cw';

	import {
		getTransactions,
		deleteTransaction,
		postTransaction,
		voidTransaction,
		getAccounts,
		bulkPostTransactions,
		bulkDeleteDrafts,
		getAccountingAiStatus,
		aiValidateTransaction
	} from '$lib/apis/accounting';
	import { getInvoice } from '$lib/apis/invoices';
	import { convertRowAmount } from '$lib/utils/currency';
	import { user, isAdmin } from '$lib/stores';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { Toggle } from '$lib/components/ui/toggle/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';
	import TablePagination from '$lib/components/gnos3-ui/TablePagination.svelte';
	import TransactionFormModal from '$lib/components/accounting/TransactionFormModal.svelte';
	import DocumentPreviewModal from '$lib/components/invoices/DocumentPreviewModal.svelte';

	const i18n: any = getContext('i18n');
	const displayCurrency = getContext<Writable<string>>('displayCurrency');
	const exchangeRates = getContext<Writable<any[]>>('exchangeRates');
	const companyCurrencyCtx = getContext<Writable<string>>('companyCurrency');

	export let companyId: number;

	// ─── Permissions (UX gating; backend enforces the real check) ──────────────────
	$: canWrite = $isAdmin || Boolean($user?.permissions?.modules?.accounting?.write);
	$: canPost = $isAdmin || Boolean($user?.permissions?.modules?.accounting?.post);
	$: canDelete = $isAdmin || Boolean($user?.permissions?.modules?.accounting?.admin);

	// ─── Data ────────────────────────────────────────────────────────────────────
	let transactions: any[] = [];
	let total = 0;
	let loading = true;
	let loadError = '';
	let accounts: any[] = [];

	// ─── Pagination ──────────────────────────────────────────────────────────────
	let currentPage = 1;
	const perPage = 20;

	// ─── Filters ─────────────────────────────────────────────────────────────────
	let filterType = '';
	let filterStatus = '';
	let filterDateFrom = '';
	let filterDateTo = '';
	let filterUnbalanced = false;
	let searchQuery = '';
	let searchDebounce: ReturnType<typeof setTimeout>;

	$: hasFilters = !!(
		filterType ||
		filterStatus ||
		filterDateFrom ||
		filterDateTo ||
		searchQuery ||
		filterUnbalanced
	);

	// ─── Expanded rows ───────────────────────────────────────────────────────────
	let expandedRows: Set<number> = new Set();

	// ─── AI validation ───────────────────────────────────────────────────────────
	let aiAvailable = false;
	let validatingId: number | null = null;

	// ─── Bulk selection ──────────────────────────────────────────────────────────
	let selectedIds: Set<number> = new Set();
	$: filteredTransactions = filterUnbalanced
		? transactions.filter((t) => isUnbalanced(t))
		: transactions;
	$: draftTransactions = filteredTransactions.filter((t) => t.status === 'draft');
	$: allDraftsSelected =
		draftTransactions.length > 0 && draftTransactions.every((t) => selectedIds.has(t.id));

	const toggleSelectAll = () => {
		if (allDraftsSelected) selectedIds = new Set();
		else selectedIds = new Set(draftTransactions.map((t) => t.id));
	};
	const toggleSelect = (id: number) => {
		if (selectedIds.has(id)) selectedIds.delete(id);
		else selectedIds.add(id);
		selectedIds = selectedIds;
	};

	const handleBulkPost = async () => {
		if (selectedIds.size === 0) return;
		try {
			const result = await bulkPostTransactions({
				company_id: companyId,
				transaction_ids: [...selectedIds]
			});
			toast.success(`${result?.posted ?? 0} ${$i18n.t('entries posted')}`);
			if (result?.skipped) {
				toast.warning(
					`${result.skipped} ${$i18n.t('not posted')}: ${(result.errors ?? []).slice(0, 3).join(' · ')}`
				);
			}
			selectedIds = new Set();
			await loadTransactions();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	let showBulkDeleteConfirm = false;

	const handleBulkDelete = async () => {
		if (selectedIds.size === 0) return;
		try {
			const result = await bulkDeleteDrafts(companyId, [...selectedIds]);
			toast.success(`${result?.deleted ?? 0} ${$i18n.t('drafts deleted')}`);
			selectedIds = new Set();
			await loadTransactions();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	// ─── Modal state ─────────────────────────────────────────────────────────────
	let showFormModal = false;
	let editTransaction: any = null;

	// ─── Invoice preview ─────────────────────────────────────────────────────────
	let showPreview = false;
	let previewInvoice: any = null;
	let previewLoading = false;

	const openInvoicePreview = async (invoiceId: number) => {
		previewLoading = true;
		try {
			const inv = await getInvoice(localStorage.token, invoiceId);
			previewInvoice = inv;
			showPreview = true;
		} catch (err) {
			toast.error($i18n.t('Failed to load invoice'));
		}
		previewLoading = false;
	};

	// ─── Delete confirmation ─────────────────────────────────────────────────────
	let showDeleteConfirm = false;
	let deleteTarget: any = null;

	// ─── Post/Void confirmation ──────────────────────────────────────────────────
	let showPostConfirm = false;
	let postTarget: any = null;
	let showVoidConfirm = false;
	let voidTarget: any = null;

	// ─── Labels ──────────────────────────────────────────────────────────────────
	// Entry types are plain outline badges (design system → Status map): colour is kept for status.
	const TYPE_LABELS: Record<string, string> = {
		invoice: 'Invoice',
		bill: 'Bill',
		payment_in: 'Payment In',
		payment_out: 'Payment Out',
		others: 'Others',
		payment: 'Payment',
		journal: 'Journal',
		adjustment: 'Adjustment'
	};

	// ─── Formatting helpers ──────────────────────────────────────────────────────
	const formatCurrency = (val: any) => {
		if (val === null || val === undefined) return '-';
		return parseFloat(val).toLocaleString(undefined, {
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		});
	};

	const isUnbalanced = (txn: any): boolean => {
		if (!txn.lines || txn.lines.length < 2) return true;
		const totalDebit = txn.lines.reduce(
			(s: number, l: any) => s + parseFloat(String(l.debit ?? 0)),
			0
		);
		const totalCredit = txn.lines.reduce(
			(s: number, l: any) => s + parseFloat(String(l.credit ?? 0)),
			0
		);
		return Math.abs(totalDebit - totalCredit) > 0.005;
	};

	const lineTotals = (txn: any) => ({
		d: (txn.lines ?? []).reduce((s: number, l: any) => s + parseFloat(String(l.debit ?? 0)), 0),
		c: (txn.lines ?? []).reduce((s: number, l: any) => s + parseFloat(String(l.credit ?? 0)), 0)
	});

	const formatDate = (val: any) => {
		if (!val) return '-';
		return dayjs(val).format('YYYY-MM-DD');
	};

	// ─── Currency conversion ─────────────────────────────────────────────────────
	$: nativeCurrency = $companyCurrencyCtx || 'EUR';

	// An entry is shown in the display currency converted FROM ITS OWN currency;
	// in the company currency it uses the rate the entry was booked at, exactly
	// as the ledger values it.
	const cvt = (amount: any, date: string | undefined, txn: any) =>
		convertRowAmount(
			amount,
			txn?.currency,
			$displayCurrency,
			nativeCurrency,
			$exchangeRates ?? [],
			date,
			txn?.exchange_rate
		);

	// ─── Data loading ────────────────────────────────────────────────────────────
	const loadTransactions = async () => {
		loading = true;
		loadError = '';
		try {
			const params: Record<string, any> = {
				limit: perPage,
				offset: (currentPage - 1) * perPage,
				company_id: companyId
			};
			if (filterType) params.type = filterType;
			if (filterStatus) params.status = filterStatus;
			if (filterDateFrom) params.date_from = filterDateFrom;
			if (filterDateTo) params.date_to = filterDateTo;
			if (searchQuery) params.search = searchQuery;

			// Check for invoice_id filter from URL
			if (browser) {
				const urlInvoiceId = $pageStore.url.searchParams.get('invoice_id');
				if (urlInvoiceId) params.invoice_id = parseInt(urlInvoiceId);
			}

			const res = await getTransactions(params);
			if (Array.isArray(res)) {
				transactions = res;
				total = res.length;
			} else if (res && res.transactions) {
				transactions = res.transactions;
				total = res.total ?? res.transactions.length;
			} else {
				transactions = [];
				total = 0;
			}
		} catch (err: any) {
			loadError = `${err?.detail ?? err}`;
			toast.error($i18n.t('Failed to load transactions') + ': ' + (err?.detail ?? err));
		}
		loading = false;
	};

	const loadAccounts = async () => {
		try {
			const res = await getAccounts({ company_id: companyId });
			accounts = Array.isArray(res) ? res : (res?.accounts ?? []);
		} catch {
			accounts = [];
		}
	};

	// ─── Search debounce ─────────────────────────────────────────────────────────
	const handleSearch = () => {
		clearTimeout(searchDebounce);
		searchDebounce = setTimeout(() => {
			currentPage = 1;
			loadTransactions();
		}, 300);
	};

	// ─── Filter changes ──────────────────────────────────────────────────────────
	const handleFilterChange = () => {
		currentPage = 1;
		loadTransactions();
	};

	const clearFilters = () => {
		filterType = '';
		filterStatus = '';
		filterDateFrom = '';
		filterDateTo = '';
		filterUnbalanced = false;
		searchQuery = '';
		handleFilterChange();
	};

	// ─── Expand/collapse ─────────────────────────────────────────────────────────
	const toggleExpand = (id: number) => {
		if (expandedRows.has(id)) {
			expandedRows.delete(id);
		} else {
			expandedRows.add(id);
		}
		expandedRows = expandedRows;
	};

	// ─── Actions ─────────────────────────────────────────────────────────────────
	const openNewEntry = () => {
		editTransaction = null;
		showFormModal = true;
	};

	const openEdit = (txn: any) => {
		editTransaction = txn;
		showFormModal = true;
	};

	const confirmPost = (txn: any) => {
		postTarget = txn;
		showPostConfirm = true;
	};

	const handlePost = async () => {
		if (!postTarget) return;
		try {
			await postTransaction(postTarget.id);
			toast.success($i18n.t('Transaction posted'));
			loadTransactions();
		} catch (err: any) {
			toast.error($i18n.t('Failed to post') + ': ' + (err?.detail ?? err?.message ?? String(err)));
		}
		postTarget = null;
	};

	const confirmVoid = (txn: any) => {
		voidTarget = txn;
		showVoidConfirm = true;
	};

	const handleVoid = async () => {
		if (!voidTarget) return;
		try {
			const result = await voidTransaction(voidTarget.id);
			const draftId = result?.correction_draft?.id;
			if (draftId) {
				toast.success(
					$i18n.t('Entry voided. Correction draft') +
						` #${draftId} ` +
						$i18n.t('created — edit and re-post when ready.')
				);
			} else {
				toast.success($i18n.t('Transaction voided'));
			}
			loadTransactions();
		} catch (err: any) {
			toast.error($i18n.t('Failed to void') + ': ' + (err?.detail ?? err));
		}
		voidTarget = null;
	};

	const confirmDelete = (txn: any) => {
		deleteTarget = txn;
		showDeleteConfirm = true;
	};

	const handleDelete = async () => {
		if (!deleteTarget) return;
		try {
			await deleteTransaction(deleteTarget.id);
			toast.success($i18n.t('Transaction deleted'));
			if (transactions.length === 1 && currentPage > 1) {
				currentPage -= 1;
			}
			loadTransactions();
		} catch (err: any) {
			toast.error($i18n.t('Failed to delete') + ': ' + (err?.detail ?? err));
		}
		deleteTarget = null;
	};

	const handleFormSave = () => {
		loadTransactions();
	};

	// ─── Pagination reactivity ───────────────────────────────────────────────────
	let mounted = false;

	$: if (mounted && currentPage) {
		loadTransactions();
	}

	// ─── Lifecycle ───────────────────────────────────────────────────────────────
	async function handleAiValidate(txnId: number) {
		validatingId = txnId;
		try {
			const result = await aiValidateTransaction(txnId);
			if (result.is_valid) {
				toast.success($i18n.t('Entry is valid'));
			} else {
				const msgs = [...result.issues, ...result.warnings].join('; ');
				toast.warning(msgs || $i18n.t('Issues found'));
			}
		} catch {
			toast.error($i18n.t('AI validation failed'));
		} finally {
			validatingId = null;
		}
	}

	// Row keyboard access: Enter / Space on the row itself (not on a control inside it).
	const rowKeydown = (e: KeyboardEvent, id: number) => {
		if (e.target !== e.currentTarget) return;
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			toggleExpand(id);
		}
	};

	onMount(() => {
		loadAccounts();
		loadTransactions().then(() => {
			mounted = true;
		});
		getAccountingAiStatus()
			.then((s) => (aiAvailable = s.available))
			.catch(() => {});
	});
</script>

<!-- An amount in the display currency, with the entry's own amount under it when converted -->
{#snippet money(value: any, txn: any)}
	{#key $displayCurrency}
		{@const c = cvt(value, txn.transaction_date, txn)}
		{#if c.converting}
			{#if c.hasRate}
				<span>{c.display} <span class="text-xs text-muted-foreground">{c.to}</span></span>
				<div class="text-xs text-muted-foreground">{c.original} {c.from}</div>
			{:else}
				<span class="inline-flex items-center gap-1">
					{c.original}
					{c.from}
					<Tip content={$i18n.t('No exchange rate available')}>
						<TriangleAlert
							class="size-3.5 text-warning"
							aria-label={$i18n.t('No exchange rate available')}
						/>
					</Tip>
				</span>
			{/if}
		{:else}
			{c.original} <span class="text-xs text-muted-foreground">{c.from}</span>
		{/if}
	{/key}
{/snippet}

<ConfirmDialog
	bind:open={showDeleteConfirm}
	title={$i18n.t('Delete Transaction')}
	description={$i18n.t(
		'Are you sure you want to delete this draft transaction? This action cannot be undone.'
	)}
	confirmLabel={$i18n.t('Delete')}
	destructive
	onconfirm={handleDelete}
	oncancel={() => (deleteTarget = null)}
/>

<ConfirmDialog
	bind:open={showPostConfirm}
	title={$i18n.t('Post Transaction')}
	description={$i18n.t(
		'Posting this transaction will make it permanent. It can only be reversed by voiding. Continue?'
	)}
	confirmLabel={$i18n.t('Post')}
	onconfirm={handlePost}
	oncancel={() => (postTarget = null)}
/>

<ConfirmDialog
	bind:open={showVoidConfirm}
	title={$i18n.t('Void Transaction')}
	description={$i18n.t('Voiding this transaction will create a reversal entry. Continue?')}
	confirmLabel={$i18n.t('Void')}
	onconfirm={handleVoid}
	oncancel={() => (voidTarget = null)}
/>

<ConfirmDialog
	bind:open={showBulkDeleteConfirm}
	title={$i18n.t('Delete selected drafts?')}
	description={$i18n.t('{{count}} draft entries will be deleted. This cannot be undone.', {
		count: selectedIds.size
	})}
	confirmLabel={$i18n.t('Delete')}
	destructive
	onconfirm={handleBulkDelete}
/>

<TransactionFormModal
	bind:show={showFormModal}
	transaction={editTransaction}
	{accounts}
	{companyId}
	on:save={handleFormSave}
/>

<DocumentPreviewModal
	bind:show={showPreview}
	invoice={previewInvoice}
	onUpdate={(updated) => {
		previewInvoice = updated;
	}}
/>

<div class="flex flex-col gap-4">
	<!-- Header: title + count, then the primary action — or the bulk bar while rows are selected -->
	<div class="flex min-h-8 flex-wrap items-center justify-between gap-2">
		<div class="flex items-baseline gap-2">
			<h2 class="text-lg font-semibold">{$i18n.t('Transactions')}</h2>
			<span class="text-sm text-muted-foreground tabular-nums">{total}</span>
		</div>
		<div class="flex items-center gap-2">
			{#if selectedIds.size > 0}
				<div
					class="flex items-center gap-1.5 text-sm"
					role="group"
					aria-label={$i18n.t('Bulk actions')}
				>
					<span class="mr-1 tabular-nums">
						<span class="font-medium">{selectedIds.size}</span>
						{$i18n.t('selected')}
					</span>
					<Button size="xs" onclick={handleBulkPost}>{$i18n.t('Post Selected')}</Button>
					<Button
						variant="ghost"
						size="xs"
						class="text-destructive hover:text-destructive"
						onclick={() => (showBulkDeleteConfirm = true)}
					>
						{$i18n.t('Delete Selected')}
					</Button>
					<Tip content={$i18n.t('Clear selection')}>
						<Button
							variant="ghost"
							size="icon-xs"
							aria-label={$i18n.t('Clear selection')}
							onclick={() => (selectedIds = new Set())}
						>
							<X />
						</Button>
					</Tip>
				</div>
			{:else if canWrite}
				<Button size="sm" onclick={openNewEntry}>
					<Plus />{$i18n.t('New Entry')}
				</Button>
			{/if}
		</div>
	</div>

	<!-- Toolbar: search and filters -->
	<div class="flex flex-wrap items-center gap-2">
		<div class="relative w-full sm:w-64">
			<Search
				class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
			/>
			<Input
				type="search"
				class="h-8 pl-8"
				placeholder={$i18n.t('Search transactions...')}
				aria-label={$i18n.t('Search transactions...')}
				bind:value={searchQuery}
				oninput={handleSearch}
			/>
		</div>

		<NativeSelect.Root
			size="sm"
			aria-label={$i18n.t('Type')}
			bind:value={filterType}
			onchange={handleFilterChange}
		>
			<NativeSelect.Option value="">{$i18n.t('All Types')}</NativeSelect.Option>
			<NativeSelect.Option value="invoice">{$i18n.t('Invoice')}</NativeSelect.Option>
			<NativeSelect.Option value="bill">{$i18n.t('Bill')}</NativeSelect.Option>
			<NativeSelect.Option value="payment_in">{$i18n.t('Payment In')}</NativeSelect.Option>
			<NativeSelect.Option value="payment_out">{$i18n.t('Payment Out')}</NativeSelect.Option>
			<NativeSelect.Option value="others">{$i18n.t('Others')}</NativeSelect.Option>
			<NativeSelect.Option value="adjustment">{$i18n.t('Adjustment')}</NativeSelect.Option>
		</NativeSelect.Root>

		<NativeSelect.Root
			size="sm"
			aria-label={$i18n.t('Status')}
			bind:value={filterStatus}
			onchange={handleFilterChange}
		>
			<NativeSelect.Option value="">{$i18n.t('All Statuses')}</NativeSelect.Option>
			<NativeSelect.Option value="draft">{$i18n.t('Draft')}</NativeSelect.Option>
			<NativeSelect.Option value="posted">{$i18n.t('Posted')}</NativeSelect.Option>
			<NativeSelect.Option value="voided">{$i18n.t('Voided')}</NativeSelect.Option>
		</NativeSelect.Root>

		<div class="flex items-center gap-1.5">
			<label for="txn-date-from" class="text-sm text-muted-foreground">{$i18n.t('From')}</label>
			<Input
				id="txn-date-from"
				type="date"
				class="h-8 w-auto tabular-nums"
				bind:value={filterDateFrom}
				onchange={handleFilterChange}
			/>
		</div>
		<div class="flex items-center gap-1.5">
			<label for="txn-date-to" class="text-sm text-muted-foreground">{$i18n.t('To')}</label>
			<Input
				id="txn-date-to"
				type="date"
				class="h-8 w-auto tabular-nums"
				bind:value={filterDateTo}
				onchange={handleFilterChange}
			/>
		</div>

		<Toggle
			variant="outline"
			pressed={filterUnbalanced}
			onPressedChange={(v) => (filterUnbalanced = v)}
		>
			<CircleAlert />
			{$i18n.t('Unbalanced')}
		</Toggle>

		{#if hasFilters}
			<Button variant="ghost" size="sm" onclick={clearFilters}>
				<X />{$i18n.t('Clear filters')}
			</Button>
		{/if}
	</div>

	<!-- Table -->
	{#if loading && transactions.length === 0}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(8) as _}
				<Skeleton class="h-8 w-full" />
			{/each}
		</div>
	{:else if loadError && transactions.length === 0}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Failed to load transactions')}</Alert.Title>
			<Alert.Description>
				<p>{loadError}</p>
				<Button variant="outline" size="sm" class="mt-2" onclick={loadTransactions}>
					<RotateCw />{$i18n.t('Retry')}
				</Button>
			</Alert.Description>
		</Alert.Root>
	{:else if filteredTransactions.length === 0}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><NotebookPen /></Empty.Media>
				<Empty.Title>
					{$i18n.t(filterUnbalanced ? 'No unbalanced transactions found' : 'No transactions found')}
				</Empty.Title>
				<Empty.Description>
					{#if hasFilters}
						{$i18n.t('Try other filters, or clear them to see every entry.')}
					{:else}
						{$i18n.t('Entries appear here when you book invoices, payments or manual entries.')}
					{/if}
				</Empty.Description>
			</Empty.Header>
			<Empty.Content>
				{#if hasFilters}
					<Button variant="outline" size="sm" onclick={clearFilters}>
						<X />{$i18n.t('Clear filters')}
					</Button>
				{:else if canWrite}
					<Button size="sm" onclick={openNewEntry}><Plus />{$i18n.t('New Entry')}</Button>
				{/if}
			</Empty.Content>
		</Empty.Root>
	{:else}
		<div class="overflow-hidden rounded-md border">
			<Table.Root>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						<Table.Head class="w-10 pl-3">
							<Checkbox
								checked={allDraftsSelected}
								indeterminate={selectedIds.size > 0 && !allDraftsSelected}
								disabled={draftTransactions.length === 0}
								onCheckedChange={toggleSelectAll}
								aria-label={$i18n.t('Select all drafts')}
							/>
						</Table.Head>
						<Table.Head>{$i18n.t('#')}</Table.Head>
						<Table.Head>{$i18n.t('Date')}</Table.Head>
						<Table.Head>{$i18n.t('Type')}</Table.Head>
						<Table.Head>{$i18n.t('Status')}</Table.Head>
						<Table.Head>{$i18n.t('Reference')}</Table.Head>
						<Table.Head>{$i18n.t('Description')}</Table.Head>
						<Table.Head class="text-right">{$i18n.t('Total')}</Table.Head>
						<Table.Head>{$i18n.t('Invoice')}</Table.Head>
						<Table.Head class="w-24"><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each filteredTransactions as txn (txn.id)}
						{@const expanded = expandedRows.has(txn.id)}
						<Table.Row
							class="cursor-pointer {txn.status === 'voided' ? 'text-muted-foreground' : ''}"
							data-state={selectedIds.has(txn.id) ? 'selected' : undefined}
							tabindex={0}
							aria-expanded={expanded}
							onclick={() => toggleExpand(txn.id)}
							onkeydown={(e: KeyboardEvent) => rowKeydown(e, txn.id)}
						>
							<!-- Checkbox: only drafts can be posted / deleted in bulk -->
							<Table.Cell class="pl-3" onclick={(e: MouseEvent) => e.stopPropagation()}>
								{#if txn.status === 'draft'}
									<Checkbox
										checked={selectedIds.has(txn.id)}
										onCheckedChange={() => toggleSelect(txn.id)}
										aria-label={$i18n.t('Select entry {{id}}', { id: txn.id })}
									/>
								{/if}
							</Table.Cell>

							<Table.Cell class="font-mono text-[13px] text-muted-foreground">{txn.id}</Table.Cell>

							<Table.Cell class="tabular-nums">{formatDate(txn.transaction_date)}</Table.Cell>

							<Table.Cell>
								<Badge variant="outline">
									{$i18n.t(TYPE_LABELS[txn.transaction_type] ?? txn.transaction_type)}
								</Badge>
							</Table.Cell>

							<Table.Cell>
								<div class="flex items-center gap-1">
									<StatusBadge kind="entry" status={txn.status} />
									{#if txn.booking_gaps?.length}
										<Tip
											content={$i18n.t(
												'Incomplete — {{n}} line(s) still need an account. Open the entry to choose them.',
												{ n: txn.booking_gaps.length }
											)}
										>
											<StatusBadge kind="entry" status="incomplete" />
										</Tip>
									{:else if isUnbalanced(txn)}
										<Tip
											content={$i18n.t('Missing double entry — debits and credits do not balance')}
										>
											<StatusBadge kind="entry" status="unbalanced" />
										</Tip>
									{/if}
								</div>
							</Table.Cell>

							<Table.Cell class="max-w-[10rem]">
								{#if txn.reference}
									<span class="block truncate font-mono text-[13px]" title={txn.reference}
										>{txn.reference}</span
									>
								{:else}
									<span class="text-muted-foreground">—</span>
								{/if}
							</Table.Cell>

							<Table.Cell class="max-w-[16rem]">
								{#if txn.description}
									<span class="block truncate" title={txn.description}>{txn.description}</span>
								{:else}
									<span class="text-muted-foreground">—</span>
								{/if}
							</Table.Cell>

							<Table.Cell
								class="text-right tabular-nums {txn.status === 'voided' ? '' : 'font-medium'}"
							>
								{@render money(txn.total, txn)}
							</Table.Cell>

							<Table.Cell onclick={(e: MouseEvent) => e.stopPropagation()}>
								{#if txn.invoice_id}
									<button
										type="button"
										class="inline-flex items-center gap-1 rounded-sm font-mono text-[13px] text-link underline-offset-4 outline-none hover:underline focus-visible:ring-[3px] focus-visible:ring-ring/50"
										title={$i18n.t('Preview invoice')}
										onclick={() => openInvoicePreview(txn.invoice_id)}
									>
										<Eye class="size-3.5" />#{txn.invoice_id}
									</button>
								{:else}
									<span class="text-muted-foreground">—</span>
								{/if}
							</Table.Cell>

							<!-- Actions: open + expand visible, the rest in the ⋯ menu -->
							<Table.Cell class="text-right" onclick={(e: MouseEvent) => e.stopPropagation()}>
								<div class="inline-flex items-center justify-end gap-0.5">
									{#if txn.status === 'draft' && canWrite}
										<Tip content={$i18n.t('Edit')}>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label={$i18n.t('Edit')}
												onclick={() => openEdit(txn)}
											>
												<Pencil />
											</Button>
										</Tip>
									{:else if txn.status === 'posted' || txn.status === 'voided'}
										<Tip content={$i18n.t('View')}>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label={$i18n.t('View')}
												onclick={() => openEdit(txn)}
											>
												<Eye />
											</Button>
										</Tip>
									{/if}

									{#if (txn.status === 'draft' && (canPost || canDelete || aiAvailable)) || (txn.status === 'posted' && canPost)}
										<DropdownMenu.Root>
											<DropdownMenu.Trigger>
												{#snippet child({ props })}
													<Button
														{...props}
														variant="ghost"
														size="icon-xs"
														aria-label={$i18n.t('More actions')}
													>
														{#if validatingId === txn.id}<Spinner />{:else}<Ellipsis />{/if}
													</Button>
												{/snippet}
											</DropdownMenu.Trigger>
											<DropdownMenu.Content align="end" class="w-48">
												{#if txn.status === 'draft' && canPost}
													<DropdownMenu.Item onSelect={() => confirmPost(txn)}>
														<Check />{$i18n.t('Post')}
													</DropdownMenu.Item>
												{/if}
												{#if aiAvailable && txn.status === 'draft'}
													<DropdownMenu.Item
														disabled={validatingId === txn.id}
														onSelect={() => handleAiValidate(txn.id)}
													>
														<Sparkles />{$i18n.t('AI Validate')}
													</DropdownMenu.Item>
												{/if}
												{#if txn.status === 'posted' && canPost}
													<DropdownMenu.Item
														variant="destructive"
														onSelect={() => confirmVoid(txn)}
													>
														<Ban />{$i18n.t('Void')}
													</DropdownMenu.Item>
												{/if}
												{#if txn.status === 'draft' && canDelete}
													{#if canPost || aiAvailable}<DropdownMenu.Separator />{/if}
													<DropdownMenu.Item
														variant="destructive"
														onSelect={() => confirmDelete(txn)}
													>
														<Trash2 />{$i18n.t('Delete')}
													</DropdownMenu.Item>
												{/if}
											</DropdownMenu.Content>
										</DropdownMenu.Root>
									{/if}

									<Tip content={expanded ? $i18n.t('Collapse') : $i18n.t('Expand')}>
										<Button
											variant="ghost"
											size="icon-xs"
											aria-label={expanded ? $i18n.t('Collapse') : $i18n.t('Expand')}
											aria-expanded={expanded}
											onclick={() => toggleExpand(txn.id)}
										>
											<ChevronDown
												class="transition-transform motion-reduce:transition-none {expanded
													? 'rotate-180'
													: ''}"
											/>
										</Button>
									</Tip>
								</div>
							</Table.Cell>
						</Table.Row>

						<!-- Expanded detail: the debit / credit lines -->
						{#if expanded}
							<Table.Row class="bg-muted/30 hover:bg-muted/30">
								<Table.Cell colspan={10} class="px-4 py-3 whitespace-normal">
									<div class="flex flex-col gap-3">
										{#if txn.lines?.length}
											{@const totals = lineTotals(txn)}
											{@const unbalanced = Math.abs(totals.d - totals.c) > 0.005}
											<div class="flex flex-col gap-1.5">
												<span class="text-sm font-medium">{$i18n.t('Journal Lines')}</span>
												<div class="overflow-hidden rounded-md border bg-card">
													<Table.Root class="text-[13px]">
														<Table.Header class="bg-muted/50">
															<Table.Row class="hover:bg-transparent">
																<Table.Head class="h-8">{$i18n.t('Account Code')}</Table.Head>
																<Table.Head class="h-8">{$i18n.t('Account Name')}</Table.Head>
																<Table.Head class="h-8 text-right">{$i18n.t('Debit')}</Table.Head>
																<Table.Head class="h-8 text-right">{$i18n.t('Credit')}</Table.Head>
																<Table.Head class="h-8">{$i18n.t('Description')}</Table.Head>
															</Table.Row>
														</Table.Header>
														<Table.Body>
															{#each txn.lines as line}
																<Table.Row class="hover:bg-transparent">
																	<Table.Cell class="py-1.5 font-mono text-[13px]">
																		{line.account_code ?? '—'}
																	</Table.Cell>
																	<Table.Cell class="py-1.5">{line.account_name ?? '—'}</Table.Cell>
																	<Table.Cell class="py-1.5 text-right tabular-nums">
																		{#if parseFloat(String(line.debit ?? 0)) > 0}
																			{@render money(line.debit, txn)}
																		{:else}
																			<span class="text-muted-foreground">—</span>
																		{/if}
																	</Table.Cell>
																	<Table.Cell class="py-1.5 text-right tabular-nums">
																		{#if parseFloat(String(line.credit ?? 0)) > 0}
																			{@render money(line.credit, txn)}
																		{:else}
																			<span class="text-muted-foreground">—</span>
																		{/if}
																	</Table.Cell>
																	<Table.Cell class="py-1.5 whitespace-normal">
																		{line.description ?? '—'}
																	</Table.Cell>
																</Table.Row>
															{/each}
														</Table.Body>
														<Table.Footer>
															<Table.Row class="hover:bg-transparent">
																<Table.Cell class="py-1.5" colspan={2}
																	>{$i18n.t('Total')}</Table.Cell
																>
																<Table.Cell class="py-1.5 text-right tabular-nums">
																	{formatCurrency(totals.d)}
																</Table.Cell>
																<Table.Cell class="py-1.5 text-right tabular-nums">
																	{formatCurrency(totals.c)}
																</Table.Cell>
																<Table.Cell class="py-1.5">
																	{#if unbalanced}
																		<StatusBadge
																			kind="entry"
																			status="unbalanced"
																			label="{$i18n.t('Unbalanced')}: {formatCurrency(
																				Math.abs(totals.d - totals.c)
																			)}"
																		/>
																	{:else}
																		<Badge variant="status">
																			<Scale class="text-success" />{$i18n.t('Balanced')}
																		</Badge>
																	{/if}
																</Table.Cell>
															</Table.Row>
														</Table.Footer>
													</Table.Root>
												</div>
											</div>
										{:else}
											<p class="text-sm text-muted-foreground">
												{$i18n.t('No line details available')}
											</p>
										{/if}

										<!-- Extra metadata -->
										<div class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
											{#if txn.currency && txn.currency !== 'USD'}
												<span>{$i18n.t('Currency')}: {txn.currency}</span>
											{/if}
											{#if txn.exchange_rate && txn.exchange_rate !== 1}
												<span class="tabular-nums"
													>{$i18n.t('Exchange Rate')}: {txn.exchange_rate}</span
												>
											{/if}
											{#if txn.notes}
												<span>{$i18n.t('Notes', { context: 'gnos3' })}: {txn.notes}</span>
											{/if}
											{#if txn.payment_id}
												<span>{$i18n.t('Payment')} #{txn.payment_id}</span>
											{/if}
											<span class="tabular-nums"
												>{$i18n.t('Created')}: {formatDate(txn.created_at)}</span
											>
											{#if txn.updated_at && txn.updated_at !== txn.created_at}
												<span class="tabular-nums"
													>{$i18n.t('Updated')}: {formatDate(txn.updated_at)}</span
												>
											{/if}
										</div>
									</div>
								</Table.Cell>
							</Table.Row>
						{/if}
					{/each}
				</Table.Body>
			</Table.Root>
		</div>

		<TablePagination bind:page={currentPage} count={total} {perPage} />
	{/if}
</div>
