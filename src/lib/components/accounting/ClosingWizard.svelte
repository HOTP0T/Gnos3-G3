<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { uiLocale } from '$lib/utils/uiLocale';
	import { buildMonthOptions, type MonthOption } from '$lib/utils/fiscalYear';
	import { taxTerm } from '$lib/utils/taxTerms';
	import { toast } from 'svelte-sonner';

	import {
		getClosingChecklist,
		yearEndClose,
		carryForwardBalances,
		generateDepreciation,
		getPeriods,
		getCompany,
		bulkPostTransactions,
		autoMatchBankStatements,
		getBankAccounts,
		closePeriod
	} from '$lib/apis/accounting';

	import Lock from '@lucide/svelte/icons/lock';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';
	import ListChecks from '@lucide/svelte/icons/list-checks';
	import CircleX from '@lucide/svelte/icons/circle-x';
	import Sparkles from '@lucide/svelte/icons/sparkles';
	import CalendarCheck from '@lucide/svelte/icons/calendar-check';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as AlertDialog from '$lib/components/ui/alert-dialog/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';

	const i18n: any = getContext('i18n');

	export let companyId: number;

	// State
	let loading = false;
	let checking = false;
	let closing = false;
	let generatingYearEnd = false;
	let carryingForward = false;
	let checklist: any = null;

	// Month selector
	let selectedMonth = '';
	let monthOptions: MonthOption[] = [];

	// Year-end preview
	let showYearEndPreview = false;
	let yearEndPreview: any = null;

	// ─── Helpers ────────────────────────────────────────────────────────────────

	let fiscalStartMonth = 1;
	let currency = '';

	const fmt = (v: any): string => {
		const n = typeof v === 'string' ? parseFloat(v) : (v ?? 0);
		if (n === 0) return '0.00';
		return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	};

	// The checklist API speaks English. The base steps are rebuilt here from their
	// stable `step` + `count` so the wizard follows the UI language; anything else
	// (country-specific checks, free-text details) goes through t() and falls back
	// to the API text when no translation exists.
	const checkLabel = (check: any): string =>
		check.step === 'tva_declaration'
			? $i18n.t('{{tax}} return', { tax: taxTerm($i18n.t, check) })
			: $i18n.t(check.label ?? check.name ?? '');

	const checkDetail = (check: any): string => {
		const n = Number(check.count ?? 0);
		switch (check.step) {
			case 'draft_entries':
				return n > 0
					? $i18n.t('{{count}} draft entries', { count: n })
					: $i18n.t('All entries are posted');
			case 'bank_reconciliation':
				if (n > 0) return $i18n.t('{{count}} unmatched bank lines', { count: n });
				break;
			case 'tva_declaration': {
				const tax = taxTerm($i18n.t, check);
				const net = Number(check.tva_net ?? 0);
				if (Math.abs(net) <= 0.01) return $i18n.t('No {{tax}} for this period', { tax });
				const amount = `${fmt(Math.abs(net))} ${check.currency ?? currency}`.trim();
				return net > 0
					? $i18n.t('Net {{tax}}: {{amount}} payable', { tax, amount })
					: $i18n.t('Net {{tax}}: {{amount}} credit', { tax, amount });
			}
			case 'trial_balance':
				if (check.status !== 'ok' && check.difference != null) {
					return $i18n.t('Unbalanced: difference of {{amount}}', {
						amount: `${fmt(check.difference)} ${currency}`.trim()
					});
				}
				break;
		}
		return check.detail ? $i18n.t(check.detail) : '';
	};

	const checkActionLabel = (check: any): string =>
		check.action_label ? $i18n.t(check.action_label) : $i18n.t('Fix');

	// Checks that stop the period from closing (`blocking` from the API); the
	// API's `blockers` strings stay the fallback for older payloads.
	const blockingChecks = (list: any): any[] => (list?.checks ?? []).filter((c: any) => c.blocking);

	// ─── Data loading ───────────────────────────────────────────────────────────

	onMount(async () => {
		loading = true;
		try {
			const [res, co] = await Promise.all([
				getPeriods({ company_id: companyId }),
				getCompany(companyId).catch(() => null)
			]);
			const periods = res.periods ?? res ?? [];
			fiscalStartMonth = Number(co?.fiscal_year_start_month ?? 1) || 1;
			currency = co?.currency ?? '';
			monthOptions = buildMonthOptions(periods, fiscalStartMonth);

			const now = new Date();
			const curKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
			const match = monthOptions.find((o) => o.value === curKey);
			if (match) {
				selectedMonth = match.value;
			} else if (monthOptions.length > 0) {
				selectedMonth = monthOptions[0].value;
			}
		} catch (err) {
			console.error('Failed to load periods:', err);
		}
		loading = false;
	});

	// ─── Run Checklist ──────────────────────────────────────────────────────────

	const handleRunChecklist = async () => {
		const opt = monthOptions.find((o) => o.value === selectedMonth);
		if (!opt) {
			toast.error($i18n.t('Please select a period'));
			return;
		}
		checking = true;
		checklist = null;
		try {
			checklist = await getClosingChecklist({
				company_id: companyId,
				period_start: opt.from,
				period_end: opt.to
			});
			checkedAt = new Date().toLocaleTimeString(uiLocale(), { hour: '2-digit', minute: '2-digit' });
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to run checklist') + ': ' + msg);
		}
		checking = false;
	};

	// ─── Action handlers ────────────────────────────────────────────────────────

	let actionBusy: string | null = null;
	const runCheckAction = async (check: any) => {
		actionBusy = check.step ?? check.action ?? '';
		try {
			await handleCheckAction(check);
		} finally {
			actionBusy = null;
		}
	};

	const handleCheckAction = async (check: any) => {
		const opt = monthOptions.find((o) => o.value === selectedMonth);
		if (!opt) return;

		if (check.action === 'bulk_post_drafts' || check.step === 'draft_entries') {
			try {
				const result = await bulkPostTransactions({
					company_id: companyId,
					period_start: opt.from,
					period_end: opt.to
				});
				toast.success(
					`${result?.posted ?? 0} ${$i18n.t('entries posted')}${result?.skipped ? `, ${result.skipped} ${$i18n.t('skipped')}` : ''}`
				);
				await handleRunChecklist();
			} catch (err: any) {
				toast.error(err?.detail ?? `${err}`);
			}
		} else if (check.action === 'auto_reconcile' || check.step === 'bank_reconciliation') {
			try {
				const banks = await getBankAccounts(companyId);
				const bankList = banks?.accounts ?? banks ?? [];
				let totalMatched = 0;
				for (const ba of bankList) {
					const result = await autoMatchBankStatements(ba.id);
					totalMatched += result?.matched ?? 0;
				}
				toast.success(`${totalMatched} ${$i18n.t('bank lines matched')}`);
				await handleRunChecklist();
			} catch (err: any) {
				toast.error(err?.detail ?? `${err}`);
			}
		} else if (check.action === 'generate_depreciation') {
			try {
				const result = await generateDepreciation(companyId, opt.to);
				const count = result?.entries_created ?? result?.count ?? 0;
				toast.success(`${count} ${$i18n.t('depreciation entries created as Draft')}`);
				await handleRunChecklist();
			} catch (err: any) {
				toast.error(err?.detail ?? `${err}`);
			}
		} else if (check.action === 'generate_tax_entry') {
			toast.info($i18n.t('Please use the Tax Declaration tab to generate tax entries'));
		}
	};

	// ─── Close Period ───────────────────────────────────────────────────────────

	// Closing locks the whole accounting period the checked month falls in, which
	// is more than that month when the company keeps yearly periods: say which.
	let showCloseConfirm = false;
	$: closeTarget = checklist?.period ?? null;
	$: closeMessage = !closeTarget
		? ''
		: closeTarget.start_date < checklist.period_start || closeTarget.end_date > checklist.period_end
			? $i18n.t(
					'This closes the whole period {{name}}, **from {{start}} to {{end}}** — not only the month you checked ({{from}} to {{to}}). No entry dated in that range can be added, changed or voided afterwards. To close one month at a time, set up monthly periods under Settings → Accounting Periods.',
					{
						name: closeTarget.name,
						start: closeTarget.start_date,
						end: closeTarget.end_date,
						from: checklist.period_start,
						to: checklist.period_end
					}
				)
			: $i18n.t(
					'Close {{name}} (**{{start}} to {{end}}**)? No entry dated in this period can be added, changed or voided afterwards.',
					{ name: closeTarget.name, start: closeTarget.start_date, end: closeTarget.end_date }
				);

	const requestClosePeriod = () => {
		if (!checklist?.period_id) {
			toast.info($i18n.t('Use the Accounting Periods section in Settings to close the period'));
			return;
		}
		showCloseConfirm = true;
	};

	const handleClosePeriod = async () => {
		if (!checklist?.period_id) {
			toast.info($i18n.t('Use the Accounting Periods section in Settings to close the period'));
			return;
		}
		closing = true;
		try {
			await closePeriod(checklist.period_id);
			toast.success($i18n.t('Period closed'));
			await handleRunChecklist();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		closing = false;
	};

	// ─── Year-End Close ─────────────────────────────────────────────────────────

	$: selectedOpt = monthOptions.find((o) => o.value === selectedMonth);
	// The year-end close is offered in the last month of the company's fiscal year (December, or March for an April – March year).
	$: isFiscalYearEnd = !!selectedOpt?.isFiscalYearEnd;

	const handleYearEndClose = async () => {
		if (!selectedOpt) return;
		generatingYearEnd = true;
		try {
			const result = await yearEndClose(companyId, {
				fiscal_year_start: selectedOpt.fiscalStart,
				fiscal_year_end: selectedOpt.to
			});
			yearEndPreview = result;
			const txId = result?.id ?? result?.transaction_id ?? '';
			toast.success(
				$i18n.t('Year-end closing entry created as Draft') + (txId ? ` (ID: ${txId})` : '')
			);
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to create year-end closing entry') + ': ' + msg);
		}
		generatingYearEnd = false;
	};

	const handleCarryForward = async () => {
		if (!selectedOpt) return;
		// Opening date = day after the fiscal year end (start of next fiscal year).
		const close = new Date(selectedOpt.to + 'T00:00:00');
		const next = new Date(close);
		next.setDate(next.getDate() + 1);
		const openingDate = `${next.getFullYear()}-${String(next.getMonth() + 1).padStart(2, '0')}-${String(next.getDate()).padStart(2, '0')}`;
		carryingForward = true;
		try {
			const result = await carryForwardBalances(companyId, {
				closing_date: selectedOpt.to,
				opening_date: openingDate
			});
			const txId = result?.transaction_id ?? result?.id ?? '';
			if (!txId) {
				// Nothing to carry: the result account is flat (year-end entry not posted yet).
				toast.warning(result?.message ?? $i18n.t('Nothing to carry forward'));
			} else {
				toast.success(
					$i18n.t('Carry-forward entry created as a draft — review it in Entries and post it') +
						` — ${result.amount} ${result.from_account} → ${result.to_account} (ID: ${txId})`
				);
			}
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to create the carry-forward entry') + ': ' + msg);
		}
		carryingForward = false;
	};

	// One status per row (design system → Status map, closing: ok / warning / blocker).
	// A check that stops the period from closing reads "Blocker" whatever its tone.
	const checkStatus = (check: any): string => {
		if (check.blocking) return 'blocker';
		if (check.status === 'warn') return 'warning';
		return check.status ?? '';
	};
	const isDone = (check: any) => check.status === 'ok' || check.status === 'pass';

	// Where each check is fixed when the API offers no one-click action.
	$: basePath = `/accounting/company/${companyId}`;
	const FIX_PAGE: Record<string, { page: string; label: string }> = {
		draft_entries: { page: 'entries', label: 'Open Entries' },
		pre_opening_entries: { page: 'entries', label: 'Open Entries' },
		legacy_bookings: { page: 'entries', label: 'Open Entries' },
		bank_reconciliation: { page: 'bank', label: 'Open Bank' },
		tva_declaration: { page: 'tax', label: 'Open Tax' },
		trial_balance: { page: 'reports', label: 'Open Reports' },
		fx_clearing_zero: { page: 'entries', label: 'Open Entries' },
		hk_profits_tax_accrued: { page: 'tax', label: 'Open Tax' },
		hk_mpf_paid: { page: 'payments', label: 'Open Payments' }
	};
	const fixLink = (check: any): { href: string; label: string } | null => {
		const step = String(check.step ?? '');
		let fix = FIX_PAGE[step];
		if (!fix) {
			if (/_fa_(cost|depreciation)$/.test(step))
				fix = { page: 'assets', label: 'Open Fixed Assets' };
			else if (/^(cn|hk)_/.test(step)) fix = { page: 'reports', label: 'Open Reports' };
		}
		return fix ? { href: `${basePath}/${fix.page}`, label: fix.label } : null;
	};
	// The API's one-click fixes (post drafts, auto-reconcile, depreciation); the tax entry
	// is made on the Tax tab, so that one is a link.
	const hasAction = (check: any) => !!check.action && check.action !== 'generate_tax_entry';

	// "**bold**" in the close confirmation → alternating plain / bold parts.
	const boldParts = (text: string) => (text ?? '').split('**');

	$: blockerCount = checklist?.blockers?.length ?? 0;
	$: selectedLabel = selectedOpt?.label ?? '';
	let checkedAt = '';
</script>

<!-- Closing locks the period: the confirmation says which dates -->
<AlertDialog.Root bind:open={showCloseConfirm}>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>{$i18n.t('Close this period?')}</AlertDialog.Title>
			<AlertDialog.Description>
				{#each boldParts(closeMessage) as part, i}{#if i % 2 === 1}<strong
							class="font-semibold text-foreground tabular-nums">{part}</strong
						>{:else}{part}{/if}{/each}
			</AlertDialog.Description>
		</AlertDialog.Header>
		<AlertDialog.Footer>
			<AlertDialog.Cancel>{$i18n.t('Cancel')}</AlertDialog.Cancel>
			<AlertDialog.Action
				onclick={() => {
					showCloseConfirm = false;
					handleClosePeriod();
				}}
			>
				<Lock />{$i18n.t('Close Period')}
			</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>

<div class="flex flex-col gap-4">
	<div class="flex flex-col gap-1">
		<h2 class="text-lg font-semibold">{$i18n.t('Closing Wizard')}</h2>
		<p class="text-sm text-muted-foreground">
			{$i18n.t('Run pre-closing checks and generate period/year-end closing entries.')}
		</p>
	</div>

	{#if loading}
		<Skeleton class="h-72 w-full max-w-3xl rounded-xl" />
	{:else}
		<Card.Root class="max-w-3xl">
			<Card.Header class="flex flex-wrap items-start justify-between gap-3 border-b">
				<div class="flex min-w-0 flex-col gap-1.5">
					<Card.Title>{$i18n.t('Pre-Closing Checklist')}</Card.Title>
					{#if selectedLabel}
						<Card.Description>
							{selectedLabel}{#if checklist && checkedAt && !checking}{' · '}{$i18n.t(
									'checked at {{time}}',
									{ time: checkedAt }
								)}{/if}
						</Card.Description>
					{/if}
				</div>
				<div class="flex flex-wrap items-center gap-2">
					{#if monthOptions.length > 0}
						<NativeSelect.Root
							id="closing-month"
							size="sm"
							bind:value={selectedMonth}
							aria-label={$i18n.t('Period')}
						>
							{#each monthOptions as opt}
								<NativeSelect.Option value={opt.value}>{opt.label}</NativeSelect.Option>
							{/each}
						</NativeSelect.Root>
					{:else}
						<span class="text-sm text-muted-foreground"
							>{$i18n.t('No accounting periods defined')}</span
						>
					{/if}
					<Button
						variant={checklist ? 'outline' : 'default'}
						size="sm"
						disabled={!selectedMonth || checking}
						onclick={handleRunChecklist}
					>
						{#if checking}<Spinner />{:else}<RefreshCw />{/if}
						{$i18n.t('Run Checklist')}
					</Button>
				</div>
			</Card.Header>

			<Card.Content>
				{#if checking}
					<div class="flex flex-col gap-3" aria-busy="true">
						{#each Array(5) as _}<Skeleton class="h-10 w-full" />{/each}
					</div>
				{:else if !checklist}
					<Empty.Root class="p-4">
						<Empty.Header>
							<Empty.Media variant="icon"><ListChecks /></Empty.Media>
							<Empty.Title>{$i18n.t('Run the checklist for the period')}</Empty.Title>
							<Empty.Description>
								{$i18n.t(
									'It checks draft entries, bank reconciliation, tax and the trial balance before the period can be closed.'
								)}
							</Empty.Description>
						</Empty.Header>
					</Empty.Root>
				{:else}
					<!-- Older payloads carry only the blocker sentences, without per-check flags -->
					{#if blockerCount > 0 && blockingChecks(checklist).length === 0}
						<Alert.Root variant="destructive" class="mb-3">
							<CircleX />
							<Alert.Title>{$i18n.t('Blockers')}</Alert.Title>
							<Alert.Description>
								<ul class="list-disc pl-4">
									{#each checklist.blockers as blocker}<li>{$i18n.t(blocker)}</li>{/each}
								</ul>
							</Alert.Description>
						</Alert.Root>
					{/if}

					<ul class="divide-y">
						{#each checklist.checks ?? [] as check}
							{@const fix = fixLink(check)}
							<li
								class="grid grid-cols-[1fr_auto] items-start gap-x-3 gap-y-1 py-3 first:pt-0 last:pb-0 sm:grid-cols-[6.5rem_1fr_auto]"
							>
								<StatusBadge
									kind="closing"
									status={checkStatus(check)}
									bare
									class="col-start-1 row-start-1 text-[13px] sm:pt-0.5"
								/>
								<div
									class="col-span-2 row-start-2 min-w-0 sm:col-span-1 sm:col-start-2 sm:row-start-1"
								>
									<div class="font-medium">{checkLabel(check)}</div>
									{#if checkDetail(check)}
										<div class="text-[13px] break-words text-muted-foreground">
											{checkDetail(check)}
										</div>
									{/if}
								</div>
								{#if !isDone(check)}
									<div class="col-start-2 row-start-1 sm:col-start-3">
										{#if hasAction(check)}
											<Button
												variant="outline"
												size="sm"
												disabled={actionBusy !== null}
												onclick={() => runCheckAction(check)}
											>
												{#if actionBusy !== null && actionBusy === (check.step ?? check.action ?? '')}
													<Spinner />
												{:else if check.action === 'auto_reconcile'}
													<Sparkles />
												{/if}
												{checkActionLabel(check)}
											</Button>
										{:else if fix}
											<Button variant="outline" size="sm" href={fix.href}
												>{$i18n.t(fix.label)}</Button
											>
										{/if}
									</div>
								{/if}
							</li>
						{/each}
					</ul>
				{/if}
			</Card.Content>

			{#if checklist && !checking}
				<Card.Footer class="flex-wrap justify-between gap-3 border-t">
					<div class="flex min-w-0 flex-wrap items-center gap-2 text-sm text-muted-foreground">
						{#if !(checklist.can_close ?? false)}
							{#if blockerCount > 0}
								<Badge variant="danger"><CircleX />{$i18n.t('Blockers')}: {blockerCount}</Badge>
							{/if}
							<span>{$i18n.t('Resolve all blockers before closing')}</span>
						{:else if closeTarget}
							<span class="tabular-nums">
								{$i18n.t('Locks {{name}} ({{start}} → {{end}})', {
									name: closeTarget.name,
									start: closeTarget.start_date,
									end: closeTarget.end_date
								})}
							</span>
						{/if}
					</div>
					<Button
						disabled={!(checklist.can_close ?? false) || closing}
						onclick={requestClosePeriod}
					>
						{#if closing}<Spinner />{:else}<Lock />{/if}
						{$i18n.t('Close Period')}
					</Button>
				</Card.Footer>
			{/if}
		</Card.Root>

		<!-- Year-end: offered in the last month of the company's fiscal year -->
		{#if checklist && !checking && isFiscalYearEnd}
			<Card.Root class="max-w-3xl">
				<Card.Header>
					<Card.Title>{$i18n.t('Year-End Closing')}</Card.Title>
					<Card.Description>
						{$i18n.t(
							'Generate year-end closing entry to zero all revenue/expense accounts into retained earnings.'
						)}
					</Card.Description>
				</Card.Header>

				{#if yearEndPreview?.lines?.length > 0}
					<Card.Content>
						<div class="overflow-hidden rounded-md border">
							<Table.Root class="text-[13px]">
								<Table.Header class="bg-muted/50">
									<Table.Row class="hover:bg-transparent">
										<Table.Head>{$i18n.t('Account Code')}</Table.Head>
										<Table.Head>{$i18n.t('Description')}</Table.Head>
										<Table.Head class="text-right">{$i18n.t('Debit')}</Table.Head>
										<Table.Head class="text-right">{$i18n.t('Credit')}</Table.Head>
									</Table.Row>
								</Table.Header>
								<Table.Body>
									{#each yearEndPreview.lines as line}
										<Table.Row>
											<Table.Cell class="font-mono">{line.account_code ?? ''}</Table.Cell>
											<Table.Cell class="whitespace-normal"
												>{line.description ?? line.account_name ?? ''}</Table.Cell
											>
											<Table.Cell class="text-right tabular-nums"
												>{line.debit ? fmt(line.debit) : ''}</Table.Cell
											>
											<Table.Cell class="text-right tabular-nums"
												>{line.credit ? fmt(line.credit) : ''}</Table.Cell
											>
										</Table.Row>
									{/each}
								</Table.Body>
							</Table.Root>
						</div>
					</Card.Content>
				{/if}

				<Card.Footer class="flex-wrap gap-2">
					<Button variant="outline" disabled={generatingYearEnd} onclick={handleYearEndClose}>
						{#if generatingYearEnd}<Spinner />{:else}<CalendarCheck />{/if}
						{generatingYearEnd
							? $i18n.t('Generating...')
							: $i18n.t('Generate Year-End Closing Entry')}
					</Button>
					<Tip
						content={$i18n.t(
							'Creates the carry-forward entry as a draft: it moves the closed result into retained earnings on the first day of the next year. You review and post it yourself. Balance-sheet accounts already open at their closing balance, so they are not re-posted. Run this after posting the year-end closing entry.'
						)}
					>
						<Button
							variant="outline"
							class="h-auto min-h-9 shrink text-left whitespace-normal"
							disabled={carryingForward}
							onclick={handleCarryForward}
						>
							{#if carryingForward}<Spinner />{/if}
							{carryingForward
								? $i18n.t('Creating...')
								: $i18n.t('Create carry-forward draft (result → retained earnings)')}
						</Button>
					</Tip>
				</Card.Footer>
			</Card.Root>
		{/if}
	{/if}
</div>
