<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { buildMonthOptions, type MonthOption } from '$lib/utils/fiscalYear';
	import { toast } from 'svelte-sonner';
	import { getProfitLoss, getPeriods, getCompany, exportProfitLoss } from '$lib/apis/accounting';
	import type { Writable } from 'svelte/store';
	import { convertAmount } from '$lib/utils/currency';
	import ReportAmount from '$lib/components/accounting/ReportAmount.svelte';

	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import Download from '@lucide/svelte/icons/download';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import FileSpreadsheet from '@lucide/svelte/icons/file-spreadsheet';

	import { Button } from '$lib/components/ui/button/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';

	const i18n: any = getContext('i18n');
	export let companyId: number;

	let loading = false;
	let loadError = '';
	let rawData: any = null;
	let companyCountry: string = '';
	let isFrench = false;

	// Display-currency conversion (company-wide selector). P&L arrives in the base
	// currency; scale money fields by the base→display rate as of the period end.
	const displayCurrency = getContext<Writable<string>>('displayCurrency');
	const exchangeRates = getContext<Writable<any[]>>('exchangeRates');
	const companyCurrency = getContext<Writable<string>>('companyCurrency');

	$: baseCcy = rawData?.currency || $companyCurrency || 'EUR';
	$: converting = !!($displayCurrency && baseCcy && $displayCurrency !== baseCcy);
	$: fx =
		converting && rawData
			? convertAmount(1, baseCcy, $displayCurrency, $exchangeRates ?? [], rawData?.date_to)
			: null;
	$: factor = converting ? (fx?.hasRate ? fx.rate : null) : 1;
	$: noRate = converting && !fx?.hasRate;
	$: displayCcy = converting ? $displayCurrency : baseCcy;
	// English number format uses '—' for zero (2 dp); French format is blank + 0 dp, fr-FR locale.
	$: fxProps = { factor, converting, displayCcy, baseCcy, zeroText: '—' };
	$: fxPropsFr = {
		factor,
		converting,
		displayCcy,
		baseCcy,
		zeroText: '',
		minFrac: 0,
		maxFrac: 0,
		locale: 'fr-FR'
	};
	$: data = rawData;

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
			companyCountry = company?.country ?? '';
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
			rawData = await getProfitLoss({
				company_id: companyId,
				date_from: opt.from,
				date_to: opt.to,
				ytd_start: opt.fiscalStart
			});
		} catch (err) {
			loadError = `${err}`;
			toast.error(`${err}`);
		}
		loading = false;
	};

	const isCostAccount = (code: string, name: string): boolean => {
		const c = code.replace(/\./g, '');
		const lname = name.toLowerCase();
		return (
			c.startsWith('54') ||
			c.startsWith('59') ||
			lname.includes('cost') ||
			lname.includes('coût') ||
			lname.includes('cogs')
		);
	};

	const isTaxSurcharge = (code: string, name: string): boolean => {
		const lname = name.toLowerCase();
		return lname.includes('tax') && (lname.includes('surcharge') || lname.includes('附加'));
	};

	const isFinancialExpense = (code: string, name: string): boolean => {
		const c = code.replace(/\./g, '');
		const lname = name.toLowerCase();
		return (
			c.startsWith('56') ||
			c.startsWith('66') ||
			lname.includes('financial') ||
			lname.includes('financ')
		);
	};

	// === French PCG classification helpers ===

	function pcgPrefix(code: string): number {
		const c = code.replace(/\./g, '');
		return parseInt(c.substring(0, 2)) || 0;
	}

	function isFrenchOperatingRevenue(code: string): boolean {
		const p = pcgPrefix(code);
		return p >= 70 && p <= 75;
	}

	function isFrenchOperatingExpense(code: string): boolean {
		const p = pcgPrefix(code);
		return p >= 60 && p <= 65;
	}

	function isFrenchFinancialRevenue(code: string): boolean {
		return pcgPrefix(code) === 76;
	}

	function isFrenchFinancialExpense(code: string): boolean {
		return pcgPrefix(code) === 66;
	}

	function isFrenchExceptionalRevenue(code: string): boolean {
		return pcgPrefix(code) === 77;
	}

	function isFrenchExceptionalExpense(code: string): boolean {
		return pcgPrefix(code) === 67;
	}

	function isFrenchIncomeTax(code: string): boolean {
		return pcgPrefix(code) === 69;
	}

	function buildFrenchStructured(d: any) {
		// Leaf accounts only — parent rows carry rolled-up subtotals from the
		// backend, so including them in category sums would double-count.
		const allRevenue = (d.revenue ?? []).filter((e: any) => !e.is_parent);
		const allExpenses = (d.expenses ?? []).filter((e: any) => !e.is_parent);

		const sumAmt = (items: any[]) =>
			items.reduce((s: number, e: any) => s + (parseFloat(e.amount) || 0), 0);
		const sumYtd = (items: any[]) =>
			items.reduce((s: number, e: any) => s + (parseFloat(e.ytd_amount) || 0), 0);

		// Operating
		const operatingRevenue = allRevenue.filter((e: any) =>
			isFrenchOperatingRevenue(e.account_code)
		);
		const operatingExpenses = allExpenses.filter((e: any) =>
			isFrenchOperatingExpense(e.account_code)
		);
		const totalOpRevenue = sumAmt(operatingRevenue);
		const totalOpRevenueYtd = sumYtd(operatingRevenue);
		const totalOpExpenses = sumAmt(operatingExpenses);
		const totalOpExpensesYtd = sumYtd(operatingExpenses);
		const resultatExploitation = totalOpRevenue - totalOpExpenses;
		const resultatExploitationYtd = totalOpRevenueYtd - totalOpExpensesYtd;

		// Financial
		const financialRevenue = allRevenue.filter((e: any) =>
			isFrenchFinancialRevenue(e.account_code)
		);
		const financialExpenses = allExpenses.filter((e: any) =>
			isFrenchFinancialExpense(e.account_code)
		);
		const totalFinRevenue = sumAmt(financialRevenue);
		const totalFinRevenueYtd = sumYtd(financialRevenue);
		const totalFinExpenses = sumAmt(financialExpenses);
		const totalFinExpensesYtd = sumYtd(financialExpenses);
		const resultatFinancier = totalFinRevenue - totalFinExpenses;
		const resultatFinancierYtd = totalFinRevenueYtd - totalFinExpensesYtd;

		// Exceptional
		const exceptionalRevenue = allRevenue.filter((e: any) =>
			isFrenchExceptionalRevenue(e.account_code)
		);
		const exceptionalExpenses = allExpenses.filter((e: any) =>
			isFrenchExceptionalExpense(e.account_code)
		);
		const totalExcRevenue = sumAmt(exceptionalRevenue);
		const totalExcRevenueYtd = sumYtd(exceptionalRevenue);
		const totalExcExpenses = sumAmt(exceptionalExpenses);
		const totalExcExpensesYtd = sumYtd(exceptionalExpenses);
		const resultatExceptionnel = totalExcRevenue - totalExcExpenses;
		const resultatExceptionnelYtd = totalExcRevenueYtd - totalExcExpensesYtd;

		// Income Tax
		const incomeTax = allExpenses.filter((e: any) => isFrenchIncomeTax(e.account_code));
		const totalIncomeTax = sumAmt(incomeTax);
		const totalIncomeTaxYtd = sumYtd(incomeTax);

		// Uncategorized (safety net)
		const categorizedRevCodes = new Set(
			[...operatingRevenue, ...financialRevenue, ...exceptionalRevenue].map(
				(e: any) => e.account_code
			)
		);
		const categorizedExpCodes = new Set(
			[...operatingExpenses, ...financialExpenses, ...exceptionalExpenses, ...incomeTax].map(
				(e: any) => e.account_code
			)
		);
		const uncategorizedRevenue = allRevenue.filter(
			(e: any) => !categorizedRevCodes.has(e.account_code)
		);
		const uncategorizedExpenses = allExpenses.filter(
			(e: any) => !categorizedExpCodes.has(e.account_code)
		);
		const totalUncatRevenue = sumAmt(uncategorizedRevenue);
		const totalUncatRevenueYtd = sumYtd(uncategorizedRevenue);
		const totalUncatExpenses = sumAmt(uncategorizedExpenses);
		const totalUncatExpensesYtd = sumYtd(uncategorizedExpenses);

		// Résultat courant avant impôts
		const resultatCourant = resultatExploitation + resultatFinancier;
		const resultatCourantYtd = resultatExploitationYtd + resultatFinancierYtd;

		// Total des produits / charges
		const totalProduits = totalOpRevenue + totalFinRevenue + totalExcRevenue + totalUncatRevenue;
		const totalProduitsYtd =
			totalOpRevenueYtd + totalFinRevenueYtd + totalExcRevenueYtd + totalUncatRevenueYtd;
		const totalCharges =
			totalOpExpenses + totalFinExpenses + totalExcExpenses + totalIncomeTax + totalUncatExpenses;
		const totalChargesYtd =
			totalOpExpensesYtd +
			totalFinExpensesYtd +
			totalExcExpensesYtd +
			totalIncomeTaxYtd +
			totalUncatExpensesYtd;

		// Net Income
		const netIncome = totalProduits - totalCharges;
		const netIncomeYtd = totalProduitsYtd - totalChargesYtd;

		return {
			operatingRevenue,
			operatingExpenses,
			totalOpRevenue,
			totalOpRevenueYtd,
			totalOpExpenses,
			totalOpExpensesYtd,
			resultatExploitation,
			resultatExploitationYtd,
			financialRevenue,
			financialExpenses,
			totalFinRevenue,
			totalFinRevenueYtd,
			totalFinExpenses,
			totalFinExpensesYtd,
			resultatFinancier,
			resultatFinancierYtd,
			exceptionalRevenue,
			exceptionalExpenses,
			totalExcRevenue,
			totalExcRevenueYtd,
			totalExcExpenses,
			totalExcExpensesYtd,
			resultatExceptionnel,
			resultatExceptionnelYtd,
			resultatCourant,
			resultatCourantYtd,
			incomeTax,
			totalIncomeTax,
			totalIncomeTaxYtd,
			uncategorizedRevenue,
			uncategorizedExpenses,
			totalUncatRevenue,
			totalUncatRevenueYtd,
			totalUncatExpenses,
			totalUncatExpensesYtd,
			totalProduits,
			totalProduitsYtd,
			totalCharges,
			totalChargesYtd,
			netIncome,
			netIncomeYtd
		};
	}

	let structured: any = null;
	$: structured = data ? (isFrench ? buildFrenchStructured(data) : buildStructured(data)) : null;

	function buildStructured(d: any) {
		// Leaf accounts only — parent rows carry rolled-up subtotals from the
		// backend, so summing them with their children would double-count.
		const revenue = (d.revenue ?? []).filter((e: any) => !e.is_parent);
		const expenses = (d.expenses ?? []).filter((e: any) => !e.is_parent);

		const costs = expenses.filter((e: any) => isCostAccount(e.account_code, e.account_name));
		const taxes = expenses.filter((e: any) => isTaxSurcharge(e.account_code, e.account_name));
		const financial = expenses.filter((e: any) =>
			isFinancialExpense(e.account_code, e.account_name)
		);
		const operating = expenses.filter(
			(e: any) =>
				!isCostAccount(e.account_code, e.account_name) &&
				!isTaxSurcharge(e.account_code, e.account_name) &&
				!isFinancialExpense(e.account_code, e.account_name)
		);

		const sumAmt = (items: any[]) =>
			items.reduce((s: number, e: any) => s + (parseFloat(e.amount) || 0), 0);
		const sumYtd = (items: any[]) =>
			items.reduce((s: number, e: any) => s + (parseFloat(e.ytd_amount) || 0), 0);

		const totalRevenue = parseFloat(d.total_revenue) || 0;
		const totalRevenueYtd = parseFloat(d.total_revenue_ytd) || 0;
		const totalCosts = sumAmt(costs);
		const totalCostsYtd = sumYtd(costs);
		const totalTaxes = sumAmt(taxes);
		const totalTaxesYtd = sumYtd(taxes);
		const grossProfit = totalRevenue - totalCosts - totalTaxes;
		const grossProfitYtd = totalRevenueYtd - totalCostsYtd - totalTaxesYtd;
		const totalOperating = sumAmt(operating);
		const totalOperatingYtd = sumYtd(operating);
		const totalFinancial = sumAmt(financial);
		const totalFinancialYtd = sumYtd(financial);
		const operatingProfit = grossProfit - totalOperating - totalFinancial;
		const operatingProfitYtd = grossProfitYtd - totalOperatingYtd - totalFinancialYtd;
		const netIncome = parseFloat(d.net_income) || 0;
		const netIncomeYtd = parseFloat(d.net_income_ytd) || 0;

		return {
			revenue,
			costs,
			taxes,
			operating,
			financial,
			totalRevenue,
			totalRevenueYtd,
			totalCosts,
			totalCostsYtd,
			totalTaxes,
			totalTaxesYtd,
			grossProfit,
			grossProfitYtd,
			totalOperating,
			totalOperatingYtd,
			totalFinancial,
			totalFinancialYtd,
			operatingProfit,
			operatingProfitYtd,
			netIncome,
			netIncomeYtd
		};
	}

	$: selectedLabel = monthOptions.find((o) => o.value === selectedMonth)?.label ?? '';
	$: selectedFiscalStart = monthOptions.find((o) => o.value === selectedMonth)?.fiscalStart ?? '';

	let lineNo = 0;
	function nextLine(): number {
		return ++lineNo;
	}
	function resetLines() {
		lineNo = 0;
	}

	// === French format helpers ===
	let collapsedSections = new Set<string>();

	function toggleSection(key: string) {
		if (collapsedSections.has(key)) {
			collapsedSections.delete(key);
		} else {
			collapsedSections.add(key);
		}
		collapsedSections = collapsedSections; // trigger reactivity
	}

	const doExport = () => {
		const opt = monthOptions.find((o) => o.value === selectedMonth);
		if (opt)
			exportProfitLoss({
				company_id: companyId,
				date_from: opt.from,
				date_to: opt.to,
				ytd_start: opt.fiscalStart
			});
	};

	// Dense report table inside a card: 13px, 6px row padding, card-edge padding at both ends.
	const TABLE =
		'text-[13px] [&_td]:py-1.5 [&_td:first-child]:pl-6 [&_th:first-child]:pl-6 [&_td:last-child]:pr-6 [&_th:last-child]:pr-6';
