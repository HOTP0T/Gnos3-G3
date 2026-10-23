<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import {
		getGeneralLedger,
		getFullGeneralLedger,
		getAccounts,
		exportGeneralLedger
	} from '$lib/apis/accounting';
	import type { Writable } from 'svelte/store';
	import { convertAmount } from '$lib/utils/currency';
	import ReportAmount from '$lib/components/accounting/ReportAmount.svelte';
	import K4miDocLink from '$lib/components/common/K4miDocLink.svelte';

	import Download from '@lucide/svelte/icons/download';
	import ExternalLink from '@lucide/svelte/icons/external-link';
	import ChevronLeft from '@lucide/svelte/icons/chevron-left';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import BookOpen from '@lucide/svelte/icons/book-open';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';

	const i18n: any = getContext('i18n');
	export let companyId: number;

	// Display-currency conversion (company-wide selector). Only the ACCOUNT view is
	// in base currency and gets scaled; the JOURNAL view shows each entry in its
	// own original transaction currency (a single factor would be wrong there).
	const displayCurrency = getContext<Writable<string>>('displayCurrency');
	const exchangeRates = getContext<Writable<any[]>>('exchangeRates');
	const companyCurrency = getContext<Writable<string>>('companyCurrency');

	let loading = false;
	let loadError = '';
	let loaded = false;
	let mode: 'journal' | 'account' = 'journal';

	let dateFrom = '';
	let dateTo = '';

	// Journal mode
	let journalEntries: any[] = [];
	let journalTotal = 0;
	let journalTotalDebit = 0;
	let journalTotalCredit = 0;
	let journalPage = 0;
	const journalPerPage = 50;

	// Account mode
	let accounts: Array<{ id: number; code: string; name: string }> = [];
	let selectedAccountId: number | '' = '';
	let rawAccountData: any = null;
	let accountPage = 0;
	const accountPerPage = 50;

	// Account-view conversion (base → display) as of the period end.
	$: baseCcy = rawAccountData?.currency || $companyCurrency || 'EUR';
	$: converting = !!($displayCurrency && baseCcy && $displayCurrency !== baseCcy);
	$: fx =
		converting && rawAccountData
			? convertAmount(1, baseCcy, $displayCurrency, $exchangeRates ?? [], dateTo || undefined)
			: null;
	$: factor = converting ? (fx?.hasRate ? fx.rate : null) : 1;
	$: noRate = converting && !fx?.hasRate;
	$: displayCcy = converting ? $displayCurrency : baseCcy;
	$: fxProps = { factor, converting, displayCcy, baseCcy };
	$: accountData = rawAccountData;

	// Journal view: each entry is in its OWN original currency. Convert a line amount
	// from the entry's currency to the display currency (returns the numeric value;
	// falls back to the original when not converting / no rate). Store args are passed
	// so the {@const}/reactive call sites recompute when the selection changes.
	// When the display currency is the company currency, an entry is valued at
	// the rate it was BOOKED at (exactly as the ledger and every report value it);
	// any other target goes through the rate table.
	function jrate(
		entryCcy: string,
		date: string,
		disp: string,
		rates: any[],
		booked?: any
	): number | null {
		const cur = (entryCcy || '').toUpperCase();
		if (!disp || !cur || disp === cur) return 1;
		const b = booked != null ? Number(booked) : NaN;
		if (disp.toUpperCase() === (baseCcy || '').toUpperCase() && b > 0) return b;
		const r = convertAmount(1, cur, disp, rates ?? [], date);
		return r.hasRate ? r.rate : null;
	}
	function jconv(
		amount: any,
		entryCcy: string,
		date: string,
		disp: string,
		rates: any[],
		booked?: any
	): { v: number; hasRate: boolean } {
		const n = typeof amount === 'string' ? parseFloat(amount) : (amount ?? 0);
		const v = isNaN(n) ? 0 : n;
		const f = jrate(entryCcy, date, disp, rates, booked);
		return f === null ? { v, hasRate: false } : { v: Math.round(v * f * 100) / 100, hasRate: true };
	}
	// Per-line entry-currency→display factor for a journal entry (feeds <ReportAmount>).
	function jfactor(
		entryCcy: string,
		date: string,
		disp: string,
		rates: any[],
		booked?: any
	): number | null {
		return jrate(entryCcy, date, disp, rates, booked);
	}
	// Journal totals in the display currency = sum of per-line converted amounts.
	$: journalDispDebit = journalEntries.reduce(
		(s, e) =>
			s +
			e.lines.reduce(
				(ls: number, l: any) =>
					ls +
					jconv(
						l.debit,
						e.currency,
						e.transaction_date,
						$displayCurrency,
						$exchangeRates ?? [],
						e.exchange_rate
					).v,
				0
			),
		0
	);
	$: journalDispCredit = journalEntries.reduce(
		(s, e) =>
			s +
			e.lines.reduce(
				(ls: number, l: any) =>
					ls +
					jconv(
						l.credit,
						e.currency,
						e.transaction_date,
						$displayCurrency,
						$exchangeRates ?? [],
						e.exchange_rate
					).v,
				0
			),
		0
	);
	$: journalConverting =
		!!$displayCurrency &&
		journalEntries.some((e) => (e.currency || '').toUpperCase() !== $displayCurrency.toUpperCase());

	const loadAccounts = async () => {
		try {
			const res = await getAccounts({ company_id: companyId, active: true });
			accounts = (Array.isArray(res) ? res : []).map((a: any) => ({
				id: a.id,
				code: a.code,
				name: a.name
			}));
		} catch (err) {
			console.error(err);
		}
	};

	const load = async () => {
		loading = true;
		loadError = '';
		try {
			if (mode === 'journal') {
				const res = await getFullGeneralLedger({
					company_id: companyId,
					date_from: dateFrom || undefined,
					date_to: dateTo || undefined,
					limit: journalPerPage,
					offset: journalPage * journalPerPage
				});
				journalEntries = res.entries ?? [];
				journalTotal = res.total ?? 0;
				journalTotalDebit = parseFloat(res.total_debit ?? 0);
				journalTotalCredit = parseFloat(res.total_credit ?? 0);
			} else {
				if (!selectedAccountId) {
					loading = false;
					return;
				}
				rawAccountData = await getGeneralLedger({
					company_id: companyId,
					account_id: selectedAccountId as number,
					date_from: dateFrom || undefined,
					date_to: dateTo || undefined,
					limit: accountPerPage,
					offset: accountPage * accountPerPage
				});
			}
		} catch (err) {
			loadError = `${err}`;
			toast.error(`${err}`);
		}
		loading = false;
		loaded = true;
	};

	const fmt = (v: any): string => {
		const n = typeof v === 'string' ? parseFloat(v) : (v ?? 0);
		if (n === 0) return '';
		return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	};

	const fmtRate = (v: any): string => {
		const n = typeof v === 'string' ? parseFloat(v) : (v ?? 1);
		if (n === 1) return '1';
		return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 8 });
	};

	// Compute original amount for a line (max of debit, credit — the gross amount)
	const origAmount = (line: any): string => {
		const d = parseFloat(line.debit) || 0;
		const c = parseFloat(line.credit) || 0;
		return fmt(Math.max(d, c));
	};

	$: if (mode === 'account' && accounts.length === 0) loadAccounts();

	// Dense report table: 13px, 6px row padding, 12px at the outer edges (design system → Reports).
	const TABLE =
		'text-[13px] [&_td]:py-1.5 [&_td:first-child]:pl-3 [&_th:first-child]:pl-3 [&_td:last-child]:pr-3 [&_th:last-child]:pr-3';
