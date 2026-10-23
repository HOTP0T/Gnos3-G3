<script lang="ts">
	import { onMount, onDestroy, getContext } from 'svelte';
	import { page as pageStore } from '$app/stores';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import { browser } from '$app/environment';

	import Search from '@lucide/svelte/icons/search';
	import Columns3 from '@lucide/svelte/icons/columns-3';
	import Ellipsis from '@lucide/svelte/icons/ellipsis';
	import Eye from '@lucide/svelte/icons/eye';
	import Check from '@lucide/svelte/icons/check';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import ExternalLink from '@lucide/svelte/icons/external-link';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import ChevronUp from '@lucide/svelte/icons/chevron-up';
	import ArrowUp from '@lucide/svelte/icons/arrow-up';
	import ArrowDown from '@lucide/svelte/icons/arrow-down';
	import ArrowUpDown from '@lucide/svelte/icons/arrow-up-down';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Receipt from '@lucide/svelte/icons/receipt';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';

	import {
		getInvoices,
		updateInvoice,
		deleteInvoice,
		reprocessInvoice,
		markInvoiceReviewed,
		getTags,
		getInvoiceStats
	} from '$lib/apis/invoices';
	import { getCompanies, getEmployees, getExpenseCategories } from '$lib/apis/accounting';
	import { k4miDocHref } from '$lib/apis/k4mi';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
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
	import FilterBar from '$lib/components/invoices/FilterBar.svelte';
	import ExportButton from '$lib/components/invoices/ExportButton.svelte';
	import DocumentPreviewModal from '$lib/components/invoices/DocumentPreviewModal.svelte';

	const i18n: any = getContext('i18n');

	// Data
	let invoices: any[] = [];
	let total = 0;
	let loading = true;
	let loadError = '';

	// Pagination
	let page = 1;
	let perPage = 50;

	// Filters
	let filters: Record<string, any> = {};
	let needsReviewFilter: boolean | undefined = undefined;
	let availableTags: string[] = [];

	// Lookups for Company / Employee / Category columns
	let companiesById: Record<number, any> = {};
	let employeesById: Record<number, any> = {};
	let categoriesById: Record<number, any> = {};

	const loadAccountingLookups = async () => {
		try {
			const compRes = await getCompanies({ active: true });
			const comps = compRes?.companies ?? compRes ?? [];
			companiesById = Object.fromEntries(
				(Array.isArray(comps) ? comps : []).map((c: any) => [c.id, c])
			);

			// Employees + categories per company, merged into a flat lookup
			const empMap: Record<number, any> = {};
			const catMap: Record<number, any> = {};
			await Promise.all(
				Object.keys(companiesById).map(async (cidStr) => {
					const cid = Number(cidStr);
					try {
						const [eRes, cRes] = await Promise.all([getEmployees(cid), getExpenseCategories(cid)]);
						for (const emp of eRes?.employees ?? []) empMap[emp.id] = emp;
						for (const cat of cRes?.categories ?? []) catMap[cat.id] = cat;
					} catch {
						// non-fatal — column will fall back to id
					}
				})
			);
			employeesById = empMap;
			categoriesById = catMap;
		} catch {
			// non-fatal
		}
	};

	// Sorting — server-side
	let sortBy = '';
	let sortDir: 'asc' | 'desc' = 'asc';

	const handleSort = (key: string) => {
		if (sortBy === key) {
			if (sortDir === 'asc') {
				sortDir = 'desc';
			} else {
				// third click: reset to default (no sort)
				sortBy = '';
				sortDir = 'asc';
			}
		} else {
			sortBy = key;
			sortDir = 'asc';
		}
		if (page !== 1) page = 1;
		else loadInvoices();
	};

	// Editing
	let editingCell: { id: number; field: string } | null = null;
	let editValue: string = '';

	// Expanded rows
	let expandedRows: Set<number> = new Set();

	// Delete confirmation
	let showDeleteConfirm = false;
	let deleteTarget: any = null;

	// Reprocess loading state
	let reprocessingIds: Set<number> = new Set();
	let reviewingIds: Set<number> = new Set();

	// Document preview
	let showPreview = false;
	let previewInvoice: any = null;

	// Search
	let searchQuery = '';
	let searchDebounce: ReturnType<typeof setTimeout>;

	const EDITABLE_COLUMNS = [
		{ key: 'vendor_name', label: 'Vendor', type: 'text' },
		{ key: 'invoice_number', label: 'Invoice #', type: 'text' },
		{ key: 'invoice_date', label: 'Date', type: 'date' },
		{ key: 'due_date', label: 'Due Date', type: 'date' },
		{ key: 'currency', label: 'Cur', type: 'text', maxLength: 3 },
		{ key: 'subtotal', label: 'Subtotal', type: 'number', align: 'right' },
		{ key: 'tax_amount', label: 'Tax', type: 'number', align: 'right' },
		{ key: 'total_amount', label: 'Total', type: 'number', align: 'right' },
		// Paid / Balance deliberately absent. They are never read from the document —
		// no extraction prompt asks for them — they are written only by the accounting
		// payments code, so showing them here presented accounting state as if it were
		// extracted invoice data, and made it hand-editable outside the ledger.
		// Payment status lives in Accounting → Company → Payments.
		{ key: 'payment_terms', label: 'Terms', type: 'text' },
		{ key: 'po_number', label: 'PO #', type: 'text' },
		{ key: 'client_name', label: 'Client', type: 'text', maxLength: 256 },
		{ key: 'description', label: 'Desc', type: 'text' }
	];

	// Column widths — persisted to localStorage
	const COL_WIDTHS_KEY = 'invoice-col-widths';
	const DEFAULT_WIDTHS: Record<string, number> = {
		vendor_name: 170,
		invoice_number: 130,
		invoice_date: 104,
		due_date: 104,
		currency: 72,
		subtotal: 104,
		tax_amount: 92,
		total_amount: 112,
		payment_terms: 110,
		po_number: 100,
		client_name: 130,
		description: 160,
		_company: 150,
		_employee: 140,
		_category: 130,
		_status: 180,
		_confidence: 120,
		_actions: 76
	};

	// Columns after the editable ones; Vendor is always shown.
	const EXTRA_COLUMNS: Array<{ key: string; label: string; sortKey?: string }> = [
		{ key: '_company', label: 'Company' },
		{ key: '_employee', label: 'Employee' },
		{ key: '_category', label: 'Category' },
		{ key: '_status', label: 'Status', sortKey: 'processing_status' },
		{ key: '_confidence', label: 'Confidence', sortKey: 'confidence_score' }
	];
	const ALL_COLUMN_KEYS = [
		...EDITABLE_COLUMNS.map((c) => c.key),
		...EXTRA_COLUMNS.map((c) => c.key)
	];
	const ALWAYS_VISIBLE = 'vendor_name';
	const COL_VISIBLE_KEY = 'invoice-table-columns';

	let visibleColumns: Set<string> = (() => {
		try {
			const saved = localStorage.getItem(COL_VISIBLE_KEY);
			return new Set<string>(saved ? JSON.parse(saved) : ALL_COLUMN_KEYS);
		} catch {
			return new Set<string>(ALL_COLUMN_KEYS);
		}
	})();

	const saveVisibleColumns = () => {
		try {
			localStorage.setItem(COL_VISIBLE_KEY, JSON.stringify(Array.from(visibleColumns)));
		} catch {}
	};

	const toggleColumn = (key: string) => {
		const next = new Set(visibleColumns);
		if (next.has(key)) next.delete(key);
		else next.add(key);
		visibleColumns = next;
		saveVisibleColumns();
	};

	const showAllColumns = () => {
		visibleColumns = new Set(ALL_COLUMN_KEYS);
		saveVisibleColumns();
	};

	$: shownEditable = EDITABLE_COLUMNS.filter(
		(c) => c.key === ALWAYS_VISIBLE || visibleColumns.has(c.key)
	);
	$: shownExtra = EXTRA_COLUMNS.filter((c) => visibleColumns.has(c.key));
	$: colCount = shownEditable.length + shownExtra.length + 1;
	$: tableWidth = [...shownEditable, ...shownExtra, { key: '_actions' }].reduce(
		(sum, c) => sum + (colWidths[c.key] ?? 100),
		0
	);

	let colWidths: Record<string, number> = (() => {
		try {
			const saved = localStorage.getItem(COL_WIDTHS_KEY);
			return saved ? { ...DEFAULT_WIDTHS, ...JSON.parse(saved) } : { ...DEFAULT_WIDTHS };
		} catch {
			return { ...DEFAULT_WIDTHS };
		}
	})();

	const saveColWidths = () => {
		try {
			localStorage.setItem(COL_WIDTHS_KEY, JSON.stringify(colWidths));
		} catch {}
	};

	// Column resize drag
	let resizing: { key: string; startX: number; startWidth: number } | null = null;

	const startResize = (e: MouseEvent, key: string) => {
		e.preventDefault();
		e.stopPropagation();
		resizing = { key, startX: e.clientX, startWidth: colWidths[key] };
		window.addEventListener('mousemove', onResizeMove);
		window.addEventListener('mouseup', onResizeUp);
	};

	const onResizeMove = (e: MouseEvent) => {
		if (!resizing) return;
		const delta = e.clientX - resizing.startX;
		colWidths[resizing.key] = Math.max(40, resizing.startWidth + delta);
		colWidths = colWidths;
	};

	const onResizeUp = () => {
		resizing = null;
		window.removeEventListener('mousemove', onResizeMove);
		window.removeEventListener('mouseup', onResizeUp);
		saveColWidths();
	};

	// The page that was last loaded: a page change reloads once (see the reactive block below).
	let lastPage = 1;

	const loadInvoices = async () => {
		loading = true;
		loadError = '';
		lastPage = page;
		try {
			const params: Record<string, any> = {
				...filters,
				limit: perPage,
				offset: (page - 1) * perPage
			};
			if (searchQuery) {
				params.q = searchQuery;
			}
			if (sortBy) {
				params.sort_by = sortBy;
				params.sort_dir = sortDir;
			}
			const res = await getInvoices(localStorage.token, params);
			if (res) {
				invoices = res.invoices;
				total = res.total;
			}
		} catch (err) {
			loadError = `${err}`;
			toast.error(`${err}`);
		}
		loading = false;
	};

	const handleFilter = (e: CustomEvent) => {
		filters = e.detail;
		page = 1;
		loadInvoices();
	};

	const handleSearch = () => {
		clearTimeout(searchDebounce);
		searchDebounce = setTimeout(() => {
			page = 1;
			loadInvoices();
		}, 300);
	};

	$: filtersActive =
		!!searchQuery || Object.values(filters).some((v) => v !== undefined && v !== '' && v !== null);

	// Inline editing
	const startEdit = (invoice: any, field: string) => {
		// Clicking inside the open editor must not reset what was typed.
		if (editingCell?.id === invoice.id && editingCell?.field === field) return;
		editingCell = { id: invoice.id, field };
		const val = invoice[field];
		if (val === null || val === undefined) {
			editValue = '';
		} else if (field === 'invoice_date' || field === 'due_date') {
			editValue = val ? dayjs(val).format('YYYY-MM-DD') : '';
		} else {
			editValue = String(val);
		}
	};

	const saveEdit = async () => {
		if (!editingCell) return;

		const { id, field } = editingCell;
		const invoice = invoices.find((inv) => inv.id === id);
		if (!invoice) return;

		// Build update payload
		let updateVal: any = editValue;
		const col = EDITABLE_COLUMNS.find((c) => c.key === field);

		if (col?.type === 'number') {
			updateVal = editValue === '' ? null : parseFloat(editValue);
		} else if (col?.type === 'date') {
			updateVal = editValue === '' ? null : editValue;
		} else {
			updateVal = editValue === '' ? null : editValue;
		}

		// Skip if value hasn't changed
		const oldVal = invoice[field];
		const oldStr = oldVal === null || oldVal === undefined ? '' : String(oldVal);
		const newStr = updateVal === null ? '' : String(updateVal);
		if (
			oldStr === newStr ||
			(col?.type === 'date' && dayjs(oldStr).format('YYYY-MM-DD') === newStr)
		) {
			editingCell = null;
			return;
		}

		try {
			const res = await updateInvoice(localStorage.token, id, { [field]: updateVal });
			if (res) {
				// Update local data
				const idx = invoices.findIndex((inv) => inv.id === id);
				if (idx !== -1) {
					invoices[idx] = res;
					invoices = invoices;
				}
				toast.success($i18n.t('Updated'));
			}
		} catch (err) {
			toast.error(`${err}`);
		}

		editingCell = null;
	};

	const cancelEdit = () => {
		editingCell = null;
	};

	const handleKeydown = (e: KeyboardEvent) => {
		if (e.key === 'Enter') {
			saveEdit();
		} else if (e.key === 'Escape') {
			cancelEdit();
		}
	};

	// Delete
	const confirmDelete = (invoice: any) => {
		deleteTarget = invoice;
		showDeleteConfirm = true;
	};

	const handleDelete = async () => {
		if (!deleteTarget) return;
		try {
			await deleteInvoice(localStorage.token, deleteTarget.id);
			toast.success($i18n.t('Invoice deleted'));
			if (invoices.length === 1 && page > 1) {
				page -= 1;
			}
			loadInvoices();
		} catch (err) {
			toast.error(`${err}`);
		}
		deleteTarget = null;
	};

	// Reprocess
	const handleReprocess = async (invoice: any) => {
		reprocessingIds.add(invoice.id);
		reprocessingIds = reprocessingIds;
		// Optimistically update row status
		const idx = invoices.findIndex((inv) => inv.id === invoice.id);
		if (idx !== -1) {
			invoices[idx] = { ...invoices[idx], processing_status: 'processing', needs_review: false };
			invoices = invoices;
		}
		try {
			await reprocessInvoice(localStorage.token, invoice.id);
			toast.success($i18n.t('Reprocessing queued'));
		} catch (err) {
			toast.error(`${err}`);
			// Revert on error
			if (idx !== -1) {
				invoices[idx] = invoice;
				invoices = invoices;
			}
		} finally {
			reprocessingIds.delete(invoice.id);
			reprocessingIds = reprocessingIds;
		}
	};

	// Mark reviewed — validate a needs-review invoice without editing a field
	const handleMarkReviewed = async (invoice: any) => {
		reviewingIds.add(invoice.id);
		reviewingIds = reviewingIds;
		const idx = invoices.findIndex((inv) => inv.id === invoice.id);
		if (idx !== -1) {
			invoices[idx] = { ...invoices[idx], needs_review: false };
			invoices = invoices;
		}
		try {
			await markInvoiceReviewed(localStorage.token, invoice.id);
			toast.success($i18n.t('Marked as reviewed'));
		} catch (err) {
			toast.error(`${err}`);
			// Revert on error
			if (idx !== -1) {
				invoices[idx] = invoice;
				invoices = invoices;
			}
		} finally {
			reviewingIds.delete(invoice.id);
			reviewingIds = reviewingIds;
		}
	};

	// Expand/collapse
	const toggleExpand = (id: number) => {
		if (expandedRows.has(id)) {
			expandedRows.delete(id);
		} else {
			expandedRows.add(id);
		}
		expandedRows = expandedRows;
	};

	// Document preview
	const openPreview = (invoice: any) => {
		previewInvoice = invoice;
		showPreview = true;
	};

	// Row actions: what each row offers
	const canMarkReviewed = (invoice: any) =>
		invoice.needs_review && invoice.processing_status !== 'processing';
	const canReprocess = (invoice: any) =>
		invoice.processing_status !== 'processing' &&
		(invoice.processing_status === 'failed' ||
			invoice.needs_review ||
			(invoice.confidence_score !== null && parseFloat(invoice.confidence_score) < 0.7));

	// Cell display helpers
	const formatCurrency = (val: any) => {
		if (val === null || val === undefined) return '—';
		return parseFloat(val).toLocaleString(undefined, {
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		});
	};

	const formatDate = (val: any) => {
		if (!val) return '—';
		return dayjs(val).format('YYYY-MM-DD');
	};

	const displayValue = (invoice: any, col: any) => {
		const val = invoice[col.key];
		if (val === null || val === undefined) return '—';
		if (col.type === 'number') return formatCurrency(val);
		if (col.type === 'date') return formatDate(val);
		return String(val);
	};

	onDestroy(() => {
		window.removeEventListener('mousemove', onResizeMove);
		window.removeEventListener('mouseup', onResizeUp);
		if (refreshInterval) {
			clearInterval(refreshInterval);
			refreshInterval = null;
		}
	});

	let mounted = false;

	// Background refresh: poll the cheap /stats heartbeat while the page is open so
	// invoices uploaded to K4mi after the table was loaded appear as "processing",
	// and rows flip to their final status when extraction finishes.
	const POLL_INTERVAL_MS = 5000;
	let refreshInterval: ReturnType<typeof setInterval> | null = null;
	let polling = false;
	let lastStats: { processing: number; total: number } | null = null;

	const pollStats = async () => {
		// Never yank rows out from under an inline edit or an open preview.
		if (polling || loading || editingCell || showPreview) return;
		polling = true;
		try {
			const stats = await getInvoiceStats(localStorage.token);
			if (!stats) return;
			const next = { processing: stats.processing ?? 0, total: stats.total ?? 0 };
			const changed =
				lastStats !== null &&
				(next.processing !== lastStats.processing || next.total !== lastStats.total);
			lastStats = next;
			// Reload while anything is in flight (statuses change as extractions
			// finish) and once more when the counts settle.
			if (next.processing > 0 || changed) {
				await loadInvoices();
			}
		} catch {
			// transient — next tick retries
		} finally {
			polling = false;
		}
	};

	// React to page changes only after initial load
	$: if (mounted && page !== lastPage) {
		loadInvoices();
	}

	onMount(() => {
		// Parse URL query params for initial filters (e.g., ?needs_review=true&vendor=...)
		if (browser) {
			const urlParams = $pageStore.url.searchParams;
			const urlVendor = urlParams.get('vendor');
			const urlNeedsReview = urlParams.get('needs_review');

			if (urlVendor) {
				searchQuery = urlVendor;
			}
			if (urlNeedsReview === 'true') {
				filters = { ...filters, needs_review: true };
				needsReviewFilter = true;
			}
		}

		loadInvoices().then(() => {
			mounted = true;
			refreshInterval = setInterval(pollStats, POLL_INTERVAL_MS);
		});
		getTags(localStorage.token)
			.then((t) => (availableTags = t ?? []))
			.catch(() => {});
		loadAccountingLookups();
	});
