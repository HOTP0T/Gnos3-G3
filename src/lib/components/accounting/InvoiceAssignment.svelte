<script lang="ts">
	import { onMount, onDestroy, getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import { toast } from 'svelte-sonner';

	import {
		getCompanyInvoices,
		getUnassignedInvoices,
		assignInvoiceToCompany,
		unassignInvoice,
		bulkAssignInvoices,
		bulkUnassignInvoices,
		confirmInvoiceCategory,
		getBookingPreview,
		getAccounts,
		getAccountingAiStatus,
		aiCategorizeInvoice,
		aiCategorizeAll,
		getAiCategorizeAllStatus,
		downloadInvoicePdf,
		getEmployees,
		getExpenseCategories
	} from '$lib/apis/accounting';
	import { updateInvoice } from '$lib/apis/invoices';
	import { convertRowAmount } from '$lib/utils/currency';
	import K4miDocLink from '$lib/components/common/K4miDocLink.svelte';
	import DocumentPreviewModal from '$lib/components/invoices/DocumentPreviewModal.svelte';
	import InvoiceCreateModal from '$lib/components/accounting/InvoiceCreateModal.svelte';

	import Sparkles from '@lucide/svelte/icons/sparkles';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import Eye from '@lucide/svelte/icons/eye';
	import Download from '@lucide/svelte/icons/download';
	import Ellipsis from '@lucide/svelte/icons/ellipsis';
	import ListFilter from '@lucide/svelte/icons/list-filter';
	import Search from '@lucide/svelte/icons/search';
	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';
	import Check from '@lucide/svelte/icons/check';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import Info from '@lucide/svelte/icons/info';
	import FileText from '@lucide/svelte/icons/file-text';
	import Inbox from '@lucide/svelte/icons/inbox';
	import ArrowUp from '@lucide/svelte/icons/arrow-up';
	import ArrowDown from '@lucide/svelte/icons/arrow-down';
	import UserMinus from '@lucide/svelte/icons/user-minus';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge, badgeVariants } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as Tabs from '$lib/components/ui/tabs/index.js';
	import * as ToggleGroup from '$lib/components/ui/toggle-group/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Popover from '$lib/components/ui/popover/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';
	import KpiCard from '$lib/components/gnos3-ui/KpiCard.svelte';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import TablePagination from '$lib/components/gnos3-ui/TablePagination.svelte';
	import { cn } from '$lib/utils/shadcn.js';

	const i18n: any = getContext('i18n');

	const displayCurrency = getContext<Writable<string>>('displayCurrency');
	const exchangeRates = getContext<Writable<any[]>>('exchangeRates');
	const companyCurrencyCtx = getContext<Writable<string>>('companyCurrency');

	export let companyId: number;

	const companyNameCtx = getContext<Writable<string>>('companyName');

	let showCreateInvoice = false;
	let loading = true;
	let companyError = '';
	let aiAvailable = false;
	let aiCategorizing = false;
	let companyInvoices: any[] = [];
	let companyTotal = 0;
	let unassignedInvoices: any[] = [];
	let unassignedTotal = 0;

	// Filters
	let searchCompany = '';
	let searchUnassigned = '';
	let showUnassigned = true;
	let filterReview: 'all' | 'review' | 'ready' = 'all';

	// Advanced filters
	let dateFrom = '';
	let dateTo = '';
	let minAmount: string = '';
	let maxAmount: string = '';
	let showCompanyFilters = false;
	let showUnassignedFilters = false;

	// Pagination
	let companyPage = 0;
	let unassignedPage = 0;
	let perPage = 50;

	// Sort (server-side)
	let companySortBy = 'invoice_date';
	let companySortDir: 'asc' | 'desc' = 'desc';
	let unassignedSortBy = 'invoice_date';
	let unassignedSortDir: 'asc' | 'desc' = 'desc';

	// Selection
	let selectedCompanyIds: Set<number> = new Set();
	let selectedUnassignedIds: Set<number> = new Set();

	// Expanded rows
	let expandedId: number | null = null;

	// Document preview modal
	let showPreview = false;
	let previewInvoice: any = null;

	// Employees + expense categories (for inline expense assignment)
	let employees: any[] = [];
	let expenseCategories: any[] = [];

	const loadExpenseLookups = async () => {
		try {
			const [empRes, catRes] = await Promise.all([
				getEmployees(companyId, { active: true }),
				getExpenseCategories(companyId)
			]);
			employees = empRes?.employees ?? [];
			expenseCategories = catRes?.categories ?? [];
		} catch (err) {
			// non-fatal — pickers will be empty
		}
	};

	const openPreview = (inv: any) => {
		previewInvoice = inv;
		showPreview = true;
	};

	const handlePreviewUpdate = (updated: any) => {
		// Refresh the invoice in both lists
		const ci = companyInvoices.findIndex((i) => i.id === updated.id);
		if (ci >= 0) {
			companyInvoices[ci] = updated;
			companyInvoices = companyInvoices;
		}
		const ui = unassignedInvoices.findIndex((i) => i.id === updated.id);
		if (ui >= 0) {
			unassignedInvoices[ui] = updated;
			unassignedInvoices = unassignedInvoices;
		}
	};

	// Stats
	let totalAmount = 0;
	let reviewCount = 0;

	// AI activity indicator
	let aiActivity = '';
	let aiProcessingIds: Set<number> = new Set();

	// "AI Categorize All" runs on the worker, one task per invoice. The rows are
	// marked `queued` server-side; poll until none are left so the banner and
	// the per-row spinners reflect real progress instead of a fire-and-forget toast.
	const AI_POLL_MS = 4000;
	const AI_POLL_MAX_MS = 30 * 60 * 1000;
	let aiBatchTotal = 0;
	let aiBatchRemaining = 0;
	let aiPollTimer: ReturnType<typeof setInterval> | null = null;
	let aiPollStartedAt = 0;

	const stopAiPolling = () => {
		if (aiPollTimer) clearInterval(aiPollTimer);
		aiPollTimer = null;
		aiBatchTotal = 0;
		aiBatchRemaining = 0;
	};

	const updateAiBanner = () => {
		const done = Math.max(aiBatchTotal - aiBatchRemaining, 0);
		aiActivity = $i18n.t('AI is suggesting accounts — {{done}} of {{total}} done', {
			done,
			total: aiBatchTotal
		});
	};

	const pollAiBatch = async () => {
		try {
			const s = await getAiCategorizeAllStatus(companyId);
			aiBatchRemaining = s.queued ?? 0;
		} catch (e: any) {
			// Session expired or access revoked: stop, otherwise this tab keeps
			// feeding the module's auth-failure rate limiter every few seconds
			// and locks the whole browser out of the API.
			if (e?.status === 401 || e?.status === 403) {
				stopAiPolling();
				aiActivity = '';
				return;
			}
			return; // transient — keep polling
		}
		await loadCompanyInvoices({ keepSelection: true });
		if (aiBatchRemaining === 0) {
			stopAiPolling();
			aiActivity = '';
			toast.success($i18n.t('AI suggestions ready — review the highlighted accounts'));
			return;
		}
		if (Date.now() - aiPollStartedAt > AI_POLL_MAX_MS) {
			stopAiPolling();
			aiActivity = '';
			toast.info($i18n.t('AI is still working in the background — refresh later to see the rest'));
			return;
		}
		updateAiBanner();
	};

	const startAiPolling = (total: number, remaining: number) => {
		stopAiPolling();
		aiBatchTotal = total;
		aiBatchRemaining = remaining;
		aiPollStartedAt = Date.now();
		updateAiBanner();
		aiPollTimer = setInterval(pollAiBatch, AI_POLL_MS);
	};

	// Account lookup for categorization display
	let accountMap: Record<string, string> = {};
	let accountsList: any[] = [];
	const loadAccounts = async () => {
		try {
			const res = await getAccounts({ company_id: companyId });
			const accts = res?.accounts ?? res ?? [];
			if (Array.isArray(accts)) {
				accountsList = accts;
				for (const a of accts) accountMap[a.code] = a.name;
			}
		} catch {}
	};
	const accountLabel = (code: string | null) => {
		if (!code) return '';
		return accountMap[code] ? `${code} ${accountMap[code]}` : code;
	};

	// Inline edit: patch invoice fields via the auth-wired API client.
	const patchInvoice = async (invoiceId: number, fields: Record<string, any>) =>
		updateInvoice(localStorage.token, invoiceId, fields);

	const saveField = async (invoiceId: number, field: string, value: string) => {
		try {
			let parsed: any = value || null;
			if (['total_amount', 'subtotal', 'tax_amount'].includes(field) && value) {
				parsed = parseFloat(value);
				if (isNaN(parsed)) parsed = null;
			}
			await patchInvoice(invoiceId, { [field]: parsed });
			toast.success($i18n.t('Saved'));
			const idx = companyInvoices.findIndex((i) => i.id === invoiceId);
			if (idx >= 0) companyInvoices[idx][field] = value;
			companyInvoices = companyInvoices;
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	// ── Booking dialog ───────────────────────────────────────────────────
	// Shows the full entry (expense/revenue, VAT, counterparty) before it is
	// created. Every account comes from the human here, a rule, or a confirmed
	// mapping; the dialog will not create an entry with a line left unresolved.
	let pickerInvoiceId: number | null = null;
	let pickerInvoice: any = null;
	let pickerMainCode = '';
	let pickerMainSearch = '';
	let bookingPlan: any = null;
	let bookingLoading = false;
	let pickCounterpartyId: number | '' = '';
	let pickTaxId: number | '' = '';
	let splitMode = false;
	let splitLines: Array<{ account_id: number | null; amount: number | null; description: string }> =
		[];
	let lineSearch: Record<string, string> = {};
	let editingLine: string | null = null; // role whose account picker is open
	// The main account was pre-selected from the AI's suggestion and nobody has
	// picked one yet. Shown as "suggested"; it is booked only when the person
	// creates the draft (design system: an AI suggestion is accepted by a person).
	let pickerSuggested = false;

	$: parentIds = new Set(accountsList.map((a: any) => a.parent_id).filter(Boolean));
	$: leafAccounts = accountsList.filter((a: any) => !parentIds.has(a.id));
	const accountById = (id: number | null | '') => accountsList.find((a: any) => a.id === id);

	const openAccountPicker = async (inv: any) => {
		pickerInvoice = inv;
		const suggested =
			!inv.final_account_code &&
			inv.suggested_account_code &&
			accountMap[inv.suggested_account_code]
				? inv.suggested_account_code
				: '';
		pickerMainCode = inv.final_account_code || suggested;
		pickerSuggested = !!suggested;
		pickerMainSearch = '';
		bookingPlan = null;
		pickCounterpartyId = '';
		pickTaxId = '';
		splitMode = false;
		splitLines = [];
		lineSearch = {};
		editingLine = null;
		pickerInvoiceId = inv.id;
		if (pickerMainCode) await refreshPlan();
	};

	const handleConfirmCategory = async (inv: any) => {
		await openAccountPicker(inv);
	};

	const closePicker = () => {
		pickerInvoiceId = null;
		pickerInvoice = null;
		pickerMainCode = '';
		pickerSuggested = false;
		bookingPlan = null;
	};

	const refreshPlan = async () => {
		if (!pickerInvoiceId || !pickerMainCode) {
			bookingPlan = null;
			return;
		}
		bookingLoading = true;
		try {
			const plan = await getBookingPreview(pickerInvoiceId, {
				account_code: pickerMainCode,
				counterparty_account_id: pickCounterpartyId === '' ? undefined : Number(pickCounterpartyId),
				tax_account_id: pickTaxId === '' ? undefined : Number(pickTaxId)
			});
			bookingPlan = plan;
			// Adopt what the engine resolved (rule / mapping / defaults) as the
			// current choice, so it is visible and can be changed.
			for (const l of plan.lines ?? []) {
				if (l.role === 'counterparty' && l.account_id && pickCounterpartyId === '')
					pickCounterpartyId = l.account_id;
				if (l.role === 'tax' && l.account_id && pickTaxId === '') pickTaxId = l.account_id;
			}
			if (!splitMode) {
				const main = (plan.lines ?? []).find((l: any) => l.role === 'main');
				splitLines = main
					? [
							{
								account_id: main.account_id ?? null,
								amount: main.amount,
								description: main.description ?? ''
							}
						]
					: [];
			}
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
			bookingPlan = null;
		}
		bookingLoading = false;
	};

	const chooseMain = async (code: string) => {
		pickerMainCode = code;
		pickerSuggested = false;
		editingLine = null;
		await refreshPlan();
	};

	const chooseLineAccount = async (role: string, id: number) => {
		if (role === 'counterparty') pickCounterpartyId = id;
		if (role === 'tax') pickTaxId = id;
		editingLine = null;
		await refreshPlan();
	};

	// The search text and account list are passed in so the {#each} re-renders
	// as the user types (Svelte tracks the template expression, not the function body).
	const candidatesFor = (line: any, q: string, leafAccounts: any[]) => {
		q = (q ?? '').toLowerCase();
		const typeOk = (a: any) =>
			line.role === 'tax'
				? ['liability', 'asset'].includes(a.account_type)
				: line.role === 'counterparty'
					? ['liability', 'asset'].includes(a.account_type)
					: true;
		const cands = (line.candidates ?? []).map((c: any) => c.id);
		return leafAccounts
			.filter(
				(a: any) => typeOk(a) && (!q || a.code.includes(q) || a.name.toLowerCase().includes(q))
			)
			.sort(
				(a: any, b: any) =>
					(cands.includes(b.id) ? 1 : 0) - (cands.includes(a.id) ? 1 : 0) ||
					a.code.localeCompare(b.code)
			)
			.slice(0, 60);
	};

	const SOURCE_LABEL: Record<string, string> = {
		human: 'chosen',
		rule: 'from rule',
		mapped: 'Tax → Accounts',
		default: 'country default — confirm',
		company: 'company default',
		missing: 'account required'
	};
	// Design system → "Booking an invoice": a gap is danger, a country default to confirm is
	// warning, anything a person chose or mapped is a neutral outline chip.
	const sourceVariant = (src: string): 'danger' | 'warning' | 'outline' =>
		src === 'missing' ? 'danger' : src === 'default' ? 'warning' : 'outline';

	$: splitTotal = Math.round(splitLines.reduce((s, l) => s + (l.amount ?? 0), 0) * 100) / 100;
	$: splitOk =
		!splitMode ||
		(splitLines.length > 0 &&
			splitLines.every((l) => l.account_id) &&
			Math.abs(splitTotal - (bookingPlan?.subtotal ?? 0)) < 0.005);
	$: planReady = !!bookingPlan && !bookingLoading && bookingPlan.complete && splitOk;

	const handleConfirmPicker = async () => {
		if (!pickerInvoiceId || !pickerMainCode || !planReady) return;
		const invoiceId = pickerInvoiceId;
		const payload: any = {
			account_code: pickerMainCode,
			counterparty_account_id: pickCounterpartyId === '' ? undefined : Number(pickCounterpartyId),
			tax_account_id: pickTaxId === '' ? undefined : Number(pickTaxId)
		};
		if (splitMode)
			payload.main_lines = splitLines.map((l) => ({
				account_id: l.account_id,
				amount: l.amount ?? 0,
				description: l.description
			}));
		closePicker();
		aiProcessingIds.add(invoiceId);
		aiProcessingIds = aiProcessingIds;
		aiActivity = $i18n.t('Creating draft entry...');
		try {
			const result = await confirmInvoiceCategory(invoiceId, payload);
			const txnId = result?.transaction_id;
			if (txnId && result?.booking_gaps?.length) {
				toast.warning(
					$i18n.t('Draft entry') +
						` #${txnId} ` +
						$i18n.t('created with lines still needing an account — open it in Entries')
				);
			} else if (txnId) {
				toast.success($i18n.t('Draft entry') + ` #${txnId} ` + $i18n.t('created'));
			} else {
				toast.success($i18n.t('Account confirmed'));
			}
			await reloadAll();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		aiProcessingIds.delete(invoiceId);
		aiProcessingIds = aiProcessingIds;
		aiActivity = '';
	};

	// Client-side review filter (quick local filter, no server round-trip)
	$: filteredCompany = companyInvoices.filter((inv) => {
		if (filterReview === 'review' && !inv.needs_review) return false;
		if (filterReview === 'ready' && inv.needs_review) return false;
		return true;
	});

	$: allCompanySelected =
		filteredCompany.length > 0 && filteredCompany.every((i) => selectedCompanyIds.has(i.id));
	$: allUnassignedSelected =
		unassignedInvoices.length > 0 &&
		unassignedInvoices.every((i) => selectedUnassignedIds.has(i.id));

	const loadCompanyInvoices = async (opts: { keepSelection?: boolean } = {}) => {
		try {
			const res = await getCompanyInvoices(companyId, {
				q: searchCompany || undefined,
				date_from: dateFrom || undefined,
				date_to: dateTo || undefined,
				min_amount: minAmount ? parseFloat(minAmount) : undefined,
				max_amount: maxAmount ? parseFloat(maxAmount) : undefined,
				sort_by: companySortBy,
				sort_dir: companySortDir,
				limit: perPage,
				offset: companyPage * perPage
			});
			companyInvoices = res.invoices ?? [];
			companyTotal = res.total ?? 0;
			totalAmount = companyInvoices.reduce((s, i) => s + (parseFloat(i.total_amount) || 0), 0);
			reviewCount = companyInvoices.filter((i) => i.needs_review).length;
			if (!opts.keepSelection) selectedCompanyIds = new Set();
			companyError = '';
		} catch (err: any) {
			companyError = err?.detail ?? `${err}`;
			toast.error(`${err}`);
		}
	};

	const loadUnassignedInvoices = async () => {
		try {
			const res = await getUnassignedInvoices({
				q: searchUnassigned || undefined,
				date_from: dateFrom || undefined,
				date_to: dateTo || undefined,
				min_amount: minAmount ? parseFloat(minAmount) : undefined,
				max_amount: maxAmount ? parseFloat(maxAmount) : undefined,
				sort_by: unassignedSortBy,
				sort_dir: unassignedSortDir,
				limit: perPage,
				offset: unassignedPage * perPage
			});
			unassignedInvoices = res.invoices ?? [];
			unassignedTotal = res.total ?? 0;
			selectedUnassignedIds = new Set();
		} catch (err) {
			toast.error(`${err}`);
		}
	};

	const reloadAll = async () => {
		await Promise.all([
			loadCompanyInvoices(),
			showUnassigned ? loadUnassignedInvoices() : Promise.resolve()
		]);
	};

	const handleBulkAssign = async () => {
		if (selectedUnassignedIds.size === 0) return;
		const count = selectedUnassignedIds.size;
		aiActivity =
			$i18n.t('AI is categorizing') +
			` ${count} ` +
			$i18n.t('invoice(s) and creating journal entries...');
		try {
			await bulkAssignInvoices(companyId, [...selectedUnassignedIds]);
			toast.success(
				$i18n.t(`${count} invoice(s) assigned — AI categorized and created draft entries`)
			);
			await reloadAll();
		} catch (err) {
			toast.error(`${err}`);
		}
		aiActivity = '';
	};

	const handleBulkUnassign = async () => {
		if (selectedCompanyIds.size === 0) return;
		try {
			await bulkUnassignInvoices(companyId, [...selectedCompanyIds]);
			toast.success($i18n.t(`${selectedCompanyIds.size} invoice(s) removed`));
			await reloadAll();
		} catch (err) {
			toast.error(`${err}`);
		}
	};

	const toggleSort = (field: string, panel: 'company' | 'unassigned') => {
		if (panel === 'company') {
			if (companySortBy === field) companySortDir = companySortDir === 'asc' ? 'desc' : 'asc';
			else {
				companySortBy = field;
				companySortDir = 'asc';
			}
			companyPage = 0;
			loadCompanyInvoices();
		} else {
			if (unassignedSortBy === field)
				unassignedSortDir = unassignedSortDir === 'asc' ? 'desc' : 'asc';
			else {
				unassignedSortBy = field;
				unassignedSortDir = 'asc';
			}
			unassignedPage = 0;
			loadUnassignedInvoices();
		}
	};

	const toggleSelectAllCompany = () => {
		if (allCompanySelected) selectedCompanyIds = new Set();
		else selectedCompanyIds = new Set(filteredCompany.map((i) => i.id));
		selectedCompanyIds = selectedCompanyIds;
	};

	const toggleSelectAllUnassigned = () => {
		if (allUnassignedSelected) selectedUnassignedIds = new Set();
		else selectedUnassignedIds = new Set(unassignedInvoices.map((i) => i.id));
		selectedUnassignedIds = selectedUnassignedIds;
	};

	const toggleCompanySelect = (id: number) => {
		if (selectedCompanyIds.has(id)) selectedCompanyIds.delete(id);
		else selectedCompanyIds.add(id);
		selectedCompanyIds = selectedCompanyIds;
	};

	const toggleUnassignedSelect = (id: number) => {
		if (selectedUnassignedIds.has(id)) selectedUnassignedIds.delete(id);
		else selectedUnassignedIds.add(id);
		selectedUnassignedIds = selectedUnassignedIds;
	};

	let searchTimer: ReturnType<typeof setTimeout>;
	const onSearchCompany = () => {
		clearTimeout(searchTimer);
		searchTimer = setTimeout(() => {
			companyPage = 0;
			loadCompanyInvoices();
		}, 300);
	};
	let searchTimer2: ReturnType<typeof setTimeout>;
	const onSearchUnassigned = () => {
		clearTimeout(searchTimer2);
		searchTimer2 = setTimeout(() => {
			unassignedPage = 0;
			loadUnassignedInvoices();
		}, 300);
	};

	const onCompanyFilterChange = () => {
		companyPage = 0;
		loadCompanyInvoices();
	};
	const onUnassignedFilterChange = () => {
		unassignedPage = 0;
		loadUnassignedInvoices();
	};

	const clearCompanyFilters = () => {
		dateFrom = '';
		dateTo = '';
		minAmount = '';
		maxAmount = '';
		companySortBy = 'invoice_date';
		companySortDir = 'desc';
		companyPage = 0;
		loadCompanyInvoices();
	};

	const clearUnassignedFilters = () => {
		dateFrom = '';
		dateTo = '';
		minAmount = '';
		maxAmount = '';
		unassignedSortBy = 'invoice_date';
		unassignedSortDir = 'desc';
		unassignedPage = 0;
		loadUnassignedInvoices();
	};

	const setCompanySortPreset = (value: string) => {
		switch (value) {
			case 'date_desc':
				companySortBy = 'invoice_date';
				companySortDir = 'desc';
				break;
			case 'date_asc':
				companySortBy = 'invoice_date';
				companySortDir = 'asc';
				break;
			case 'amount_desc':
				companySortBy = 'total_amount';
				companySortDir = 'desc';
				break;
			case 'amount_asc':
				companySortBy = 'total_amount';
				companySortDir = 'asc';
				break;
			case 'vendor_asc':
				companySortBy = 'vendor_name';
				companySortDir = 'asc';
				break;
			case 'vendor_desc':
				companySortBy = 'vendor_name';
				companySortDir = 'desc';
				break;
		}
		companyPage = 0;
		loadCompanyInvoices();
	};

	const setUnassignedSortPreset = (value: string) => {
		switch (value) {
			case 'date_desc':
				unassignedSortBy = 'invoice_date';
				unassignedSortDir = 'desc';
				break;
			case 'date_asc':
				unassignedSortBy = 'invoice_date';
				unassignedSortDir = 'asc';
				break;
			case 'amount_desc':
				unassignedSortBy = 'total_amount';
				unassignedSortDir = 'desc';
				break;
			case 'amount_asc':
				unassignedSortBy = 'total_amount';
				unassignedSortDir = 'asc';
				break;
			case 'vendor_asc':
				unassignedSortBy = 'vendor_name';
				unassignedSortDir = 'asc';
				break;
			case 'vendor_desc':
				unassignedSortBy = 'vendor_name';
				unassignedSortDir = 'desc';
				break;
		}
		unassignedPage = 0;
		loadUnassignedInvoices();
	};

	$: companySortPreset = `${companySortBy === 'total_amount' ? 'amount' : companySortBy === 'vendor_name' ? 'vendor' : 'date'}_${companySortDir}`;
	$: unassignedSortPreset = `${unassignedSortBy === 'total_amount' ? 'amount' : unassignedSortBy === 'vendor_name' ? 'vendor' : 'date'}_${unassignedSortDir}`;

	// ─── Currency conversion ────────────────────────────────────────────────────
	$: nativeCurrency = $companyCurrencyCtx || 'EUR';

	// Try to get native currency from company data when loaded
	const _trySetNativeCurrency = (currency: string) => {
		if (currency) nativeCurrency = currency;
	};

	// Each invoice is shown in the selected display currency converted FROM ITS
	// OWN currency (a EUR bill is EUR, whatever the company's books are in).
	// In the company currency the row shows the figure the books use, sent by the
	// server (`base_amount`: the rate of the invoice's own entry, else the rate an
	// entry for it would carry; none when no current rate is on file) — not the
	// nearest rate in the browser's windowed rate list.
	const cvt = (amount: any, date?: string, rowCurrency?: string | null, inv?: any) => {
		const c = convertRowAmount(
			amount,
			rowCurrency,
			$displayCurrency,
			nativeCurrency,
			$exchangeRates ?? [],
			date
		);
		if (!c.converting || !inv?.base_rate_source || c.to !== (inv.base_currency ?? '').toUpperCase())
			return c;
		return inv.base_amount != null
			? { ...c, display: fmt2(Number(inv.base_amount)), hasRate: true }
			: { ...c, display: '', hasRate: false };
	};

	// The summary card: every invoice converted into the display currency (or the
	// company currency), so mixed-currency lists add up to something meaningful.
	$: summaryCurrency = ($displayCurrency || nativeCurrency || '').toUpperCase();
	$: summary = (() => {
		let sum = 0;
		let missing = 0;
		for (const i of companyInvoices) {
			const c = cvt(i.total_amount, i.invoice_date, i.currency, i);
			if (!c.hasRate) {
				missing += 1;
				continue;
			}
			sum += parseFloat(String(c.display).replace(/[^0-9.-]/g, '')) || 0;
		}
		return { sum, missing };
	})();

	const fmt = (amount: string | number | null, cur: string = 'USD'): string => {
		if (!amount) return '-';
		const n = typeof amount === 'string' ? parseFloat(amount) : amount;
		return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	};

	const fmt2 = (n: number | null | undefined): string =>
		n ? n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '';

	$: activeFilterCount = [dateFrom, dateTo, minAmount, maxAmount].filter(Boolean).length;

	// The invoice fields editable in the expanded row (saved on blur, as before)
	const INVOICE_FIELDS: Array<{ field: string; label: string; type: 'text' | 'date' | 'number' }> =
		[
			{ field: 'vendor_name', label: 'Vendor', type: 'text' },
			{ field: 'client_name', label: 'Client', type: 'text' },
			{ field: 'invoice_number', label: 'Invoice #', type: 'text' },
			{ field: 'invoice_date', label: 'Invoice Date', type: 'date' },
			{ field: 'due_date', label: 'Due Date', type: 'date' },
			{ field: 'total_amount', label: 'Total Amount', type: 'number' },
			{ field: 'subtotal', label: 'Subtotal', type: 'number' },
			{ field: 'tax_amount', label: 'Tax Amount', type: 'number' },
			{ field: 'currency', label: 'Currency', type: 'text' },
			{ field: 'description', label: 'Description', type: 'text' },
			{ field: 'po_number', label: 'PO#', type: 'text' },
			{ field: 'business_unit', label: 'Business Unit', type: 'text' }
		];

	async function handleAiCategorizeAll() {
		aiCategorizing = true;
		try {
			const result = await aiCategorizeAll(companyId);
			const queued = result.queued ?? 0;
			if (queued === 0) {
				toast.info($i18n.t('Nothing to categorize — every invoice already has an account'));
				return;
			}
			toast.success($i18n.t('{{n}} invoice(s) queued for AI suggestion', { n: queued }));
			await loadCompanyInvoices({ keepSelection: true }); // rows now carry `queued`
			startAiPolling(queued, queued);
		} catch (e) {
			toast.error($i18n.t('AI categorization failed'));
		} finally {
			aiCategorizing = false;
		}
	}

	async function handleAiCategorizeOne(invoiceId: number) {
		aiProcessingIds.add(invoiceId);
		aiProcessingIds = aiProcessingIds;
		try {
			const result = await aiCategorizeInvoice(invoiceId);
			if (result.status === 'suggested') {
				toast.success($i18n.t(`AI suggests: ${result.account_code} (${result.reasoning})`));
				await loadCompanyInvoices({ keepSelection: true });
			} else {
				toast.info($i18n.t('AI could not determine account'));
			}
		} catch (e) {
			toast.error($i18n.t('AI categorization failed'));
		} finally {
			aiProcessingIds.delete(invoiceId);
			aiProcessingIds = aiProcessingIds;
		}
	}

	onMount(async () => {
		await Promise.all([
			loadCompanyInvoices(),
			loadAccounts(),
			loadUnassignedInvoices(),
			loadExpenseLookups()
		]);
		loading = false;
		// Non-blocking AI status check
		getAccountingAiStatus()
			.then((s) => (aiAvailable = s.available))
			.catch(() => (aiAvailable = false));
		// A batch started earlier (or on another tab) may still be running
		getAiCategorizeAllStatus(companyId)
			.then((s) => {
				if ((s.queued ?? 0) > 0) startAiPolling(s.queued, s.queued);
			})
			.catch(() => {});
	});

	onDestroy(stopAiPolling);
</script>

<!-- Sortable column header (server-side sort) -->
{#snippet sortHead(
	field: string,
	label: string,
	panel: 'company' | 'unassigned',
	right: boolean = false
)}
	{@const active = (panel === 'company' ? companySortBy : unassignedSortBy) === field}
	{@const dir = panel === 'company' ? companySortDir : unassignedSortDir}
	<Table.Head
		class={right ? 'text-right' : ''}
		aria-sort={active ? (dir === 'asc' ? 'ascending' : 'descending') : undefined}
	>
		<button
			type="button"
			class={cn(
				'-mx-1 inline-flex items-center gap-1 rounded-sm px-1 hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none',
				right && 'flex-row-reverse'
			)}
			onclick={() => toggleSort(field, panel)}
		>
			{$i18n.t(label)}
			{#if active}
				{#if dir === 'asc'}<ArrowUp class="size-3.5 text-muted-foreground" />{:else}<ArrowDown
						class="size-3.5 text-muted-foreground"
					/>{/if}
			{/if}
		</button>
	</Table.Head>
{/snippet}

<!-- Amount in the display currency, converted from the invoice's own currency -->
{#snippet amountCell(inv: any)}
	<Table.Cell class="text-right tabular-nums">
		{#key $displayCurrency}
			{@const c = cvt(inv.total_amount, inv.invoice_date, inv.currency, inv)}
			{#if c.converting}
				{#if c.hasRate}
					<div class="font-medium">
						{c.display} <span class="text-xs font-normal text-muted-foreground">{c.to}</span>
					</div>
					<div class="text-xs text-muted-foreground">{c.original} {c.from}</div>
				{:else}
					<span class="inline-flex items-center gap-1">
						{c.original}
						<span class="text-xs text-muted-foreground">{c.from}</span>
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
	</Table.Cell>
{/snippet}

<!-- Secondary filters (shared by both lists, as before) -->
{#snippet filtersPopover(panel: 'company' | 'unassigned')}
	{@const onChange = panel === 'company' ? onCompanyFilterChange : onUnassignedFilterChange}
	<Popover.Root>
		<Popover.Trigger>
			{#snippet child({ props })}
				<Button {...props} variant="outline" size="sm">
					<ListFilter />{$i18n.t('Filters')}
					{#if activeFilterCount > 0}<Badge variant="count">{activeFilterCount}</Badge>{/if}
				</Button>
			{/snippet}
		</Popover.Trigger>
		<Popover.Content align="start" class="w-80">
			<div class="grid gap-3">
				<div class="grid grid-cols-2 gap-3">
					<div class="grid gap-1.5">
						<Label for="{panel}-date-from" class="text-[13px]">{$i18n.t('From')}</Label>
						<Input
							id="{panel}-date-from"
							type="date"
							class="h-8"
							bind:value={dateFrom}
							onchange={onChange}
						/>
					</div>
					<div class="grid gap-1.5">
						<Label for="{panel}-date-to" class="text-[13px]">{$i18n.t('To')}</Label>
						<Input
							id="{panel}-date-to"
							type="date"
							class="h-8"
							bind:value={dateTo}
							onchange={onChange}
						/>
					</div>
					<div class="grid gap-1.5">
						<Label for="{panel}-min" class="text-[13px]">{$i18n.t('Min Amount')}</Label>
						<Input
							id="{panel}-min"
							type="number"
							step="0.01"
							placeholder="0.00"
							class="h-8 text-right tabular-nums"
							bind:value={minAmount}
							onchange={onChange}
						/>
					</div>
					<div class="grid gap-1.5">
						<Label for="{panel}-max" class="text-[13px]">{$i18n.t('Max Amount')}</Label>
						<Input
							id="{panel}-max"
							type="number"
							step="0.01"
							placeholder="0.00"
							class="h-8 text-right tabular-nums"
							bind:value={maxAmount}
							onchange={onChange}
						/>
					</div>
				</div>
				<div class="grid gap-1.5">
					<Label for="{panel}-sort" class="text-[13px]">{$i18n.t('Sort')}</Label>
					<NativeSelect.Root
						id="{panel}-sort"
						size="sm"
						class="w-full"
						value={panel === 'company' ? companySortPreset : unassignedSortPreset}
						onchange={(e: Event) => {
							const v = (e.currentTarget as HTMLSelectElement).value;
							if (panel === 'company') setCompanySortPreset(v);
							else setUnassignedSortPreset(v);
						}}
					>
						<NativeSelect.Option value="date_desc">{$i18n.t('Date (newest)')}</NativeSelect.Option>
						<NativeSelect.Option value="date_asc">{$i18n.t('Date (oldest)')}</NativeSelect.Option>
						<NativeSelect.Option value="amount_desc"
							>{$i18n.t('Amount (highest)')}</NativeSelect.Option
						>
						<NativeSelect.Option value="amount_asc"
							>{$i18n.t('Amount (lowest)')}</NativeSelect.Option
						>
						<NativeSelect.Option value="vendor_asc">{$i18n.t('Vendor (A-Z)')}</NativeSelect.Option>
						<NativeSelect.Option value="vendor_desc">{$i18n.t('Vendor (Z-A)')}</NativeSelect.Option>
					</NativeSelect.Root>
				</div>
				<div class="flex justify-end">
					<Button
						variant="ghost"
						size="sm"
						onclick={panel === 'company' ? clearCompanyFilters : clearUnassignedFilters}
					>
						{$i18n.t('Clear Filters')}
					</Button>
				</div>
			</div>
		</Popover.Content>
	</Popover.Root>
{/snippet}

{#snippet searchBox(id: string, placeholder: string, panel: 'company' | 'unassigned')}
	<div class="relative w-full sm:w-72">
		<Search
			class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
		/>
		{#if panel === 'company'}
			<Input
				{id}
				type="search"
				class="h-8 pl-8"
				{placeholder}
				aria-label={placeholder}
				bind:value={searchCompany}
				oninput={onSearchCompany}
			/>
		{:else}
			<Input
				{id}
				type="search"
				class="h-8 pl-8"
				{placeholder}
				aria-label={placeholder}
				bind:value={searchUnassigned}
				oninput={onSearchUnassigned}
			/>
		{/if}
	</div>
{/snippet}

<div class="flex flex-col gap-4">
	{#if loading}
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(12.5rem,100%),1fr))] gap-4">
			{#each Array(3) as _}<Skeleton class="h-[104px] rounded-xl" />{/each}
		</div>
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(8) as _}<Skeleton class="h-8 w-full" />{/each}
		</div>
	{:else}
		<!-- AI activity: the batch shows "X of N done" with a progress bar; one-off work a spinner -->
		{#if aiActivity}
			<Card.Root size="sm" class="gap-2.5" aria-live="polite">
				<Card.Content class="grid gap-2.5">
					<div class="flex items-center gap-2 text-sm font-medium">
						{#if aiBatchTotal > 0}
							<Sparkles class="size-4 shrink-0" aria-hidden="true" />
						{:else}
							<Spinner class="size-4 shrink-0" />
						{/if}
						<span>{aiActivity}</span>
					</div>
					{#if aiBatchTotal > 0}
						<Progress
							value={Math.round(
								(Math.max(aiBatchTotal - aiBatchRemaining, 0) / Math.max(aiBatchTotal, 1)) * 100
							)}
							max={100}
							aria-label={$i18n.t('AI suggestions')}
						/>
					{/if}
				</Card.Content>
			</Card.Root>
		{/if}

		<!-- Stats -->
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(12.5rem,100%),1fr))] gap-4">
			<KpiCard label={$i18n.t('Invoice Treatment')} value={companyTotal} />
			{#key $displayCurrency}
				<KpiCard
					label={$i18n.t('Total Amount')}
					value={`${summary.sum.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${summaryCurrency}`}
				>
					{#snippet footer()}
						{#if summary.missing > 0}
							<span class="inline-flex items-center gap-1">
								<TriangleAlert class="size-3.5 text-warning" aria-hidden="true" />
								{$i18n.t('{{n}} invoice(s) without an exchange rate not included', {
									n: summary.missing
								})}
							</span>
						{/if}
					{/snippet}
				</KpiCard>
			{/key}
			<KpiCard label={$i18n.t('Needs Review')} value={reviewCount}>
				{#snippet action()}
					{#if reviewCount > 0}<StatusBadge kind="booking" status="review" />{/if}
				{/snippet}
			</KpiCard>
		</div>

		<!-- Company invoices: toolbar -->
		<div class="flex flex-wrap items-center gap-2">
			<Tabs.Root
				value={filterReview}
				onValueChange={(v) => {
					filterReview = v as typeof filterReview;
				}}
			>
				<Tabs.List>
					<Tabs.Trigger value="all">{$i18n.t('All')}</Tabs.Trigger>
					<Tabs.Trigger value="review">{$i18n.t('Needs Review')}</Tabs.Trigger>
					<Tabs.Trigger value="ready">{$i18n.t('Ready')}</Tabs.Trigger>
				</Tabs.List>
			</Tabs.Root>
			{@render searchBox(
				'inv-search',
				$i18n.t('Search by vendor, invoice #, client...'),
				'company'
			)}
			{@render filtersPopover('company')}

			<div class="ml-auto flex flex-wrap items-center gap-2">
				{#if selectedCompanyIds.size > 0}
					<div
						class="flex items-center gap-2 rounded-lg border bg-card py-1 pr-1 pl-3 text-sm shadow-md"
					>
						<span
							><span class="font-medium tabular-nums">{selectedCompanyIds.size}</span>
							{$i18n.t('selected')}</span
						>
						<Button
							variant="ghost"
							size="xs"
							class="text-destructive hover:text-destructive"
							onclick={handleBulkUnassign}
						>
							<UserMinus />{$i18n.t('Unassign Selected')}
						</Button>
						<Tip content={$i18n.t('Clear')}>
							<Button
								variant="ghost"
								size="icon-xs"
								aria-label={$i18n.t('Clear')}
								onclick={() => {
									selectedCompanyIds = new Set();
								}}
							>
								<X />
							</Button>
						</Tip>
					</div>
				{:else}
					{#if aiAvailable && companyInvoices.some((i) => !i.final_account_code)}
						<Tip
							content={$i18n.t(
								'The accounting AI will suggest an account for every invoice without one (vendors with a rule use the rule)'
							)}
						>
							<Button
								variant="outline"
								size="sm"
								disabled={aiCategorizing || aiBatchTotal > 0}
								onclick={handleAiCategorizeAll}
							>
								{#if aiCategorizing || aiBatchTotal > 0}<Spinner />{:else}<Sparkles />{/if}
								{$i18n.t('AI Categorize All')}
							</Button>
						</Tip>
					{/if}
					<Button
						variant="outline"
						size="sm"
						onclick={() => {
							showUnassigned = !showUnassigned;
							if (showUnassigned) loadUnassignedInvoices();
						}}
					>
						{showUnassigned ? $i18n.t('Hide Unassigned') : $i18n.t('Browse Unassigned')}
					</Button>
					<Button
						variant="outline"
						size="sm"
						onclick={() => {
							showCreateInvoice = true;
						}}
					>
						<Plus />{$i18n.t('Create Invoice')}
					</Button>
				{/if}
				<NativeSelect.Root
					size="sm"
					value={perPage}
					aria-label={$i18n.t('Rows per page')}
					onchange={(e: Event) => {
						perPage = Number((e.currentTarget as HTMLSelectElement).value);
						companyPage = 0;
						loadCompanyInvoices();
					}}
				>
					<NativeSelect.Option value={20}>20</NativeSelect.Option>
					<NativeSelect.Option value={50}>50</NativeSelect.Option>
					<NativeSelect.Option value={100}>100</NativeSelect.Option>
				</NativeSelect.Root>
			</div>
		</div>

		<!-- Company invoices: table -->
		{#if companyError && companyInvoices.length === 0}
			<Alert.Root variant="destructive">
				<CircleAlert />
				<Alert.Title>{$i18n.t('Could not load the invoices')}</Alert.Title>
				<Alert.Description>{companyError}</Alert.Description>
				<Alert.Action>
					<Button variant="outline" size="sm" onclick={() => loadCompanyInvoices()}>
						{$i18n.t('Retry')}
					</Button>
				</Alert.Action>
			</Alert.Root>
		{:else if filteredCompany.length === 0}
			<Empty.Root class="border border-dashed">
				<Empty.Header>
					<Empty.Media variant="icon"><FileText /></Empty.Media>
					<Empty.Title>{$i18n.t('No invoices assigned to this company')}</Empty.Title>
					<Empty.Description>
						{$i18n.t('Assign invoices from the unassigned list, or create one.')}
					</Empty.Description>
				</Empty.Header>
				{#if !showUnassigned}
					<Empty.Content>
						<Button
							variant="outline"
							size="sm"
							onclick={() => {
								showUnassigned = true;
								loadUnassignedInvoices();
							}}
						>
							{$i18n.t('Browse Unassigned')}
						</Button>
					</Empty.Content>
				{/if}
			</Empty.Root>
		{:else}
			<div class="overflow-hidden rounded-md border">
				<Table.Root>
					<Table.Header class="bg-muted/50">
						<Table.Row class="hover:bg-transparent">
							<Table.Head class="w-8">
								<Checkbox
									checked={allCompanySelected}
									onCheckedChange={toggleSelectAllCompany}
									aria-label={$i18n.t('Select all')}
								/>
							</Table.Head>
							{@render sortHead('invoice_number', 'Invoice #', 'company')}
							{@render sortHead('vendor_name', 'Vendor', 'company')}
							{@render sortHead('client_name', 'Client', 'company')}
							{@render sortHead('invoice_date', 'Date', 'company')}
							{@render sortHead('total_amount', 'Amount', 'company', true)}
							<Table.Head>{$i18n.t('Status')}</Table.Head>
							<Table.Head>{$i18n.t('Account', { context: 'gnos3' })}</Table.Head>
							<Table.Head>{$i18n.t('Employee')}</Table.Head>
							<Table.Head>{$i18n.t('Category')}</Table.Head>
							<Table.Head>{$i18n.t('Journal')}</Table.Head>
							<Table.Head>{$i18n.t('Payment')}</Table.Head>
							<Table.Head class="w-16"><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head
							>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each filteredCompany as inv (inv.id)}
							<Table.Row
								class={cn('cursor-pointer', expandedId === inv.id && 'bg-muted/50')}
								data-state={selectedCompanyIds.has(inv.id) ? 'selected' : undefined}
								aria-expanded={expandedId === inv.id}
								tabindex={0}
								onclick={() => {
									expandedId = expandedId === inv.id ? null : inv.id;
								}}
								onkeydown={(e: KeyboardEvent) => {
									if (e.target !== e.currentTarget) return;
									if (e.key === 'Enter' || e.key === ' ') {
										e.preventDefault();
										expandedId = expandedId === inv.id ? null : inv.id;
									}
								}}
							>
								<Table.Cell onclick={(e: MouseEvent) => e.stopPropagation()}>
									<Checkbox
										checked={selectedCompanyIds.has(inv.id)}
										onCheckedChange={() => toggleCompanySelect(inv.id)}
										aria-label={$i18n.t('Select')}
									/>
								</Table.Cell>
								<Table.Cell class="font-mono text-[13px]">
									{#if inv.k4mi_document_id}<K4miDocLink
											docId={inv.k4mi_document_id}
											title={$i18n.t('Open in K4mi')}
											stopPropagation>{inv.invoice_number ?? '—'}</K4miDocLink
										>{:else}{inv.invoice_number ?? '—'}{/if}
								</Table.Cell>
								<Table.Cell class="max-w-[10rem] truncate" title={inv.vendor_name ?? ''}
									>{inv.vendor_name ?? '—'}</Table.Cell
								>
								<Table.Cell class="max-w-[10rem] truncate" title={inv.client_name ?? ''}
									>{inv.client_name ?? '—'}</Table.Cell
								>
								<Table.Cell class="tabular-nums">{inv.invoice_date ?? '—'}</Table.Cell>
								{@render amountCell(inv)}
								<Table.Cell>
									<StatusBadge kind="booking" status={inv.needs_review ? 'review' : 'ready'} />
								</Table.Cell>
								<Table.Cell onclick={(e: MouseEvent) => e.stopPropagation()}>
									{#if inv.final_account_code}
										<Tip
											content="{accountLabel(inv.final_account_code)} — {$i18n.t(
												'click to change'
											)}"
										>
											<button
												type="button"
												class={cn(
													badgeVariants({ variant: 'outline' }),
													'cursor-pointer hover:bg-accent'
												)}
												onclick={() => openAccountPicker(inv)}
											>
												<Check aria-hidden="true" /><span class="font-mono"
													>{inv.final_account_code}</span
												>
											</button>
										</Tip>
									{:else if inv.categorization_status === 'queued' || aiProcessingIds.has(inv.id)}
										<Tip content={$i18n.t('AI is suggesting an account for this invoice')}>
											<Badge variant="status">
												<LoaderCircle
													class="animate-spin motion-reduce:animate-none"
													aria-hidden="true"
												/>{$i18n.t('AI…')}
											</Badge>
										</Tip>
									{:else if inv.suggested_account_code}
										<Tip
											content="{$i18n.t('AI suggestion')}: {accountLabel(
												inv.suggested_account_code
											)}"
										>
											<button
												type="button"
												class={cn(badgeVariants({ variant: 'info' }), 'cursor-pointer')}
												onclick={() => openAccountPicker(inv)}
											>
												<Sparkles aria-hidden="true" /><span class="font-mono"
													>{inv.suggested_account_code}</span
												>
												{$i18n.t('suggested')}
											</button>
										</Tip>
									{:else}
										<span class="inline-flex items-center gap-1">
											<Tip content={$i18n.t('Click to assign account')}>
												<Button variant="outline" size="xs" onclick={() => openAccountPicker(inv)}>
													{$i18n.t('Assign')}
												</Button>
											</Tip>
											{#if aiAvailable}
												<Tip content={$i18n.t('AI categorize')}>
													<Button
														variant="ghost"
														size="icon-xs"
														aria-label={$i18n.t('AI categorize')}
														onclick={() => handleAiCategorizeOne(inv.id)}
													>
														<Sparkles />
													</Button>
												</Tip>
											{/if}
										</span>
									{/if}
								</Table.Cell>
								<Table.Cell
									class="max-w-[9rem] truncate"
									title={employees.find((e) => e.id === inv.employee_id)?.full_name ?? ''}
									onclick={(e: MouseEvent) => e.stopPropagation()}
								>
									{#if inv.employee_id}
										{@const emp = employees.find((e) => e.id === inv.employee_id)}
										{emp?.full_name ?? `#${inv.employee_id}`}
									{:else}
										<span class="text-muted-foreground">—</span>
									{/if}
								</Table.Cell>
								<Table.Cell onclick={(e: MouseEvent) => e.stopPropagation()}>
									{#if inv.expense_category_id}
										{@const cat = expenseCategories.find((c) => c.id === inv.expense_category_id)}
										{cat?.label ?? `#${inv.expense_category_id}`}
									{:else}
										<span class="text-muted-foreground">—</span>
									{/if}
								</Table.Cell>
								<Table.Cell onclick={(e: MouseEvent) => e.stopPropagation()}>
									{#if inv.transaction_id}
										<Tip
											content={inv.transaction_status === 'draft'
												? $i18n.t('Draft — review and post in Entries tab')
												: $i18n.t('Posted')}
										>
											<StatusBadge
												kind="entry"
												status={inv.transaction_status === 'draft' ? 'draft' : 'posted'}
											/>
										</Tip>
									{:else}
										<span class="text-muted-foreground">—</span>
									{/if}
								</Table.Cell>
								<Table.Cell>
									{#if inv.payment_status === 'paid'}
										<StatusBadge kind="booking" status="paid" />
									{:else if inv.transaction_id}
										<StatusBadge kind="booking" status="unpaid" />
									{:else}
										<span class="text-muted-foreground">—</span>
									{/if}
								</Table.Cell>
								<Table.Cell class="text-right" onclick={(e: MouseEvent) => e.stopPropagation()}>
									<div class="inline-flex items-center gap-0.5">
										<Tip content={$i18n.t('Preview')}>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label={$i18n.t('Preview')}
												onclick={() => openPreview(inv)}
											>
												<Eye />
											</Button>
										</Tip>
										<DropdownMenu.Root>
											<DropdownMenu.Trigger>
												{#snippet child({ props })}
													<Button
														{...props}
														variant="ghost"
														size="icon-xs"
														aria-label={$i18n.t('More actions')}
													>
														<Ellipsis />
													</Button>
												{/snippet}
											</DropdownMenu.Trigger>
											<DropdownMenu.Content align="end" class="w-52">
												{#if inv.source === 'manual'}
													<DropdownMenu.Item onSelect={() => downloadInvoicePdf(inv.id)}>
														<Download />{$i18n.t('Download PDF')}
													</DropdownMenu.Item>
													<DropdownMenu.Separator />
												{/if}
												<DropdownMenu.Item
													variant="destructive"
													onSelect={() => {
														unassignInvoice(companyId, inv.id)
															.then(() => {
																toast.success($i18n.t('Removed'));
																reloadAll();
															})
															.catch((e) => toast.error(`${e}`));
													}}
												>
													<UserMinus />{$i18n.t('Remove')}
												</DropdownMenu.Item>
											</DropdownMenu.Content>
										</DropdownMenu.Root>
									</div>
								</Table.Cell>
							</Table.Row>
							{#if expandedId === inv.id}
								<Table.Row class="bg-muted/30 hover:bg-muted/30">
									<Table.Cell colspan={13} class="p-4 whitespace-normal">
										<div class="sticky left-0 grid max-w-[calc(100vw-4rem)] gap-4">
											<!-- Journal Entry Summary -->
											{#if inv.transaction_lines?.length > 0}
												<div class="grid gap-2">
													<div class="flex items-center gap-2 text-sm font-medium">
														{$i18n.t('Journal Entry')}
														{#if inv.transaction_id}
															<span class="font-mono text-[13px] text-muted-foreground"
																>#{inv.transaction_id}</span
															>
															<StatusBadge kind="entry" status={inv.transaction_status} />
														{/if}
													</div>
													<div class="max-w-3xl overflow-hidden rounded-md border bg-card">
														<Table.Root>
															<Table.Header class="bg-muted/50">
																<Table.Row class="hover:bg-transparent">
																	<Table.Head class="h-8">{$i18n.t('Account', { context: 'gnos3' })}</Table.Head>
																	<Table.Head class="h-8">{$i18n.t('Name', { context: 'gnos3' })}</Table.Head>
																	<Table.Head class="h-8 text-right">{$i18n.t('Debit')}</Table.Head>
																	<Table.Head class="h-8 text-right">{$i18n.t('Credit')}</Table.Head
																	>
																</Table.Row>
															</Table.Header>
															<Table.Body>
																{#each inv.transaction_lines as line}
																	<Table.Row class="hover:bg-transparent">
																		<Table.Cell class="py-1.5 font-mono text-[13px]"
																			>{line.account_code}</Table.Cell
																		>
																		<Table.Cell class="py-1.5 text-muted-foreground"
																			>{line.account_name}</Table.Cell
																		>
																		<Table.Cell class="py-1.5 text-right tabular-nums">
																			{line.debit > 0 ? fmt2(line.debit) : ''}
																		</Table.Cell>
																		<Table.Cell class="py-1.5 text-right tabular-nums">
																			{line.credit > 0 ? fmt2(line.credit) : ''}
																		</Table.Cell>
																	</Table.Row>
																{/each}
															</Table.Body>
														</Table.Root>
													</div>
												</div>
											{:else if inv.final_account_code && !inv.transaction_id}
												<Alert.Root variant="warning" class="max-w-3xl">
													<TriangleAlert />
													<Alert.Description>
														{$i18n.t(
															'Account assigned — create a journal entry in the Entries tab to complete the double-entry.'
														)}
													</Alert.Description>
												</Alert.Root>
											{/if}

											<!-- Invoice Fields (saved on blur) -->
											<div
												class="grid grid-cols-[repeat(auto-fill,minmax(min(11rem,100%),1fr))] gap-3"
											>
												{#each INVOICE_FIELDS as { field, label, type }}
													<div class="grid gap-1.5">
														<Label for="inv-{inv.id}-{field}" class="text-[13px]"
															>{$i18n.t(label)}</Label
														>
														<Input
															id="inv-{inv.id}-{field}"
															{type}
															step={type === 'number' ? '0.01' : undefined}
															maxlength={field === 'currency' ? 3 : undefined}
															value={inv[field] ?? ''}
															class={cn(
																'h-8 bg-card',
																type === 'number' && 'text-right tabular-nums',
																field === 'currency' && 'uppercase'
															)}
															onblur={(e: FocusEvent) =>
																saveField(
																	inv.id,
																	field,
																	(e.currentTarget as HTMLInputElement).value
																)}
														/>
													</div>
												{/each}
												<div class="grid gap-1.5">
													<Label for="inv-{inv.id}-employee" class="text-[13px]"
														>{$i18n.t('Employee')}</Label
													>
													<NativeSelect.Root
														id="inv-{inv.id}-employee"
														size="sm"
														class="w-full bg-card"
														value={inv.employee_id ?? ''}
														disabled={inv.expense_sheet_id != null}
														onchange={(e: Event) =>
															saveField(
																inv.id,
																'employee_id',
																(e.currentTarget as HTMLSelectElement).value
															)}
													>
														<NativeSelect.Option value=""
															>{$i18n.t('Unassigned')}</NativeSelect.Option
														>
														{#each employees as emp}
															<NativeSelect.Option value={emp.id}
																>{emp.full_name} ({emp.code})</NativeSelect.Option
															>
														{/each}
													</NativeSelect.Root>
												</div>
												<div class="grid gap-1.5">
													<Label for="inv-{inv.id}-category" class="text-[13px]"
														>{$i18n.t('Expense Category')}</Label
													>
													<NativeSelect.Root
														id="inv-{inv.id}-category"
														size="sm"
														class="w-full bg-card"
														value={inv.expense_category_id ?? ''}
														disabled={!inv.employee_id}
														onchange={(e: Event) =>
															saveField(
																inv.id,
																'expense_category_id',
																(e.currentTarget as HTMLSelectElement).value
															)}
													>
														<NativeSelect.Option value=""
															>{$i18n.t('Uncategorized')}</NativeSelect.Option
														>
														{#each expenseCategories.filter((c) => c.is_active) as cat}
															<NativeSelect.Option value={cat.id}>{cat.label}</NativeSelect.Option>
														{/each}
													</NativeSelect.Root>
													{#if inv.expense_category_source}
														<div class="text-xs text-muted-foreground">
															{$i18n.t('source')}: {inv.expense_category_source}
															{#if inv.expense_category_confidence}
																({Math.round(parseFloat(inv.expense_category_confidence) * 100)}%)
															{/if}
														</div>
													{/if}
												</div>
											</div>
										</div>
									</Table.Cell>
								</Table.Row>
							{/if}
						{/each}
					</Table.Body>
				</Table.Root>
			</div>
			<TablePagination
				bind:page={
					() => companyPage + 1,
					(v) => {
						companyPage = v - 1;
						loadCompanyInvoices();
					}
				}
				count={companyTotal}
				{perPage}
			/>
		{/if}

		<!-- Unassigned Panel -->
		{#if showUnassigned}
			<Card.Root>
				<Card.Header>
					<Card.Title class="flex items-center gap-2 text-base">
						{$i18n.t('Unassigned Invoices')}
						<Badge variant="count">{unassignedTotal}</Badge>
					</Card.Title>
					<Card.Action>
						<Tip content={$i18n.t('Hide Unassigned')}>
							<Button
								variant="ghost"
								size="icon-sm"
								aria-label={$i18n.t('Hide Unassigned')}
								onclick={() => {
									showUnassigned = false;
								}}
							>
								<X />
							</Button>
						</Tip>
					</Card.Action>
				</Card.Header>
				<Card.Content class="grid gap-4">
					<div class="flex flex-wrap items-center gap-2">
						{@render searchBox('unassigned-search', $i18n.t('Search unassigned...'), 'unassigned')}
						{@render filtersPopover('unassigned')}
						{#if selectedUnassignedIds.size > 0}
							<div
								class="ml-auto flex items-center gap-2 rounded-lg border bg-card py-1 pr-1 pl-3 text-sm shadow-md"
							>
								<span
									><span class="font-medium tabular-nums">{selectedUnassignedIds.size}</span>
									{$i18n.t('selected')}</span
								>
								<Button size="xs" onclick={handleBulkAssign}>{$i18n.t('Assign Selected')}</Button>
								<Tip content={$i18n.t('Clear')}>
									<Button
										variant="ghost"
										size="icon-xs"
										aria-label={$i18n.t('Clear')}
										onclick={() => {
											selectedUnassignedIds = new Set();
										}}
									>
										<X />
									</Button>
								</Tip>
							</div>
						{/if}
					</div>

					{#if unassignedInvoices.length === 0}
						<Empty.Root class="border border-dashed py-8">
							<Empty.Header>
								<Empty.Media variant="icon"><Inbox /></Empty.Media>
								<Empty.Title>{$i18n.t('No unassigned invoices')}</Empty.Title>
								<Empty.Description>
									{$i18n.t('Invoices extracted from K4mi that belong to no company appear here.')}
								</Empty.Description>
							</Empty.Header>
						</Empty.Root>
					{:else}
						<div class="overflow-hidden rounded-md border">
							<Table.Root>
								<Table.Header class="bg-muted/50">
									<Table.Row class="hover:bg-transparent">
										<Table.Head class="w-8">
											<Checkbox
												checked={allUnassignedSelected}
												onCheckedChange={toggleSelectAllUnassigned}
												aria-label={$i18n.t('Select all')}
											/>
										</Table.Head>
										{@render sortHead('invoice_number', 'Invoice #', 'unassigned')}
										{@render sortHead('vendor_name', 'Vendor', 'unassigned')}
										{@render sortHead('client_name', 'Client', 'unassigned')}
										{@render sortHead('invoice_date', 'Date', 'unassigned')}
										{@render sortHead('total_amount', 'Amount', 'unassigned', true)}
										<Table.Head class="w-28"
											><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head
										>
									</Table.Row>
								</Table.Header>
								<Table.Body>
									{#each unassignedInvoices as inv (inv.id)}
										<Table.Row
											data-state={selectedUnassignedIds.has(inv.id) ? 'selected' : undefined}
										>
											<Table.Cell>
												<Checkbox
													checked={selectedUnassignedIds.has(inv.id)}
													onCheckedChange={() => toggleUnassignedSelect(inv.id)}
													aria-label={$i18n.t('Select')}
												/>
											</Table.Cell>
											<Table.Cell class="font-mono text-[13px]">
												{#if inv.k4mi_document_id}<K4miDocLink
														docId={inv.k4mi_document_id}
														title={$i18n.t('Open in K4mi')}
														stopPropagation>{inv.invoice_number ?? '—'}</K4miDocLink
													>{:else}{inv.invoice_number ?? '—'}{/if}
											</Table.Cell>
											<Table.Cell class="max-w-[10rem] truncate" title={inv.vendor_name ?? ''}
												>{inv.vendor_name ?? '—'}</Table.Cell
											>
											<Table.Cell class="max-w-[10rem] truncate" title={inv.client_name ?? ''}
												>{inv.client_name ?? '—'}</Table.Cell
											>
											<Table.Cell class="tabular-nums">{inv.invoice_date ?? '—'}</Table.Cell>
											{@render amountCell(inv)}
											<Table.Cell class="text-right">
												<div class="inline-flex items-center gap-1">
													<Tip content={$i18n.t('Preview')}>
														<Button
															variant="ghost"
															size="icon-xs"
															aria-label={$i18n.t('Preview')}
															onclick={(e: MouseEvent) => {
																e.stopPropagation();
																openPreview(inv);
															}}
														>
															<Eye />
														</Button>
													</Tip>
													<Button
														variant="outline"
														size="xs"
														onclick={() => {
															assignInvoiceToCompany(companyId, inv.id)
																.then(() => {
																	toast.success($i18n.t('Assigned'));
																	reloadAll();
																})
																.catch((e) => toast.error(`${e}`));
														}}>{$i18n.t('Assign')}</Button
													>
												</div>
											</Table.Cell>
										</Table.Row>
									{/each}
								</Table.Body>
							</Table.Root>
						</div>
						<TablePagination
							bind:page={
								() => unassignedPage + 1,
								(v) => {
									unassignedPage = v - 1;
									loadUnassignedInvoices();
								}
							}
							count={unassignedTotal}
							{perPage}
						/>
					{/if}
				</Card.Content>
			</Card.Root>
		{/if}
	{/if}
</div>

{#if !loading}
	<DocumentPreviewModal
		bind:show={showPreview}
		invoice={previewInvoice}
		onUpdate={handlePreviewUpdate}
	/>
{/if}

<!-- Booking dialog — MUST be outside the {#if loading}{:else} block to avoid re-renders.
	 Every line shows where its account came from; the draft cannot be created with a gap. -->
<Dialog.Root
	open={pickerInvoiceId !== null}
	onOpenChange={(v) => {
		if (!v) closePicker();
	}}
>
	<Dialog.Content class="max-h-[90vh] gap-5 overflow-y-auto sm:max-w-3xl [&>*]:min-w-0">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Book invoice')}</Dialog.Title>
			<Dialog.Description class="truncate">
				<span class="font-mono text-[13px]">{pickerInvoice?.invoice_number ?? ''}</span>
				· {pickerInvoice?.vendor_name ?? ''} ·
				<span class="tabular-nums"
					>{pickerInvoice?.currency ?? ''} {pickerInvoice?.total_amount ?? ''}</span
				>
			</Dialog.Description>
		</Dialog.Header>

		<!-- Expense / revenue account -->
		<div class="flex flex-col gap-2">
			<div class="flex flex-wrap items-center justify-between gap-2">
				<span class="text-sm font-medium">{$i18n.t('Expense / Revenue Account')}</span>
				{#if pickerMainCode && bookingPlan}
					<ToggleGroup.Root
						type="single"
						variant="outline"
						size="sm"
						value={splitMode ? 'split' : 'single'}
						onValueChange={(v) => {
							if (!v || (v === 'split') === splitMode) return;
							splitMode = !splitMode;
							if (!splitMode) refreshPlan();
						}}
						aria-label={$i18n.t('Split')}
					>
						<ToggleGroup.Item value="single">{$i18n.t('Single account')}</ToggleGroup.Item>
						<ToggleGroup.Item value="split">{$i18n.t('Split across accounts')}</ToggleGroup.Item>
					</ToggleGroup.Root>
				{/if}
			</div>
			{#if pickerMainCode && editingLine !== 'main'}
				<div class="flex items-center gap-2 rounded-md border bg-muted/50 px-3 py-2">
					{#if pickerSuggested}
						<Sparkles class="size-4 shrink-0 text-info" aria-hidden="true" />
					{:else}
						<Check class="size-4 shrink-0 text-success" aria-hidden="true" />
					{/if}
					<span class="min-w-0 flex-1 truncate">
						<span class="font-mono text-[13px]">{pickerMainCode}</span>
						{accountMap[pickerMainCode] || ''}
					</span>
					<Button
						variant="link"
						size="xs"
						class="h-auto px-0"
						onclick={() => {
							editingLine = 'main';
						}}>{$i18n.t('Change')}</Button
					>
				</div>
				{#if pickerSuggested}
					<p class="text-sm text-muted-foreground">
						{$i18n.t(
							'Suggested by the accounting AI. Check it: nothing is booked until you create the draft entry.'
						)}
					</p>
				{/if}
			{:else}
				<div class="relative">
					<Search
						class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
					/>
					<Input
						type="search"
						class="pl-8"
						placeholder={$i18n.t('Search accounts...')}
						aria-label={$i18n.t('Search accounts...')}
						oninput={(e: Event) => {
							pickerMainSearch = (e.currentTarget as HTMLInputElement).value;
						}}
					/>
				</div>
				<div
					class="max-h-40 overflow-y-auto rounded-md border"
					role="listbox"
					aria-label={$i18n.t('Account', { context: 'gnos3' })}
				>
					{#each leafAccounts.filter((a) => !pickerMainSearch || a.code.includes(pickerMainSearch) || a.name
								.toLowerCase()
								.includes(pickerMainSearch.toLowerCase())) as acct}
						<button
							type="button"
							role="option"
							aria-selected={acct.code === pickerMainCode}
							class="flex w-full items-baseline gap-2 border-b px-3 py-1.5 text-left text-sm last:border-b-0 hover:bg-accent focus-visible:bg-accent focus-visible:outline-none"
							onclick={() => chooseMain(acct.code)}
						>
							<span class="font-mono text-[13px]">{acct.code}</span>
							<span class="truncate text-muted-foreground">{acct.name}</span>
						</button>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Split lines -->
		{#if splitMode && bookingPlan}
			<div class="grid gap-2 rounded-md border p-3">
				{#each splitLines as sl, i}
					<div class="flex flex-wrap items-center gap-2 sm:flex-nowrap">
						<NativeSelect.Root
							size="sm"
							class="min-w-0 flex-1"
							value={sl.account_id ?? ''}
							aria-label={$i18n.t('Account', { context: 'gnos3' })}
							onchange={(e: Event) => {
								const v = (e.currentTarget as HTMLSelectElement).value;
								sl.account_id = v ? Number(v) : null;
								splitLines = splitLines;
							}}
						>
							<NativeSelect.Option value="">{$i18n.t('— account —')}</NativeSelect.Option>
							{#each leafAccounts.filter( (a) => ['expense', 'revenue'].includes(a.account_type) ) as a}
								<NativeSelect.Option value={a.id}>{a.code} - {a.name}</NativeSelect.Option>
							{/each}
						</NativeSelect.Root>
						<Input
							type="number"
							step="0.01"
							class="h-8 w-28 text-right tabular-nums"
							aria-label={$i18n.t('Amount')}
							bind:value={sl.amount}
						/>
						<Input
							type="text"
							class="h-8 min-w-0 flex-1"
							placeholder={$i18n.t('Description')}
							aria-label={$i18n.t('Description')}
							bind:value={sl.description}
						/>
						<Tip content={$i18n.t('Remove')}>
							<Button
								variant="ghost"
								size="icon-xs"
								aria-label={$i18n.t('Remove')}
								onclick={() => {
									splitLines = splitLines.filter((_, j) => j !== i);
								}}
							>
								<X />
							</Button>
						</Tip>
					</div>
				{/each}
				<div class="flex items-center justify-between gap-2 text-sm">
					<Button
						variant="ghost"
						size="xs"
						onclick={() => {
							splitLines = [...splitLines, { account_id: null, amount: null, description: '' }];
						}}
					>
						<Plus />{$i18n.t('Add line')}
					</Button>
					{#if Math.abs(splitTotal - (bookingPlan.subtotal ?? 0)) < 0.005}
						<span class="text-muted-foreground tabular-nums">
							{$i18n.t('Lines')}: {splitTotal.toFixed(2)} / {$i18n.t('net')}: {(
								bookingPlan.subtotal ?? 0
							).toFixed(2)}
						</span>
					{:else}
						<span class="inline-flex items-center gap-1 text-destructive tabular-nums">
							<CircleAlert class="size-3.5" aria-hidden="true" />
							{$i18n.t('Lines')}: {splitTotal.toFixed(2)} / {$i18n.t('net')}: {(
								bookingPlan.subtotal ?? 0
							).toFixed(2)}
						</span>
					{/if}
				</div>
			</div>
		{/if}

		<!-- The entry (stays on screen while a selection is re-resolved) -->
		{#if bookingLoading && !bookingPlan}
			<div class="flex items-center gap-2 text-sm text-muted-foreground">
				<Spinner />
				{$i18n.t('Resolving accounts...')}
			</div>
		{:else if bookingPlan}
			<div
				class={cn(
					'overflow-hidden rounded-md border transition-opacity',
					bookingLoading && 'opacity-60'
				)}
				aria-busy={bookingLoading}
			>
				<Table.Root>
					<Table.Header class="bg-muted/50">
						<Table.Row class="hover:bg-transparent">
							<Table.Head>{$i18n.t('Line')}</Table.Head>
							<Table.Head>{$i18n.t('Account', { context: 'gnos3' })}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Debit')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Credit')}</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each bookingPlan.lines as line}
							{#if !(splitMode && line.role === 'main')}
								<Table.Row
									class={cn(
										'align-top hover:bg-transparent',
										line.source === 'missing' && 'bg-warning/5 hover:bg-warning/5'
									)}
								>
									<Table.Cell class="min-w-[9rem] whitespace-normal">
										<div class="font-medium">{$i18n.t(line.label)}</div>
										{#if line.description}
											<div class="text-xs text-muted-foreground">{line.description}</div>
										{/if}
									</Table.Cell>
									<Table.Cell class="min-w-[16rem] whitespace-normal">
										{#if line.role === 'main'}
											{#if line.account_code}
												<span
													><span class="font-mono text-[13px]">{line.account_code}</span>
													{line.account_name}</span
												>
											{/if}
											{#if pickerSuggested && line.source !== 'missing'}
												<div>
													<Badge variant="info">
														<Sparkles aria-hidden="true" />{$i18n.t('suggested')}
													</Badge>
												</div>
											{/if}
											{#if line.source === 'missing'}
												<!-- chosen above ("Change"); shown here so the gap is visible on its line -->
												<div class="grid justify-items-start gap-1">
													{#if !line.account_code}
														<span class="text-muted-foreground">{$i18n.t('No account')}</span>
													{/if}
													<Badge variant="danger">{$i18n.t(SOURCE_LABEL.missing)}</Badge>
													{#if line.note}
														<div class="flex items-start gap-1 text-xs text-muted-foreground">
															<TriangleAlert
																class="mt-px size-3.5 shrink-0 text-warning"
																aria-hidden="true"
															/>
															<span>{$i18n.t(line.note)}</span>
														</div>
													{/if}
												</div>
											{/if}
										{:else if editingLine === line.role}
											<div class="grid gap-1.5">
												<Input
													type="search"
													class="h-8"
													placeholder={$i18n.t('Search accounts...')}
													aria-label={$i18n.t('Search accounts...')}
													oninput={(e: Event) => {
														lineSearch = {
															...lineSearch,
															[line.role]: (e.currentTarget as HTMLInputElement).value
														};
													}}
												/>
												<div class="max-h-36 overflow-y-auto rounded-md border bg-card">
													{#each candidatesFor(line, lineSearch[line.role] ?? '', leafAccounts) as a}
														<button
															type="button"
															class="flex w-full items-baseline gap-2 border-b px-2 py-1 text-left text-sm last:border-b-0 hover:bg-accent focus-visible:bg-accent focus-visible:outline-none"
															onclick={() => chooseLineAccount(line.role, a.id)}
														>
															<span class="font-mono text-[13px]">{a.code}</span>
															<span class="min-w-0 flex-1 truncate text-muted-foreground"
																>{a.name}</span
															>
															{#if (line.candidates ?? []).some((c: any) => c.id === a.id)}
																<Badge variant="outline">{$i18n.t('suggested')}</Badge>
															{/if}
														</button>
													{/each}
												</div>
											</div>
										{:else}
											<div class="grid justify-items-start gap-1">
												{#if line.account_id}
													<span
														><span class="font-mono text-[13px]">{line.account_code}</span>
														{line.account_name}</span
													>
												{:else}
													<span class="text-muted-foreground">{$i18n.t('No account')}</span>
												{/if}
												<span class="inline-flex flex-wrap items-center gap-1.5">
													<Badge variant={sourceVariant(line.source)}>
														{$i18n.t(SOURCE_LABEL[line.source] ?? line.source)}
													</Badge>
													{#if line.account_id}
														<Button
															variant="link"
															size="xs"
															class="h-auto px-0"
															onclick={() => {
																editingLine = line.role;
															}}>{$i18n.t('Change')}</Button
														>
													{:else}
														<Button
															size="xs"
															onclick={() => {
																editingLine = line.role;
															}}>{$i18n.t('Choose')}</Button
														>
													{/if}
												</span>
												{#if line.note}
													<div class="flex items-start gap-1 text-xs text-muted-foreground">
														<TriangleAlert
															class="mt-px size-3.5 shrink-0 text-warning"
															aria-hidden="true"
														/>
														<span>{$i18n.t(line.note)}</span>
													</div>
												{/if}
											</div>
										{/if}
									</Table.Cell>
									<Table.Cell class="text-right tabular-nums">{fmt2(line.debit)}</Table.Cell>
									<Table.Cell class="text-right tabular-nums">{fmt2(line.credit)}</Table.Cell>
								</Table.Row>
							{/if}
						{/each}
					</Table.Body>
				</Table.Root>
			</div>
			{#if bookingPlan.exchange_rate && bookingPlan.exchange_rate.currency !== bookingPlan.exchange_rate.base}
				<div
					class={cn(
						'flex items-center gap-1.5 text-sm',
						bookingPlan.exchange_rate.rate ? 'text-muted-foreground' : 'text-destructive'
					)}
				>
					{#if bookingPlan.exchange_rate.rate}
						<Info class="size-3.5 shrink-0" aria-hidden="true" />
					{:else}
						<CircleAlert class="size-3.5 shrink-0" aria-hidden="true" />
					{/if}
					<span class="tabular-nums">
						{bookingPlan.exchange_rate.currency} → {bookingPlan.exchange_rate.base}:
						{bookingPlan.exchange_rate.rate
							? `${bookingPlan.exchange_rate.rate} (${$i18n.t('rate on file')}, ${bookingPlan.exchange_rate.date})`
							: $i18n.t('no rate on file for {{date}} — add it in Exchange Rates', {
									date: bookingPlan.exchange_rate.date
								})}
					</span>
				</div>
			{/if}
			{#if (bookingPlan.warnings ?? []).length > 0}
				<Alert.Root variant="warning">
					<TriangleAlert />
					<Alert.Description class="grid gap-1">
						{#each bookingPlan.warnings ?? [] as w}
							<p>{$i18n.t(w)}</p>
						{/each}
					</Alert.Description>
				</Alert.Root>
			{/if}
			{#if !bookingPlan.complete}
				<Alert.Root variant="warning">
					<TriangleAlert />
					<Alert.Description class="text-foreground">
						{$i18n.t(
							"Every line needs an account before the entry can be created — nothing is guessed. Rules (Settings → Rules), Tax → Accounts and the company's default AP/AR account fill these in automatically next time."
						)}
					</Alert.Description>
				</Alert.Root>
			{/if}
		{:else if pickerMainCode === ''}
			<p class="text-sm text-muted-foreground">
				{$i18n.t('Pick the expense / revenue account to see the full entry.')}
			</p>
		{/if}

		<Dialog.Footer>
			<Button variant="outline" onclick={closePicker}>{$i18n.t('Cancel')}</Button>
			<Button disabled={!planReady} onclick={handleConfirmPicker}
				>{$i18n.t('Create Draft Entry')}</Button
			>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Invoice Create Modal -->
<InvoiceCreateModal
	bind:show={showCreateInvoice}
	{companyId}
	companyName={$companyNameCtx || ''}
	on:save={() => {
		loadCompanyInvoices();
	}}
/>
