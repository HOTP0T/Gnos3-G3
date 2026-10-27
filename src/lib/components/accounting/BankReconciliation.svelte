<script lang="ts">
	import { onMount, onDestroy, getContext, tick, type ComponentProps } from 'svelte';
	import type { Writable } from 'svelte/store';
	import { convertAmount } from '$lib/utils/currency';
	import { toast } from 'svelte-sonner';
	import {
		getBankAccounts,
		createBankAccount,
		updateBankAccount,
		getBankStatements,
		importBankStatement,
		autoMatchBankStatements,
		matchBankStatement,
		unmatchBankStatement,
		excludeBankStatement,
		includeBankStatement,
		getAccounts,
		editBankStatementLine,
		getTransactions,
		downloadBankStatementTemplate,
		createMatchGroup,
		getStatementImports,
		undoStatementImport
	} from '$lib/apis/accounting';
	import { uiLocale } from '$lib/utils/uiLocale';
	import PaymentFormModal from '$lib/components/accounting/PaymentFormModal.svelte';
	import TransactionFormModal from '$lib/components/accounting/TransactionFormModal.svelte';

	import Sparkles from '@lucide/svelte/icons/sparkles';
	import Upload from '@lucide/svelte/icons/upload';
	import Download from '@lucide/svelte/icons/download';
	import Plus from '@lucide/svelte/icons/plus';
	import Landmark from '@lucide/svelte/icons/landmark';
	import Search from '@lucide/svelte/icons/search';
	import Pencil from '@lucide/svelte/icons/pencil';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import Ellipsis from '@lucide/svelte/icons/ellipsis';
	import X from '@lucide/svelte/icons/x';
	import ArrowLeftRight from '@lucide/svelte/icons/arrow-left-right';
	import NotebookPen from '@lucide/svelte/icons/notebook-pen';
	import Ban from '@lucide/svelte/icons/ban';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import FileSpreadsheet from '@lucide/svelte/icons/file-spreadsheet';
	import ListFilter from '@lucide/svelte/icons/list-filter';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge, badgeVariants } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as ToggleGroup from '$lib/components/ui/toggle-group/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';
	import { cn } from '$lib/utils/shadcn.js';

	const i18n: any = getContext('i18n');
	export let companyId: number;

	let bankAccounts: any[] = [];
	let accounts: any[] = [];
	let selectedBankId: number | null = null;
	let statements: any[] = [];
	let loading = true;
	let statementsLoading = false;
	let loadError = '';
	let statementsError = '';

	// New bank account form
	let showNewBank = false;
	let newBankName = '';
	let newBankAccountId: number | null = null;
	let newBankCurrency = '';
	let newBankInboundId: number | null = null;
	let newBankOutboundId: number | null = null;

	// Edit the selected bank account's GL mapping
	let showEditBank = false;
	let editBankAccountId: number | null = null;
	let editBankInboundId: number | null = null;
	let editBankOutboundId: number | null = null;

	// A line the accountant considers done. Used to tell "nothing posted yet"
	// apart from "posted nowhere", which look identical without it.
	const isLineMatched = (line: any) =>
		['manual_matched', 'auto_matched'].includes(line?.match_status);

	const toggleEditBank = () => {
		showEditBank = !showEditBank;
		if (!showEditBank) return;
		const ba = bankAccounts.find((b) => b.id === selectedBankId);
		editBankAccountId = ba?.account_id ?? null;
		editBankInboundId = ba?.default_inbound_account_id ?? null;
		editBankOutboundId = ba?.default_outbound_account_id ?? null;
	};

	const handleSaveBankAccounts = async () => {
		if (!selectedBankId) return;
		try {
			await updateBankAccount(selectedBankId, {
				account_id: editBankAccountId,
				default_inbound_account_id: editBankInboundId,
				default_outbound_account_id: editBankOutboundId
			});
			bankAccounts = await getBankAccounts(companyId);
			showEditBank = false;
			toast.success($i18n.t('Bank account updated'));
		} catch (err) {
			toast.error(`${err}`);
		}
	};

	// Only detail accounts may be posted to — an account with sub-accounts is a
	// roll-up header, and an entry landing on it never shows in the sub-ledger.
	$: controlAccountIds = new Set(accounts.filter((a) => a.parent_id).map((a) => a.parent_id));
	$: postableAccounts = accounts.filter((a) => !controlAccountIds.has(a.id));

	// Filter
	let statusFilter = '';
	let searchQuery = '';
	let dateFrom = '';
	let dateTo = '';
	let directionFilter: '' | 'credit' | 'debit' = '';

	// Import modal
	let showImportModal = false;
	let importCurrency = '';
	let importFileInput: HTMLInputElement | null = null;
	let importFile: File | null = null;
	let importing = false;
	// Recent imports of the selected account, each undoable until a line is in use.
	let recentImports: any[] = [];
	let undoTarget: { batch_id: string; lines: number } | null = null;
	let showUndoConfirm = false;

	// Inline reference editing
	let editingRefLineId: number | null = null;
	let editRefValue = '';

	// Auto-reconcile loading
	let autoReconciling = false;

	// Expandable matched details row
	let expandedLineId: number | null = null;

	// Match popover — unified entry list with optional multi-select
	let matchingLineId: number | null = null;
	let matchSearchQuery = '';
	let matchCandidates: any[] = [];
	let matchLoading = false;
	let matchMultiSelect = false; // toggle for multi-select mode
	let matchSelectedIds: Set<number> = new Set(); // selected transaction IDs for multi-match
	let matchCreating = false;

	// Multi-BSL selection for N:1 matching
	let selectedBslIds: Set<number> = new Set();
	let showMultiMatchModal = false;
	let multiMatchInvoices: any[] = [];
	let multiMatchAllocations: Map<number, number> = new Map();
	let multiMatchLoading = false;
	let multiMatchCreating = false;

	// Create entry modal
	let showCreateEntryModal = false;
	let createEntryBslId: number | null = null;
	let createEntryPrefill: ComponentProps<typeof TransactionFormModal>['prefill'] = null;

	// Payment modal state
	let showPaymentModal = false;
	let paymentPrefill: any = null;
	let payingLineId: number | null = null;

	const handlePay = (line: any) => {
		const amount = Math.abs(parseFloat(line.amount) || 0);
		const isInbound = parseFloat(line.amount) > 0;
		payingLineId = line.id;
		paymentPrefill = {
			payment_date: line.transaction_date || new Date().toISOString().slice(0, 10),
			amount,
			currency: selectedBankCurrency || 'EUR',
			direction: isInbound ? 'inbound' : 'outbound',
			method: 'bank_transfer',
			payer: isInbound ? line.description || '' : '',
			payee: isInbound ? '' : line.description || '',
			reference: line.reference || line.description || '',
			invoice_id: line.matched_txn_invoice_id || null,
			_bank_statement_line_id: line.id
		};
		showPaymentModal = true;
	};

	const handlePaymentSaved = async () => {
		toast.success($i18n.t('Payment recorded'));
		showPaymentModal = false;
		payingLineId = null;
		await loadStatements();
	};

	const CURRENCIES = [
		'EUR',
		'USD',
		'GBP',
		'CNY',
		'JPY',
		'CHF',
		'CAD',
		'AUD',
		'HKD',
		'SGD',
		'SEK',
		'NOK',
		'DKK',
		'NZD',
		'KRW',
		'INR',
		'BRL',
		'ZAR',
		'MXN',
		'PLN',
		'CZK',
		'TRY',
		'THB',
		'TWD',
		'MAD',
		'XOF'
	];

	// Display currency + rates come from the company-wide context (the selector at
	// the top of every company page), so the bank tab converts consistently with the
	// rest of the accounting UI rather than having its own control.
	const displayCurrency = getContext<Writable<string>>('displayCurrency');
	const exchangeRates = getContext<Writable<any[]>>('exchangeRates');

	// Bank statement amounts are in the selected bank account's currency; convert
	// that into the chosen display currency (nearest-date rate from the shared set).
	// `to` and `rates` are passed in (not read from the store inside) so that the
	// {@const} call sites genuinely depend on them and recompute when the display
	// currency changes between two non-native currencies.
	function cvt(
		amount: any,
		date: string | undefined,
		to: string,
		rates: any[]
	): { display: string; hasRate: boolean } {
		const num = typeof amount === 'string' ? parseFloat(amount) : (amount ?? 0);
		const native = selectedBankCurrency;
		if (!num || !to || !native || to === native) {
			return { display: '', hasRate: true };
		}
		const result = convertAmount(num, native, to, rates ?? [], date);
		return {
			display: result.hasRate
				? result.converted.toLocaleString(undefined, {
						minimumFractionDigits: 2,
						maximumFractionDigits: 2
					})
				: '',
			hasRate: result.hasRate
		};
	}

	const load = async () => {
		loading = true;
		try {
			const [baData, acctData] = await Promise.all([
				getBankAccounts(companyId),
				getAccounts({ company_id: companyId })
			]);
			bankAccounts = baData ?? [];
			const accts = acctData?.accounts ?? acctData ?? [];
			accounts = Array.isArray(accts) ? accts : [];
			if (bankAccounts.length > 0 && !selectedBankId) {
				selectedBankId = bankAccounts[0].id;
				await loadStatements();
			}
			loadError = '';
		} catch (err: any) {
			loadError = err?.detail ?? `${err}`;
			toast.error(err?.detail ?? `${err}`);
		}
		loading = false;
	};

	const loadStatements = async () => {
		if (!selectedBankId) return;
		statementsLoading = true;
		try {
			const params: Record<string, any> = {};
			if (statusFilter) params.status = statusFilter;
			statements = (await getBankStatements(selectedBankId, params)) ?? [];
			statementsError = '';
		} catch (err: any) {
			statementsError = err?.detail ?? `${err}`;
			toast.error(err?.detail ?? `${err}`);
		}
		statementsLoading = false;
	};

	onMount(async () => {
		await load();
	});

	const handleCreateBank = async () => {
		if (!newBankName) return;
		try {
			await createBankAccount(companyId, {
				name: newBankName,
				account_id: newBankAccountId,
				currency: (newBankCurrency || '').toUpperCase() || undefined,
				default_inbound_account_id: newBankInboundId,
				default_outbound_account_id: newBankOutboundId
			});
			toast.success($i18n.t('Bank account created'));
			showNewBank = false;
			newBankName = '';
			newBankCurrency = '';
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	// Import modal handlers
	const openImportModal = () => {
		importCurrency = selectedBankCurrency || 'EUR';
		importFile = null;
		if (importFileInput) importFileInput.value = '';
		showImportModal = true;
		loadImports();
	};

	const loadImports = async () => {
		recentImports = selectedBankId ? await getStatementImports(selectedBankId).catch(() => []) : [];
	};

	const askUndoImport = (batch: { batch_id: string; lines: number }) => {
		undoTarget = batch;
		showUndoConfirm = true;
	};

	const doUndoImport = async () => {
		if (!selectedBankId || !undoTarget) return;
		try {
			const res = await undoStatementImport(selectedBankId, undoTarget.batch_id);
			toast.success($i18n.t('Import undone: {{count}} lines removed', { count: res.deleted }));
			await loadStatements();
			await loadImports();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		undoTarget = null;
	};

	const importDay = (iso: string) => {
		const [y, m, d] = String(iso).slice(0, 10).split('-').map(Number);
		return new Date(y, m - 1, d).toLocaleDateString(uiLocale(), { day: 'numeric', month: 'short', year: 'numeric' });
	};

	const handleImport = async () => {
		if (!selectedBankId || !importFile) {
			toast.error($i18n.t('Please select a CSV file'));
			return;
		}
		importing = true;
		try {
			const currency = importCurrency || selectedBankCurrency || undefined;
			const res = await importBankStatement(selectedBankId, importFile, currency);
			toast.success($i18n.t('Imported {{count}} lines', { count: res.imported ?? 0 }), {
				action: res.imported
					? {
							label: $i18n.t('Undo'),
							onClick: () => askUndoImport({ batch_id: res.batch_id, lines: res.imported })
						}
					: undefined
			});
			showImportModal = false;
			await loadStatements();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		importing = false;
	};

	// Auto-reconcile
	const handleAutoReconcile = async () => {
		if (!selectedBankId) return;
		autoReconciling = true;
		try {
			const res = await autoMatchBankStatements(selectedBankId);
			toast.success(
				$i18n.t('Matched {{matched}} lines, {{remaining}} remaining', {
					matched: res.matched ?? 0,
					remaining: res.remaining ?? 0
				})
			);
			await loadStatements();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		autoReconciling = false;
	};

	// A line with a recorded payment asks first (ConfirmDialog instead of window.confirm).
	let showUnmatchConfirm = false;
	let pendingUnmatchId: number | null = null;

	const doUnmatch = async (lineId: number) => {
		try {
			await unmatchBankStatement(lineId);
			await loadStatements();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const handleUnmatch = async (lineId: number) => {
		const line = statements.find((s: any) => s.id === lineId);
		if (line?.payment_id) {
			pendingUnmatchId = lineId;
			showUnmatchConfirm = true;
			return;
		}
		await doUnmatch(lineId);
	};

	const handleExclude = async (lineId: number) => {
		try {
			await excludeBankStatement(lineId);
			await loadStatements();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const handleInclude = async (lineId: number) => {
		try {
			await includeBankStatement(lineId);
			await loadStatements();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	// Reference inline editing
	const startEditRef = (line: any) => {
		editingRefLineId = line.id;
		editRefValue = line.reference ?? '';
	};

	const saveEditRef = async () => {
		if (editingRefLineId === null) return;
		const original = statements.find((s) => s.id === editingRefLineId);
		if (!original) return;
		if (editRefValue !== (original.reference ?? '')) {
			try {
				await editBankStatementLine(editingRefLineId, { reference: editRefValue });
				toast.success($i18n.t('Reference updated'));
				await loadStatements();
			} catch (err: any) {
				toast.error(err?.detail ?? `${err}`);
			}
		}
		editingRefLineId = null;
	};

	const handleRefKeydown = (e: KeyboardEvent) => {
		if (e.key === 'Escape') editingRefLineId = null;
		if (e.key === 'Enter') saveEditRef();
	};

	// Manual match popover — unified entry list with optional multi-select
	const openMatchPopover = async (line: any) => {
		matchingLineId = line.id;
		matchSearchQuery = '';
		matchMultiSelect = false;
		matchSelectedIds = new Set();
		matchLoading = true;
		matchCandidates = [];
		try {
			const res = await getTransactions({ company_id: companyId, status: 'posted', limit: 100 });
			const all = res?.transactions ?? res ?? [];
			const txns = Array.isArray(all) ? all : [];

			// Sum allocated amounts per transaction across all BSLs' match groups
			const txnAllocated = new Map<number, number>();
			for (const s of statements) {
				if (s.match_groups) {
					for (const mg of s.match_groups) {
						if (mg.transactions) {
							for (const t of mg.transactions) {
								txnAllocated.set(
									t.transaction_id,
									(txnAllocated.get(t.transaction_id) || 0) + parseFloat(t.allocated_amount || 0)
								);
							}
						}
					}
				}
			}

			const bankLine = statements.find((s) => s.id === matchingLineId);
			const bankAmount = bankLine ? Math.abs(parseFloat(bankLine.amount)) : 0;
			const bankAmountRaw = bankLine ? parseFloat(bankLine.amount) : 0;
			const isCredit = bankAmountRaw > 0;
			const bankDesc = (bankLine?.description ?? '').toLowerCase();
			const bankRef = (bankLine?.reference ?? '').toLowerCase();

			matchCandidates = txns
				.map((t: any) => {
					const totalDebit = (t.lines ?? []).reduce(
						(sum: number, l: any) => sum + parseFloat(l.debit || 0),
						0
					);
					const allocated = txnAllocated.get(t.id) || 0;
					const remaining = totalDebit - allocated;
					const amountMatch = bankAmount > 0 && Math.abs(remaining - bankAmount) < 0.02;
					const txnType = (t.transaction_type ?? '').toLowerCase();
					const directionMatch = isCredit
						? ['invoice', 'sale', 'payment_in', 'others'].includes(txnType)
						: ['bill', 'purchase', 'payment_out', 'others'].includes(txnType);
					const txnDesc = (t.description ?? '').toLowerCase();
					const txnRef = (t.reference ?? '').toLowerCase();
					let nameScore = 0;
					const bankWords = (bankDesc + ' ' + bankRef)
						.split(/\s+/)
						.filter((w: string) => w.length > 2);
					const txnWords = (txnDesc + ' ' + txnRef)
						.split(/\s+/)
						.filter((w: string) => w.length > 2);
					if (bankWords.length > 0 && txnWords.length > 0) {
						const matches = bankWords.filter((bw: string) =>
							txnWords.some((tw: string) => tw.includes(bw) || bw.includes(tw))
						);
						nameScore = matches.length / Math.max(bankWords.length, 1);
					}
					const bankDate = bankLine?.transaction_date ?? '';
					const txnDate = t.transaction_date ?? '';
					const dateDiff =
						bankDate && txnDate
							? Math.abs(new Date(bankDate).getTime() - new Date(txnDate).getTime()) / 86400000
							: 999;
					let score = 0;
					if (amountMatch) score += 0.4;
					if (directionMatch) score += 0.2;
					score += nameScore * 0.25;
					score += Math.max(0, 1 - dateDiff / 60) * 0.15;
					return {
						...t,
						_totalAmount: totalDebit,
						_allocated: allocated,
						_remaining: remaining,
						_amountMatch: amountMatch,
						_directionMatch: directionMatch,
						_nameScore: nameScore,
						_dateDiff: dateDiff,
						_score: score
					};
				})
				.filter((t: any) => t._remaining > 0.01) // hide fully-covered entries
				.sort((a: any, b: any) => b._score - a._score);
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
			matchCandidates = [];
		}
		matchLoading = false;
	};

	// Toggle entry selection in multi-select mode
	const toggleMatchEntry = (txnId: number) => {
		if (matchSelectedIds.has(txnId)) {
			matchSelectedIds.delete(txnId);
		} else {
			matchSelectedIds.add(txnId);
		}
		matchSelectedIds = new Set(matchSelectedIds);
	};

	// Single-select: match one entry to the BSL
	const handleMatchSelect = async (transactionId: number) => {
		if (matchingLineId === null) return;
		try {
			await matchBankStatement(matchingLineId, transactionId);
			toast.success($i18n.t('Statement line matched'));
			matchingLineId = null;
			await loadStatements();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	// Multi-select: match multiple entries to the BSL
	const handleMatchMultiple = async () => {
		if (matchingLineId === null || matchSelectedIds.size === 0) return;
		matchCreating = true;
		try {
			const selectedTxns = matchCandidates.filter((t: any) => matchSelectedIds.has(t.id));
			const txnAllocations = selectedTxns.map((t: any) => ({
				transaction_id: t.id,
				allocated_amount: t._totalAmount
			}));
			const bslAmount = txnAllocations.reduce((s: number, a: any) => s + a.allocated_amount, 0);
			await createMatchGroup(companyId, {
				bsl_allocations: [{ bank_statement_line_id: matchingLineId, allocated_amount: bslAmount }],
				transaction_allocations: txnAllocations
			});

			toast.success($i18n.t(`Matched ${matchSelectedIds.size} entries`));
			matchingLineId = null;
			matchSelectedIds = new Set();
			matchMultiSelect = false;
			await loadStatements();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		matchCreating = false;
	};

	$: matchSelectedTotal = Array.from(matchSelectedIds).reduce((sum, id) => {
		const txn = matchCandidates.find((t: any) => t.id === id);
		return sum + (txn?._totalAmount ?? 0);
	}, 0);

	$: filteredMatchCandidates = matchCandidates
		.filter((item: any) => {
			if (!matchSearchQuery) return true;
			const q = matchSearchQuery.toLowerCase();
			return (
				(item.reference ?? '').toLowerCase().includes(q) ||
				(item.description ?? '').toLowerCase().includes(q) ||
				String(item._totalAmount ?? item.total ?? '').includes(q) ||
				String(item.id).includes(q)
			);
		})
		.slice(0, 20);

	// Multi-BSL selection helpers
	const toggleBslSelection = (lineId: number) => {
		if (selectedBslIds.has(lineId)) {
			selectedBslIds.delete(lineId);
		} else {
			selectedBslIds.add(lineId);
		}
		selectedBslIds = new Set(selectedBslIds);
	};

	$: selectedBslTotal = Array.from(selectedBslIds).reduce((sum, id) => {
		const line = statements.find((s: any) => s.id === id);
		return (
			sum + (line ? Math.abs(parseFloat(line.amount)) - parseFloat(line.allocated_total || 0) : 0)
		);
	}, 0);

	const openMultiMatchModal = async () => {
		if (selectedBslIds.size < 1) return;
		showMultiMatchModal = true;
		multiMatchAllocations = new Map();
		multiMatchLoading = true;
		try {
			const res = await getTransactions({ company_id: companyId, status: 'posted', limit: 200 });
			const all = res?.transactions ?? res ?? [];

			// Sum allocated amounts per transaction across all match groups
			const txnAllocated = new Map<number, number>();
			for (const s of statements) {
				if (s.match_groups) {
					for (const mg of s.match_groups) {
						if (mg.transactions) {
							for (const t of mg.transactions) {
								txnAllocated.set(
									t.transaction_id,
									(txnAllocated.get(t.transaction_id) || 0) + parseFloat(t.allocated_amount || 0)
								);
							}
						}
					}
				}
			}

			multiMatchInvoices = (Array.isArray(all) ? all : [])
				.map((t: any) => {
					const totalDebit = (t.lines ?? []).reduce(
						(sum: number, l: any) => sum + parseFloat(l.debit || 0),
						0
					);
					const allocated = txnAllocated.get(t.id) || 0;
					const remaining = totalDebit - allocated;
					return { ...t, _totalAmount: totalDebit, _remaining: remaining };
				})
				.filter((t: any) => t._remaining > 0.01);
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
			multiMatchInvoices = [];
		}
		multiMatchLoading = false;
	};

	$: multiMatchAllocTotal = Array.from(multiMatchAllocations.values()).reduce((s, v) => s + v, 0);
	$: multiMatchRemaining = selectedBslTotal - multiMatchAllocTotal;

	const toggleMultiMatchEntry = (txn: any) => {
		if (multiMatchAllocations.has(txn.id)) {
			multiMatchAllocations.delete(txn.id);
		} else {
			const remaining = selectedBslTotal - multiMatchAllocTotal;
			multiMatchAllocations.set(txn.id, Math.min(txn._totalAmount, remaining));
		}
		multiMatchAllocations = new Map(multiMatchAllocations);
	};

	const handleMultiMatchCreate = async () => {
		if (selectedBslIds.size === 0 || multiMatchAllocations.size === 0) return;
		multiMatchCreating = true;
		try {
			const bslAllocs = Array.from(selectedBslIds).map((id) => {
				const line = statements.find((s: any) => s.id === id);
				const unalloc = line
					? Math.abs(parseFloat(line.amount)) - parseFloat(line.allocated_total || 0)
					: 0;
				return { bank_statement_line_id: id, allocated_amount: unalloc };
			});
			const txnAllocs = Array.from(multiMatchAllocations.entries()).map(([txn_id, amt]) => ({
				transaction_id: txn_id,
				allocated_amount: amt
			}));
			await createMatchGroup(companyId, {
				bsl_allocations: bslAllocs,
				transaction_allocations: txnAllocs
			});
			toast.success($i18n.t('Match group created'));
			showMultiMatchModal = false;
			selectedBslIds = new Set();
			multiMatchAllocations = new Map();
			await loadStatements();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		multiMatchCreating = false;
	};

	// Close match popover on outside click
	const handleDocumentClick = (e: MouseEvent) => {
		if (matchingLineId !== null) {
			const target = e.target as HTMLElement;
			if (!target.closest('.match-popover') && !target.closest('.match-trigger')) {
				matchingLineId = null;
			}
		}
	};

	onMount(() => {
		document.addEventListener('click', handleDocumentClick);
	});
	onDestroy(() => {
		document.removeEventListener('click', handleDocumentClick);
	});

	// Create entry from unmatched line — opens the full TransactionFormModal
	// The entry opens on the line's date, text and currency, with the bank's GL
	// account on the side the money moved (in → debit the bank, out → credit it).
	// The counterpart carries the balancing amount but no account: a person picks it.
	const openCreateEntry = (line: any) => {
		const signed = parseFloat(line.amount) || 0;
		const allocated = parseFloat(line.allocated_total || 0) || 0;
		const open = Math.round((Math.abs(signed) - allocated) * 100) / 100;
		const amount = open > 0.005 ? open : Math.abs(signed);
		const inbound = signed > 0;
		const text = line.description || line.reference || '';
		const bankGlId = bankAccounts.find((b) => b.id === selectedBankId)?.account_id ?? null;
		createEntryPrefill = {
			transaction_date: line.transaction_date ? String(line.transaction_date).slice(0, 10) : '',
			currency: selectedBankCurrency || undefined,
			reference: line.reference || '',
			description: text,
			lines: [
				{
					account_id: bankGlId,
					debit: inbound ? amount : null,
					credit: inbound ? null : amount,
					description: text
				},
				{
					account_id: null,
					debit: inbound ? null : amount,
					credit: inbound ? amount : null,
					description: ''
				}
			]
		};
		createEntryBslId = line.id;
		showCreateEntryModal = true;
	};

	const handleCreateEntrySave = async () => {
		showCreateEntryModal = false;
		createEntryBslId = null;
		createEntryPrefill = null;
		await loadStatements();
	};

	const fmt = (v: any): string => {
		const n = typeof v === 'string' ? parseFloat(v) : (v ?? 0);
		if (n === 0) return '—';
		return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	};

	const fmtSigned = (v: any): string => {
		const n = typeof v === 'string' ? parseFloat(v) : (v ?? 0);
		return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	};

	// Segmented filters: a single-choice toggle group can be switched off by clicking the
	// pressed item; put the current choice back instead of leaving nothing pressed.
	let statusSeg = 'all';
	let directionSeg = 'all';
	const onStatusSeg = (v: string) => {
		if (!v) {
			tick().then(() => (statusSeg = statusFilter || 'all'));
			return;
		}
		statusFilter = v === 'all' ? '' : v;
		loadStatements();
	};
	const onDirectionSeg = (v: string) => {
		if (!v) {
			tick().then(() => (directionSeg = directionFilter || 'all'));
			return;
		}
		directionFilter = (v === 'all' ? '' : v) as typeof directionFilter;
	};
	$: directionSeg = directionFilter || 'all';

	// Account pickers keep number | null (the "—" option is the empty string)
	const idFrom = (e: Event): number | null => {
		const v = (e.currentTarget as HTMLSelectElement).value;
		return v ? Number(v) : null;
	};

	$: matchedCount = statements.filter((s) =>
		['auto_matched', 'manual_matched'].includes(s.match_status)
	).length;
	$: partialCount = statements.filter((s) => s.match_status === 'partial_matched').length;
	$: unmatchedCount = statements.filter((s) => s.match_status === 'unmatched').length;
	$: selectedBankCurrency = bankAccounts.find((ba) => ba.id === selectedBankId)?.currency || '';
	$: showConverted = $displayCurrency && $displayCurrency !== selectedBankCurrency;

	// Summary card computations
	$: bankBalance =
		statements.length > 0 ? statements.reduce((sum, s) => sum + (parseFloat(s.amount) || 0), 0) : 0;
	$: glBalance = (() => {
		// Approximate: sum of matched transaction amounts
		// In a real scenario, this would come from the API, but we approximate from statement data
		return statements
			.filter((s) => s.match_status !== 'unmatched')
			.reduce((sum, s) => sum + (parseFloat(s.amount) || 0), 0);
	})();
	$: reconDifference = bankBalance - glBalance;
	$: isReconciled = Math.abs(reconDifference) < 0.01;

	// Client-side search & filter on loaded statements
	$: filteredStatements = statements.filter((s: any) => {
		// Text search
		if (searchQuery) {
			const q = searchQuery.toLowerCase();
			const match =
				(s.description ?? '').toLowerCase().includes(q) ||
				(s.reference ?? '').toLowerCase().includes(q) ||
				String(s.amount ?? '').includes(q) ||
				(s.transaction_date ?? '').includes(q);
			if (!match) return false;
		}
		// Date range
		if (dateFrom && s.transaction_date < dateFrom) return false;
		if (dateTo && s.transaction_date > dateTo) return false;
		// Direction
		if (directionFilter === 'credit' && parseFloat(s.amount) <= 0) return false;
		if (directionFilter === 'debit' && parseFloat(s.amount) >= 0) return false;
		return true;
	});

	const handleGlobalKeydown = (e: KeyboardEvent) => {
		if (e.key === 'Escape') {
			if (showMultiMatchModal) showMultiMatchModal = false;
			else if (showImportModal) showImportModal = false;
			else if (showCreateEntryModal) showCreateEntryModal = false;
		}
	};

	onMount(() => {
		window.addEventListener('keydown', handleGlobalKeydown);
	});
	onDestroy(() => {
		window.removeEventListener('keydown', handleGlobalKeydown);
	});
</script>

<!-- An amount in the bank's currency, converted to the display currency when it differs -->
{#snippet bankAmount(line: any, abs: number)}
	{#if showConverted}
		{@const c = cvt(abs, line.transaction_date, $displayCurrency, $exchangeRates)}
		{#if c.hasRate}
			{c.display}
			<span class="block text-xs text-muted-foreground">{fmt(abs)} {selectedBankCurrency}</span>
		{:else}
			{fmt(abs)}
		{/if}
	{:else}
		{fmt(abs)}
	{/if}
{/snippet}

{#snippet accountOptions(list: any[])}
	<NativeSelect.Option value="">—</NativeSelect.Option>
	{#each list as acct}
		<NativeSelect.Option value={acct.id}>{acct.code} — {acct.name}</NativeSelect.Option>
	{/each}
{/snippet}

<!-- Import Statement -->
<Dialog.Root bind:open={showImportModal}>
	<Dialog.Content class="sm:max-w-md [&>*]:min-w-0">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Import Statement')}</Dialog.Title>
		</Dialog.Header>
		<div class="grid gap-4">
			<!-- File picker: a button over a hidden input, the chosen file on its own row
			     (as the other accounting pickers: logo, attachments, opening balances) -->
			<div class="grid gap-1.5" role="group" aria-labelledby="bank-import-file-label">
				<div id="bank-import-file-label" class="text-sm leading-none font-medium">
					{$i18n.t('Bank Statement (CSV or Excel)')} *
				</div>
				<input
					bind:this={importFileInput}
					type="file"
					accept=".csv,.xlsx,.xls"
					class="sr-only"
					tabindex="-1"
					aria-hidden="true"
					onchange={(e) => (importFile = e.currentTarget.files?.[0] ?? null)}
				/>
				{#if importFile}
					<div class="flex items-center gap-2 rounded-md border px-3 py-1.5 text-sm">
						<FileSpreadsheet class="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
						<span class="min-w-0 flex-1 truncate" title={importFile.name}>{importFile.name}</span>
						<Button
							variant="link"
							size="xs"
							class="h-auto px-0"
							disabled={importing}
							onclick={() => importFileInput?.click()}>{$i18n.t('Change')}</Button
						>
						<Tip content={$i18n.t('Remove file')}>
							<Button
								variant="ghost"
								size="icon-xs"
								aria-label={$i18n.t('Remove file')}
								disabled={importing}
								onclick={() => {
									importFile = null;
									if (importFileInput) importFileInput.value = '';
								}}
							>
								<X />
							</Button>
						</Tip>
					</div>
				{:else}
					<div class="flex flex-wrap items-center gap-2">
						<Button variant="outline" size="sm" onclick={() => importFileInput?.click()}>
							<Upload />{$i18n.t('Choose file')}
						</Button>
						<span class="text-sm text-muted-foreground">{$i18n.t('.csv, .xlsx or .xls')}</span>
					</div>
				{/if}
			</div>
			<div class="grid gap-1.5">
				<Label for="bank-import-currency">{$i18n.t('Currency')}</Label>
				<NativeSelect.Root id="bank-import-currency" class="w-full" bind:value={importCurrency}>
					{#each CURRENCIES as c}
						<NativeSelect.Option value={c}>{c}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
				<p class="text-sm text-muted-foreground">
					{$i18n.t('Defaults to the bank account currency')}
				</p>
			</div>
			<Button variant="outline" class="w-full" onclick={downloadBankStatementTemplate}>
				<Download />{$i18n.t('Download Sample Template (.xlsx)')}
			</Button>
			{#if recentImports.length}
				<div class="grid gap-1.5">
					<p class="text-sm font-medium">{$i18n.t('Recent imports')}</p>
					<ul class="divide-y rounded-lg border">
						{#each recentImports as batch (batch.batch_id)}
							<li class="flex items-center gap-3 px-3 py-2 text-sm">
								<div class="min-w-0 flex-1">
									<p class="truncate">
										{$i18n.t('{{count}} lines', { count: batch.lines })} ·
										{importDay(batch.first_date)} – {importDay(batch.last_date)}
									</p>
									<p class="text-xs text-muted-foreground">
										{$i18n.t('Imported {{date}}', { date: importDay(batch.imported_at) })}{#if batch.in_use}
											· {$i18n.t('{{count}} in use', { count: batch.in_use })}{/if}
									</p>
								</div>
								<Button
									variant="ghost"
									size="sm"
									disabled={batch.in_use > 0}
									title={batch.in_use
										? $i18n.t('Unmatch its lines before undoing this import')
										: undefined}
									onclick={() => askUndoImport(batch)}>{$i18n.t('Undo')}</Button
								>
							</li>
						{/each}
					</ul>
				</div>
			{/if}
		</div>
		<Dialog.Footer>
			<Button
				variant="outline"
				disabled={importing}
				onclick={() => {
					showImportModal = false;
				}}>{$i18n.t('Cancel')}</Button
			>
			<Button disabled={importing || !importFile} onclick={handleImport}>
				{#if importing}
					<Spinner />{$i18n.t('Importing...')}
				{:else}
					<Upload />{$i18n.t('Import')}
				{/if}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- New bank account -->
<Dialog.Root bind:open={showNewBank}>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-lg [&>*]:min-w-0">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('New Bank')}</Dialog.Title>
		</Dialog.Header>
		<div class="grid gap-4">
			<div class="grid gap-3 sm:grid-cols-[1fr_6rem]">
				<div class="grid gap-1.5">
					<Label for="new-bank-name">{$i18n.t('Name', { context: 'gnos3' })}</Label>
					<Input
						id="new-bank-name"
						type="text"
						bind:value={newBankName}
						placeholder={$i18n.t('Main checking account')}
					/>
				</div>
				<div class="grid gap-1.5">
					<Label for="new-bank-currency">{$i18n.t('Currency')}</Label>
					<Input
						id="new-bank-currency"
						type="text"
						maxlength={3}
						class="font-mono uppercase"
						bind:value={newBankCurrency}
						placeholder={selectedBankCurrency || 'USD'}
					/>
				</div>
			</div>
			<div class="grid gap-1.5">
				<Label for="new-bank-gl">{$i18n.t('GL Account')}</Label>
				<NativeSelect.Root
					id="new-bank-gl"
					class="w-full"
					value={newBankAccountId ?? ''}
					onchange={(e: Event) => (newBankAccountId = idFrom(e))}
				>
					{@render accountOptions(postableAccounts.filter((a) => a.account_type === 'asset'))}
				</NativeSelect.Root>
			</div>
			<div class="grid gap-3 sm:grid-cols-2">
				<div class="grid gap-1.5">
					<Label for="new-bank-out">{$i18n.t('Payments out →')}</Label>
					<NativeSelect.Root
						id="new-bank-out"
						class="w-full"
						value={newBankOutboundId ?? ''}
						title={$i18n.t(
							'Account debited when money leaves this bank and the party is not identified'
						)}
						onchange={(e: Event) => (newBankOutboundId = idFrom(e))}
					>
						{@render accountOptions(postableAccounts)}
					</NativeSelect.Root>
					<p class="text-xs text-muted-foreground">
						{$i18n.t(
							'Account debited when money leaves this bank and the party is not identified'
						)}
					</p>
				</div>
				<div class="grid gap-1.5">
					<Label for="new-bank-in">{$i18n.t('Payments in →')}</Label>
					<NativeSelect.Root
						id="new-bank-in"
						class="w-full"
						value={newBankInboundId ?? ''}
						title={$i18n.t(
							'Account credited when money arrives in this bank and the party is not identified'
						)}
						onchange={(e: Event) => (newBankInboundId = idFrom(e))}
					>
						{@render accountOptions(postableAccounts)}
					</NativeSelect.Root>
					<p class="text-xs text-muted-foreground">
						{$i18n.t(
							'Account credited when money arrives in this bank and the party is not identified'
						)}
					</p>
				</div>
			</div>
		</div>
		<Dialog.Footer>
			<Button
				variant="outline"
				onclick={() => {
					showNewBank = false;
				}}>{$i18n.t('Cancel')}</Button
			>
			<Button disabled={!newBankName} onclick={handleCreateBank}>{$i18n.t('Create')}</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- The selected bank account's GL mapping -->
<Dialog.Root bind:open={showEditBank}>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-lg [&>*]:min-w-0">
		<Dialog.Header>
			<Dialog.Title>
				{bankAccounts.find((b) => b.id === selectedBankId)?.name ?? ''} · {$i18n.t('Accounts')}
			</Dialog.Title>
			<Dialog.Description>
				{$i18n.t(
					"Where entries from this bank's statements post. Only detail accounts are listed — an account with sub-accounts cannot be posted to."
				)}
			</Dialog.Description>
		</Dialog.Header>
		<div class="grid gap-4">
			<div class="grid gap-1.5">
				<Label for="edit-bank-gl">{$i18n.t('Bank GL Account')}</Label>
				<NativeSelect.Root
					id="edit-bank-gl"
					class="w-full"
					value={editBankAccountId ?? ''}
					onchange={(e: Event) => (editBankAccountId = idFrom(e))}
				>
					{@render accountOptions(postableAccounts.filter((a) => a.account_type === 'asset'))}
				</NativeSelect.Root>
			</div>
			<div class="grid gap-3 sm:grid-cols-2">
				<div class="grid gap-1.5">
					<Label for="edit-bank-out">{$i18n.t('Payments out →')}</Label>
					<NativeSelect.Root
						id="edit-bank-out"
						class="w-full"
						value={editBankOutboundId ?? ''}
						onchange={(e: Event) => (editBankOutboundId = idFrom(e))}
					>
						{@render accountOptions(postableAccounts)}
					</NativeSelect.Root>
				</div>
				<div class="grid gap-1.5">
					<Label for="edit-bank-in">{$i18n.t('Payments in →')}</Label>
					<NativeSelect.Root
						id="edit-bank-in"
						class="w-full"
						value={editBankInboundId ?? ''}
						onchange={(e: Event) => (editBankInboundId = idFrom(e))}
					>
						{@render accountOptions(postableAccounts)}
					</NativeSelect.Root>
				</div>
			</div>
		</div>
		<Dialog.Footer>
			<Button
				variant="outline"
				onclick={() => {
					showEditBank = false;
				}}>{$i18n.t('Cancel')}</Button
			>
			<Button onclick={handleSaveBankAccounts}>{$i18n.t('Save')}</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Create Entry Modal (reuses the same form as the Entries tab) -->
<TransactionFormModal
	bind:show={showCreateEntryModal}
	transaction={null}
	{accounts}
	{companyId}
	bankStatementLineId={createEntryBslId}
	prefill={createEntryPrefill}
	on:save={handleCreateEntrySave}
/>

<div class="flex flex-col gap-4">
	<!-- Header: Bank selector + actions -->
	<div class="flex flex-wrap items-center gap-2">
		{#if bankAccounts.length > 0}
			<NativeSelect.Root
				size="sm"
				class="max-w-72"
				value={selectedBankId}
				aria-label={$i18n.t('Bank account')}
				onchange={(e: Event) => {
					selectedBankId = Number((e.currentTarget as HTMLSelectElement).value);
					loadStatements();
				}}
			>
				{#each bankAccounts as ba}
					<NativeSelect.Option value={ba.id}
						>{ba.name}{ba.currency ? ` (${ba.currency})` : ''}</NativeSelect.Option
					>
				{/each}
			</NativeSelect.Root>
			{#if selectedBankCurrency}
				<Badge variant="outline" class="font-mono">{selectedBankCurrency}</Badge>
			{/if}
			{#if showConverted}
				<Tip
					content={$i18n.t('Change the display currency from the selector at the top of the page')}
				>
					<span class="text-sm text-muted-foreground">→ {$displayCurrency}</span>
				</Tip>
			{/if}
		{/if}
		{#if selectedBankId}
			<Button variant="ghost" size="sm" onclick={toggleEditBank}>{$i18n.t('Accounts')}</Button>
		{/if}
		<Button
			variant="ghost"
			size="sm"
			onclick={() => {
				showNewBank = true;
			}}><Plus />{$i18n.t('New Bank')}</Button
		>
		{#if selectedBankId}
			<div class="ml-auto flex flex-wrap items-center gap-2">
				<Button variant="outline" size="sm" onclick={openImportModal}>
					<Upload />{$i18n.t('Import Statement')}
				</Button>
				<Button size="sm" disabled={autoReconciling} onclick={handleAutoReconcile}>
					{#if autoReconciling}<Spinner />{:else}<Sparkles />{/if}
					{$i18n.t('Auto-Reconcile')}
				</Button>
			</div>
		{/if}
	</div>

	{#if loading}
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(10rem,100%),1fr))] gap-3">
			{#each Array(4) as _}<Skeleton class="h-[88px] rounded-xl" />{/each}
		</div>
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(8) as _}<Skeleton class="h-8 w-full" />{/each}
		</div>
	{:else if loadError && bankAccounts.length === 0}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Could not load the bank accounts')}</Alert.Title>
			<Alert.Description>{loadError}</Alert.Description>
			<Alert.Action>
				<Button variant="outline" size="sm" onclick={load}>{$i18n.t('Retry')}</Button>
			</Alert.Action>
		</Alert.Root>
	{:else if selectedBankId}
		<!-- Auto-Reconcile AI Loading Banner -->
		{#if autoReconciling}
			<Alert.Root aria-live="polite">
				<Sparkles />
				<Alert.Title class="flex items-center gap-2">
					{$i18n.t('AI is matching bank statement lines to GL transactions...')}
					<Spinner class="size-3.5" />
				</Alert.Title>
			</Alert.Root>
		{/if}

		<!-- Reconciliation Summary Cards -->
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(10rem,100%),1fr))] gap-3">
			<Card.Root size="sm" class="gap-1">
				<Card.Content class="grid gap-1">
					<div class="text-sm text-muted-foreground">{$i18n.t('Bank Balance')}</div>
					<div class="text-xl leading-7 font-semibold tabular-nums">{fmtSigned(bankBalance)}</div>
					<div class="text-[13px] text-muted-foreground">{selectedBankCurrency}</div>
				</Card.Content>
			</Card.Root>
			<Card.Root size="sm" class="gap-1">
				<Card.Content class="grid gap-1">
					<div class="text-sm text-muted-foreground">{$i18n.t('GL Balance')}</div>
					<div class="text-xl leading-7 font-semibold tabular-nums">{fmtSigned(glBalance)}</div>
					<div class="text-[13px] text-muted-foreground">{$i18n.t('Matched lines')}</div>
				</Card.Content>
			</Card.Root>
			<Card.Root size="sm" class="gap-1">
				<Card.Content class="grid gap-1">
					<div class="text-sm text-muted-foreground">{$i18n.t('Difference')}</div>
					<div class="flex items-center gap-1.5 text-xl leading-7 font-semibold tabular-nums">
						{#if !isReconciled}<TriangleAlert
								class="size-4 shrink-0 text-warning"
								aria-hidden="true"
							/>{/if}
						{fmtSigned(reconDifference)}
					</div>
					<div class="text-[13px] text-muted-foreground">{$i18n.t('Bank - GL')}</div>
				</Card.Content>
			</Card.Root>
			<Card.Root size="sm" class="gap-1">
				<Card.Content class="grid gap-1">
					<div class="text-sm text-muted-foreground">{$i18n.t('Status')}</div>
					<div class="flex flex-wrap items-center gap-2 pt-1">
						{#if isReconciled}
							<Badge variant="success"><CircleCheck />{$i18n.t('Reconciled')}</Badge>
							<span class="text-[13px] text-muted-foreground tabular-nums"
								>{matchedCount}/{statements.length} {$i18n.t('matched')}</span
							>
						{:else}
							<Badge variant="warning"><TriangleAlert />{$i18n.t('Unreconciled')}</Badge>
							<span class="text-[13px] text-muted-foreground tabular-nums"
								>{unmatchedCount} {$i18n.t('lines remaining')}</span
							>
						{/if}
					</div>
				</Card.Content>
			</Card.Root>
		</div>

		<!-- Filters + Search -->
		<div class="flex flex-wrap items-center gap-2">
			<ToggleGroup.Root
				type="single"
				variant="outline"
				size="sm"
				bind:value={statusSeg}
				onValueChange={onStatusSeg}
				aria-label={$i18n.t('Match status')}
			>
				{#each [['all', 'All'], ['unmatched', 'Unmatched'], ['partial_matched', 'Partial'], ['auto_matched', 'Auto'], ['manual_matched', 'Manual'], ['excluded', 'Excluded']] as [val, label]}
					<ToggleGroup.Item value={val}>{$i18n.t(label)}</ToggleGroup.Item>
				{/each}
			</ToggleGroup.Root>
			<ToggleGroup.Root
				type="single"
				variant="outline"
				size="sm"
				bind:value={directionSeg}
				onValueChange={onDirectionSeg}
				aria-label={$i18n.t('Direction')}
			>
				{#each [['all', 'All'], ['credit', 'Credit (In)'], ['debit', 'Debit (Out)']] as [val, label]}
					<ToggleGroup.Item value={val}>{$i18n.t(label)}</ToggleGroup.Item>
				{/each}
			</ToggleGroup.Root>
			<div class="relative min-w-[12rem] flex-1">
				<Search
					class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
				/>
				<Input
					type="search"
					class="h-8 pl-8"
					bind:value={searchQuery}
					placeholder={$i18n.t('Search description, reference, amount...')}
					aria-label={$i18n.t('Search description, reference, amount...')}
				/>
			</div>
			<Input
				type="date"
				class="h-8 w-auto"
				bind:value={dateFrom}
				aria-label={$i18n.t('From')}
				title={$i18n.t('From')}
			/>
			<Input
				type="date"
				class="h-8 w-auto"
				bind:value={dateTo}
				aria-label={$i18n.t('To')}
				title={$i18n.t('To')}
			/>
			{#if searchQuery || dateFrom || dateTo || directionFilter}
				<Button
					variant="ghost"
					size="sm"
					onclick={() => {
						searchQuery = '';
						dateFrom = '';
						dateTo = '';
						directionFilter = '';
					}}><X />{$i18n.t('Clear')}</Button
				>
			{/if}
		</div>
		{#if searchQuery || dateFrom || dateTo || directionFilter}
			<div class="-mt-2 text-sm text-muted-foreground tabular-nums">
				{filteredStatements.length} / {statements.length}
				{$i18n.t('lines')}
			</div>
		{/if}

		{#if statementsLoading}
			<div class="flex flex-col gap-2 rounded-md border p-3">
				{#each Array(8) as _}<Skeleton class="h-8 w-full" />{/each}
			</div>
		{:else if statementsError && statements.length === 0}
			<Alert.Root variant="destructive">
				<CircleAlert />
				<Alert.Title>{$i18n.t('Could not load the statement lines')}</Alert.Title>
				<Alert.Description>{statementsError}</Alert.Description>
				<Alert.Action>
					<Button variant="outline" size="sm" onclick={loadStatements}>{$i18n.t('Retry')}</Button>
				</Alert.Action>
			</Alert.Root>
		{:else if statements.length === 0}
			<Empty.Root class="border border-dashed">
				<Empty.Header>
					<Empty.Media variant="icon"><FileSpreadsheet /></Empty.Media>
					<Empty.Title>{$i18n.t('No statement lines. Import a CSV to get started.')}</Empty.Title>
				</Empty.Header>
				<Empty.Content>
					<Button variant="outline" size="sm" onclick={openImportModal}>
						<Upload />{$i18n.t('Import Statement')}
					</Button>
				</Empty.Content>
			</Empty.Root>
		{:else}
			{#if selectedBslIds.size > 0}
				<div
					class="flex w-fit flex-wrap items-center gap-2 rounded-lg border bg-card py-1 pr-1 pl-3 text-sm shadow-md"
				>
					<span>
						<span class="font-medium tabular-nums">{selectedBslIds.size}</span>
						{$i18n.t('line(s) selected')} ·
						<span class="tabular-nums">{$i18n.t('Total')}: {fmt(selectedBslTotal)}</span>
					</span>
					<Button size="xs" onclick={openMultiMatchModal}>
						<ArrowLeftRight />{$i18n.t('Match Selected to Entry(s)')}
					</Button>
					<Tip content={$i18n.t('Clear')}>
						<Button
							variant="ghost"
							size="icon-xs"
							aria-label={$i18n.t('Clear')}
							onclick={() => {
								selectedBslIds = new Set();
							}}
						>
							<X />
						</Button>
					</Tip>
				</div>
			{/if}
			<div class="overflow-hidden rounded-md border">
				<Table.Root>
					<Table.Header class="bg-muted/50">
						<Table.Row class="hover:bg-transparent">
							<Table.Head class="w-8">
								<Checkbox
									checked={selectedBslIds.size > 0 &&
										selectedBslIds.size ===
											filteredStatements.filter((s) =>
												['unmatched', 'partial_matched'].includes(s.match_status)
											).length}
									aria-label={$i18n.t('Select all')}
									onCheckedChange={(v) => {
										if (v === true) {
											selectedBslIds = new Set(
												filteredStatements
													.filter((s) => ['unmatched', 'partial_matched'].includes(s.match_status))
													.map((s) => s.id)
											);
										} else {
											selectedBslIds = new Set();
										}
									}}
								/>
							</Table.Head>
							<Table.Head>{$i18n.t('#')}</Table.Head>
							<Table.Head>{$i18n.t('Date')}</Table.Head>
							<Table.Head>{$i18n.t('Description')}</Table.Head>
							<Table.Head>{$i18n.t('Reference')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Debit')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Credit')}</Table.Head>
							<Table.Head class="text-center">{$i18n.t('Currency')}</Table.Head>
							<Table.Head>{$i18n.t('Status')}</Table.Head>
							<Table.Head>{$i18n.t('Posted to')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Actions')}</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#if filteredStatements.length === 0 && statements.length > 0}
							<Table.Row class="hover:bg-transparent">
								<Table.Cell colspan={11} class="py-8 text-center text-muted-foreground">
									<span class="inline-flex items-center gap-2">
										<ListFilter class="size-4" aria-hidden="true" />{$i18n.t(
											'No lines match your filters.'
										)}
									</span>
								</Table.Cell>
							</Table.Row>
						{/if}
						{#each filteredStatements as line (line.id)}
							{@const amt = parseFloat(line.amount)}
							<Table.Row data-state={selectedBslIds.has(line.id) ? 'selected' : undefined}>
								<Table.Cell>
									{#if ['unmatched', 'partial_matched'].includes(line.match_status)}
										<Checkbox
											checked={selectedBslIds.has(line.id)}
											aria-label={$i18n.t('Select')}
											onCheckedChange={() => toggleBslSelection(line.id)}
										/>
									{/if}
								</Table.Cell>
								<Table.Cell class="font-mono text-[13px] text-muted-foreground"
									>{line.id}</Table.Cell
								>
								<Table.Cell class="tabular-nums">{line.transaction_date}</Table.Cell>
								<Table.Cell class="max-w-[16rem] truncate" title={line.description ?? ''}
									>{line.description ?? '—'}</Table.Cell
								>
								<Table.Cell class="font-mono text-[13px]">
									{#if editingRefLineId === line.id}
										<!-- svelte-ignore a11y_autofocus -->
										<Input
											type="text"
											class="h-7 w-32 font-mono text-[13px]"
											aria-label={$i18n.t('Edit reference')}
											bind:value={editRefValue}
											onkeydown={handleRefKeydown}
											onblur={saveEditRef}
											autofocus
										/>
									{:else}
										<span class="inline-flex items-center gap-1">
											{#if line.reference}{line.reference}{:else}<span class="text-muted-foreground"
													>—</span
												>{/if}
											<Tip content={$i18n.t('Edit reference')}>
												<Button
													variant="ghost"
													size="icon-xs"
													class="size-6 text-muted-foreground"
													aria-label={$i18n.t('Edit reference')}
													onclick={() => startEditRef(line)}
												>
													<Pencil class="size-3.5" />
												</Button>
											</Tip>
										</span>
									{/if}
								</Table.Cell>
								<!-- Debit (outflow) -->
								<Table.Cell class="text-right tabular-nums">
									{#if amt < 0}{@render bankAmount(line, Math.abs(amt))}{/if}
								</Table.Cell>
								<!-- Credit (inflow) -->
								<Table.Cell class="text-right tabular-nums">
									{#if amt > 0}{@render bankAmount(line, amt)}{/if}
								</Table.Cell>
								<Table.Cell class="text-center font-mono text-[13px] text-muted-foreground"
									>{showConverted ? $displayCurrency : selectedBankCurrency || '—'}</Table.Cell
								>
								<Table.Cell>
									<div class="flex flex-col items-start gap-1">
										<span class="inline-flex items-center gap-1.5">
											<StatusBadge kind="bank" status={line.match_status} />
											{#if line.match_status === 'partial_matched'}
												<span class="text-xs text-muted-foreground tabular-nums"
													>{fmt(line.allocated_total)}/{fmt(Math.abs(amt))}</span
												>
											{/if}
										</span>
										{#if line.matched_transaction_id || (line.match_groups && line.match_groups.length > 0)}
											<button
												type="button"
												class="inline-flex items-center gap-1 rounded-sm text-xs text-link hover:underline focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
												aria-expanded={expandedLineId === line.id}
												onclick={(e) => {
													e.stopPropagation();
													expandedLineId = expandedLineId === line.id ? null : line.id;
												}}
											>
												<ChevronRight
													class="size-3.5 transition-transform {expandedLineId === line.id
														? 'rotate-90'
														: ''}"
												/>
												{#if line.matched_transaction_id}
													<span class="font-mono">#{line.matched_transaction_id}</span>
												{/if}
												{#if line.match_groups && line.match_groups.length > 0}
													<span>{line.match_groups.length} {$i18n.t('group(s)')}</span>
												{/if}
											</button>
										{/if}
									</div>
								</Table.Cell>
								<!-- Which GL account this line was actually posted to. A reconciled
								     line with nothing here is booked nowhere — the bank says the money
								     moved and the ledger has no entry for it. -->
								<Table.Cell>
									{#if line.posting?.primary_account_code}
										<div class="flex items-baseline gap-1.5">
											<span class="font-mono text-[13px]">{line.posting.primary_account_code}</span>
											<span class="max-w-[10rem] truncate text-muted-foreground"
												>{line.posting.primary_account_name}</span
											>
											{#if line.posting.extra_count}
												<Badge variant="count">+{line.posting.extra_count}</Badge>
											{/if}
										</div>
									{:else if isLineMatched(line)}
										<Tip
											content={$i18n.t(
												'This line is marked reconciled but no accounting entry exists for it'
											)}
										>
											<Badge variant="danger"><CircleAlert />{$i18n.t('Not posted')}</Badge>
										</Tip>
									{:else}
										<span class="text-muted-foreground">—</span>
									{/if}
								</Table.Cell>
								<Table.Cell class="text-right">
									<div class="inline-flex items-center justify-end gap-1">
										{#if line.match_status === 'excluded'}
											<Button variant="ghost" size="xs" onclick={() => handleInclude(line.id)}
												>{$i18n.t('Include')}</Button
											>
										{:else if line.match_status === 'unmatched' || line.match_status === 'partial_matched'}
											<Button
												variant="outline"
												size="xs"
												class="match-trigger"
												aria-expanded={matchingLineId === line.id}
												onclick={(e: MouseEvent) => {
													e.stopPropagation();
													if (matchingLineId === line.id) {
														matchingLineId = null;
													} else {
														openMatchPopover(line);
													}
												}}
											>
												{line.match_status === 'partial_matched'
													? $i18n.t('Match More')
													: $i18n.t('Match')}
												<ChevronDown />
											</Button>
											{#if line.match_status === 'partial_matched'}
												<Button variant="ghost" size="xs" onclick={() => handleUnmatch(line.id)}
													>{$i18n.t('Unmatch')}</Button
												>
											{:else}
												<!-- Record the line as a payment: the form resolves the bank side from this
												     bank account and the settled account from a bank-line rule, the bank
												     account's defaults or the company AP/AR default — nothing is guessed. -->
												<Tip
													content={line.suggested_bank_fee_rule
														? $i18n.t(
																'A bank-line rule matches this description — the payment form will pre-fill the account'
															)
														: $i18n.t(
																'Record this line as a payment (the settled account is resolved from rules and defaults)'
															)}
												>
													<Button
														variant="outline"
														size="xs"
														onclick={(e: MouseEvent) => {
															e.stopPropagation();
															handlePay(line);
														}}
													>
														{line.suggested_bank_fee_rule
															? $i18n.t('Bank Fee')
															: $i18n.t('Record Payment')}
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
													<DropdownMenu.Content align="end" class="w-64">
														<DropdownMenu.Item onSelect={() => openCreateEntry(line)}>
															<NotebookPen />
															<div class="grid">
																<span>{$i18n.t('Journal')}</span>
																<span class="text-xs text-muted-foreground"
																	>{$i18n.t(
																		'Write a journal entry by hand for this line (interest, a transfer, an unusual movement)'
																	)}</span
																>
															</div>
														</DropdownMenu.Item>
														<DropdownMenu.Separator />
														<DropdownMenu.Item onSelect={() => handleExclude(line.id)}>
															<Ban />{$i18n.t('Exclude')}
														</DropdownMenu.Item>
													</DropdownMenu.Content>
												</DropdownMenu.Root>
											{/if}
										{:else}
											<Button variant="ghost" size="xs" onclick={() => handleUnmatch(line.id)}
												>{$i18n.t('Unmatch')}</Button
											>
											<!-- Posted = a posted entry moves this bank account (created from the line
											     or booked earlier and matched). Offering "Post" on such a line would
											     book the money a second time. -->
											{#if line.posting?.bank_leg_status === 'posted'}
												<Tip
													content={line.posting.source === 'settlement'
														? $i18n.t('Payment entry created from this line')
														: $i18n.t('The matched entry already moves this bank account')}
												>
													<StatusBadge kind="entry" status="posted" />
												</Tip>
											{:else if line.posting?.bank_leg_status === 'draft'}
												<Tip
													content={$i18n.t(
														'The entry that moves this bank account is still a draft — complete and post it under Entries'
													)}
												>
													<a
														href="/accounting/company/{companyId}/entries?id={line.posting
															.bank_leg_entry_id}"
														class={cn(
															badgeVariants({ variant: 'status' }),
															'hover:bg-accent hover:text-foreground'
														)}
													>
														<StatusBadge
															kind="entry"
															status="draft"
															label={$i18n.t('Draft entry')}
															bare
														/>
													</a>
												</Tip>
											{:else}
												<Tip
													content={$i18n.t(
														'The matched entry does not move this bank account — record the payment'
													)}
												>
													<Button
														variant="outline"
														size="xs"
														onclick={(e: MouseEvent) => {
															e.stopPropagation();
															handlePay(line);
														}}>{$i18n.t('Post')}</Button
													>
												</Tip>
											{/if}
										{/if}
									</div>
								</Table.Cell>
							</Table.Row>
							<!-- Expandable matched details row -->
							{#if expandedLineId === line.id && (line.matched_transaction_id || (line.match_groups && line.match_groups.length > 0))}
								<Table.Row class="bg-muted/30 hover:bg-muted/30">
									<Table.Cell colspan={11} class="p-4 whitespace-normal">
										<div
											class="sticky left-0 grid w-full max-w-[min(64rem,calc(100vw-4rem))] gap-4"
										>
											<!-- What this line actually booked, before the matched-entry list.
											     `settlement` means reconciling created a payment entry; otherwise
											     the accounts come from the entry the line was matched against. -->
											{#if line.posting}
												<div class="grid gap-2">
													<div class="text-sm">
														<span class="font-medium">{$i18n.t('Posted to')}</span>
														<span class="text-muted-foreground">
															· {line.posting.source === 'settlement'
																? $i18n.t('settlement entry created on reconciliation')
																: $i18n.t('accounts of the matched entry')}
															{#if line.posting.settlement_entry?.entry_number}
																· <span class="font-mono text-[13px]"
																	>{line.posting.settlement_entry.entry_number}</span
																>
															{/if}
														</span>
													</div>
													<div class="overflow-hidden rounded-md border bg-card">
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
																{#each line.posting.counterparts ?? [] as cp}
																	<Table.Row class="hover:bg-transparent">
																		<Table.Cell class="py-1.5 font-mono text-[13px]"
																			>{cp.account_code}</Table.Cell
																		>
																		<Table.Cell class="py-1.5">{cp.account_name}</Table.Cell>
																		<Table.Cell class="py-1.5 text-right tabular-nums"
																			>{parseFloat(cp.debit) ? fmt(cp.debit) : '—'}</Table.Cell
																		>
																		<Table.Cell class="py-1.5 text-right tabular-nums"
																			>{parseFloat(cp.credit) ? fmt(cp.credit) : '—'}</Table.Cell
																		>
																	</Table.Row>
																{/each}
																{#if line.posting.bank_account}
																	<Table.Row class="hover:bg-transparent">
																		<Table.Cell class="py-1.5 font-mono text-[13px]"
																			>{line.posting.bank_account.account_code}</Table.Cell
																		>
																		<Table.Cell class="py-1.5">
																			{line.posting.bank_account.account_name}
																			<span class="text-muted-foreground"
																				>({$i18n.t('bank side')})</span
																			>
																		</Table.Cell>
																		<Table.Cell class="py-1.5 text-right text-muted-foreground"
																			>—</Table.Cell
																		>
																		<Table.Cell class="py-1.5 text-right text-muted-foreground"
																			>—</Table.Cell
																		>
																	</Table.Row>
																{/if}
															</Table.Body>
														</Table.Root>
													</div>
												</div>
											{:else if isLineMatched(line)}
												<Alert.Root variant="destructive">
													<CircleAlert />
													<Alert.Title>{$i18n.t('No accounting entry for this line')}</Alert.Title>
													<Alert.Description>
														{$i18n.t(
															'The line is marked reconciled but nothing was booked to the ledger. Unmatch it and reconcile again, or post the entry manually.'
														)}
													</Alert.Description>
												</Alert.Root>
											{/if}
											<div class="grid gap-2">
												<div class="text-sm font-medium">{$i18n.t('Matched Entries')}</div>
												<div class="overflow-hidden rounded-md border bg-card">
													<Table.Root>
														<Table.Header class="bg-muted/50">
															<Table.Row class="hover:bg-transparent">
																<Table.Head class="h-8">#</Table.Head>
																<Table.Head class="h-8">{$i18n.t('Date')}</Table.Head>
																<Table.Head class="h-8">{$i18n.t('Type')}</Table.Head>
																<Table.Head class="h-8">{$i18n.t('Reference')}</Table.Head>
																<Table.Head class="h-8">{$i18n.t('Description')}</Table.Head>
																<Table.Head class="h-8 text-right">{$i18n.t('Amount')}</Table.Head>
																<Table.Head class="h-8">{$i18n.t('Status')}</Table.Head>
															</Table.Row>
														</Table.Header>
														<Table.Body>
															{#if line.matched_transaction_id && line.matched_txn_type}
																<Table.Row class="hover:bg-transparent">
																	<Table.Cell class="py-1.5 font-mono text-[13px]">
																		<a
																			href="/accounting/company/{companyId}/entries"
																			class="text-link underline-offset-4 hover:underline"
																			>#{line.matched_transaction_id}</a
																		>
																	</Table.Cell>
																	<Table.Cell class="py-1.5 tabular-nums"
																		>{line.matched_txn_date ?? '—'}</Table.Cell
																	>
																	<Table.Cell class="py-1.5 text-muted-foreground"
																		>{line.matched_txn_type}</Table.Cell
																	>
																	<Table.Cell class="py-1.5 font-mono text-[13px]"
																		>{line.matched_txn_reference ?? '—'}</Table.Cell
																	>
																	<Table.Cell
																		class="max-w-[16rem] truncate py-1.5"
																		title={line.matched_txn_description ?? ''}
																		>{line.matched_txn_description ?? '—'}</Table.Cell
																	>
																	<Table.Cell class="py-1.5 text-right font-medium tabular-nums"
																		>{fmt(Math.abs(amt))}</Table.Cell
																	>
																	<Table.Cell class="py-1.5">
																		<StatusBadge kind="bank" status="matched" />
																	</Table.Cell>
																</Table.Row>
															{/if}
															{#if line.match_groups}
																{#each line.match_groups as mg}
																	{#if mg.transactions && mg.transactions.length > 0}
																		{#each mg.transactions as txn}
																			<Table.Row class="hover:bg-transparent">
																				<Table.Cell class="py-1.5 font-mono text-[13px]">
																					<a
																						href="/accounting/company/{companyId}/entries"
																						class="text-link underline-offset-4 hover:underline"
																						>#{txn.transaction_id}</a
																					>
																				</Table.Cell>
																				<Table.Cell class="py-1.5 tabular-nums"
																					>{txn.date ?? '—'}</Table.Cell
																				>
																				<Table.Cell class="py-1.5 text-muted-foreground"
																					>{txn.type ?? '—'}</Table.Cell
																				>
																				<Table.Cell class="py-1.5 font-mono text-[13px]"
																					>{txn.reference ?? '—'}</Table.Cell
																				>
																				<Table.Cell
																					class="max-w-[16rem] truncate py-1.5"
																					title={txn.description ?? ''}
																					>{txn.description ?? '—'}</Table.Cell
																				>
																				<Table.Cell
																					class="py-1.5 text-right font-medium tabular-nums"
																					>{fmt(txn.allocated_amount)}</Table.Cell
																				>
																				<Table.Cell class="py-1.5">
																					<Badge variant="outline"
																						>{$i18n.t('Group')}
																						<span class="font-mono">#{mg.id}</span></Badge
																					>
																				</Table.Cell>
																			</Table.Row>
																		{/each}
																	{:else}
																		<Table.Row class="hover:bg-transparent">
																			<Table.Cell class="py-1.5" colspan={5}>
																				<Badge variant="outline"
																					>{$i18n.t('Group')}
																					<span class="font-mono">#{mg.id}</span></Badge
																				>
																				<span class="ml-2 text-muted-foreground tabular-nums"
																					>{$i18n.t('Allocated')}: {fmt(mg.allocated_amount)}</span
																				>
																			</Table.Cell>
																			<Table.Cell class="py-1.5 text-right font-medium tabular-nums"
																				>{fmt(mg.allocated_amount)}</Table.Cell
																			>
																			<Table.Cell class="py-1.5"></Table.Cell>
																		</Table.Row>
																	{/if}
																{/each}
															{/if}
															{#if !line.matched_transaction_id && (!line.match_groups || line.match_groups.length === 0)}
																<Table.Row class="hover:bg-transparent">
																	<Table.Cell
																		colspan={7}
																		class="py-4 text-center text-muted-foreground"
																		>{$i18n.t('No matched entries found.')}</Table.Cell
																	>
																</Table.Row>
															{/if}
														</Table.Body>
													</Table.Root>
												</div>
											</div>
										</div>
									</Table.Cell>
								</Table.Row>
							{/if}
							<!-- Match panel (shown below the row when matching) -->
							{#if matchingLineId === line.id}
								<Table.Row class="match-popover bg-muted/30 hover:bg-muted/30">
									<Table.Cell colspan={11} class="p-4 whitespace-normal">
										<div
											class="sticky left-0 grid w-full max-w-[min(64rem,calc(100vw-4rem))] gap-3"
										>
											<div class="flex flex-wrap items-center justify-between gap-2">
												<div class="flex flex-wrap items-baseline gap-x-2 gap-y-1 text-sm">
													<span class="font-medium">{$i18n.t('Match to entry')}:</span>
													<span class="text-muted-foreground tabular-nums"
														>{line.transaction_date} — {line.description} — {fmt(line.amount)}</span
													>
													{#if parseFloat(line.allocated_total || 0) > 0}
														<span class="text-muted-foreground tabular-nums"
															>({$i18n.t('Unallocated')}: {fmt(
																line.unallocated_amount ??
																	Math.abs(amt) - parseFloat(line.allocated_total || 0)
															)})</span
														>
													{/if}
												</div>
												<div class="flex items-center gap-3">
													<div class="flex items-center gap-2">
														<Checkbox
															id="match-multi-{line.id}"
															checked={matchMultiSelect}
															onCheckedChange={(v) => {
																matchMultiSelect = v === true;
																matchSelectedIds = new Set();
															}}
														/>
														<Label for="match-multi-{line.id}" class="font-normal"
															>{$i18n.t('Multi-select')}</Label
														>
													</div>
													<Button
														variant="ghost"
														size="xs"
														onclick={() => {
															matchingLineId = null;
														}}><X />{$i18n.t('Close')}</Button
													>
												</div>
											</div>

											<!-- Multi-select summary bar -->
											{#if matchMultiSelect && matchSelectedIds.size > 0}
												<div
													class="flex w-fit flex-wrap items-center gap-3 rounded-lg border bg-card py-1 pr-1 pl-3 text-sm shadow-md"
												>
													<span
														>{$i18n.t('Selected')}:
														<span class="font-medium tabular-nums">{matchSelectedIds.size}</span>
														{$i18n.t('entries')}</span
													>
													<span
														>{$i18n.t('Total')}:
														<span class="font-medium tabular-nums">{fmt(matchSelectedTotal)}</span
														></span
													>
													<Button
														size="xs"
														disabled={matchSelectedIds.size === 0 || matchCreating}
														onclick={handleMatchMultiple}
													>
														{#if matchCreating}
															<Spinner />{$i18n.t('Matching...')}
														{:else}
															{$i18n.t('Match Selected')}
														{/if}
													</Button>
												</div>
											{/if}

											<div class="relative">
												<Search
													class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
												/>
												<Input
													type="search"
													class="h-8 bg-card pl-8"
													bind:value={matchSearchQuery}
													placeholder={$i18n.t(
														'Search by reference, description, amount, or #ID...'
													)}
													aria-label={$i18n.t(
														'Search by reference, description, amount, or #ID...'
													)}
												/>
											</div>

											{#if matchLoading}
												<div class="flex flex-col gap-2 rounded-md border bg-card p-3">
													{#each Array(4) as _}<Skeleton class="h-7 w-full" />{/each}
												</div>
											{:else if filteredMatchCandidates.length === 0}
												<div
													class="rounded-md border border-dashed bg-card py-6 text-center text-sm text-muted-foreground"
												>
													{$i18n.t(
														'No posted entries found. Create a journal entry first, then match.'
													)}
												</div>
											{:else}
												<div class="max-h-72 overflow-y-auto rounded-md border bg-card">
													<Table.Root>
														<Table.Header class="sticky top-0 z-10 bg-muted">
															<Table.Row class="hover:bg-transparent">
																{#if matchMultiSelect}<Table.Head class="h-8 w-8"
																		><span class="sr-only">{$i18n.t('Select')}</span></Table.Head
																	>{/if}
																<Table.Head class="h-8"
																	><span class="sr-only">{$i18n.t('Match')}</span></Table.Head
																>
																<Table.Head class="h-8">#</Table.Head>
																<Table.Head class="h-8">{$i18n.t('Date')}</Table.Head>
																<Table.Head class="h-8">{$i18n.t('Type')}</Table.Head>
																<Table.Head class="h-8">{$i18n.t('Reference')}</Table.Head>
																<Table.Head class="h-8">{$i18n.t('Description')}</Table.Head>
																<Table.Head class="h-8 text-right">{$i18n.t('Amount')}</Table.Head>
																{#if !matchMultiSelect}<Table.Head class="h-8"
																		><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head
																	>{/if}
															</Table.Row>
														</Table.Header>
														<Table.Body>
															{#each filteredMatchCandidates as txn}
																{@const isSelected = matchSelectedIds.has(txn.id)}
																<Table.Row data-state={isSelected ? 'selected' : undefined}>
																	{#if matchMultiSelect}
																		<Table.Cell class="py-1.5">
																			<Checkbox
																				checked={isSelected}
																				aria-label={$i18n.t('Select')}
																				onCheckedChange={() => toggleMatchEntry(txn.id)}
																			/>
																		</Table.Cell>
																	{/if}
																	<Table.Cell class="py-1.5">
																		<div class="flex flex-wrap gap-1">
																			{#if txn._amountMatch}
																				<Badge variant="success"
																					><CircleCheck />{$i18n.t('Amount')}</Badge
																				>
																			{/if}
																			{#if txn._nameScore > 0.3}
																				<Badge variant="outline">{$i18n.t('Name', { context: 'gnos3' })}</Badge>
																			{/if}
																			{#if txn.invoice_id}
																				<Badge variant="outline">{$i18n.t('Invoice')}</Badge>
																			{/if}
																		</div>
																	</Table.Cell>
																	<Table.Cell
																		class="py-1.5 font-mono text-[13px] text-muted-foreground"
																		>{txn.id}</Table.Cell
																	>
																	<Table.Cell class="py-1.5 tabular-nums"
																		>{txn.transaction_date ?? '—'}</Table.Cell
																	>
																	<Table.Cell class="py-1.5 text-muted-foreground"
																		>{txn.transaction_type ?? '—'}</Table.Cell
																	>
																	<Table.Cell
																		class="max-w-[12rem] truncate py-1.5 font-mono text-[13px]"
																		title={txn.reference ?? ''}>{txn.reference ?? '—'}</Table.Cell
																	>
																	<Table.Cell
																		class="max-w-[14rem] truncate py-1.5"
																		title={txn.description ?? ''}
																		>{txn.description ?? '—'}</Table.Cell
																	>
																	<Table.Cell class="py-1.5 text-right font-medium tabular-nums"
																		>{fmt(txn._totalAmount ?? txn.total ?? 0)}</Table.Cell
																	>
																	{#if !matchMultiSelect}
																		<Table.Cell class="py-1.5 text-right">
																			<Button
																				variant="outline"
																				size="xs"
																				onclick={() => handleMatchSelect(txn.id)}
																				>{$i18n.t('Select')}</Button
																			>
																		</Table.Cell>
																	{/if}
																</Table.Row>
															{/each}
														</Table.Body>
													</Table.Root>
												</div>
											{/if}
										</div>
									</Table.Cell>
								</Table.Row>
							{/if}
						{/each}
					</Table.Body>
				</Table.Root>
			</div>
		{/if}
	{:else}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><Landmark /></Empty.Media>
				<Empty.Title>{$i18n.t('No bank accounts. Create one to start reconciling.')}</Empty.Title>
			</Empty.Header>
			<Empty.Content>
				<Button
					size="sm"
					onclick={() => {
						showNewBank = true;
					}}><Plus />{$i18n.t('New Bank')}</Button
				>
			</Empty.Content>
		</Empty.Root>
	{/if}
</div>

<!-- Multi-BSL Match Modal -->
<Dialog.Root bind:open={showMultiMatchModal}>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-3xl [&>*]:min-w-0">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Match Multiple Bank Lines to Entry(s)')}</Dialog.Title>
			<Dialog.Description>
				{selectedBslIds.size}
				{$i18n.t('bank statement line(s)')} — {$i18n.t('Total')}:
				<span class="font-medium text-foreground tabular-nums">{fmt(selectedBslTotal)}</span>
			</Dialog.Description>
		</Dialog.Header>

		<!-- Allocation summary -->
		{#if multiMatchAllocations.size > 0}
			<div class="grid grid-cols-3 gap-3 rounded-md border bg-muted/50 px-4 py-3 text-sm">
				<div>
					<div class="text-muted-foreground">{$i18n.t('BSL Total')}</div>
					<div class="font-semibold tabular-nums">{fmt(selectedBslTotal)}</div>
				</div>
				<div>
					<div class="text-muted-foreground">{$i18n.t('Allocated')}</div>
					<div class="font-semibold tabular-nums">{fmt(multiMatchAllocTotal)}</div>
				</div>
				<div>
					<div class="text-muted-foreground">{$i18n.t('Remaining')}</div>
					<div class="flex items-center gap-1.5 font-semibold tabular-nums">
						{#if multiMatchRemaining < 0.01}
							<CircleCheck class="size-4 text-success" aria-hidden="true" />
						{:else}
							<TriangleAlert class="size-4 text-warning" aria-hidden="true" />
						{/if}
						{fmt(multiMatchRemaining)}
					</div>
				</div>
			</div>
		{/if}

		{#if multiMatchLoading}
			<div class="flex flex-col gap-2 rounded-md border p-3">
				{#each Array(5) as _}<Skeleton class="h-7 w-full" />{/each}
			</div>
		{:else if multiMatchInvoices.length === 0}
			<div class="rounded-md border border-dashed py-8 text-center text-sm text-muted-foreground">
				{$i18n.t('No posted entries found.')}
			</div>
		{:else}
			<div class="max-h-80 overflow-y-auto rounded-md border">
				<Table.Root>
					<Table.Header class="sticky top-0 z-10 bg-muted">
						<Table.Row class="hover:bg-transparent">
							<Table.Head class="w-8"><span class="sr-only">{$i18n.t('Select')}</span></Table.Head>
							<Table.Head>#</Table.Head>
							<Table.Head>{$i18n.t('Date')}</Table.Head>
							<Table.Head>{$i18n.t('Type')}</Table.Head>
							<Table.Head>{$i18n.t('Reference')}</Table.Head>
							<Table.Head>{$i18n.t('Description')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Amount')}</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each multiMatchInvoices as txn}
							{@const isSelected = multiMatchAllocations.has(txn.id)}
							<Table.Row data-state={isSelected ? 'selected' : undefined}>
								<Table.Cell>
									<Checkbox
										checked={isSelected}
										aria-label={$i18n.t('Select')}
										onCheckedChange={() => toggleMultiMatchEntry(txn)}
									/>
								</Table.Cell>
								<Table.Cell class="font-mono text-[13px] text-muted-foreground">{txn.id}</Table.Cell
								>
								<Table.Cell class="tabular-nums">{txn.transaction_date ?? '—'}</Table.Cell>
								<Table.Cell class="text-muted-foreground">{txn.transaction_type ?? '—'}</Table.Cell>
								<Table.Cell
									class="max-w-[10rem] truncate font-mono text-[13px]"
									title={txn.reference ?? ''}>{txn.reference ?? '—'}</Table.Cell
								>
								<Table.Cell class="max-w-[14rem] truncate" title={txn.description ?? ''}
									>{txn.description ?? '—'}</Table.Cell
								>
								<Table.Cell class="text-right font-medium tabular-nums"
									>{fmt(txn._totalAmount ?? 0)}</Table.Cell
								>
							</Table.Row>
						{/each}
					</Table.Body>
				</Table.Root>
			</div>
		{/if}

		<Dialog.Footer>
			<Button
				variant="outline"
				onclick={() => {
					showMultiMatchModal = false;
				}}>{$i18n.t('Cancel')}</Button
			>
			<Button
				disabled={multiMatchAllocations.size === 0 || multiMatchCreating}
				onclick={handleMultiMatchCreate}
			>
				{#if multiMatchCreating}
					<Spinner />{$i18n.t('Creating...')}
				{:else}
					{$i18n.t('Create Match Group')}
				{/if}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<ConfirmDialog
	bind:open={showUndoConfirm}
	title={$i18n.t('Undo this import?')}
	description={$i18n.t(
		'The {{count}} lines of this import are removed from the statement. Nothing else changes; you can import the file again.',
		{ count: undoTarget?.lines ?? 0 }
	)}
	confirmLabel={$i18n.t('Undo import')}
	destructive
	onconfirm={doUndoImport}
	oncancel={() => {
		undoTarget = null;
	}}
/>

<ConfirmDialog
	bind:open={showUnmatchConfirm}
	title={$i18n.t('Unmatch this line?')}
	description={$i18n.t(
		'This line has a recorded payment. Unmatching will keep the payment but break the reconciliation link. Continue?'
	)}
	confirmLabel={$i18n.t('Unmatch')}
	onconfirm={async () => {
		if (pendingUnmatchId !== null) await doUnmatch(pendingUnmatchId);
		pendingUnmatchId = null;
	}}
	oncancel={() => {
		pendingUnmatchId = null;
	}}
/>

<PaymentFormModal
	bind:show={showPaymentModal}
	{accounts}
	{companyId}
	prefill={paymentPrefill}
	on:save={handlePaymentSaved}
/>