</script>

<!-- French Compte de résultat: a collapsible section, its account lines, subtotals and results -->
{#snippet frSection(key: string, label: string, total: number, totalYtd: number)}
	{@const collapsed = collapsedSections.has(key)}
	<Table.Row class="cursor-pointer bg-muted/50 font-medium" onclick={() => toggleSection(key)}>
		<Table.Cell>
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
		</Table.Cell>
		{#if collapsed}
			<Table.Cell class="text-right tabular-nums"
				><ReportAmount value={total} {...fxPropsFr} /></Table.Cell
			>
			<Table.Cell class="text-right tabular-nums"
				><ReportAmount value={totalYtd} {...fxPropsFr} /></Table.Cell
			>
		{:else}
			<Table.Cell></Table.Cell>
			<Table.Cell></Table.Cell>
		{/if}
	</Table.Row>
{/snippet}

{#snippet frItem(item: any, indented: boolean, muted: boolean)}
	<Table.Row class={muted ? 'text-muted-foreground' : ''}>
		<Table.Cell style={indented ? `padding-left: ${32 + (item.level ?? 0) * 16}px` : undefined}
			>{item.account_name}</Table.Cell
		>
		<Table.Cell class="text-right tabular-nums"
			><ReportAmount value={item.amount} {...fxPropsFr} /></Table.Cell
		>
		<Table.Cell class="text-right tabular-nums"
			><ReportAmount value={item.ytd_amount} {...fxPropsFr} /></Table.Cell
		>
	</Table.Row>
{/snippet}

{#snippet frLine(label: string, value: number, valueYtd: number, strong: boolean)}
	<Table.Row class="border-t {strong ? 'font-semibold' : 'font-medium'}">
		<Table.Cell>{label}</Table.Cell>
		<Table.Cell class="text-right tabular-nums"><ReportAmount {value} {...fxPropsFr} /></Table.Cell>
		<Table.Cell class="text-right tabular-nums"
			><ReportAmount value={valueYtd} {...fxPropsFr} /></Table.Cell
		>
	</Table.Row>
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
					aria-label={$i18n.t('Month')}
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
		{#if structured}
			<Button variant="outline" size="sm" onclick={doExport}>
				<Download />
				{$i18n.t('Export Excel')}
			</Button>
		{/if}
	</div>

	{#if loading}
		<div class="flex max-w-4xl flex-col gap-2 rounded-xl border p-4">
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
	{:else if structured}
		{@const _ = resetLines()}

		<Card.Root class="max-w-4xl min-w-0 gap-4 overflow-hidden pb-0">
			<Card.Header>
				<Card.Title class="text-base"
					>{isFrench ? $i18n.t('Income statement') : $i18n.t('Profit & Loss')}</Card.Title
				>
				<Card.Description class="flex flex-wrap items-center gap-x-2 gap-y-1 tabular-nums">
					<span>{selectedLabel}</span>
					{#if displayCcy}<span>· {$i18n.t('Currency')}: {displayCcy}</span>{/if}
					{#if noRate}
						<span class="inline-flex items-center gap-1 text-foreground">
							<TriangleAlert class="size-4 text-warning" />
							({$i18n.t('no rate for')}
							{$displayCurrency}, {$i18n.t('showing')}
							{baseCcy})
						</span>
					{/if}
				</Card.Description>
			</Card.Header>
			<Card.Content class="px-0">
				{#if isFrench}
					<!-- ========== FRENCH FORMAT: Compte de Résultat (HACANTHE) ========== -->
					<Table.Root class={TABLE}>
						<Table.Header class="bg-muted/50">
							<Table.Row class="hover:bg-transparent">
								<Table.Head class="h-auto py-2"
									><span class="sr-only">{$i18n.t('Income statement')}</span></Table.Head
								>
								<Table.Head class="h-auto w-36 min-w-28 py-2 text-right">
									<div>{$i18n.t('Current Period')}</div>
									<div class="text-xs font-normal text-muted-foreground">{selectedLabel}</div>
								</Table.Head>
								<Table.Head class="h-auto w-36 min-w-28 py-2 text-right">
									<div>{$i18n.t('Year to Date')}</div>
									<div class="text-xs font-normal text-muted-foreground tabular-nums">
										{selectedFiscalStart} — {data.date_to}
									</div>
								</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							<!-- ===== 1. Produits d'exploitation ===== -->
							{@render frSection(
								'prodExpl',
								$i18n.t('Operating income'),
								structured.totalOpRevenue,
								structured.totalOpRevenueYtd
							)}
							{#if !collapsedSections.has('prodExpl')}
								{#each structured.operatingRevenue as item}
									{@render frItem(item, true, false)}
								{/each}
								{@render frLine(
									$i18n.t('TOTAL OPERATING INCOME'),
									structured.totalOpRevenue,
									structured.totalOpRevenueYtd,
									false
								)}
							{/if}

							<!-- ===== 2. Charges d'exploitation ===== -->
							{@render frSection(
								'charExpl',
								$i18n.t('Operating expenses'),
								structured.totalOpExpenses,
								structured.totalOpExpensesYtd
							)}
							{#if !collapsedSections.has('charExpl')}
								{#each structured.operatingExpenses as item}
									{@render frItem(item, true, false)}
								{/each}
								{@render frLine(
									$i18n.t('TOTAL OPERATING EXPENSES'),
									structured.totalOpExpenses,
									structured.totalOpExpensesYtd,
									false
								)}
							{/if}

							<!-- ===== 3. RÉSULTAT D'EXPLOITATION ===== -->
							{@render frLine(
								$i18n.t('OPERATING RESULT'),
								structured.resultatExploitation,
								structured.resultatExploitationYtd,
								true
							)}

							<!-- ===== 4. Produits financiers ===== -->
							{@render frSection(
								'prodFin',
								$i18n.t('Financial income'),
								structured.totalFinRevenue,
								structured.totalFinRevenueYtd
							)}
							{#if !collapsedSections.has('prodFin')}
								{#each structured.financialRevenue as item}
									{@render frItem(item, true, false)}
								{/each}
								{@render frLine(
									$i18n.t('TOTAL FINANCIAL INCOME'),
									structured.totalFinRevenue,
									structured.totalFinRevenueYtd,
									false
								)}
							{/if}

							<!-- ===== 5. Charges financières ===== -->
							{@render frSection(
								'charFin',
								$i18n.t('Financial expenses'),
								structured.totalFinExpenses,
								structured.totalFinExpensesYtd
							)}
							{#if !collapsedSections.has('charFin')}
								{#each structured.financialExpenses as item}
									{@render frItem(item, true, false)}
								{/each}
								{@render frLine(
									$i18n.t('TOTAL FINANCIAL EXPENSES'),
									structured.totalFinExpenses,
									structured.totalFinExpensesYtd,
									false
								)}
							{/if}

							<!-- ===== 6. RÉSULTAT FINANCIER ===== -->
							{@render frLine(
								$i18n.t('FINANCIAL RESULT'),
								structured.resultatFinancier,
								structured.resultatFinancierYtd,
								true
							)}

							<!-- ===== 7. RÉSULTAT COURANT AVANT IMPÔTS ===== -->
							{@render frLine(
								$i18n.t('ORDINARY RESULT BEFORE TAX'),
								structured.resultatCourant,
								structured.resultatCourantYtd,
								true
							)}

							<!-- ===== 8. Produits exceptionnels ===== -->
							{@render frSection(
								'prodExc',
								$i18n.t('Exceptional income'),
								structured.totalExcRevenue,
								structured.totalExcRevenueYtd
							)}
							{#if !collapsedSections.has('prodExc')}
								{#each structured.exceptionalRevenue as item}
									{@render frItem(item, true, false)}
								{/each}
								{@render frLine(
									$i18n.t('TOTAL EXCEPTIONAL INCOME'),
									structured.totalExcRevenue,
									structured.totalExcRevenueYtd,
									false
								)}
							{/if}

							<!-- ===== 9. Charges exceptionnelles ===== -->
							{@render frSection(
								'charExc',
								$i18n.t('Exceptional expenses'),
								structured.totalExcExpenses,
								structured.totalExcExpensesYtd
							)}
							{#if !collapsedSections.has('charExc')}
								{#each structured.exceptionalExpenses as item}
									{@render frItem(item, true, false)}
								{/each}
								{@render frLine(
									$i18n.t('TOTAL EXCEPTIONAL EXPENSES'),
									structured.totalExcExpenses,
									structured.totalExcExpensesYtd,
									false
								)}
							{/if}

							<!-- ===== 10. RÉSULTAT EXCEPTIONNEL ===== -->
							{@render frLine(
								$i18n.t('EXCEPTIONAL RESULT'),
								structured.resultatExceptionnel,
								structured.resultatExceptionnelYtd,
								true
							)}

							<!-- ===== 11. Participation & Impôts ===== -->
							{#each structured.incomeTax as item}
								{@render frItem(item, false, false)}
							{/each}

							<!-- Uncategorized (safety net) -->
							{#each structured.uncategorizedRevenue as item}
								{@render frItem(item, false, true)}
							{/each}
							{#each structured.uncategorizedExpenses as item}
								{@render frItem(item, false, true)}
							{/each}

							<!-- ===== 12. TOTAL DES PRODUITS ===== -->
							{@render frLine(
								$i18n.t('TOTAL INCOME'),
								structured.totalProduits,
								structured.totalProduitsYtd,
								true
							)}

							<!-- ===== 13. TOTAL DES CHARGES ===== -->
							{@render frLine(
								$i18n.t('TOTAL EXPENSES'),
								structured.totalCharges,
								structured.totalChargesYtd,
								true
							)}
						</Table.Body>

						<!-- ===== 14. BÉNÉFICE OU PERTE ===== -->
						<Table.Footer class="font-semibold">
							<Table.Row class="hover:bg-transparent">
								<Table.Cell class="whitespace-normal"
									>{$i18n.t(
										'PROFIT OR LOSS (total income − total expenses)'
									)}</Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={structured.netIncome} {...fxPropsFr} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={structured.netIncomeYtd} {...fxPropsFr} /></Table.Cell
								>
							</Table.Row>
						</Table.Footer>
					</Table.Root>
				{:else}
					<!-- ========== DEFAULT FORMAT (US/other) ========== -->
					<Table.Root class={TABLE}>
						<Table.Header class="bg-muted/50">
							<Table.Row class="hover:bg-transparent">
								<Table.Head class="h-auto py-2"
									><span class="sr-only">{$i18n.t('PROFIT & LOSS')}</span></Table.Head
								>
								<Table.Head class="h-auto w-10 py-2 text-center">#</Table.Head>
								<Table.Head class="h-auto w-36 min-w-28 py-2 text-right">
									<div>{$i18n.t('Current Period')}</div>
									<div class="text-xs font-normal text-muted-foreground">{selectedLabel}</div>
								</Table.Head>
								<Table.Head class="h-auto w-36 min-w-28 py-2 text-right">
									<div>{$i18n.t('Year to Date')}</div>
									<div class="text-xs font-normal text-muted-foreground tabular-nums">
										{selectedFiscalStart} — {data.date_to}
									</div>
								</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							<!-- Revenue -->
							<Table.Row class="font-medium">
								<Table.Cell>{$i18n.t('Revenue')}</Table.Cell>
								<Table.Cell class="text-center text-muted-foreground tabular-nums"
									>{nextLine()}</Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={structured.totalRevenue} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={structured.totalRevenueYtd} {...fxProps} /></Table.Cell
								>
							</Table.Row>
							{#each structured.revenue as item}
								<Table.Row>
									<Table.Cell style="padding-left: {32 + item.level * 16}px"
										>{item.account_name}</Table.Cell
									>
									<Table.Cell class="text-center text-muted-foreground tabular-nums"
										>{nextLine()}</Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										><ReportAmount value={item.amount} {...fxProps} /></Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										><ReportAmount value={item.ytd_amount} {...fxProps} /></Table.Cell
									>
								</Table.Row>
							{/each}

							<!-- Cost of sales -->
							{#if structured.costs.length > 0}
								<Table.Row>
									<Table.Cell class="text-muted-foreground"
										>{$i18n.t('Less: Cost of sales')}</Table.Cell
									>
									<Table.Cell class="text-center text-muted-foreground tabular-nums"
										>{nextLine()}</Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										><ReportAmount value={structured.totalCosts} {...fxProps} /></Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										><ReportAmount value={structured.totalCostsYtd} {...fxProps} /></Table.Cell
									>
								</Table.Row>
								{#each structured.costs as item}
									<Table.Row>
										<Table.Cell style="padding-left: {40 + item.level * 16}px"
											>{item.account_name}</Table.Cell
										>
										<Table.Cell class="text-center text-muted-foreground tabular-nums"
											>{nextLine()}</Table.Cell
										>
										<Table.Cell class="text-right tabular-nums"
											><ReportAmount value={item.amount} {...fxProps} /></Table.Cell
										>
										<Table.Cell class="text-right tabular-nums"
											><ReportAmount value={item.ytd_amount} {...fxProps} /></Table.Cell
										>
									</Table.Row>
								{/each}
							{/if}

							<!-- Taxes and surcharges -->
							{#if structured.taxes.length > 0}
								<Table.Row>
									<Table.Cell class="text-muted-foreground"
										>{$i18n.t('Less: Taxes and surcharges')}</Table.Cell
									>
									<Table.Cell class="text-center text-muted-foreground tabular-nums"
										>{nextLine()}</Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										><ReportAmount value={structured.totalTaxes} {...fxProps} /></Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										><ReportAmount value={structured.totalTaxesYtd} {...fxProps} /></Table.Cell
									>
								</Table.Row>
							{/if}

							<!-- Gross Profit -->
							<Table.Row class="border-t font-semibold">
								<Table.Cell>{$i18n.t('Gross Profit')}</Table.Cell>
								<Table.Cell class="text-center font-normal text-muted-foreground tabular-nums"
									>{nextLine()}</Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={structured.grossProfit} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={structured.grossProfitYtd} {...fxProps} /></Table.Cell
								>
							</Table.Row>

							<!-- Operating expenses -->
							{#if structured.operating.length > 0}
								<Table.Row>
									<Table.Cell class="text-muted-foreground"
										>{$i18n.t('Less: Operating expenses')}</Table.Cell
									>
									<Table.Cell class="text-center text-muted-foreground tabular-nums"
										>{nextLine()}</Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										><ReportAmount value={structured.totalOperating} {...fxProps} /></Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										><ReportAmount value={structured.totalOperatingYtd} {...fxProps} /></Table.Cell
									>
								</Table.Row>
								{#each structured.operating as item}
									<Table.Row>
										<Table.Cell style="padding-left: {40 + item.level * 16}px"
											>{item.account_name}</Table.Cell
										>
										<Table.Cell class="text-center text-muted-foreground tabular-nums"
											>{nextLine()}</Table.Cell
										>
										<Table.Cell class="text-right tabular-nums"
											><ReportAmount value={item.amount} {...fxProps} /></Table.Cell
										>
										<Table.Cell class="text-right tabular-nums"
											><ReportAmount value={item.ytd_amount} {...fxProps} /></Table.Cell
										>
									</Table.Row>
								{/each}
							{/if}

							<!-- Financial expenses -->
							{#if structured.financial.length > 0}
								<Table.Row>
									<Table.Cell class="text-muted-foreground"
										>{$i18n.t('Less: Financial expenses')}</Table.Cell
									>
									<Table.Cell class="text-center text-muted-foreground tabular-nums"
										>{nextLine()}</Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										><ReportAmount value={structured.totalFinancial} {...fxProps} /></Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										><ReportAmount value={structured.totalFinancialYtd} {...fxProps} /></Table.Cell
									>
								</Table.Row>
							{/if}

							<!-- Operating Profit -->
							<Table.Row class="border-t font-semibold">
								<Table.Cell>{$i18n.t('Operating Profit')}</Table.Cell>
								<Table.Cell class="text-center font-normal text-muted-foreground tabular-nums"
									>{nextLine()}</Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={structured.operatingProfit} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={structured.operatingProfitYtd} {...fxProps} /></Table.Cell
								>
							</Table.Row>
						</Table.Body>
						<Table.Footer class="font-semibold">
							<Table.Row class="hover:bg-transparent">
								<Table.Cell colspan={2}>{$i18n.t('Net Income')}</Table.Cell>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={structured.netIncome} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={structured.netIncomeYtd} {...fxProps} /></Table.Cell
								>
							</Table.Row>
						</Table.Footer>
					</Table.Root>
				{/if}
			</Card.Content>
		</Card.Root>
	{:else}
		<Empty.Root class="max-w-4xl border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><FileSpreadsheet /></Empty.Media>
				<Empty.Title>{$i18n.t('Profit & Loss')}</Empty.Title>
				<Empty.Description>{$i18n.t('Choose a period, then Generate.')}</Empty.Description>
			</Empty.Header>
		</Empty.Root>
	{/if}
</div>
