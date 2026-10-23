<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { buildMonthOptions, type MonthOption } from '$lib/utils/fiscalYear';
	import { toast } from 'svelte-sonner';
	import {
		getTrialBalance,
		getPeriods,
		getCompany,
		exportTrialBalance
	} from '$lib/apis/accounting';
	import type { Writable } from 'svelte/store';
	import { convertAmount } from '$lib/utils/currency';
	import ReportAmount from '$lib/components/accounting/ReportAmount.svelte';

	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import Download from '@lucide/svelte/icons/download';
	import Scale from '@lucide/svelte/icons/scale';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import FileSpreadsheet from '@lucide/svelte/icons/file-spreadsheet';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
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

	// Display-currency conversion, driven by the company-wide selector. The report
	// arrives in the company base currency; when a different display currency is
	// selected we scale every money field by the base→display rate as of `as_of`.
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
	$: fxProps = { factor, converting, displayCcy, baseCcy };
	$: data = rawData;

	let selectedMonth = '';
	let monthOptions: MonthOption[] = [];

	// Manual override mode
	let manualMode = false;
	let manualPeriodStart = '';
	let manualAsOf = '';
	let manualYtdStart = '';

	let fiscalStartMonth = 1;

	onMount(async () => {
		try {
			const [res, co] = await Promise.all([
				getPeriods({ company_id: companyId }),
				getCompany(companyId).catch(() => null)
			]);
			const periods = res.periods ?? res ?? [];
			fiscalStartMonth = Number(co?.fiscal_year_start_month ?? 1) || 1;
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
	});

	const load = async () => {
		let periodStart: string | undefined;
		let asOf: string | undefined;
		let ytdStart: string | undefined;

		if (manualMode) {
			periodStart = manualPeriodStart || undefined;
			asOf = manualAsOf || undefined;
			ytdStart = manualYtdStart || undefined;
		} else {
			const opt = monthOptions.find((o) => o.value === selectedMonth);
			if (!opt) {
				toast.error($i18n.t('Please select a period'));
				return;
			}
			periodStart = opt.from;
			asOf = opt.to;
			ytdStart = opt.fiscalStart;
		}

		loading = true;
		loadError = '';
		try {
			rawData = await getTrialBalance({
				company_id: companyId,
				as_of: asOf,
				period_start: periodStart,
				ytd_start: ytdStart
			});
		} catch (err) {
			loadError = `${err}`;
			toast.error(`${err}`);
		}
		loading = false;
	};

	const doExport = () => {
		const opt = monthOptions.find((o) => o.value === selectedMonth);
		exportTrialBalance({
			company_id: companyId,
			as_of: manualMode ? manualAsOf : opt?.to,
			period_start: manualMode ? manualPeriodStart : opt?.from,
			ytd_start: manualMode ? manualYtdStart : opt?.fiscalStart
		});
	};

	$: selectedOpt = monthOptions.find((o) => o.value === selectedMonth);

	// Dense report table: 13px, 6px row padding, 12px at the outer edges (design system → Reports).
	const TABLE =
		'text-[13px] [&_td]:py-1.5 [&_td:first-child]:pl-3 [&_th:first-child]:pl-3 [&_td:last-child]:pr-3 [&_th:last-child]:pr-3';
	const NUM_HEAD = 'min-w-24 text-right whitespace-normal leading-tight';
</script>

<div class="flex min-w-0 flex-col gap-4">
	<div class="flex flex-wrap items-end gap-2">
		{#if !manualMode}
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
				<span class="flex h-8 items-center text-sm text-muted-foreground"
					>{$i18n.t('No periods defined')}</span
				>
			{/if}
		{:else}
			<div class="grid gap-1.5">
				<Label for="tb-period-start">{$i18n.t('Period Start')}</Label>
				<Input id="tb-period-start" type="date" class="h-8 w-40" bind:value={manualPeriodStart} />
			</div>
			<div class="grid gap-1.5">
				<Label for="tb-as-of">{$i18n.t('As Of (Period End)')}</Label>
				<Input id="tb-as-of" type="date" class="h-8 w-40" bind:value={manualAsOf} />
			</div>
			<div class="grid gap-1.5">
				<Label for="tb-ytd-start">{$i18n.t('Fiscal Year Start')}</Label>
				<Input
					id="tb-ytd-start"
					type="date"
					class="h-8 w-40"
					placeholder={$i18n.t('YTD')}
					bind:value={manualYtdStart}
				/>
			</div>
		{/if}
		<Button size="sm" disabled={loading || (!manualMode && !selectedMonth)} onclick={load}>
			{#if loading}<Spinner />{/if}
			{$i18n.t('Generate', { context: 'gnos3' })}
		</Button>
		{#if data}
			<Button variant="outline" size="sm" onclick={doExport}>
				<Download />
				{$i18n.t('Export Excel')}
			</Button>
		{/if}
		<Button variant="ghost" size="sm" onclick={() => (manualMode = !manualMode)}>
			{manualMode ? $i18n.t('Use Period Selector') : $i18n.t('Manual Dates')}
		</Button>
	</div>
	{#if !manualMode && selectedOpt}
		<p class="-mt-2 text-sm text-muted-foreground tabular-nums">
			{$i18n.t('Period')}: {selectedOpt.from} — {selectedOpt.to} · {$i18n.t('Fiscal Year Start')}: {selectedOpt.fiscalStart}
		</p>
	{/if}

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
	{:else if data}
		{#if !data.is_balanced}
			<Alert.Root variant="destructive">
				<CircleAlert />
				<Alert.Title>{$i18n.t('Unbalanced')}</Alert.Title>
				<Alert.Description>
					{$i18n.t('Total debits do not equal total credits. Review the entries of this period.')}
				</Alert.Description>
			</Alert.Root>
		{/if}

		<div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
			<span class="font-medium text-foreground">{$i18n.t('Trial Balance')}</span>
			{#if displayCcy}<Badge variant="outline">{displayCcy}</Badge>{/if}
			{#if noRate}
				<span
					class="inline-flex items-center gap-1 text-foreground"
					title={$i18n.t('Add a rate in Settings → Exchange Rates')}
				>
					<TriangleAlert class="size-4 text-warning" />
					({$i18n.t('no rate for')}
					{$displayCurrency}, {$i18n.t('showing')}
					{baseCcy})
				</span>
			{/if}
			{#if data.period_label}<span>{$i18n.t('Period')}: {data.period_label}</span>{/if}
			{#if data.period_start}<span class="tabular-nums">({data.period_start} — {data.as_of})</span>
			{:else}<span class="tabular-nums">{$i18n.t('As of')} {data.as_of}</span>{/if}
			{#if data.opening_balance_date}<span class="tabular-nums"
					>{$i18n.t('Opening as of')} {data.opening_balance_date}</span
				>{/if}
		</div>

		{#if (data.rows ?? []).length === 0}
			<Empty.Root class="border border-dashed">
				<Empty.Header>
					<Empty.Media variant="icon"><FileSpreadsheet /></Empty.Media>
					<Empty.Title>{$i18n.t('No balances for this period.')}</Empty.Title>
					<Empty.Description>{$i18n.t('Post entries, or pick another period.')}</Empty.Description>
				</Empty.Header>
			</Empty.Root>
		{:else}
			<div class="overflow-hidden rounded-md border">
				<Table.Root class={TABLE}>
					<Table.Header class="bg-muted/50">
						<Table.Row class="hover:bg-transparent">
							{#if data.period_label}<Table.Head>{$i18n.t('Period')}</Table.Head>{/if}
							<Table.Head>{$i18n.t('Account Code')}</Table.Head>
							<Table.Head>{$i18n.t('Account Name')}</Table.Head>
							<Table.Head class={NUM_HEAD}>{$i18n.t('Opening Bal. (DR)')}</Table.Head>
							<Table.Head class={NUM_HEAD}>{$i18n.t('Opening Bal. (CR)')}</Table.Head>
							<Table.Head class={NUM_HEAD}>{$i18n.t('Movement (DR)')}</Table.Head>
							<Table.Head class={NUM_HEAD}>{$i18n.t('Movement (CR)')}</Table.Head>
							<Table.Head class={NUM_HEAD}>{$i18n.t('Accum. YTD (DR)')}</Table.Head>
							<Table.Head class={NUM_HEAD}>{$i18n.t('Accum. YTD (CR)')}</Table.Head>
							<Table.Head class={NUM_HEAD}>{$i18n.t('Ending Bal. (DR)')}</Table.Head>
							<Table.Head class={NUM_HEAD}>{$i18n.t('Ending Bal. (CR)')}</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each data.rows as row}
							<Table.Row class={row.is_parent ? 'bg-muted/30 font-medium' : ''}>
								{#if data.period_label}<Table.Cell class="text-muted-foreground tabular-nums"
										>{data.period_label}</Table.Cell
									>{/if}
								<Table.Cell
									class="font-mono text-[13px]"
									style="padding-left: {12 + (row.level || 0) * 16}px"
									>{row.account_code}</Table.Cell
								>
								<Table.Cell>{row.account_name}</Table.Cell>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={row.opening_debit} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={row.opening_credit} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={row.movement_debit} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={row.movement_credit} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={row.accumulated_debit} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={row.accumulated_credit} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={row.ending_debit} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={row.ending_credit} {...fxProps} /></Table.Cell
								>
							</Table.Row>
						{/each}
					</Table.Body>
					<Table.Footer>
						<Table.Row class="hover:bg-transparent">
							<Table.Cell colspan={data.period_label ? 3 : 2}>
								<span class="inline-flex items-center gap-2">
									{$i18n.t('Total')}
									{#if data.is_balanced}
										<Badge variant="status" class="font-medium">
											<Scale class="text-success" aria-hidden="true" />{$i18n.t('Balanced')}
										</Badge>
									{:else}
										<Badge variant="danger">
											<CircleAlert aria-hidden="true" />{$i18n.t('Unbalanced')}
										</Badge>
									{/if}
								</span>
							</Table.Cell>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={data.total_opening_debit} {...fxProps} /></Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={data.total_opening_credit} {...fxProps} /></Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={data.total_movement_debit} {...fxProps} /></Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={data.total_movement_credit} {...fxProps} /></Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={data.total_accumulated_debit} {...fxProps} /></Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={data.total_accumulated_credit} {...fxProps} /></Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={data.total_debit} {...fxProps} /></Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={data.total_credit} {...fxProps} /></Table.Cell
							>
						</Table.Row>
					</Table.Footer>
				</Table.Root>
			</div>
		{/if}
	{:else}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><FileSpreadsheet /></Empty.Media>
				<Empty.Title>{$i18n.t('Trial Balance')}</Empty.Title>
				<Empty.Description>{$i18n.t('Choose a period, then Generate.')}</Empty.Description>
			</Empty.Header>
		</Empty.Root>
	{/if}
</div>
