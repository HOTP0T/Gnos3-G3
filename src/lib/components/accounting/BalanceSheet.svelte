<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { buildMonthOptions, type MonthOption } from '$lib/utils/fiscalYear';
	import { toast } from 'svelte-sonner';
	import {
		getBalanceSheet,
		getPeriods,
		getCompany,
		exportBalanceSheet
	} from '$lib/apis/accounting';
	import type { Writable } from 'svelte/store';
	import { convertAmount } from '$lib/utils/currency';
	import ReportAmount from '$lib/components/accounting/ReportAmount.svelte';

	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import Download from '@lucide/svelte/icons/download';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import Scale from '@lucide/svelte/icons/scale';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import FileSpreadsheet from '@lucide/svelte/icons/file-spreadsheet';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';

	const i18n: any = getContext('i18n');
	export let companyId: number;

	let loading = false;
	let loadError = '';
	let rawData: any = null;
	let isFrench = false;

	// Display-currency conversion (company-wide selector). The balance sheet arrives
	// in the base currency; scale money fields by the base→display rate as of `as_of`.
	const displayCurrency = getContext<Writable<string>>('displayCurrency');
	const exchangeRates = getContext<Writable<any[]>>('exchangeRates');
	const companyCurrency = getContext<Writable<string>>('companyCurrency');

	$: baseCcy = rawData?.currency || $companyCurrency || 'EUR';
	$: converting = !!($displayCurrency && baseCcy && $displayCurrency !== baseCcy);
	$: fx =
		converting && rawData
			? convertAmount(1, baseCcy, $displayCurrency, $exchangeRates ?? [], rawData?.as_of)
			: null;
	$: factor = converting ? (fx?.hasRate ? fx.rate : null) : 1;
	$: noRate = converting && !fx?.hasRate;
	$: displayCcy = converting ? $displayCurrency : baseCcy;
	// English format uses '—' for zero; French format is blank + fr-FR locale (both 2 dp).
	$: fxProps = { factor, converting, displayCcy, baseCcy, zeroText: '—' };
	$: fxPropsFr = { factor, converting, displayCcy, baseCcy, zeroText: '', locale: 'fr-FR' };
	$: data = rawData;

	// Month picker — user picks a month, we derive as_of and period_start from fiscal year
	let selectedMonth = '';
	let monthOptions: MonthOption[] = [];

	let fiscalStartMonth = 1;

	onMount(async () => {
		try {
			const [res, company] = await Promise.all([
				getPeriods({ company_id: companyId }),
				getCompany(companyId)
			]);
			const periods = res.periods ?? res ?? [];
			fiscalStartMonth = Number(company?.fiscal_year_start_month ?? 1) || 1;
			monthOptions = buildMonthOptions(periods, fiscalStartMonth);

			const country = (company?.country ?? '').trim().toLowerCase();
			isFrench = country === 'france' || country === 'fr';

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
	});

	const load = async () => {
		const opt = monthOptions.find((o) => o.value === selectedMonth);
		if (!opt) {
			toast.error($i18n.t('Please select a period'));
			return;
		}
		loading = true;
		loadError = '';
		try {
			rawData = await getBalanceSheet({
				company_id: companyId,
				as_of: opt.asOf,
				period_start: opt.fiscalStart
			});
		} catch (err) {
			loadError = `${err}`;
			toast.error(`${err}`);
		}
		loading = false;
	};

	const doExport = () => {
		const opt = monthOptions.find((o) => o.value === selectedMonth);
		if (opt)
			exportBalanceSheet({ company_id: companyId, as_of: opt.asOf, period_start: opt.fiscalStart });
	};

	const isCurrentAsset = (code: string): boolean => {
		const root = code.replace(/\./g, '');
		const prefix = parseInt(root.substring(0, 2));
		return prefix < 20 || (prefix >= 31 && prefix <= 39);
	};

	const isCurrentLiability = (code: string): boolean => {
		const root = code.replace(/\./g, '');
		const prefix = parseInt(root.substring(0, 2));
		return prefix >= 40 && prefix <= 49;
	};

	// Leaf accounts only — parent rows carry rolled-up subtotals from the backend,
	// so summing them with their children would double-count. Grand totals still
	// come from the backend (data.total_*).
	$: assets = data ? (data.assets ?? []).filter((i: any) => !i.is_parent) : [];
	$: liabilities = data ? (data.liabilities ?? []).filter((i: any) => !i.is_parent) : [];
	$: equity = data ? (data.equity ?? []).filter((i: any) => !i.is_parent) : [];
	$: assetGroups = data ? groupAssets(assets) : { current: [], nonCurrent: [] };
	$: liabGroups = data ? groupLiabilities(liabilities) : { current: [], nonCurrent: [] };
	$: selectedLabel = monthOptions.find((o) => o.value === selectedMonth)?.label ?? '';

	function groupAssets(items: any[]) {
		const current = items.filter((i: any) => isCurrentAsset(i.account_code));
		const nonCurrent = items.filter((i: any) => !isCurrentAsset(i.account_code));
		return { current, nonCurrent };
	}

	function groupLiabilities(items: any[]) {
		const current = items.filter((i: any) => isCurrentLiability(i.account_code));
		const nonCurrent = items.filter((i: any) => !isCurrentLiability(i.account_code));
		return { current, nonCurrent };
	}

	const sumBeg = (items: any[]): number =>
		items.reduce((s: number, i: any) => s + (parseFloat(i.beginning_balance) || 0), 0);
	const sumEnd = (items: any[]): number =>
		items.reduce((s: number, i: any) => s + (parseFloat(i.balance) || 0), 0);

	// === French Bilan grouping ===

	function frPcgPrefix(code: string): number {
		const c = code.replace(/\./g, '');
		return parseInt(c.substring(0, 2)) || 0;
	}

	function frPcgPrefix3(code: string): number {
		const c = code.replace(/\./g, '');
		return parseInt(c.substring(0, 3)) || 0;
	}

	// Amortization/depreciation estimation (accounts 28x, 29x, 39x offset their parent asset)
	function isAmortAccount(code: string): boolean {
		const c = code.replace(/\./g, '');
		return c.startsWith('28') || c.startsWith('29') || c.startsWith('39');
	}

	const sumAmort = (items: any[]): number => {
		return items
			.filter((i: any) => isAmortAccount(i.account_code))
			.reduce((s: number, i: any) => s + Math.abs(parseFloat(i.balance) || 0), 0);
	};

	// Collapsible sections
	let collapsedSections = new Set<string>();

	function toggleSection(key: string) {
		if (collapsedSections.has(key)) {
			collapsedSections.delete(key);
		} else {
			collapsedSections.add(key);
		}
		collapsedSections = collapsedSections; // trigger reactivity
	}

	// --- French Bilan Actif grouping ---
	interface FrenchActifGroups {
		immoIncorporelles: any[];
		immoCorporelles: any[];
		immoFinancieres: any[];
		stocks: any[];
		creances: any[];
		valeursMob: any[];
		disponibilites: any[];
		chargesConstatees: any[];
		otherAssets: any[];
	}

	function buildFrenchActifGroups(items: any[]): FrenchActifGroups {
		const groups: FrenchActifGroups = {
			immoIncorporelles: [],
			immoCorporelles: [],
			immoFinancieres: [],
			stocks: [],
			creances: [],
			valeursMob: [],
			disponibilites: [],
			chargesConstatees: [],
			otherAssets: []
		};
		for (const item of items) {
			const p2 = frPcgPrefix(item.account_code);
			const p3 = frPcgPrefix3(item.account_code);
			if (p2 === 20 || (p2 === 21 && p3 <= 212)) {
				groups.immoIncorporelles.push(item);
			} else if ((p2 === 21 && p3 > 212) || p2 === 22 || p2 === 23) {
				groups.immoCorporelles.push(item);
			} else if (p2 === 26 || p2 === 27) {
				groups.immoFinancieres.push(item);
			} else if (p2 === 28 || p2 === 29) {
				// amortization accounts — attribute to fixed asset groups
				// For simplicity put them in corporelles (they affect Amort column)
				groups.immoCorporelles.push(item);
			} else if (p2 >= 31 && p2 <= 39) {
				groups.stocks.push(item);
			} else if (p2 >= 40 && p2 <= 49) {
				groups.creances.push(item);
			} else if (p2 === 50) {
				groups.valeursMob.push(item);
			} else if (p2 >= 51 && p2 <= 53) {
				groups.disponibilites.push(item);
			} else if (p2 === 48) {
				groups.chargesConstatees.push(item);
			} else {
				groups.otherAssets.push(item);
			}
		}
		return groups;
	}

	// --- French Bilan Passif grouping ---
	interface FrenchPassifGroups {
		capitauxPropres: any[];
		autresFondsPropres: any[];
		provisions: any[];
		empruntsEtDettes: any[];
		otherPassif: any[];
	}

	function buildFrenchPassifGroups(liabilities: any[], equity: any[]): FrenchPassifGroups {
		const groups: FrenchPassifGroups = {
			capitauxPropres: [],
			autresFondsPropres: [],
			provisions: [],
			empruntsEtDettes: [],
			otherPassif: []
		};
		// Equity items
		for (const item of equity) {
			const p2 = frPcgPrefix(item.account_code);
			if (p2 >= 10 && p2 <= 14) {
				groups.capitauxPropres.push(item);
			} else if (p2 === 15) {
				groups.provisions.push(item);
			} else {
				groups.autresFondsPropres.push(item);
			}
		}
		// Liability items
		for (const item of liabilities) {
			const p2 = frPcgPrefix(item.account_code);
			if (p2 === 15) {
				groups.provisions.push(item);
			} else if ((p2 >= 16 && p2 <= 17) || (p2 >= 40 && p2 <= 51)) {
				groups.empruntsEtDettes.push(item);
			} else {
				groups.otherPassif.push(item);
			}
		}
		return groups;
	}

	$: frActif = data && isFrench ? buildFrenchActifGroups(assets) : null;
	$: frPassif = data && isFrench ? buildFrenchPassifGroups(liabilities, equity) : null;

	// Helper: all fixed asset items
	$: frFixedItems = frActif
		? [...frActif.immoIncorporelles, ...frActif.immoCorporelles, ...frActif.immoFinancieres]
		: [];
	$: frCurrentItems = frActif
		? [
				...frActif.stocks,
				...frActif.creances,
				...frActif.valeursMob,
				...frActif.disponibilites,
				...frActif.chargesConstatees,
				...frActif.otherAssets
			]
		: [];

	let lineNo = 0;
	function nextLine(): number {
		return ++lineNo;
	}
	function resetLines() {
		lineNo = 0;
	}

	// Dense report table: 13px, 6px row padding, 12px at the outer edges (design system → Reports).
	const TABLE =
		'text-[13px] [&_td]:py-1.5 [&_td:first-child]:pl-3 [&_th:first-child]:pl-3 [&_td:last-child]:pr-3 [&_th:last-child]:pr-3';
</script>

{#snippet balanceBadge()}
	{#if data.is_balanced}
		<Badge variant="status">
			<Scale class="text-success" aria-hidden="true" />{$i18n.t('Balanced')}
		</Badge>
	{:else}
		<Badge variant="danger"><CircleAlert aria-hidden="true" />{$i18n.t('Unbalanced')}</Badge>
	{/if}
{/snippet}

<!-- French Bilan: a section bar (collapsible when it has a key), account lines, subtotals -->
{#snippet frSection(key: string | null, label: string, colspan: number, total: number | null)}
	{#if key}
		{@const collapsed = collapsedSections.has(key)}
		<Table.Row class="cursor-pointer bg-muted/50 font-medium" onclick={() => toggleSection(key)}>
			<Table.Cell {colspan}>
				<div class="flex items-center justify-between gap-4">
					<button
						type="button"
						class="-ml-1 inline-flex items-center gap-1.5 rounded-sm px-1 text-left focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
						aria-expanded={!collapsed}
						onclick={(e) => {
							e.stopPropagation();
							toggleSection(key);
						}}
					>
						<ChevronDown
							class="size-3.5 text-muted-foreground transition-transform motion-reduce:transition-none {collapsed
								? '-rotate-90'
								: ''}"
							aria-hidden="true"
						/>
						{label}
					</button>
					{#if collapsed && total !== null}
						<span class="tabular-nums"><ReportAmount value={total} {...fxPropsFr} /></span>
					{/if}
				</div>
			</Table.Cell>
		</Table.Row>
	{:else}
		<Table.Row class="bg-muted/50 font-medium hover:bg-muted/50">
			<Table.Cell {colspan}>{label}</Table.Cell>
		</Table.Row>
	{/if}
{/snippet}

{#snippet frGroup(label: string, colspan: number)}
	<Table.Row class="hover:bg-transparent">
		<Table.Cell {colspan} class="pt-3 font-medium" style="padding-left: 24px">{label}</Table.Cell>
	</Table.Row>
{/snippet}

{#snippet actifRow(item: any, pad: number, brut: any, amort: any, net: any)}
	<Table.Row>
		<Table.Cell style="padding-left: {pad}px">{item.account_name}</Table.Cell>
		<Table.Cell class="text-right tabular-nums"
			><ReportAmount value={brut} {...fxPropsFr} /></Table.Cell
		>
		<Table.Cell class="text-right tabular-nums"
			>{#if amort !== null}<ReportAmount value={amort} {...fxPropsFr} />{/if}</Table.Cell
		>
		<Table.Cell class="text-right tabular-nums"
			><ReportAmount value={net} {...fxPropsFr} /></Table.Cell
		>
		<Table.Cell class="text-right tabular-nums"
			><ReportAmount value={item.beginning_balance} {...fxPropsFr} /></Table.Cell
		>
	</Table.Row>
{/snippet}

{#snippet passifRow(item: any)}
	<Table.Row>
		<Table.Cell style="padding-left: 24px">{item.account_name}</Table.Cell>
		<Table.Cell class="text-right tabular-nums"
			><ReportAmount value={item.balance} {...fxPropsFr} /></Table.Cell
		>
		<Table.Cell class="text-right tabular-nums"
			><ReportAmount value={item.beginning_balance} {...fxPropsFr} /></Table.Cell
		>
	</Table.Row>
{/snippet}

<!-- Default format: one account line, a group label, a sub-total -->
{#snippet bsItem(item: any)}
	<Table.Row>
		<Table.Cell style="padding-left: {12 + item.level * 10}px">{item.account_name}</Table.Cell>
		<Table.Cell class="text-center text-muted-foreground tabular-nums">{nextLine()}</Table.Cell>
		<Table.Cell class="text-right tabular-nums"
			><ReportAmount value={item.beginning_balance} {...fxProps} /></Table.Cell
		>
		<Table.Cell class="text-right tabular-nums"
			><ReportAmount value={item.balance} {...fxProps} /></Table.Cell
		>
	</Table.Row>
{/snippet}

{#snippet bsGroup(label: string)}
	<Table.Row class="hover:bg-transparent">
		<Table.Cell colspan={4} class="pt-3 text-xs font-medium text-muted-foreground"
			>{label}</Table.Cell
		>
	</Table.Row>
{/snippet}

{#snippet bsSubtotal(label: string, beg: any, end: any, strong: boolean)}
	<Table.Row class="border-t {strong ? 'font-semibold' : 'font-medium'}">
		<Table.Cell colspan={2}>{label}</Table.Cell>
		<Table.Cell class="text-right tabular-nums"
			><ReportAmount value={beg} {...fxProps} /></Table.Cell
		>
		<Table.Cell class="text-right tabular-nums"
			><ReportAmount value={end} {...fxProps} /></Table.Cell
		>
	</Table.Row>
{/snippet}

{#snippet bsHead()}
	<Table.Header class="bg-muted/50">
		<Table.Row class="hover:bg-transparent">
			<Table.Head><span class="sr-only">{$i18n.t('Account', { context: 'gnos3' })}</span></Table.Head>
			<Table.Head class="w-8 text-center">#</Table.Head>
			<Table.Head class="w-32 min-w-28 text-right">{$i18n.t('Beg. Balance')}</Table.Head>
			<Table.Head class="w-32 min-w-28 text-right">{$i18n.t('End. Balance')}</Table.Head>
		</Table.Row>
	</Table.Header>
{/snippet}

<div class="flex min-w-0 flex-col gap-4">
	<div class="flex flex-wrap items-center gap-2">
		{#if monthOptions.length > 0}
			<div class="relative">
				<CalendarDays
					class="pointer-events-none absolute top-1/2 left-2.5 z-10 size-4 -translate-y-1/2 text-muted-foreground"
				/>
				<NativeSelect.Root
					size="sm"
					class="[&>select]:pl-8"
					bind:value={selectedMonth}
					aria-label={$i18n.t('As of end of')}
					title={$i18n.t('As of end of')}
				>
					{#each monthOptions as opt}
						<NativeSelect.Option value={opt.value}>{opt.label}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
			</div>
		{:else}
			<span class="text-sm text-muted-foreground">{$i18n.t('No accounting periods defined')}</span>
		{/if}
		<Button size="sm" disabled={loading || !selectedMonth} onclick={load}>
			{#if loading}<Spinner />{/if}
			{$i18n.t('Generate', { context: 'gnos3' })}
		</Button>
		{#if data}
			<Button variant="outline" size="sm" onclick={doExport}>
				<Download />
				{$i18n.t('Export Excel')}
			</Button>
		{/if}
	</div>

	{#if loading}
		<div class="grid min-w-0 grid-cols-1 gap-4 md:grid-cols-2">
			{#each [0, 1] as _}
				<div class="flex flex-col gap-2 rounded-md border p-3">
					{#each Array(8) as __}
						<Skeleton class="h-6 w-full" />
					{/each}
				</div>
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
	{:else if data}
		{@const _ = resetLines()}
		<div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
			{#if displayCcy}<span>{$i18n.t('Currency')}: {displayCcy}</span>{/if}
			{#if noRate}
				<span class="inline-flex items-center gap-1 text-foreground">
					<TriangleAlert class="size-4 text-warning" />
					({$i18n.t('no rate for')}
					{$displayCurrency}, {$i18n.t('showing')}
					{baseCcy})
				</span>
			{/if}
			{#if data.opening_balance_date}<span class="tabular-nums"
					>{$i18n.t('Opening balances as of')} {data.opening_balance_date}</span
				>{/if}
		</div>

		{#if isFrench && frActif && frPassif}
			<!-- ========== FRENCH FORMAT: Bilan Actif + Bilan Passif (HACANTHE reference) ========== -->
			{@const fixedGross = sumEnd(frFixedItems.filter((i) => !isAmortAccount(i.account_code)))}
			{@const fixedAmort = sumAmort(frFixedItems)}
			{@const fixedNet = fixedGross - fixedAmort}
			{@const currentGross = sumEnd(frCurrentItems.filter((i) => !isAmortAccount(i.account_code)))}
			{@const currentAmort = sumAmort(frCurrentItems)}
			{@const currentNet = currentGross - currentAmort}
			{@const totalPassif = parseFloat(data.total_liabilities) + parseFloat(data.total_equity)}

			<!-- ===== BILAN ACTIF ===== -->
			<section class="min-w-0 overflow-hidden rounded-md border">
				<div class="flex flex-wrap items-center justify-between gap-2 border-b px-3 py-2.5">
					<h3 class="text-sm font-semibold">{$i18n.t('Balance sheet — Assets')}</h3>
					<span class="text-xs text-muted-foreground tabular-nums"
						>{$i18n.t('As of')} {data.as_of}</span
					>
				</div>
				<Table.Root class={TABLE}>
					<Table.Header class="bg-muted/50">
						<Table.Row class="hover:bg-transparent">
							<Table.Head><span class="sr-only">{$i18n.t('Balance sheet — Assets')}</span></Table.Head>
							<Table.Head class="w-28 min-w-28 text-right">{$i18n.t('Gross')}</Table.Head>
							<Table.Head class="w-28 min-w-28 text-right">{$i18n.t('Depr. & prov.')}</Table.Head>
							<Table.Head class="w-28 min-w-28 text-right">{$i18n.t('Net')}</Table.Head>
							<Table.Head class="w-28 min-w-28 text-right">{$i18n.t('Net (prior year)')}</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						<!-- ── Actif immobilise ── -->
						{@render frSection('actif-immobilise', $i18n.t('Fixed assets'), 5, fixedNet)}
						{#if !collapsedSections.has('actif-immobilise')}
							<!-- Immobilisations incorporelles -->
							{#if frActif.immoIncorporelles.length > 0}
								{@render frGroup($i18n.t('Intangible assets'), 5)}
								{#each frActif.immoIncorporelles as item}
									{@render actifRow(
										item,
										36,
										isAmortAccount(item.account_code) ? 0 : item.balance,
										isAmortAccount(item.account_code) ? Math.abs(parseFloat(item.balance) || 0) : 0,
										item.balance
									)}
								{/each}
							{/if}

							<!-- Immobilisations corporelles -->
							{#if frActif.immoCorporelles.length > 0}
								{@render frGroup($i18n.t('Tangible assets'), 5)}
								{#each frActif.immoCorporelles as item}
									{@render actifRow(
										item,
										36,
										isAmortAccount(item.account_code) ? 0 : item.balance,
										isAmortAccount(item.account_code) ? Math.abs(parseFloat(item.balance) || 0) : 0,
										isAmortAccount(item.account_code) ? 0 : parseFloat(item.balance) || 0
									)}
								{/each}
							{/if}

							<!-- Immobilisations financieres -->
							{#if frActif.immoFinancieres.length > 0}
								{@render frGroup($i18n.t('Financial assets'), 5)}
								{#each frActif.immoFinancieres as item}
									{@render actifRow(
										item,
										36,
										isAmortAccount(item.account_code) ? 0 : item.balance,
										isAmortAccount(item.account_code) ? Math.abs(parseFloat(item.balance) || 0) : 0,
										item.balance
									)}
								{/each}
							{/if}

							<!-- Subtotal: ACTIF IMMOBILISE -->
							<Table.Row class="border-t font-medium">
								<Table.Cell class="text-right">{$i18n.t('TOTAL FIXED ASSETS')}</Table.Cell>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={fixedGross} {...fxPropsFr} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={fixedAmort} {...fxPropsFr} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={fixedNet} {...fxPropsFr} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={sumBeg(frFixedItems)} {...fxPropsFr} /></Table.Cell
								>
							</Table.Row>
						{/if}

						<!-- ── Actif circulant ── -->
						{@render frSection('actif-circulant', $i18n.t('Current assets'), 5, currentNet)}
						{#if !collapsedSections.has('actif-circulant')}
							<!-- Stocks et en-cours -->
							{#if frActif.stocks.length > 0}
								{@render frGroup($i18n.t('Inventories and work in progress'), 5)}
								{#each frActif.stocks as item}
									{@render actifRow(item, 36, item.balance, null, item.balance)}
								{/each}
							{/if}

							<!-- Creances -->
							{#if frActif.creances.length > 0}
								{@render frGroup($i18n.t('Receivables'), 5)}
								{#each frActif.creances as item}
									{@render actifRow(item, 36, item.balance, null, item.balance)}
								{/each}
							{/if}

							<!-- Valeurs mobilieres de placement -->
							{#if frActif.valeursMob.length > 0}
								{@render frGroup($i18n.t('Marketable securities'), 5)}
								{#each frActif.valeursMob as item}
									{@render actifRow(item, 36, item.balance, null, item.balance)}
								{/each}
							{/if}

							<!-- Disponibilites, charges constatees d'avance, other assets -->
							{#each frActif.disponibilites as item}
								{@render actifRow(item, 24, item.balance, null, item.balance)}
							{/each}
							{#each frActif.chargesConstatees as item}
								{@render actifRow(item, 24, item.balance, null, item.balance)}
							{/each}
							{#each frActif.otherAssets as item}
								{@render actifRow(item, 24, item.balance, null, item.balance)}
							{/each}

							<!-- Subtotal: ACTIF CIRCULANT -->
							<Table.Row class="border-t font-medium">
								<Table.Cell class="text-right">{$i18n.t('TOTAL CURRENT ASSETS')}</Table.Cell>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={currentGross} {...fxPropsFr} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={currentAmort} {...fxPropsFr} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={currentNet} {...fxPropsFr} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={sumBeg(frCurrentItems)} {...fxPropsFr} /></Table.Cell
								>
							</Table.Row>
						{/if}
					</Table.Body>
					<Table.Footer class="font-semibold">
						<Table.Row class="hover:bg-transparent">
							<Table.Cell>{$i18n.t('TOTAL ASSETS')}</Table.Cell>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={fixedGross + currentGross} {...fxPropsFr} /></Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={fixedAmort + currentAmort} {...fxPropsFr} /></Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={data.total_assets} {...fxPropsFr} /></Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={sumBeg(assets)} {...fxPropsFr} /></Table.Cell
							>
						</Table.Row>
					</Table.Footer>
				</Table.Root>
			</section>

			<!-- ===== BILAN PASSIF ===== -->
			<section class="min-w-0 overflow-hidden rounded-md border">
				<div class="flex flex-wrap items-center justify-between gap-2 border-b px-3 py-2.5">
					<h3 class="text-sm font-semibold">{$i18n.t('Balance sheet — Liabilities and equity')}</h3>
					{@render balanceBadge()}
				</div>
				<Table.Root class={TABLE}>
					<Table.Header class="bg-muted/50">
						<Table.Row class="hover:bg-transparent">
							<Table.Head><span class="sr-only">{$i18n.t('Balance sheet — Liabilities and equity')}</span></Table.Head>
							<Table.Head class="w-32 min-w-28 text-right">{$i18n.t('Current year')}</Table.Head>
							<Table.Head class="w-32 min-w-28 text-right">{$i18n.t('Prior year')}</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						<!-- ── Capitaux propres ── -->
						{@render frSection(
							'capitaux-propres',
							$i18n.t('Equity'),
							3,
							sumEnd(frPassif.capitauxPropres)
						)}
						{#if !collapsedSections.has('capitaux-propres')}
							{#each frPassif.capitauxPropres as item}
								{@render passifRow(item)}
							{/each}
							<Table.Row class="border-t font-medium">
								<Table.Cell class="text-right">{$i18n.t('TOTAL EQUITY')}</Table.Cell>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount
										value={sumEnd(frPassif.capitauxPropres)}
										{...fxPropsFr}
									/></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount
										value={sumBeg(frPassif.capitauxPropres)}
										{...fxPropsFr}
									/></Table.Cell
								>
							</Table.Row>
						{/if}

						<!-- ── Autres fonds propres ── -->
						{#if frPassif.autresFondsPropres.length > 0}
							{@render frSection(null, $i18n.t('Other equity'), 3, null)}
							{#each frPassif.autresFondsPropres as item}
								{@render passifRow(item)}
							{/each}
						{/if}

						<!-- ── Provisions pour risques et charges ── -->
						{#if frPassif.provisions.length > 0}
							{@render frSection(null, $i18n.t('Provisions for liabilities and charges'), 3, null)}
							{#each frPassif.provisions as item}
								{@render passifRow(item)}
							{/each}
						{/if}

						<!-- ── Emprunts et dettes ── -->
						{@render frSection(
							'emprunts-dettes',
							$i18n.t('Borrowings and payables'),
							3,
							sumEnd(frPassif.empruntsEtDettes)
						)}
						{#if !collapsedSections.has('emprunts-dettes')}
							{#each frPassif.empruntsEtDettes as item}
								{@render passifRow(item)}
							{/each}
							<Table.Row class="border-t font-medium">
								<Table.Cell class="text-right">{$i18n.t('TOTAL BORROWINGS AND PAYABLES')}</Table.Cell>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount
										value={sumEnd(frPassif.empruntsEtDettes)}
										{...fxPropsFr}
									/></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount
										value={sumBeg(frPassif.empruntsEtDettes)}
										{...fxPropsFr}
									/></Table.Cell
								>
							</Table.Row>
						{/if}

						<!-- Other passif -->
						{#each frPassif.otherPassif as item}
							{@render passifRow(item)}
						{/each}
					</Table.Body>
					<Table.Footer class="font-semibold">
						<Table.Row class="hover:bg-transparent">
							<Table.Cell>{$i18n.t('TOTAL LIABILITIES AND EQUITY')}</Table.Cell>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={totalPassif} {...fxPropsFr} /></Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount
									value={sumBeg(liabilities) + sumBeg(equity)}
									{...fxPropsFr}
								/></Table.Cell
							>
						</Table.Row>
					</Table.Footer>
				</Table.Root>
			</section>
		{:else}
			<!-- ========== DEFAULT FORMAT (US/other): Assets left, Liabilities + Equity right ========== -->
			<div class="grid min-w-0 grid-cols-1 items-start gap-4 md:grid-cols-2">
				<!-- LEFT: Assets -->
				<section class="min-w-0 overflow-hidden rounded-md border">
					<div class="flex flex-wrap items-center justify-between gap-2 border-b px-3 py-2.5">
						<h3 class="text-sm font-semibold">{$i18n.t('Assets')}</h3>
						<span class="text-xs text-muted-foreground tabular-nums"
							>{$i18n.t('As of')} {data.as_of}</span
						>
					</div>
					<Table.Root class={TABLE}>
						{@render bsHead()}
						<Table.Body>
							{#if assetGroups.current.length > 0}
								{@render bsGroup($i18n.t('Current assets:'))}
								{#each assetGroups.current as item}
									{@render bsItem(item)}
								{/each}
								{@render bsSubtotal(
									$i18n.t('Sub-total current assets'),
									sumBeg(assetGroups.current),
									sumEnd(assetGroups.current),
									false
								)}
							{/if}

							{#if assetGroups.nonCurrent.length > 0}
								{@render bsGroup($i18n.t('Non-current assets:'))}
								{#each assetGroups.nonCurrent as item}
									{@render bsItem(item)}
								{/each}
								{@render bsSubtotal(
									$i18n.t('Sub-total non-current assets'),
									sumBeg(assetGroups.nonCurrent),
									sumEnd(assetGroups.nonCurrent),
									false
								)}
							{/if}
						</Table.Body>
						<Table.Footer class="font-semibold">
							<Table.Row class="hover:bg-transparent">
								<Table.Cell colspan={2}>{$i18n.t('Total Assets')}</Table.Cell>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={sumBeg(assets)} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={data.total_assets} {...fxProps} /></Table.Cell
								>
							</Table.Row>
						</Table.Footer>
					</Table.Root>
				</section>

				<!-- RIGHT: Liabilities & Equity -->
				<section class="min-w-0 overflow-hidden rounded-md border">
					<div class="flex flex-wrap items-center justify-between gap-2 border-b px-3 py-2.5">
						<h3 class="text-sm font-semibold">{$i18n.t("Liabilities & Owners' Equity")}</h3>
						{@render balanceBadge()}
					</div>
					<Table.Root class={TABLE}>
						{@render bsHead()}
						<Table.Body>
							{#if liabGroups.current.length > 0}
								{@render bsGroup($i18n.t('Current liabilities:'))}
								{#each liabGroups.current as item}
									{@render bsItem(item)}
								{/each}
								{@render bsSubtotal(
									$i18n.t('Sub-total current liabilities'),
									sumBeg(liabGroups.current),
									sumEnd(liabGroups.current),
									false
								)}
							{/if}

							{#if liabGroups.nonCurrent.length > 0}
								{@render bsGroup($i18n.t('Non-current liabilities:'))}
								{#each liabGroups.nonCurrent as item}
									{@render bsItem(item)}
								{/each}
								{@render bsSubtotal(
									$i18n.t('Sub-total non-current liabilities'),
									sumBeg(liabGroups.nonCurrent),
									sumEnd(liabGroups.nonCurrent),
									false
								)}
							{/if}

							{@render bsSubtotal(
								$i18n.t('Total Liabilities'),
								sumBeg(liabilities),
								data.total_liabilities,
								true
							)}

							{#if equity.length > 0}
								{@render bsGroup($i18n.t("Owner's equity:"))}
								{#each equity as item}
									{@render bsItem(item)}
								{/each}
								{@render bsSubtotal(
									$i18n.t("Total Owner's Equity"),
									sumBeg(equity),
									data.total_equity,
									true
								)}
							{/if}
						</Table.Body>
						<Table.Footer class="font-semibold">
							<Table.Row class="hover:bg-transparent">
								<Table.Cell colspan={2}>{$i18n.t('Total Liabilities & Equity')}</Table.Cell>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount
										value={sumBeg(liabilities) + sumBeg(equity)}
										{...fxProps}
									/></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount
										value={parseFloat(data.total_liabilities) + parseFloat(data.total_equity)}
										{...fxProps}
									/></Table.Cell
								>
							</Table.Row>
						</Table.Footer>
					</Table.Root>
				</section>
			</div>
		{/if}
	{:else}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><FileSpreadsheet /></Empty.Media>
				<Empty.Title>{$i18n.t('Balance Sheet')}</Empty.Title>
				<Empty.Description>{$i18n.t('Choose a period, then Generate.')}</Empty.Description>
			</Empty.Header>
		</Empty.Root>
	{/if}
</div>
