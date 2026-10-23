<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { buildMonthOptions, type MonthOption } from '$lib/utils/fiscalYear';
	import { toast } from 'svelte-sonner';
	import { getCashFlow, getPeriods, getCompany, exportCashFlow } from '$lib/apis/accounting';
	import type { Writable } from 'svelte/store';
	import { convertAmount } from '$lib/utils/currency';
	import ReportAmount from '$lib/components/accounting/ReportAmount.svelte';

	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import Download from '@lucide/svelte/icons/download';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import FileSpreadsheet from '@lucide/svelte/icons/file-spreadsheet';

	import { Button } from '$lib/components/ui/button/index.js';
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

	// Display-currency conversion (company-wide selector). Cash Flow figures are raw
	// debit/credit sums (base currency for a single-currency company); scale by the
	// base→display rate as of the period end when a display currency is selected.
	const displayCurrency = getContext<Writable<string>>('displayCurrency');
	const exchangeRates = getContext<Writable<any[]>>('exchangeRates');
	const companyCurrency = getContext<Writable<string>>('companyCurrency');

	$: baseCcy = $companyCurrency || 'EUR';
	$: converting = !!($displayCurrency && baseCcy && $displayCurrency !== baseCcy);
	$: fx =
		converting && rawData
			? convertAmount(1, baseCcy, $displayCurrency, $exchangeRates ?? [], rawData?.date_to)
			: null;
	$: factor = converting ? (fx?.hasRate ? fx.rate : null) : 1;
	$: noRate = converting && !fx?.hasRate;
	$: displayCcy = converting ? $displayCurrency : baseCcy;
	$: fxProps = { factor, converting, displayCcy, baseCcy, zeroText: null };
	$: data = rawData;

	let selectedMonth = '';
	let monthOptions: MonthOption[] = [];

	let fiscalStartMonth = 1;

	const load = async () => {
		const opt = monthOptions.find((o) => o.value === selectedMonth);
		if (!opt) {
			toast.error($i18n.t('Please select a period'));
			return;
		}
		loading = true;
		loadError = '';
		try {
			rawData = await getCashFlow({ company_id: companyId, date_from: opt.from, date_to: opt.to });
		} catch (err) {
			loadError = `${err}`;
			toast.error(`${err}`);
		}
		loading = false;
	};

	const doExport = () => {
		const opt = monthOptions.find((o) => o.value === selectedMonth);
		if (opt) exportCashFlow({ company_id: companyId, date_from: opt.from, date_to: opt.to });
	};

	// Dense report table: 13px, 6px row padding, 12px at the outer edges (design system → Reports).
	const TABLE =
		'text-[13px] [&_td]:py-1.5 [&_td:first-child]:pl-3 [&_th:first-child]:pl-3 [&_td:last-child]:pr-3 [&_th:last-child]:pr-3';

	onMount(async () => {
		try {
			const [res, co] = await Promise.all([
				getPeriods({ company_id: companyId }),
				getCompany(companyId).catch(() => null)
			]);
			const periods = res.periods ?? res ?? [];
			fiscalStartMonth = Number(co?.fiscal_year_start_month ?? 1) || 1;
			monthOptions = buildMonthOptions(periods, fiscalStartMonth);
			if (monthOptions.length > 0) selectedMonth = monthOptions[0].value;
		} catch {}
	});
</script>

