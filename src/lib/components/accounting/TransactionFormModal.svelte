<script lang="ts">
	import { getContext, createEventDispatcher, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';

	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';
	import Check from '@lucide/svelte/icons/check';
	import ChevronsUpDown from '@lucide/svelte/icons/chevrons-up-down';
	import Link2 from '@lucide/svelte/icons/link-2';
	import ExternalLink from '@lucide/svelte/icons/external-link';
	import Paperclip from '@lucide/svelte/icons/paperclip';
	import FileText from '@lucide/svelte/icons/file-text';
	import Sparkles from '@lucide/svelte/icons/sparkles';
	import Scale from '@lucide/svelte/icons/scale';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import BookmarkPlus from '@lucide/svelte/icons/bookmark-plus';
	import Trash2 from '@lucide/svelte/icons/trash-2';

	import {
		createTransaction,
		updateTransaction,
		getJournalTemplates,
		createTemplateFromTransaction,
		deleteJournalTemplate,
		uploadAttachment,
		getAccountingAiStatus,
		aiValidateTransaction,
		postTransaction,
		matchBankStatement,
		getTransactionInvoices,
		setTransactionInvoices,
		getCompany,
		convertCurrency
	} from '$lib/apis/accounting';
	import { INVOICE_API_BASE_URL } from '$lib/constants';
	import { fetchAsBlobUrl } from '$lib/utils/blobPreview';
	import K4miDocLink from '$lib/components/common/K4miDocLink.svelte';
	import InvoiceSelector from '$lib/components/accounting/InvoiceSelector.svelte';
	import AccountFormModal from '$lib/components/accounting/AccountFormModal.svelte';

	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Popover from '$lib/components/ui/popover/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;
	export let transaction: any = null;
	export let accounts: any[] = [];
	export let companyId: number;
	export let bankStatementLineId: number | null = null; // when set, shows "Direct Match" option

	// Determine read-only mode for posted/voided transactions
	$: readOnly = transaction && (transaction.status === 'posted' || transaction.status === 'voided');

	// Direct match: when creating from the Bank tab, auto-post + match to BSL
	let directMatch = false;
	$: if (bankStatementLineId) directMatch = true;

	// Form state
	let formData: {
		transaction_date: string;
		transaction_type: string;
		currency: string;
		exchange_rate: string; // '' = let the backend auto-fill from live rates
		reference: string;
		description: string;
		invoice_id: number | null;
	} = {
		transaction_date: '',
		transaction_type: 'others',
		currency: 'USD',
		exchange_rate: '',
		reference: '',
		description: '',
		invoice_id: null
	};

	// Company base currency + live-rate hint for the exchange-rate field.
	let baseCurrency = '';
	let rateHint = '';
	// Set when the booking engine left an exchange_rate gap on this draft.
	let rateGapNote = '';
	let rateMissing = false;
	let lastShow = false;

	const loadBaseCurrency = async () => {
		try {
			const c = await getCompany(companyId);
			baseCurrency = (c?.currency || 'USD').toUpperCase();
		} catch {
			if (!baseCurrency) baseCurrency = 'USD';
		}
	};

	// Resolve it as soon as the company is known, not just on open, so the form
	// never renders a foreign default while the lookup is still in flight.
	$: if (companyId) loadBaseCurrency();

	// Prefill the exchange rate from the resolved live rate (company override →
	// global → triangulate). The accountant can still override the value.
	const refreshRate = async () => {
		const cur = (formData.currency || '').toUpperCase();
		if (!cur || cur === baseCurrency) {
			// Back on the base currency: clear any rate left over from a foreign
			// one. The field is hidden here, so a stale value would be submitted
			// unseen and scale the entry through every report.
			formData.exchange_rate = '';
			rateHint = '';
			rateMissing = false;
			return;
		}
		try {
			const res = await convertCurrency({
				company_id: companyId,
				from_currency: cur,
				to_currency: baseCurrency,
				amount: 1,
				as_of: formData.transaction_date || undefined
			});
			if (res?.rate && res?.exact) {
				formData.exchange_rate = String(res.rate);
				rateMissing = false;
				// Rates publish once a business day, so the rate for an entry dated
				// over a weekend is Friday's — correct, but worth saying out loud so
				// the date on the entry and the date on the rate are not read as a
				// mismatch.
				rateHint =
					res.stale_days > 0
						? $i18n.t(
								'Auto-filled from the rate published {{date}} ({{days}} day(s) before this entry — the latest on or before it).',
								{ date: res.rate_date, days: res.stale_days }
							)
						: $i18n.t('Auto-filled from live rates ({{date}})', { date: res.rate_date });
			} else if (res?.rate) {
				// A rate exists, but the lookup had to reach further back than a
				// weekend for it. Showing it would book a number nobody chose, so
				// offer it as a reference and leave the field empty for the
				// accountant to confirm or replace.
				formData.exchange_rate = '';
				rateMissing = true;
				rateHint = $i18n.t(
					'No recent rate on file for this entry’s date. The nearest is {{rate}} from {{date}}, {{days}} days earlier — enter the rate to use, or fill the gap under Settings → Exchange Rates.',
					{ rate: res.rate, date: res.rate_date, days: res.stale_days }
				);
			}
		} catch {
			formData.exchange_rate = '';
			rateMissing = true;
			rateHint = $i18n.t(
				'No exchange rate available for {{pair}} — enter it below, or add it under Settings → Exchange Rates.',
				{ pair: `${cur} → ${baseCurrency}` }
			);
		}
	};

	// On each open: resolve the company's currency FIRST, default a new entry to
	// it, then prefill the rate. A hardcoded default (it used to be 'USD') means
	// every entry in a non-USD company opens on a foreign currency and auto-fills
	// a conversion rate nobody asked for.
	$: if (show !== lastShow) {
		lastShow = show;
		if (show) {
			loadBaseCurrency().then(() => {
				if (!transaction) formData.currency = baseCurrency;
				refreshRate();
			});
		}
	}

	let invoiceLabel = '';
	let invoiceK4miDocId: number | null = null;
	let showInvoiceSelector = false;

	// Additional linked invoices (beyond the primary) — persisted via the junction.
	let extraInvoices: any[] = [];
	let showExtraInvoiceSelector = false;

	// Journal templates
	let journalTemplates: any[] = [];
	let selectedTemplateId: number | null = null;
	let savingTemplate = false;
	let showDeleteTemplateConfirm = false;
	let templateNameOpen = false;
	let templateName = '';

	async function loadTemplates() {
		try {
			const res = await getJournalTemplates(companyId);
			journalTemplates = Array.isArray(res) ? res : [];
		} catch {
			journalTemplates = [];
		}
	}

	function applyTemplate(templateId: number) {
		const tpl = journalTemplates.find((t: any) => t.id === templateId);
		if (!tpl) return;
		formData.transaction_type = tpl.transaction_type || 'journal';
		formData.currency = tpl.currency || baseCurrency || 'USD';
		formData.reference = tpl.reference_prefix || '';
		formData.description = tpl.description || '';
		lines = (tpl.lines_template || []).map((l: any) => {
			const acct = accounts.find((a: any) => a.code === l.account_code);
			return {
				account_id: acct?.id ?? null,
				debit: parseFloat(l.debit) || null,
				credit: parseFloat(l.credit) || null,
				description: l.description || ''
			};
		});
		if (lines.length < 2) {
			while (lines.length < 2)
				lines.push({ account_id: null, debit: null, credit: null, description: '' });
		}
		// Keep selectedTemplateId so the user can delete the chosen template.
	}

	// Asked for confirmation first (ConfirmDialog below).
	async function handleDeleteTemplate() {
		if (!selectedTemplateId) return;
		try {
			await deleteJournalTemplate(selectedTemplateId);
			toast.success($i18n.t('Template deleted'));
			selectedTemplateId = null;
			await loadTemplates();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	}

	// The template name comes from the popover next to "Save as Template".
	async function saveAsTemplate() {
		if (!transaction?.id) return;
		const name = templateName.trim();
		if (!name) return;
		savingTemplate = true;
		try {
			await createTemplateFromTransaction(transaction.id, name);
			toast.success($i18n.t('Template saved'));
			templateNameOpen = false;
			templateName = '';
			await loadTemplates();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		savingTemplate = false;
	}

	// Attachments
	let attachmentUrls: string[] = [];
	let uploading = false;
	let attachmentInput: HTMLInputElement;

	async function handleAttachmentUpload() {
		if (!attachmentInput?.files?.length) return;
		uploading = true;
		try {
			for (const file of attachmentInput.files) {
				const result = await uploadAttachment(file);
				attachmentUrls = [...attachmentUrls, result.url];
			}
			attachmentInput.value = '';
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		uploading = false;
	}

	function removeAttachment(index: number) {
		attachmentUrls = attachmentUrls.filter((_, i) => i !== index);
	}

	// Attachment endpoints require Bearer auth, so we can't drop the URL into
	// <a href> — fetch with the right header and open the response as a blob.
	async function openAttachment(relativeUrl: string) {
		const token = typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null;
		if (!token) {
			toast.error($i18n.t('Not authenticated'));
			return;
		}
		const result = await fetchAsBlobUrl(`${INVOICE_API_BASE_URL}${relativeUrl}`, token);
		if (!result) {
			toast.error($i18n.t('Could not open attachment'));
			return;
		}
		window.open(result.url, '_blank', 'noopener,noreferrer');
		// Revoke once the new tab has loaded the bytes into its own context.
		setTimeout(() => URL.revokeObjectURL(result.url), 60_000);
	}

	// `gap` marks a line the booking engine could not resolve (display only, never sent).
	let lines: Array<{
		account_id: number | null;
		debit: number | null;
		credit: number | null;
		description: string;
		gap?: string;
		gapNote?: string;
	}> = [];

	let saving = false;

	// Account picker per line (a combobox: search + list in a popover)
	let accountSearchIdx: number | null = null; // which line's picker is open
	let accountSearchQuery = '';

	const openAccountSearch = (idx: number) => {
		accountSearchIdx = idx;
		accountSearchQuery = '';
	};

	const selectAccount = (idx: number, accountId: number) => {
		lines[idx].account_id = accountId;
		lines = lines;
		accountSearchIdx = null;
		accountSearchQuery = '';
	};

	const findAccount = (accountId: number | null) =>
		accountId ? accounts.find((a: any) => a.id === accountId) : null;

	$: filteredAccounts = accounts.filter((a: any) => {
		if (!accountSearchQuery) return true;
		const q = accountSearchQuery.toLowerCase();
		return (a.code ?? '').toLowerCase().includes(q) || (a.name ?? '').toLowerCase().includes(q);
	});

	// Inline account creation
	let showCreateAccount = false;
	let createAccountForLineIdx: number | null = null;

	const openCreateAccount = (idx: number) => {
		createAccountForLineIdx = idx;
		accountSearchIdx = null;
		showCreateAccount = true;
	};

	const handleAccountCreated = (e: CustomEvent) => {
		const newAccount = e.detail;
		if (newAccount?.id) {
			// Add to local accounts list and select it
			accounts = [...accounts, newAccount];
			if (createAccountForLineIdx !== null) {
				lines[createAccountForLineIdx].account_id = newAccount.id;
				lines = lines;
			}
		}
		showCreateAccount = false;
		createAccountForLineIdx = null;
	};

	// Reset form when modal opens or transaction changes
	$: if (show) {
		resetForm();
		loadTemplates();
	}

	function resetForm() {
		templateNameOpen = false;
		templateName = '';
		validationResult = null;
		if (transaction) {
			formData = {
				transaction_date: transaction.transaction_date?.slice(0, 10) ?? '',
				transaction_type: transaction.transaction_type ?? 'journal',
				currency: transaction.currency ?? baseCurrency ?? 'USD',
				exchange_rate: transaction.exchange_rate != null ? String(transaction.exchange_rate) : '',
				reference: transaction.reference ?? '',
				description: transaction.description ?? '',
				invoice_id: transaction.invoice_id ?? null
			};
			invoiceLabel = transaction.invoice_id ? `#${transaction.invoice_id}` : '';
			// Load additional (non-primary) linked invoices from the junction.
			extraInvoices = [];
			if (transaction.id) {
				getTransactionInvoices(transaction.id)
					.then((refs) => (extraInvoices = refs.filter((r: any) => !r.is_primary)))
					.catch(() => {});
			}
			attachmentUrls = transaction.attachment_urls ?? [];
			lines =
				transaction.lines?.map((l: any) => ({
					account_id: l.account_id ?? null,
					debit: parseFloat(String(l.debit ?? l.debit_amount ?? 0)) || null,
					credit: parseFloat(String(l.credit ?? l.credit_amount ?? 0)) || null,
					description: l.description ?? ''
				})) ?? [];
			// Lines the booking engine could not resolve: shown as lines awaiting an
			// account. Saving with every account chosen clears the gaps server-side.
			rateGapNote = '';
			for (const g of transaction.booking_gaps ?? []) {
				if (g.role === 'exchange_rate') {
					// Not a line: the entry needs a rate, not an account.
					rateGapNote = g.note ?? '';
					continue;
				}
				const amt = parseFloat(String(g.amount ?? 0)) || null;
				lines = [
					...lines,
					{
						account_id: null,
						debit: g.side === 'debit' ? amt : null,
						credit: g.side === 'credit' ? amt : null,
						description: g.description ?? g.label ?? '',
						gap: g.label ?? g.role ?? '',
						gapNote: g.note ?? ''
					}
				];
			}
		} else {
			formData = {
				transaction_date: new Date().toISOString().slice(0, 10),
				transaction_type: 'others',
				currency: baseCurrency || 'USD',
				exchange_rate: '',
				reference: '',
				description: '',
				invoice_id: null
			};
			invoiceLabel = '';
			extraInvoices = [];
			attachmentUrls = [];
			rateGapNote = '';
			lines = [
				{ account_id: null, debit: null, credit: null, description: '' },
				{ account_id: null, debit: null, credit: null, description: '' }
			];
		}
	}

	function handleExtraInvoiceSelect(event: CustomEvent) {
		const invoice = event.detail;
		if (!invoice?.id) return;
		if (invoice.id === formData.invoice_id) {
			toast.info($i18n.t('Already the primary linked invoice'));
			return;
		}
		if (extraInvoices.some((e) => e.invoice_id === invoice.id)) return;
		extraInvoices = [
			...extraInvoices,
			{
				invoice_id: invoice.id,
				invoice_number: invoice.invoice_number,
				vendor_or_client: invoice.client_name || invoice.vendor_name,
				total_amount: invoice.total_amount,
				k4mi_document_id: invoice.k4mi_document_id ?? null
			}
		];
	}

	function removeExtraInvoice(invoiceId: number) {
		extraInvoices = extraInvoices.filter((e) => e.invoice_id !== invoiceId);
	}

	function handleInvoiceSelect(event: CustomEvent) {
		const invoice = event.detail;
		formData.invoice_id = invoice.id;
		invoiceLabel = invoice.invoice_number
			? `${invoice.invoice_number} — ${invoice.vendor_name ?? ''}`
			: `#${invoice.id} — ${invoice.vendor_name ?? ''}`;
		invoiceK4miDocId = invoice.k4mi_document_id ?? null;
		// Auto-fill from invoice if creating new
		if (!transaction?.id) {
			if (invoice.invoice_date) formData.transaction_date = invoice.invoice_date.slice(0, 10);
			if (invoice.currency) formData.currency = invoice.currency;
			if (invoice.invoice_number) formData.reference = invoice.invoice_number;
			if (invoice.vendor_name) formData.description = `Invoice from ${invoice.vendor_name}`;
			if (invoice.total_amount) {
				const amount = parseFloat(String(invoice.total_amount));
				if (amount > 0 && lines.length >= 2) {
					lines[0].debit = amount;
					lines[0].credit = null;
					lines[1].debit = null;
					lines[1].credit = amount;
					lines = lines;
				}
			}
			// Pre-select AI-suggested or confirmed expense account
			const suggestedCode = invoice.final_account_code || invoice.suggested_account_code;
			if (suggestedCode && accounts.length > 0 && lines.length >= 1) {
				const acct = accounts.find((a: any) => a.code === suggestedCode);
				if (acct) {
					lines[0].account_id = acct.id;
					lines[0].description = `${invoice.vendor_name ?? 'Expense'} — AI: ${acct.code} ${acct.name}`;
					lines = lines;
				}
			}
		}
	}

	function clearInvoice() {
		formData.invoice_id = null;
		invoiceLabel = '';
	}

	// Running balance
	$: totalDebit = lines.reduce((sum, l) => sum + (l.debit ?? 0), 0);
	$: totalCredit = lines.reduce((sum, l) => sum + (l.credit ?? 0), 0);
	$: balanceDiff = Math.round((totalDebit - totalCredit) * 100) / 100;
	$: isBalanced = balanceDiff === 0;
	$: allAccountsSet = lines.every((l) => l.account_id !== null && l.account_id !== undefined);
	$: canSubmit = !readOnly && !saving && isBalanced && lines.length >= 2 && allAccountsSet;

	// Display only: gap lines still waiting for an account, lines without one, the base amount.
	$: openGapCount = lines.filter((l) => l.gap && !l.account_id).length;
	$: missingAccountCount = lines.filter(
		(l) => l.account_id === null || l.account_id === undefined
	).length;
	$: entryCurrency = (formData.currency || '').toUpperCase();
	$: isForeign = !!entryCurrency && !!baseCurrency && entryCurrency !== baseCurrency;
	$: rateNumber = Number(formData.exchange_rate) || 0;

	const fmt = (n: number) =>
		n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

	function addLine() {
		lines = [...lines, { account_id: null, debit: null, credit: null, description: '' }];
	}

	function removeLine(index: number) {
		lines = lines.filter((_, i) => i !== index);
	}

	// AI validation
	let aiAvailable = false;
	let validating = false;
	let validationResult: {
		is_valid: boolean;
		issues: string[];
		warnings: string[];
		suggestions: string[];
	} | null = null;

	// Check AI status on mount
	onMount(() => {
		getAccountingAiStatus()
			.then((s) => (aiAvailable = s.available))
			.catch(() => {});
	});

	async function handleValidate() {
		if (!transaction?.id) {
			toast.info('Save the entry first to validate');
			return;
		}
		validating = true;
		try {
			validationResult = await aiValidateTransaction(transaction.id);
			if (validationResult?.is_valid) {
				toast.success('Entry looks good!');
			} else {
				toast.warning(`Found ${validationResult?.issues.length ?? 0} issue(s)`);
			}
		} catch {
			toast.error('AI validation failed');
		} finally {
			validating = false;
		}
	}

	async function handleSubmit() {
		if (!canSubmit) return;
		saving = true;

		const payload: Record<string, any> = {
			...formData,
			attachment_urls: attachmentUrls.length > 0 ? attachmentUrls : undefined,
			lines: lines.map((l) => ({
				account_id: l.account_id,
				debit: l.debit ?? 0,
				credit: l.credit ?? 0,
				description: l.description
			}))
		};

		// Only include invoice_id if set
		if (!formData.invoice_id) {
			delete payload.invoice_id;
		}

		// exchange_rate: empty = let the backend auto-fill from the live rate table.
		if (payload.exchange_rate === '' || payload.exchange_rate == null) {
			delete payload.exchange_rate;
		} else {
			payload.exchange_rate = Number(payload.exchange_rate);
		}

		try {
			let result;
			let savedTxnId: number | null = null;
			if (transaction?.id) {
				result = await updateTransaction(transaction.id, payload);
				savedTxnId = transaction.id;
				toast.success($i18n.t('Transaction updated'));
			} else {
				result = await createTransaction(payload, companyId);
				const txnId = result?.id ?? result?.transaction?.id;
				savedTxnId = txnId ?? null;

				// Direct match: post the entry and match it to the BSL
				if (directMatch && bankStatementLineId && txnId) {
					await postTransaction(txnId);
					await matchBankStatement(bankStatementLineId, txnId);
					toast.success($i18n.t('Entry created, posted, and matched'));
				} else {
					toast.success($i18n.t('Transaction created'));
				}
			}

			// Persist additional invoice links (junction). Non-fatal on failure.
			if (savedTxnId) {
				try {
					await setTransactionInvoices(
						savedTxnId,
						extraInvoices.map((e) => e.invoice_id)
					);
				} catch (e) {
					toast.error($i18n.t('Entry saved, but linking extra invoices failed'));
				}
			}
			dispatch('save', result);
			show = false;
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Error') + ': ' + msg);
		} finally {
			saving = false;
		}
	}
</script>

<!-- The account picker of one journal line: a combobox (search + list) in a popover -->
{#snippet accountPicker(idx: number, line: any)}
	{@const acct = findAccount(line.account_id)}
	{@const isGap = !!line.gap && !line.account_id}
	<Popover.Root
		open={accountSearchIdx === idx}
		onOpenChange={(o) => {
			if (o) openAccountSearch(idx);
			else if (accountSearchIdx === idx) accountSearchIdx = null;
		}}
	>
		<Popover.Trigger>
			{#snippet child({ props })}
				<button
					{...props}
					type="button"
					class="flex h-8 w-full min-w-0 items-center justify-between gap-2 rounded-md border border-input bg-transparent px-2.5 text-left text-sm shadow-xs transition-colors outline-none hover:bg-accent/50 focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 aria-invalid:border-destructive aria-invalid:ring-[3px] aria-invalid:ring-destructive/20 dark:bg-input/30"
					aria-invalid={isGap ? 'true' : undefined}
				>
					{#if acct}
						<span class="min-w-0 truncate">
							<span class="font-mono text-[13px]">{acct.code}</span>
							{acct.name}
						</span>
					{:else if line.account_id}
						<span class="truncate font-mono text-[13px]">#{line.account_id}</span>
					{:else}
						<span class="truncate text-muted-foreground">-- {$i18n.t('Select account')} --</span>
					{/if}
					<ChevronsUpDown class="size-4 shrink-0 opacity-50" />
				</button>
			{/snippet}
		</Popover.Trigger>
		<Popover.Content align="start" class="w-[min(24rem,calc(100vw-2rem))] gap-0 p-0">
			<div class="border-b p-2">
				<Input
					class="h-8"
					placeholder={$i18n.t('Search accounts...')}
					aria-label={$i18n.t('Search accounts...')}
					bind:value={accountSearchQuery}
					onkeydown={(e: KeyboardEvent) => {
						if (e.key === 'Enter') {
							e.preventDefault();
							const first = filteredAccounts[0];
							if (first) selectAccount(idx, first.id);
						}
					}}
				/>
			</div>
			<div class="max-h-64 overflow-y-auto p-1">
				{#each filteredAccounts.slice(0, 30) as account (account.id)}
					<button
						type="button"
						class="flex w-full items-baseline gap-2 rounded-sm px-2 py-1.5 text-left text-sm outline-none hover:bg-accent focus-visible:bg-accent"
						onclick={() => selectAccount(idx, account.id)}
					>
						<span class="font-mono text-[13px]">{account.code}</span>
						<span class="min-w-0 flex-1 truncate text-muted-foreground">{account.name}</span>
						{#if account.id === line.account_id}<Check class="size-4 self-center" />{/if}
					</button>
				{/each}
				{#if filteredAccounts.length === 0}
					<p class="px-2 py-3 text-center text-sm text-muted-foreground">
						{$i18n.t('No accounts found')}
					</p>
				{/if}
			</div>
			<div class="border-t p-1">
				<button
					type="button"
					class="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-left text-sm text-link outline-none hover:bg-accent focus-visible:bg-accent"
					onclick={() => openCreateAccount(idx)}
				>
					<Plus class="size-4" />{$i18n.t('Create new account')}
				</button>
			</div>
		</Popover.Content>
	</Popover.Root>
	{#if isGap}
		<p class="mt-1 text-xs whitespace-normal text-destructive">
			{$i18n.t(line.gap)} · {$i18n.t('account required')}
		</p>
		{#if line.gapNote}
			<p class="mt-0.5 text-xs whitespace-normal text-muted-foreground">{line.gapNote}</p>
		{/if}
	{/if}
{/snippet}

<Dialog.Root bind:open={show}>
	<Dialog.Content class="max-h-[90vh] gap-5 overflow-y-auto sm:max-w-3xl">
		<!-- Header: title, status, what the entry is -->
		<Dialog.Header>
			<div class="flex flex-wrap items-center gap-2 pr-8">
				<Dialog.Title>
					{#if readOnly}
						{$i18n.t('View Transaction')}
					{:else if transaction?.id}
						{$i18n.t('Edit Transaction')}
					{:else}
						{$i18n.t('New Transaction')}
					{/if}
				</Dialog.Title>
				{#if transaction?.status}
					<StatusBadge kind="entry" status={transaction.status} />
				{/if}
				{#if openGapCount > 0}
					<StatusBadge
						kind="entry"
						status="incomplete"
						label="{$i18n.t('Incomplete')} · {$i18n.t('{{n}} line(s)', { n: openGapCount })}"
					/>
				{/if}
			</div>
			<Dialog.Description>
				{#if transaction?.id}
					<span class="font-mono text-[13px]">#{transaction.id}</span>
					{#if transaction.reference}
						· <span class="font-mono text-[13px]">{transaction.reference}</span>
					{/if}
					{#if transaction.invoice_id}
						· {$i18n.t('Invoice')} #{transaction.invoice_id}
					{/if}
				{:else}
					{$i18n.t('Debits must equal credits, and every line needs an account.')}
				{/if}
			</Dialog.Description>
		</Dialog.Header>

		<!-- Template selector (only when creating new) -->
		{#if !transaction?.id && journalTemplates.length > 0}
			<div class="flex flex-wrap items-center gap-2">
				<Label for="je-template" class="whitespace-nowrap">{$i18n.t('From Template')}</Label>
				<NativeSelect.Root
					id="je-template"
					size="sm"
					class="min-w-48 flex-1"
					bind:value={selectedTemplateId}
					onchange={() => {
						if (selectedTemplateId) applyTemplate(selectedTemplateId);
					}}
				>
					<NativeSelect.Option value={null}>{$i18n.t('Select a template...')}</NativeSelect.Option>
					{#each journalTemplates as tpl}
						<NativeSelect.Option value={tpl.id}>{tpl.name}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
				{#if selectedTemplateId}
					<Tip content={$i18n.t('Delete template')}>
						<Button
							variant="ghost"
							size="icon-sm"
							class="text-destructive hover:text-destructive"
							aria-label={$i18n.t('Delete template')}
							onclick={() => (showDeleteTemplateConfirm = true)}
						>
							<Trash2 />
						</Button>
					</Tip>
				{/if}
			</div>
		{/if}

		<!-- Fields: Date · Type · Currency · Reference; the exchange rate (foreign currency only)
		     takes the start of the next row, dense flow keeps Reference on the first -->
		<div class="grid grid-flow-row-dense grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-4">
			<div class="grid content-start gap-2">
				<Label for="je-date">{$i18n.t('Date')}</Label>
				<Input
					id="je-date"
					type="date"
					class="tabular-nums"
					bind:value={formData.transaction_date}
					onchange={refreshRate}
					disabled={readOnly}
				/>
			</div>

			<div class="grid content-start gap-2">
				<Label for="je-type">{$i18n.t('Type')}</Label>
				<NativeSelect.Root
					id="je-type"
					class="w-full"
					bind:value={formData.transaction_type}
					disabled={readOnly}
				>
					<NativeSelect.Option value="invoice">{$i18n.t('Invoice')}</NativeSelect.Option>
					<NativeSelect.Option value="bill">{$i18n.t('Bill')}</NativeSelect.Option>
					<NativeSelect.Option value="payment_in">{$i18n.t('Payment In')}</NativeSelect.Option>
					<NativeSelect.Option value="payment_out">{$i18n.t('Payment Out')}</NativeSelect.Option>
					<NativeSelect.Option value="others">{$i18n.t('Others')}</NativeSelect.Option>
					<NativeSelect.Option value="adjustment">{$i18n.t('Adjustment')}</NativeSelect.Option>
				</NativeSelect.Root>
			</div>

			<div class="grid content-start gap-2">
				<Label for="je-currency">{$i18n.t('Currency')}</Label>
				<Input
					id="je-currency"
					type="text"
					class="font-mono uppercase"
					bind:value={formData.currency}
					oninput={refreshRate}
					maxlength={3}
					placeholder="USD"
					disabled={readOnly}
				/>
			</div>

			<!-- Exchange rate (auto-filled from live rates; overridable) -->
			{#if (formData.currency || '').toUpperCase() !== baseCurrency}
				<div class="grid content-start gap-2 sm:col-span-2">
					<Label for="je-rate">
						{$i18n.t('Exchange Rate')}
						<span class="font-normal text-muted-foreground"
							>{(formData.currency || '').toUpperCase()} → {baseCurrency}</span
						>
					</Label>
					<Input
						id="je-rate"
						type="number"
						step="0.00000001"
						min="0"
						class="text-right tabular-nums"
						bind:value={formData.exchange_rate}
						placeholder="1.0"
						disabled={readOnly}
					/>
					{#if rateHint}
						<p class="flex gap-1.5 text-[13px] leading-[18px] text-muted-foreground">
							{#if rateMissing}
								<TriangleAlert class="mt-0.5 size-3.5 shrink-0 text-warning" />
							{/if}
							<span>{rateHint}</span>
						</p>
					{/if}
				</div>
			{/if}

			<div class="grid content-start gap-2">
				<Label for="je-reference">{$i18n.t('Reference')}</Label>
				<Input
					id="je-reference"
					type="text"
					class="font-mono placeholder:font-sans"
					bind:value={formData.reference}
					placeholder={$i18n.t('Reference number')}
					disabled={readOnly}
				/>
			</div>

			<div class="col-span-full grid gap-2">
				<Label for="je-description">{$i18n.t('Description')}</Label>
				<Textarea
					id="je-description"
					class="min-h-16 resize-none"
					rows={2}
					bind:value={formData.description}
					placeholder={$i18n.t('Transaction description')}
					disabled={readOnly}
				/>
			</div>
		</div>

		<!-- A missing exchange rate is a notice on the entry, not a line -->
		{#if rateGapNote}
			<Alert.Root variant="warning">
				<TriangleAlert />
				<Alert.Title>{$i18n.t('No exchange rate for this entry')}</Alert.Title>
				<Alert.Description>{rateGapNote}</Alert.Description>
			</Alert.Root>
		{/if}

		<!-- Linked invoices -->
		<div class="grid gap-2 text-sm">
			<div class="flex flex-wrap items-center gap-x-2 gap-y-1">
				<Link2 class="size-4 text-muted-foreground" />
				<span class="text-muted-foreground">
					{$i18n.t('Linked Invoice')}
					<span class="sr-only">({$i18n.t('optional')})</span>
				</span>
				{#if invoiceLabel}
					<span class="font-medium">{invoiceLabel}</span>
					{#if invoiceK4miDocId}
						<K4miDocLink
							docId={invoiceK4miDocId}
							extraClass="inline-flex text-link"
							title={$i18n.t('Open in K4mi')}
						>
							<ExternalLink class="size-3.5" />
							<span class="sr-only">{$i18n.t('Open in K4mi')}</span>
						</K4miDocLink>
					{/if}
					{#if !readOnly}
						<Button
							variant="ghost"
							size="xs"
							class="text-muted-foreground hover:text-destructive"
							onclick={clearInvoice}
						>
							{$i18n.t('Remove')}
						</Button>
					{/if}
				{:else}
					<span class="text-muted-foreground">{$i18n.t('No invoice linked')}</span>
				{/if}
				{#if !readOnly}
					<Separator orientation="vertical" class="mx-1 h-4!" />
					<Button variant="link" size="sm" onclick={() => (showInvoiceSelector = true)}>
						{$i18n.t('Browse Invoices')}
					</Button>
				{/if}
			</div>

			<!-- Additional related invoices (multi-link) -->
			<div class="flex flex-wrap items-center gap-x-2 gap-y-1 pl-6">
				<span class="text-muted-foreground">{$i18n.t('Related invoices')}</span>
				{#each extraInvoices as ei}
					<Badge variant="outline" class="gap-1 font-mono text-[12px]">
						{#if ei.k4mi_document_id}
							<K4miDocLink
								docId={ei.k4mi_document_id}
								extraClass="text-link underline-offset-4 hover:underline"
								title={$i18n.t('Open in K4mi')}
								>{ei.invoice_number ?? `#${ei.invoice_id}`}</K4miDocLink
							>
						{:else}
							{ei.invoice_number ?? `#${ei.invoice_id}`}
						{/if}
						{#if !readOnly}
							<button
								type="button"
								class="-mr-0.5 rounded-sm text-muted-foreground outline-none hover:text-destructive focus-visible:ring-[3px] focus-visible:ring-ring/50"
								aria-label={$i18n.t('Remove')}
								title={$i18n.t('Remove')}
								onclick={() => removeExtraInvoice(ei.invoice_id)}
							>
								<X class="size-3" />
							</button>
						{/if}
					</Badge>
				{:else}
					<span class="text-muted-foreground">{$i18n.t('None')}</span>
				{/each}
				{#if !readOnly}
					<Button variant="ghost" size="xs" onclick={() => (showExtraInvoiceSelector = true)}>
						<Plus />{$i18n.t('Add invoice')}
					</Button>
				{/if}
			</div>
		</div>

		<!-- Journal lines -->
		<div class="grid gap-2">
			<div class="flex items-center justify-between">
				<h3 class="text-sm font-medium">{$i18n.t('Journal Lines')}</h3>
				{#if !readOnly}
					<Button variant="ghost" size="sm" onclick={addLine}>
						<Plus />{$i18n.t('Add Line')}
					</Button>
				{/if}
			</div>

			<div class="overflow-hidden rounded-md border">
				<Table.Root>
					<Table.Header class="bg-muted/50">
						<Table.Row class="hover:bg-transparent">
							<Table.Head class="min-w-[16rem]">{$i18n.t('Account', { context: 'gnos3' })}</Table.Head>
							<Table.Head class="w-32 text-right">{$i18n.t('Debit')}</Table.Head>
							<Table.Head class="w-32 text-right">{$i18n.t('Credit')}</Table.Head>
							<Table.Head class="min-w-[10rem]">{$i18n.t('Description')}</Table.Head>
							{#if !readOnly}
								<Table.Head class="w-10"
									><span class="sr-only">{$i18n.t('Remove')}</span></Table.Head
								>
							{/if}
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each lines as line, idx}
							{#if readOnly}
								{@const acct = findAccount(line.account_id)}
								<Table.Row class="hover:bg-transparent">
									<Table.Cell>
										{#if acct}
											<span class="font-mono text-[13px]">{acct.code}</span>
											{acct.name}
										{:else if line.account_id}
											<span class="font-mono text-[13px]">#{line.account_id}</span>
										{:else}
											<span class="text-muted-foreground">—</span>
										{/if}
									</Table.Cell>
									<Table.Cell class="text-right tabular-nums">
										{line.debit ? fmt(line.debit) : '—'}
									</Table.Cell>
									<Table.Cell class="text-right tabular-nums">
										{line.credit ? fmt(line.credit) : '—'}
									</Table.Cell>
									<Table.Cell class="whitespace-normal">{line.description || '—'}</Table.Cell>
								</Table.Row>
							{:else}
								<Table.Row
									class="align-top hover:bg-transparent {line.gap && !line.account_id
										? 'bg-warning/5 hover:bg-warning/5'
										: ''}"
								>
									<Table.Cell class="min-w-[16rem] align-top">
										{@render accountPicker(idx, line)}
									</Table.Cell>
									<Table.Cell class="align-top">
										<Input
											type="number"
											step="0.01"
											min="0"
											class="h-8 min-w-24 text-right tabular-nums"
											aria-label={$i18n.t('Debit')}
											bind:value={line.debit}
											placeholder="0.00"
										/>
									</Table.Cell>
									<Table.Cell class="align-top">
										<Input
											type="number"
											step="0.01"
											min="0"
											class="h-8 min-w-24 text-right tabular-nums"
											aria-label={$i18n.t('Credit')}
											bind:value={line.credit}
											placeholder="0.00"
										/>
									</Table.Cell>
									<Table.Cell class="align-top">
										<Input
											type="text"
											class="h-8 min-w-[10rem]"
											aria-label={$i18n.t('Description')}
											bind:value={line.description}
											placeholder={$i18n.t('Line memo')}
										/>
									</Table.Cell>
									<Table.Cell class="align-top">
										<Tip content={$i18n.t('Remove line')} disabled={lines.length <= 2}>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label={$i18n.t('Remove line')}
												disabled={lines.length <= 2}
												onclick={() => removeLine(idx)}
											>
												<X />
											</Button>
										</Tip>
									</Table.Cell>
								</Table.Row>
							{/if}
						{/each}
					</Table.Body>
					<Table.Footer>
						<Table.Row class="hover:bg-transparent">
							<Table.Cell>{$i18n.t('Totals')}</Table.Cell>
							<Table.Cell class="text-right tabular-nums">{fmt(totalDebit)}</Table.Cell>
							<Table.Cell class="text-right tabular-nums">{fmt(totalCredit)}</Table.Cell>
							<Table.Cell colspan={readOnly ? 1 : 2}>
								{#if isBalanced}
									<Badge variant="status"><Scale class="text-success" />{$i18n.t('Balanced')}</Badge
									>
								{:else}
									<StatusBadge
										kind="entry"
										status="unbalanced"
										label="{$i18n.t('Unbalanced')} ({balanceDiff > 0 ? '+' : ''}{fmt(balanceDiff)})"
									/>
								{/if}
							</Table.Cell>
						</Table.Row>
					</Table.Footer>
				</Table.Root>
			</div>
		</div>

		<!-- Gap lines: the user fixes them right here, on the highlighted lines -->
		{#if !readOnly && openGapCount > 0}
			<Alert.Root variant="warning">
				<TriangleAlert />
				<Alert.Title>
					{$i18n.t('{{n}} line(s) still need an account', { n: openGapCount })}
				</Alert.Title>
				<Alert.Description>
					{$i18n.t(
						'Nothing is guessed: choose the account on each highlighted line, or map a default in Settings → Booking Defaults. The entry can be saved once every line has an account.'
					)}
				</Alert.Description>
			</Alert.Root>
		{/if}

		<!-- Attachments -->
		<div class="grid gap-2">
			<div class="flex items-center justify-between">
				<h3 class="text-sm font-medium">{$i18n.t('Attachments')}</h3>
				{#if !readOnly}
					<input
						bind:this={attachmentInput}
						type="file"
						multiple
						class="hidden"
						onchange={handleAttachmentUpload}
					/>
					<Button
						variant="ghost"
						size="sm"
						disabled={uploading}
						onclick={() => attachmentInput?.click()}
					>
						{#if uploading}
							<Spinner />{$i18n.t('Uploading...')}
						{:else}
							<Paperclip />{$i18n.t('Attach File')}
						{/if}
					</Button>
				{/if}
			</div>
			{#if attachmentUrls.length > 0}
				<ul class="grid gap-1">
					{#each attachmentUrls as url, i}
						<li class="flex items-center gap-2 rounded-md border px-3 py-1.5 text-sm">
							<FileText class="size-4 shrink-0 text-muted-foreground" />
							<button
								type="button"
								class="min-w-0 flex-1 truncate rounded-sm text-left text-link underline-offset-4 outline-none hover:underline focus-visible:ring-[3px] focus-visible:ring-ring/50"
								onclick={() => openAttachment(url)}
							>
								{url.split('/').pop()}
							</button>
							{#if !readOnly}
								<Tip content={$i18n.t('Remove')}>
									<Button
										variant="ghost"
										size="icon-xs"
										aria-label={$i18n.t('Remove')}
										onclick={() => removeAttachment(i)}
									>
										<X />
									</Button>
								</Tip>
							{/if}
						</li>
					{/each}
				</ul>
			{:else}
				<p class="text-sm text-muted-foreground">{$i18n.t('No attachments')}</p>
			{/if}
		</div>

		<!-- AI validation results -->
		{#if validationResult}
			<Alert.Root variant={validationResult.is_valid ? 'default' : 'destructive'}>
				{#if validationResult.is_valid}
					<CircleCheck class="text-success!" />
				{:else}
					<CircleAlert />
				{/if}
				<Alert.Title>
					{validationResult.is_valid ? $i18n.t('Entry is valid') : $i18n.t('Issues found')}
				</Alert.Title>
				<Alert.Description>
					<ul class="grid list-disc gap-0.5 pl-4">
						{#each validationResult.issues as issue}
							<li>{issue}</li>
						{/each}
						{#each validationResult.warnings as warning}
							<li class="text-muted-foreground">{$i18n.t(warning)}</li>
						{/each}
						{#each validationResult.suggestions as suggestion}
							<li class="text-muted-foreground">{suggestion}</li>
						{/each}
					</ul>
				</Alert.Description>
			</Alert.Root>
		{/if}

		<!-- What the primary button will book -->
		{#if !readOnly}
			<div class="grid gap-1.5 rounded-md border bg-muted/40 px-3 py-2.5 text-sm">
				<span class="text-[13px] font-medium">{$i18n.t('This will book:')}</span>
				{#if isBalanced && lines.length >= 2 && allAccountsSet}
					<p>
						{transaction?.id ? $i18n.t('The draft entry, updated:') : $i18n.t('A draft entry:')}
						{$i18n.t('{{n}} lines', { n: lines.length })} ·
						<span class="tabular-nums">{entryCurrency} {fmt(totalDebit)}</span>
						{$i18n.t('debit = credit')}
						{#if isForeign && rateNumber > 0}
							· <span class="tabular-nums">{baseCurrency} {fmt(totalDebit * rateNumber)}</span>
							{$i18n.t('at')} <span class="tabular-nums">{formData.exchange_rate}</span>
						{/if}
					</p>
					{#if directMatch && bankStatementLineId && !transaction?.id}
						<p class="text-muted-foreground">
							{$i18n.t('Then it is posted and matched to the bank statement line.')}
						</p>
					{/if}
				{:else}
					<p class="text-muted-foreground">{$i18n.t('Nothing yet. Before saving:')}</p>
					<ul class="grid gap-1">
						{#if !isBalanced}
							<li class="flex items-center gap-1.5">
								<CircleAlert class="size-4 shrink-0 text-destructive" />
								<span class="tabular-nums">
									{$i18n.t('Debits and credits differ by {{diff}}', {
										diff: fmt(Math.abs(balanceDiff))
									})}
								</span>
							</li>
						{/if}
						{#if !allAccountsSet}
							<li class="flex items-center gap-1.5">
								<CircleAlert class="size-4 shrink-0 text-destructive" />
								{$i18n.t('{{n}} line(s) without an account', { n: missingAccountCount })}
							</li>
						{/if}
						{#if lines.length < 2}
							<li class="flex items-center gap-1.5">
								<CircleAlert class="size-4 shrink-0 text-destructive" />
								{$i18n.t('An entry needs at least two lines')}
							</li>
						{/if}
					</ul>
				{/if}
			</div>
		{/if}

		<!-- Footer -->
		<Dialog.Footer class="gap-3 sm:items-center sm:justify-between">
			<div class="flex flex-wrap items-center gap-2">
				{#if bankStatementLineId && !transaction?.id}
					<div class="flex items-center gap-2">
						<Checkbox id="je-direct-match" bind:checked={directMatch} />
						<Label for="je-direct-match" class="text-[13px] font-normal text-muted-foreground">
							{$i18n.t('Direct match — post entry and match to bank statement line')}
						</Label>
					</div>
				{/if}
				{#if transaction?.id}
					<Popover.Root bind:open={templateNameOpen}>
						<Popover.Trigger>
							{#snippet child({ props })}
								<Button {...props} variant="ghost" size="sm" disabled={savingTemplate}>
									<BookmarkPlus />{$i18n.t('Save as Template')}
								</Button>
							{/snippet}
						</Popover.Trigger>
						<Popover.Content align="start" class="w-72">
							<form
								class="grid gap-3"
								onsubmit={(e) => {
									e.preventDefault();
									saveAsTemplate();
								}}
							>
								<div class="grid gap-2">
									<Label for="je-template-name">{$i18n.t('Template name')}</Label>
									<Input id="je-template-name" class="h-8" bind:value={templateName} />
								</div>
								<div class="flex justify-end gap-2">
									<Button variant="outline" size="sm" onclick={() => (templateNameOpen = false)}>
										{$i18n.t('Cancel')}
									</Button>
									<Button
										type="submit"
										variant="secondary"
										size="sm"
										disabled={!templateName.trim() || savingTemplate}
									>
										{#if savingTemplate}<Spinner />{/if}
										{$i18n.t('Save Template')}
									</Button>
								</div>
							</form>
						</Popover.Content>
					</Popover.Root>
				{/if}
			</div>

			<div class="flex flex-wrap items-center justify-end gap-2">
				<Button variant="outline" onclick={() => (show = false)}>
					{readOnly ? $i18n.t('Close') : $i18n.t('Cancel')}
				</Button>
				{#if !readOnly}
					{#if aiAvailable && transaction?.id}
						<Button variant="outline" disabled={validating} onclick={handleValidate}>
							{#if validating}<Spinner />{:else}<Sparkles />{/if}
							{validating ? $i18n.t('Validating...') : $i18n.t('AI Validate')}
						</Button>
					{/if}
					<Button disabled={!canSubmit} onclick={handleSubmit}>
						{#if saving}
							<Spinner />{$i18n.t('Saving...')}
						{:else if transaction?.id}
							{$i18n.t('Update')}
						{:else}
							{$i18n.t('Create')}
						{/if}
					</Button>
				{/if}
			</div>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Opened from inside the dialog: created after it, so their portals stack above it -->
<InvoiceSelector bind:show={showInvoiceSelector} on:select={handleInvoiceSelect} />
<InvoiceSelector bind:show={showExtraInvoiceSelector} on:select={handleExtraInvoiceSelect} />
<AccountFormModal
	bind:show={showCreateAccount}
	{accounts}
	{companyId}
	on:save={handleAccountCreated}
/>
<ConfirmDialog
	bind:open={showDeleteTemplateConfirm}
	title={$i18n.t('Delete this journal template?')}
	description={journalTemplates.find((t) => t.id === selectedTemplateId)?.name ?? ''}
	confirmLabel={$i18n.t('Delete')}
	destructive
	onconfirm={handleDeleteTemplate}
/>