</script>

<ConfirmDialog
	bind:open={showDeleteConfirm}
	title={$i18n.t('Delete invoice?')}
	description={deleteTarget
		? `${deleteTarget.invoice_number || deleteTarget.vendor_name || `#${deleteTarget.id}`} ${$i18n.t(
				'and its extracted data will be removed. The K4mi document stays. This cannot be undone.'
			)}`
		: ''}
	confirmLabel={$i18n.t('Delete')}
	destructive
	onconfirm={handleDelete}
	oncancel={() => (deleteTarget = null)}
/>

<DocumentPreviewModal
	bind:show={showPreview}
	invoice={previewInvoice}
	onUpdate={(updated) => {
		const idx = invoices.findIndex((inv) => inv.id === updated.id);
		if (idx !== -1) {
			invoices[idx] = updated;
			invoices = invoices;
		}
		previewInvoice = updated;
	}}
/>

{#snippet sortLabel(sortKey: string, label: string, right: boolean)}
	<button
		type="button"
		class="-mx-1 inline-flex max-w-full items-center gap-1 rounded-sm px-1 hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none {right
			? 'flex-row-reverse'
			: ''}"
		on:click={() => handleSort(sortKey)}
		aria-sort={sortBy === sortKey ? (sortDir === 'asc' ? 'ascending' : 'descending') : undefined}
	>
		<span class="truncate">{$i18n.t(label)}</span>
		{#if sortBy === sortKey}
			{#if sortDir === 'asc'}<ArrowUp
					class="size-3.5 shrink-0 text-muted-foreground"
				/>{:else}<ArrowDown class="size-3.5 shrink-0 text-muted-foreground" />{/if}
		{:else}
			<ArrowUpDown class="size-3.5 shrink-0 text-muted-foreground/50" />
		{/if}
	</button>
{/snippet}

{#snippet resizeHandle(key: string)}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="absolute top-0 right-0 h-full w-1.5 cursor-col-resize opacity-0 transition-opacity hover:bg-ring/60 hover:opacity-100"
		on:mousedown={(e) => startResize(e, key)}
	></div>
{/snippet}

<div class="flex flex-col gap-4">
	<!-- Toolbar: search, faceted filters, Columns, Export -->
	<div class="flex flex-wrap items-center gap-2">
		<div class="relative w-full sm:w-64">
			<Search
				class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
			/>
			<Input
				type="search"
				class="h-8 pl-8"
				aria-label={$i18n.t('Search invoices...')}
				placeholder={$i18n.t('Search invoices...')}
				bind:value={searchQuery}
				oninput={handleSearch}
			/>
		</div>

		<FilterBar bind:needsReview={needsReviewFilter} {availableTags} on:filter={handleFilter} />

		<div class="ml-auto flex items-center gap-2">
			<DropdownMenu.Root>
				<DropdownMenu.Trigger>
					{#snippet child({ props })}
						<Button {...props} variant="outline" size="sm">
							<Columns3 />{$i18n.t('Columns')}
						</Button>
					{/snippet}
				</DropdownMenu.Trigger>
				<DropdownMenu.Content align="end" class="max-h-[60vh] w-56 overflow-y-auto">
					<DropdownMenu.Label>{$i18n.t('Visible columns')}</DropdownMenu.Label>
					{#each [...EDITABLE_COLUMNS, ...EXTRA_COLUMNS] as col}
						<DropdownMenu.CheckboxItem
							checked={col.key === ALWAYS_VISIBLE || visibleColumns.has(col.key)}
							disabled={col.key === ALWAYS_VISIBLE}
							closeOnSelect={false}
							onCheckedChange={() => col.key !== ALWAYS_VISIBLE && toggleColumn(col.key)}
						>
							{$i18n.t(col.label)}
						</DropdownMenu.CheckboxItem>
					{/each}
					<DropdownMenu.Separator />
					<DropdownMenu.Item onSelect={showAllColumns}>{$i18n.t('Show all')}</DropdownMenu.Item>
				</DropdownMenu.Content>
			</DropdownMenu.Root>

			<ExportButton {invoices} />
		</div>
	</div>

	{#if loadError && invoices.length === 0 && !loading}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Could not load invoices.')}</Alert.Title>
			<Alert.Description>
				<p>{loadError}</p>
				<Button variant="outline" size="sm" class="mt-2" onclick={loadInvoices}>
					<RefreshCw />{$i18n.t('Retry')}
				</Button>
			</Alert.Description>
		</Alert.Root>
	{:else if loading && invoices.length === 0}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(8) as _}
				<Skeleton class="h-8 w-full" />
			{/each}
		</div>
	{:else if invoices.length === 0}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><Receipt /></Empty.Media>
				<Empty.Title>{$i18n.t('No invoices found')}</Empty.Title>
				<Empty.Description>
					{#if filtersActive}
						{$i18n.t('Try another search or clear the filters.')}
					{:else}
						{$i18n.t('Tag a K4mi document with')} <code>invoice</code>
						{$i18n.t('to extract one.')}
					{/if}
				</Empty.Description>
			</Empty.Header>
		</Empty.Root>
	{:else}
		<!-- Table box: wide, scrolls sideways with Vendor pinned -->
		<div class="overflow-hidden rounded-md border">
			<Table.Root class="table-fixed text-[13px]" style="width: {tableWidth}px; min-width: 100%;">
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						{#each shownEditable as col (col.key)}
							<Table.Head
								class="relative {col.align === 'right' ? 'text-right' : ''} {col.key ===
								ALWAYS_VISIBLE
									? 'sticky left-0 z-[2] bg-[color-mix(in_oklab,var(--muted)_50%,var(--background))] shadow-[inset_-1px_0_0_var(--border)]'
									: ''}"
								style="width: {colWidths[col.key]}px"
							>
								{@render sortLabel(col.key, col.label, col.align === 'right')}
								{@render resizeHandle(col.key)}
							</Table.Head>
						{/each}
						{#each shownExtra as col (col.key)}
							<Table.Head class="relative" style="width: {colWidths[col.key]}px">
								{#if col.sortKey}
									{@render sortLabel(col.sortKey, col.label, false)}
								{:else}
									{$i18n.t(col.label)}
								{/if}
								{@render resizeHandle(col.key)}
							</Table.Head>
						{/each}
						<Table.Head style="width: {colWidths._actions}px">
							<span class="sr-only">{$i18n.t('Actions')}</span>
						</Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each invoices as invoice (invoice.id)}
						{@const busy = reprocessingIds.has(invoice.id) || reviewingIds.has(invoice.id)}
						<Table.Row class="group">
							{#each shownEditable as col (col.key)}
								{@const editing = editingCell?.id === invoice.id && editingCell?.field === col.key}
								<Table.Cell
									class="cursor-pointer overflow-hidden px-2.5 py-1 {col.align === 'right'
										? 'text-right tabular-nums'
										: ''} {col.key === ALWAYS_VISIBLE
										? 'sticky left-0 z-[1] bg-background font-medium shadow-[inset_-1px_0_0_var(--border)] group-hover:bg-[color-mix(in_oklab,var(--muted)_50%,var(--background))]'
										: ''}"
									style="max-width: {colWidths[col.key]}px"
									onclick={() => startEdit(invoice, col.key)}
								>
									{#if editing}
										<!-- svelte-ignore a11y_autofocus -->
										<input
											class="h-7 w-full min-w-0 rounded-md border border-ring bg-background px-1.5 text-[13px] ring-[3px] ring-ring/50 outline-none {col.align ===
											'right'
												? 'text-right tabular-nums'
												: ''}"
											type={col.type === 'date'
												? 'date'
												: col.type === 'number'
													? 'number'
													: 'text'}
											step={col.type === 'number' ? '0.01' : undefined}
											maxlength={col.type === 'text' ? col.maxLength : undefined}
											aria-label={$i18n.t(col.label)}
											bind:value={editValue}
											on:keydown={handleKeydown}
											on:blur={saveEdit}
											autofocus
										/>
									{:else}
										{@const rawVal = invoice[col.key]}
										{#if rawVal !== null && rawVal !== undefined && String(rawVal) !== ''}
											<span
												class="block truncate {col.key === 'invoice_number' ||
												col.key === 'po_number'
													? 'font-mono text-[12.5px]'
													: ''} {col.key === 'currency' ? 'text-muted-foreground' : ''}"
												title={String(rawVal)}>{displayValue(invoice, col)}</span
											>
										{:else}
											<span class="block truncate text-muted-foreground">—</span>
										{/if}
									{/if}
								</Table.Cell>
							{/each}

							{#each shownExtra as col (col.key)}
								<Table.Cell
									class="overflow-hidden px-2.5 py-1"
									style="max-width: {colWidths[col.key]}px"
								>
									{#if col.key === '_company'}
										{#if invoice.company_id && companiesById[invoice.company_id]}
											<Badge
												variant="secondary"
												class="max-w-full justify-start"
												title={companiesById[invoice.company_id].name}
											>
												<span class="truncate">{companiesById[invoice.company_id].name}</span>
											</Badge>
										{:else}
											<span class="text-muted-foreground">—</span>
										{/if}
									{:else if col.key === '_employee'}
										{#if invoice.employee_id && employeesById[invoice.employee_id]}
											{@const emp = employeesById[invoice.employee_id]}
											<Badge
												variant="secondary"
												class="max-w-full justify-start"
												title="{emp.full_name} ({emp.code})"
											>
												<span class="truncate">{emp.full_name}</span>
											</Badge>
										{:else}
											<span class="text-muted-foreground">—</span>
										{/if}
									{:else if col.key === '_category'}
										{#if invoice.expense_category_id && categoriesById[invoice.expense_category_id]}
											<Badge
												variant="secondary"
												class="max-w-full justify-start"
												title={categoriesById[invoice.expense_category_id].label}
											>
												<span class="truncate"
													>{categoriesById[invoice.expense_category_id].label}</span
												>
											</Badge>
										{:else}
											<span class="text-muted-foreground">—</span>
										{/if}
									{:else if col.key === '_status'}
										<div class="flex items-center gap-1">
											<StatusBadge kind="extraction" status={invoice.processing_status} />
											{#if invoice.needs_review}
												<span class="inline-flex" title={$i18n.t('Needs review')}>
													<StatusBadge
														kind="extraction"
														status="needs_review"
														label={$i18n.t('Review')}
													/>
												</span>
											{/if}
										</div>
									{:else if col.key === '_confidence'}
										{#if invoice.confidence_score !== null && invoice.confidence_score !== undefined}
											<StatusBadge kind="confidence" status={invoice.confidence_score} />
										{:else}
											<span class="text-muted-foreground">—</span>
										{/if}
									{/if}
								</Table.Cell>
							{/each}

							<!-- Actions: one contextual button, the rest in the menu -->
							<Table.Cell class="px-1.5 py-1 text-right">
								<div class="flex items-center justify-end gap-0.5">
									{#if canMarkReviewed(invoice)}
										<Tip
											content={$i18n.t(
												'Mark reviewed — clears the flag and removes the needs-review tag in K4mi'
											)}
										>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label={$i18n.t('Mark reviewed')}
												disabled={reviewingIds.has(invoice.id)}
												onclick={() => handleMarkReviewed(invoice)}
											>
												{#if reviewingIds.has(invoice.id)}<Spinner />{:else}<Check />{/if}
											</Button>
										</Tip>
									{:else if invoice.processing_status === 'failed'}
										<Tip content={$i18n.t('Reprocess')}>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label={$i18n.t('Reprocess')}
												disabled={reprocessingIds.has(invoice.id)}
												onclick={() => handleReprocess(invoice)}
											>
												{#if reprocessingIds.has(invoice.id)}<Spinner />{:else}<RotateCcw />{/if}
											</Button>
										</Tip>
									{:else}
										<Tip content={$i18n.t('Preview')}>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label={$i18n.t('Preview')}
												onclick={() => openPreview(invoice)}
											>
												<Eye />
											</Button>
										</Tip>
									{/if}

									<DropdownMenu.Root>
										<DropdownMenu.Trigger>
											{#snippet child({ props })}
												<Button
													{...props}
													variant="ghost"
													size="icon-xs"
													aria-label={$i18n.t('More actions')}
												>
													{#if busy}<Spinner />{:else}<Ellipsis />{/if}
												</Button>
											{/snippet}
										</DropdownMenu.Trigger>
										<DropdownMenu.Content align="end" class="w-56">
											<DropdownMenu.Label class="truncate text-muted-foreground">
												{invoice.invoice_number || invoice.vendor_name || `#${invoice.id}`}
											</DropdownMenu.Label>
											<DropdownMenu.Item onSelect={() => openPreview(invoice)}>
												<Eye />{$i18n.t('Preview')}
											</DropdownMenu.Item>
											<DropdownMenu.Item onSelect={() => toggleExpand(invoice.id)}>
												{#if expandedRows.has(invoice.id)}<ChevronUp />{:else}<ChevronDown />{/if}
												{$i18n.t('Details')}
											</DropdownMenu.Item>
											{#if invoice.k4mi_document_id}
												<DropdownMenu.Item>
													{#snippet child({ props })}
														<a
															{...props}
															href={k4miDocHref(invoice.k4mi_document_id)}
															target="_blank"
															rel="noopener noreferrer"
														>
															<ExternalLink />{$i18n.t('Open in K4mi')}
														</a>
													{/snippet}
												</DropdownMenu.Item>
											{/if}
											{#if canMarkReviewed(invoice)}
												<DropdownMenu.Item
													disabled={reviewingIds.has(invoice.id)}
													onSelect={() => handleMarkReviewed(invoice)}
												>
													<Check />{$i18n.t('Mark reviewed')}
												</DropdownMenu.Item>
											{/if}
											{#if canReprocess(invoice)}
												<DropdownMenu.Item
													disabled={reprocessingIds.has(invoice.id)}
													onSelect={() => handleReprocess(invoice)}
												>
													<RotateCcw />{$i18n.t('Reprocess')}
												</DropdownMenu.Item>
											{/if}
											<DropdownMenu.Separator />
											<DropdownMenu.Item
												variant="destructive"
												onSelect={() => confirmDelete(invoice)}
											>
												<Trash2 />{$i18n.t('Delete')}
											</DropdownMenu.Item>
										</DropdownMenu.Content>
									</DropdownMenu.Root>
								</div>
							</Table.Cell>
						</Table.Row>

						<!-- Expanded detail row -->
						{#if expandedRows.has(invoice.id)}
							<Table.Row class="bg-muted/30 hover:bg-muted/30">
								<Table.Cell colspan={colCount} class="p-0 whitespace-normal">
									<div class="sticky left-0 grid max-w-[min(72rem,100vw)] gap-6 p-4 lg:grid-cols-2">
										<!-- Left: raw extraction & errors -->
										<div class="flex min-w-0 flex-col gap-4">
											{#if invoice.extraction_raw}
												<div>
													<div class="mb-1.5 text-sm font-medium">{$i18n.t('Raw Extraction')}</div>
													<pre
														class="max-h-48 overflow-auto rounded-md border bg-muted p-3 font-mono text-xs">{JSON.stringify(
															invoice.extraction_raw,
															null,
															2
														)}</pre>
												</div>
											{/if}

											{#if invoice.extraction_errors?.length}
												<div>
													<div class="mb-1.5 text-sm font-medium">
														{$i18n.t('Extraction Errors')}
													</div>
													<ul class="grid gap-1 text-sm">
														{#each invoice.extraction_errors as error}
															<li class="flex items-start gap-1.5 text-destructive">
																<CircleAlert class="mt-0.5 size-3.5 shrink-0" />{error}
															</li>
														{/each}
													</ul>
												</div>
											{/if}

											<dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 text-sm">
												<dt class="text-muted-foreground">{$i18n.t('K4mi ID')}</dt>
												<dd class="font-mono text-[13px]">{invoice.k4mi_document_id ?? '—'}</dd>
												{#if invoice.extraction_model}
													<dt class="text-muted-foreground">{$i18n.t('Model')}</dt>
													<dd class="font-mono text-[13px] break-all">
														{invoice.extraction_model}
													</dd>
												{/if}
												{#if invoice.user_corrected}
													<dt class="text-muted-foreground">{$i18n.t('Edits')}</dt>
													<dd>
														<Badge variant="outline"><Pencil />{$i18n.t('User Corrected')}</Badge>
													</dd>
												{/if}
											</dl>
										</div>

										<!-- Right: line items, notes, tags -->
										<div class="flex min-w-0 flex-col gap-4">
											{#if invoice.line_items?.length}
												<div>
													<div class="mb-1.5 text-sm font-medium">{$i18n.t('Line Items')}</div>
													<div class="overflow-hidden rounded-md border bg-background">
														<Table.Root class="text-[13px]">
															<Table.Header class="bg-muted/50">
																<Table.Row class="hover:bg-transparent">
																	<Table.Head class="h-8">{$i18n.t('Description')}</Table.Head>
																	<Table.Head class="h-8 text-right">{$i18n.t('Qty')}</Table.Head>
																	<Table.Head class="h-8 text-right">{$i18n.t('Price')}</Table.Head>
																	<Table.Head class="h-8 text-right">{$i18n.t('Amount')}</Table.Head
																	>
																</Table.Row>
															</Table.Header>
															<Table.Body>
																{#each invoice.line_items as item}
																	<Table.Row>
																		<Table.Cell class="py-1.5 whitespace-normal"
																			>{item.description ?? '—'}</Table.Cell
																		>
																		<Table.Cell class="py-1.5 text-right tabular-nums"
																			>{item.quantity ?? '—'}</Table.Cell
																		>
																		<Table.Cell class="py-1.5 text-right tabular-nums"
																			>{item.unit_price != null
																				? formatCurrency(item.unit_price)
																				: '—'}</Table.Cell
																		>
																		<Table.Cell class="py-1.5 text-right tabular-nums"
																			>{item.amount != null
																				? formatCurrency(item.amount)
																				: '—'}</Table.Cell
																		>
																	</Table.Row>
																{/each}
															</Table.Body>
														</Table.Root>
													</div>
												</div>
											{/if}

											{#if invoice.k4mi_notes?.length}
												<div>
													<div class="mb-1.5 text-sm font-medium">{$i18n.t('Notes', { context: 'gnos3' })}</div>
													<div class="grid gap-2">
														{#each invoice.k4mi_notes as note}
															<div
																class="rounded-md border bg-background px-3 py-2 text-sm whitespace-pre-wrap"
															>
																{note.text || note.note || ''}
															</div>
														{/each}
													</div>
												</div>
											{/if}

											{#if invoice.k4mi_tags?.length}
												<div>
													<div class="mb-1.5 text-sm font-medium">{$i18n.t('Tags')}</div>
													<div class="flex flex-wrap gap-1">
														{#each invoice.k4mi_tags as tag}
															<Badge variant="outline">{tag}</Badge>
														{/each}
													</div>
												</div>
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

		<!-- Count and pagination -->
		<div class="flex flex-wrap items-center gap-x-6 gap-y-2">
			<TablePagination bind:page count={total} {perPage} class="min-w-0 flex-1" />
			<div class="flex items-center gap-2">
				<Label for="invoice-per-page" class="font-normal text-muted-foreground"
					>{$i18n.t('Per page')}</Label
				>
				<NativeSelect.Root
					id="invoice-per-page"
					size="sm"
					value={String(perPage)}
					onchange={(e: Event) => {
						perPage = Number((e.currentTarget as HTMLSelectElement).value);
						page = 1;
						loadInvoices();
					}}
				>
					<NativeSelect.Option value="25">25</NativeSelect.Option>
					<NativeSelect.Option value="50">50</NativeSelect.Option>
					<NativeSelect.Option value="100">100</NativeSelect.Option>
				</NativeSelect.Root>
			</div>
		</div>
	{/if}
</div>