{#snippet group(label: string)}
	<Table.Row class="bg-muted/50 font-medium hover:bg-muted/50">
		<Table.Cell colspan={2}>{label}</Table.Cell>
	</Table.Row>
{/snippet}

{#snippet line(label: string, value: any)}
	<Table.Row>
		<Table.Cell style="padding-left: 32px">{label}</Table.Cell>
		<Table.Cell class="text-right tabular-nums"><ReportAmount {value} {...fxProps} /></Table.Cell>
	</Table.Row>
{/snippet}

{#snippet accountLine(item: any)}
	<Table.Row>
		<Table.Cell class="whitespace-normal" style="padding-left: 32px">
			<span class="font-mono text-[13px] text-muted-foreground">{item.account_code}</span>
			{item.account_name}
		</Table.Cell>
		<Table.Cell class="text-right tabular-nums"
			><ReportAmount value={item.change} {...fxProps} /></Table.Cell
		>
	</Table.Row>
{/snippet}

{#snippet subtotal(label: string, value: any)}
	<Table.Row class="border-t font-medium">
		<Table.Cell>{label}</Table.Cell>
		<Table.Cell class="text-right tabular-nums"><ReportAmount {value} {...fxProps} /></Table.Cell>
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
					aria-label={$i18n.t('Period')}
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

	{#if data && displayCcy && !loading && !loadError}
		<div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
			<span>{$i18n.t('Currency')}: {displayCcy}</span>
			{#if noRate}
				<span class="inline-flex items-center gap-1 text-foreground">
					<TriangleAlert class="size-4 text-warning" />
					({$i18n.t('no rate for')}
					{$displayCurrency}, {$i18n.t('showing')}
					{baseCcy})
				</span>
			{/if}
		</div>
	{/if}

	{#if loading}
		<div class="flex max-w-3xl flex-col gap-2 rounded-md border p-3">
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
	{:else if data}
		<div class="max-w-3xl min-w-0 overflow-hidden rounded-md border">
			<Table.Root class={TABLE}>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						<Table.Head>{$i18n.t('Item')}</Table.Head>
						<Table.Head class="w-40 min-w-32 text-right">{$i18n.t('Amount')}</Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					<!-- Operating Activities -->
					{@render group($i18n.t('Operating Activities'))}
					{@render line($i18n.t('Net Income'), data.net_income)}
					{#if data.depreciation}
						{@render line($i18n.t('Add: Depreciation'), data.depreciation)}
					{/if}
					{#each data.working_capital_changes ?? [] as item}
						{@render accountLine(item)}
					{/each}
					{@render subtotal($i18n.t('Cash from Operations'), data.cash_from_operations)}

					<!-- Investing Activities -->
					{@render group($i18n.t('Investing Activities'))}
					{#each data.investing_activities ?? [] as item}
						{@render accountLine(item)}
					{/each}
					{@render subtotal($i18n.t('Cash from Investing'), data.cash_from_investing)}

					<!-- Financing Activities -->
					{@render group($i18n.t('Financing Activities'))}
					{#each data.financing_activities ?? [] as item}
						{@render accountLine(item)}
					{/each}
					{@render subtotal($i18n.t('Cash from Financing'), data.cash_from_financing)}
				</Table.Body>
				<!-- Summary -->
				<Table.Footer>
					<Table.Row class="font-semibold hover:bg-transparent">
						<Table.Cell>{$i18n.t('Net Change in Cash')}</Table.Cell>
						<Table.Cell class="text-right tabular-nums"
							><ReportAmount value={data.net_change_in_cash} {...fxProps} /></Table.Cell
						>
					</Table.Row>
					<Table.Row class="hover:bg-transparent">
						<Table.Cell>{$i18n.t('Opening Cash')}</Table.Cell>
						<Table.Cell class="text-right tabular-nums"
							><ReportAmount value={data.opening_cash} {...fxProps} /></Table.Cell
						>
					</Table.Row>
					<Table.Row class="border-t font-semibold hover:bg-transparent">
						<Table.Cell>{$i18n.t('Closing Cash')}</Table.Cell>
						<Table.Cell class="text-right tabular-nums"
							><ReportAmount value={data.closing_cash} {...fxProps} /></Table.Cell
						>
					</Table.Row>
				</Table.Footer>
			</Table.Root>
		</div>
	{:else}
		<Empty.Root class="max-w-3xl border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><FileSpreadsheet /></Empty.Media>
				<Empty.Title>{$i18n.t('Cash Flow')}</Empty.Title>
				<Empty.Description>{$i18n.t('Choose a period, then Generate.')}</Empty.Description>
			</Empty.Header>
		</Empty.Root>
	{/if}
</div>