</script>

{#snippet voidedBadge(tip: string)}
	<Tip content={tip}>
		<StatusBadge kind="entry" status="voided" label={$i18n.t('voided')} />
	</Tip>
{/snippet}

{#snippet pager(pageIdx: number, total: number, perPage: number, go: (p: number) => void)}
	<div class="flex flex-wrap items-center justify-end gap-2 text-sm">
		<span class="text-muted-foreground tabular-nums"
			>{$i18n.t('Page', { context: 'gnos3' })} {pageIdx + 1} / {Math.ceil(total / perPage)}</span
		>
		<Button variant="outline" size="sm" disabled={pageIdx === 0} onclick={() => go(pageIdx - 1)}>
			<ChevronLeft />{$i18n.t('Previous')}
		</Button>
		<Button
			variant="outline"
			size="sm"
			disabled={(pageIdx + 1) * perPage >= total}
			onclick={() => go(pageIdx + 1)}
		>
			{$i18n.t('Next')}<ChevronRight />
		</Button>
	</div>
{/snippet}

<div class="flex min-w-0 flex-col gap-4">
	<!-- Filters -->
	<div class="flex flex-wrap items-end gap-2">
		<div class="grid gap-1.5">
			<Label for="gl-mode">{$i18n.t('View')}</Label>
			<NativeSelect.Root id="gl-mode" size="sm" bind:value={mode}>
				<NativeSelect.Option value="journal">{$i18n.t('Journal View')}</NativeSelect.Option>
				<NativeSelect.Option value="account">{$i18n.t('Account View')}</NativeSelect.Option>
			</NativeSelect.Root>
		</div>
		{#if mode === 'account'}
			<div class="grid min-w-0 gap-1.5">
				<Label for="gl-account">{$i18n.t('Account', { context: 'gnos3' })}</Label>
				<NativeSelect.Root
					id="gl-account"
					size="sm"
					class="w-64 max-w-full"
					bind:value={selectedAccountId}
				>
					<NativeSelect.Option value="">{$i18n.t('Select account...')}</NativeSelect.Option>
					{#each accounts as acct}<NativeSelect.Option value={acct.id}
							>{acct.code} — {acct.name}</NativeSelect.Option
						>{/each}
				</NativeSelect.Root>
			</div>
		{/if}
		<div class="grid gap-1.5">
			<Label for="gl-from">{$i18n.t('From')}</Label>
			<Input id="gl-from" type="date" class="h-8 w-40" bind:value={dateFrom} />
		</div>
		<div class="grid gap-1.5">
			<Label for="gl-to">{$i18n.t('To')}</Label>
			<Input id="gl-to" type="date" class="h-8 w-40" bind:value={dateTo} />
		</div>
		<Button
			size="sm"
			disabled={loading}
			onclick={() => {
				journalPage = 0;
				accountPage = 0;
				load();
			}}
		>
			{#if loading}<Spinner />{/if}
			{$i18n.t('Load')}
		</Button>
		{#if (mode === 'journal' && journalEntries.length > 0) || (mode === 'account' && accountData)}
			<Button
				variant="outline"
				size="sm"
				onclick={() =>
					exportGeneralLedger({
						company_id: companyId,
						date_from: dateFrom || undefined,
						date_to: dateTo || undefined
					})}
			>
				<Download />
				{$i18n.t('Export Excel')}
			</Button>
		{/if}
	</div>

	{#if loading}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(10) as _}
				<Skeleton class="h-6 w-full" />
			{/each}
		</div>
	{:else if loadError}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Could not load the report.')}</Alert.Title>
			<Alert.Description>{loadError}</Alert.Description>
			<Alert.Action>
				<Button variant="outline" size="sm" onclick={load}>{$i18n.t('Retry')}</Button>
			</Alert.Action>
		</Alert.Root>
	{:else if mode === 'journal' && loaded}
		<!-- Journal View matching sample: Period | Reference | Description | Account Code | Account Name | Currency | Exch Rate | Orig Amount | Debit | Credit -->
		{#if journalEntries.length === 0}
			<Empty.Root class="border border-dashed">
				<Empty.Header>
					<Empty.Media variant="icon"><BookOpen /></Empty.Media>
					<Empty.Title>{$i18n.t('No journal entries found.')}</Empty.Title>
					<Empty.Description>{$i18n.t('Widen the dates, then Load.')}</Empty.Description>
				</Empty.Header>
			</Empty.Root>
		{:else}
			<div class="overflow-hidden rounded-md border">
				<Table.Root class={TABLE}>
					<Table.Header class="bg-muted/50">
						<Table.Row class="hover:bg-transparent">
							<Table.Head>{$i18n.t('#')}</Table.Head>
							<Table.Head>{$i18n.t('Period')}</Table.Head>
							<Table.Head>{$i18n.t('Reference')}</Table.Head>
							<Table.Head>{$i18n.t('Description')}</Table.Head>
							<Table.Head>{$i18n.t('Account Code')}</Table.Head>
							<Table.Head>{$i18n.t('Account Name')}</Table.Head>
							<Table.Head>{$i18n.t('Currency')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Exch. Rate')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Orig. Amount')}</Table.Head>
							<Table.Head class="min-w-28 text-right">{$i18n.t('Debit')}</Table.Head>
							<Table.Head class="min-w-28 text-right">{$i18n.t('Credit')}</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each journalEntries as entry}
							{#each entry.lines as line, lineIdx}
								<!-- One block per entry: a rule between entries, none between its lines -->
								<Table.Row
									class="{lineIdx < entry.lines.length - 1 ? 'border-b-0' : ''} {entry.status ===
									'voided'
										? 'text-muted-foreground'
										: ''}"
								>
									<Table.Cell class="font-mono text-[13px]" title="ID: {entry.transaction_id}">
										{#if lineIdx === 0}
											<span class="inline-flex items-center gap-1.5">
												{entry.entry_number || entry.transaction_id || ''}
												{#if entry.status === 'voided'}
													{@render voidedBadge(
														$i18n.t(
															'This entry was voided; its reversal below cancels it. Both are kept for the audit trail and net to zero.'
														)
													)}
												{/if}
											</span>
										{/if}
									</Table.Cell>
									<Table.Cell class="font-mono text-[13px]"
										>{lineIdx === 0 ? entry.period : ''}</Table.Cell
									>
									<Table.Cell class="font-mono text-[13px]">
										{#if lineIdx === 0 && entry.k4mi_document_id}
											<K4miDocLink
												docId={entry.k4mi_document_id}
												title={$i18n.t('Open in K4mi')}
												extraClass="inline-flex items-center gap-1 text-link underline-offset-4 hover:underline"
												>{entry.reference ?? ''}<ExternalLink
													class="size-3"
													aria-hidden="true"
												/></K4miDocLink
											>
										{:else if lineIdx === 0}{entry.reference ?? ''}{/if}
									</Table.Cell>
									<Table.Cell class="max-w-[200px] truncate"
										>{lineIdx === 0 ? (entry.description ?? '') : ''}</Table.Cell
									>
									<Table.Cell class="font-mono text-[13px]">{line.account_code}</Table.Cell>
									<Table.Cell>{line.account_name}</Table.Cell>
									<Table.Cell>{lineIdx === 0 ? entry.currency : ''}</Table.Cell>
									<Table.Cell class="text-right tabular-nums"
										>{lineIdx === 0 ? fmtRate(entry.exchange_rate) : ''}</Table.Cell
									>
									<Table.Cell class="text-right tabular-nums">{origAmount(line)}</Table.Cell>
									<Table.Cell class="text-right tabular-nums"
										>{#key $displayCurrency}<ReportAmount
												value={line.debit}
												factor={jfactor(
													entry.currency,
													entry.transaction_date,
													$displayCurrency,
													$exchangeRates ?? [],
													entry.exchange_rate
												)}
												converting={!!$displayCurrency &&
													(entry.currency || '').toUpperCase() !== $displayCurrency.toUpperCase()}
												displayCcy={$displayCurrency}
												baseCcy={entry.currency}
											/>{/key}</Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										>{#key $displayCurrency}<ReportAmount
												value={line.credit}
												factor={jfactor(
													entry.currency,
													entry.transaction_date,
													$displayCurrency,
													$exchangeRates ?? [],
													entry.exchange_rate
												)}
												converting={!!$displayCurrency &&
													(entry.currency || '').toUpperCase() !== $displayCurrency.toUpperCase()}
												displayCcy={$displayCurrency}
												baseCcy={entry.currency}
											/>{/key}</Table.Cell
									>
								</Table.Row>
							{/each}
						{/each}
					</Table.Body>
					<Table.Footer>
						<Table.Row class="hover:bg-transparent">
							<Table.Cell colspan={9}>{$i18n.t('Total')}</Table.Cell>
							<Table.Cell class="text-right tabular-nums"
								>{#key $displayCurrency}{#if journalConverting}{fmt(journalDispDebit)}
										<span class="text-[10px] font-normal text-muted-foreground"
											>{$displayCurrency}</span
										>{:else}{fmt(journalTotalDebit)}{/if}{/key}</Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								>{#key $displayCurrency}{#if journalConverting}{fmt(journalDispCredit)}
										<span class="text-[10px] font-normal text-muted-foreground"
											>{$displayCurrency}</span
										>{:else}{fmt(journalTotalCredit)}{/if}{/key}</Table.Cell
							>
						</Table.Row>
					</Table.Footer>
				</Table.Root>
			</div>
		{/if}

		{#if journalTotal > journalPerPage}
			{@render pager(journalPage, journalTotal, journalPerPage, (p) => {
				journalPage = p;
				load();
			})}
		{/if}
	{:else if mode === 'account' && accountData}
		{@const hasSubAccounts = accountData.entries.some((e: any) => e.account_code)}
		<div class="flex flex-wrap items-baseline gap-x-3 gap-y-1 text-sm">
			<span class="font-medium">
				<span class="font-mono text-[13px]">{accountData.account_code}</span> — {accountData.account_name}
			</span>
			{#if hasSubAccounts}<span class="text-muted-foreground"
					>({$i18n.t('incl. sub-accounts')})</span
				>{/if}
			<span class="text-muted-foreground"
				>{$i18n.t('Opening')}:
				<span class="text-foreground tabular-nums"
					><ReportAmount value={accountData.opening_balance} {...fxProps} zeroText={null} /></span
				></span
			>
			{#if accountData.opening_balance_date}<span class="text-muted-foreground tabular-nums"
					>({$i18n.t('as of')} {accountData.opening_balance_date})</span
				>{/if}
			{#if displayCcy}<span class="text-muted-foreground">· {displayCcy}</span>{/if}
			{#if noRate}
				<span class="inline-flex items-center gap-1">
					<TriangleAlert class="size-4 text-warning" />
					({$i18n.t('no rate for')}
					{$displayCurrency})
				</span>
			{/if}
		</div>

		<div class="overflow-hidden rounded-md border">
			<Table.Root class={TABLE}>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						<Table.Head>{$i18n.t('Date')}</Table.Head>
						{#if hasSubAccounts}<Table.Head>{$i18n.t('Account', { context: 'gnos3' })}</Table.Head>{/if}
						<Table.Head>{$i18n.t('Reference')}</Table.Head>
						<Table.Head>{$i18n.t('Description')}</Table.Head>
						<Table.Head class="min-w-28 text-right">{$i18n.t('Debit')}</Table.Head>
						<Table.Head class="min-w-28 text-right">{$i18n.t('Credit')}</Table.Head>
						<Table.Head class="min-w-28 text-right">{$i18n.t('Running Balance')}</Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each accountData.entries as entry}
						<Table.Row class={entry.status === 'voided' ? 'text-muted-foreground' : ''}>
							<Table.Cell class="tabular-nums">
								<span class="inline-flex items-center gap-1.5">
									{entry.transaction_date}
									{#if entry.status === 'voided'}
										{@render voidedBadge(
											$i18n.t(
												'This entry was voided; its reversal cancels it. Both are kept for the audit trail and net to zero.'
											)
										)}
									{/if}
								</span>
							</Table.Cell>
							{#if hasSubAccounts}
								<Table.Cell>
									{#if entry.account_code}
										<span class="font-mono text-[13px]">{entry.account_code}</span>
										<span class="ml-1 text-xs text-muted-foreground"
											>{entry.account_name ?? ''}</span
										>
									{/if}
								</Table.Cell>
							{/if}
							<Table.Cell class="font-mono text-[13px]">
								{#if entry.k4mi_document_id}
									<K4miDocLink
										docId={entry.k4mi_document_id}
										title={$i18n.t('Open in K4mi')}
										extraClass="inline-flex items-center gap-1 text-link underline-offset-4 hover:underline"
										>{entry.reference ?? ''}<ExternalLink
											class="size-3"
											aria-hidden="true"
										/></K4miDocLink
									>
								{:else}{entry.reference ?? ''}{/if}
							</Table.Cell>
							<Table.Cell class="max-w-[28rem] truncate">{entry.description ?? ''}</Table.Cell>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={entry.debit} {...fxProps} /></Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={entry.credit} {...fxProps} /></Table.Cell
							>
							<Table.Cell class="text-right font-medium tabular-nums"
								><ReportAmount value={entry.running_balance} {...fxProps} /></Table.Cell
							>
						</Table.Row>
					{:else}
						<Table.Row class="hover:bg-transparent">
							<Table.Cell
								colspan={hasSubAccounts ? 7 : 6}
								class="py-6 text-center text-muted-foreground"
								>{$i18n.t('No journal entries found.')}</Table.Cell
							>
						</Table.Row>
					{/each}
				</Table.Body>
				<Table.Footer>
					<Table.Row class="hover:bg-transparent">
						<Table.Cell colspan={hasSubAccounts ? 6 : 5}>{$i18n.t('Closing Balance')}</Table.Cell>
						<Table.Cell class="text-right tabular-nums"
							><ReportAmount value={accountData.closing_balance} {...fxProps} /></Table.Cell
						>
					</Table.Row>
				</Table.Footer>
			</Table.Root>
		</div>

		{#if accountData.total > accountPerPage}
			{@render pager(accountPage, accountData.total, accountPerPage, (p) => {
				accountPage = p;
				load();
			})}
		{/if}
	{:else}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><BookOpen /></Empty.Media>
				<Empty.Title>{$i18n.t('General Ledger')}</Empty.Title>
				<Empty.Description>
					{mode === 'account'
						? $i18n.t('Select an account, then Load.')
						: $i18n.t('Choose dates, then Load.')}
				</Empty.Description>
			</Empty.Header>
		</Empty.Root>
	{/if}
</div>
