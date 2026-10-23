<script lang="ts">
	// Statutory financial statements — the fixed-line filings a jurisdiction
	// prescribes, as opposed to the account-by-account reports next door. Which
	// layout applies is decided by the company's country on the backend: China
	// (小企业会计准则, assets side by side with liabilities + equity) and Hong Kong
	// (SME-FRS, one vertical column down to net assets, then equity). The
	// component renders whatever line list the API returns.
	import { onMount, getContext } from 'svelte';
	import { buildMonthOptions, type MonthOption } from '$lib/utils/fiscalYear';
	import { toast } from 'svelte-sonner';
	import type { Writable } from 'svelte/store';

	import {
		getPeriods,
		getCompany,
		getStatutoryBalanceSheet,
		getStatutoryProfitLoss,
		exportStatutoryBalanceSheet,
		exportStatutoryProfitLoss,
		type StatementLine
	} from '$lib/apis/accounting';
	import { convertAmount } from '$lib/utils/currency';
	import ReportAmount from '$lib/components/accounting/ReportAmount.svelte';

	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import Download from '@lucide/svelte/icons/download';
	import Scale from '@lucide/svelte/icons/scale';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import FileSpreadsheet from '@lucide/svelte/icons/file-spreadsheet';

	import { Button } from '$lib/components/ui/button/index.js';
	import * as Tabs from '$lib/components/ui/tabs/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { cn } from '$lib/utils/shadcn.js';

	const i18n: any = getContext('i18n');
	export let companyId: number;
	export let layoutLabel: string | null = null;
	export let layoutKey: string | null = null;
	export let presentation: 'side_by_side' | 'vertical' | null = null;

	$: hk = layoutKey === 'hk_sme';
	$: vertical = (presentation ?? (hk ? 'vertical' : 'side_by_side')) === 'vertical';
	$: tabs = hk
		? [
				{ id: 'balance-sheet', label: 'Statement of Financial Position' },
				{ id: 'profit-loss', label: 'Statement of Profit or Loss' }
			]
		: [
				{ id: 'balance-sheet', label: 'Balance Sheet' },
				{ id: 'profit-loss', label: 'Profit & Loss' }
			];

	type Which = 'balance-sheet' | 'profit-loss';
	let which: Which = 'balance-sheet';
	let loading = false;
	let loadError = '';
	let bs: any = null;
	let pl: any = null;

	const displayCurrency = getContext<Writable<string>>('displayCurrency');
	const exchangeRates = getContext<Writable<any[]>>('exchangeRates');
	const companyCurrency = getContext<Writable<string>>('companyCurrency');

	$: active = which === 'balance-sheet' ? bs : pl;
	$: baseCcy = active?.currency || $companyCurrency || 'CNY';
	$: converting = !!($displayCurrency && baseCcy && $displayCurrency !== baseCcy);
	$: fx =
		converting && active
			? convertAmount(1, baseCcy, $displayCurrency, $exchangeRates ?? [], active?.as_of)
			: null;
	$: fxProps = {
		factor: converting ? (fx?.hasRate ? fx.rate : null) : 1,
		converting,
		displayCcy: converting ? $displayCurrency : baseCcy,
		baseCcy
	};

	let selectedMonth = '';
	let monthOptions: MonthOption[] = [];

	onMount(async () => {
		try {
			const [res, co] = await Promise.all([
				getPeriods({ company_id: companyId }),
				getCompany(companyId).catch(() => null)
			]);
			monthOptions = buildMonthOptions(
				res.periods ?? res ?? [],
				Number(co?.fiscal_year_start_month ?? 1) || 1
			);
			const now = new Date();
			const curKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
			selectedMonth =
				monthOptions.find((o) => o.value === curKey)?.value ?? monthOptions[0]?.value ?? '';
			if (selectedMonth) await load();
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
			if (which === 'balance-sheet') {
				bs = await getStatutoryBalanceSheet({ company_id: companyId, as_of: opt.to });
			} else {
				pl = await getStatutoryProfitLoss({ company_id: companyId, as_of: opt.to });
			}
		} catch (err) {
			loadError = `${err}`;
			toast.error(`${err}`);
		}
		loading = false;
	};

	const doExport = async () => {
		const opt = monthOptions.find((o) => o.value === selectedMonth);
		if (!opt) return;
		if (which === 'balance-sheet')
			await exportStatutoryBalanceSheet({ company_id: companyId, as_of: opt.to });
		else await exportStatutoryProfitLoss({ company_id: companyId, as_of: opt.to });
	};

	// Reload when the statement or the month changes.
	$: if (selectedMonth && which) {
		load();
	}

	// Lines read in the UI language. The layout's own Chinese wording is the
	// official one, so it is used as is when the UI is in that script (CAS lines
	// are Simplified, HK lines Traditional); every other language translates the
	// English line. The Excel export keeps both, as filed.
	$: officialZh = $i18n.language === (hk ? 'zh-TW' : 'zh-CN');
	$: label = (l: StatementLine) => (officialZh ? l.label_zh : $i18n.t(l.label_en)).trim();
	const visible = (rows: any[]) => (rows ?? []).filter((l: any) => !l.hidden);
	const monthHeader = (m: string) => (m.includes('-') ? m : `${pl?.fiscal_year}/${m}`);
	const rowClass = (l: StatementLine) =>
		l.header
			? 'bg-muted/50 font-medium hover:bg-muted/50'
			: l.is_total
				? 'border-t font-semibold'
				: l.memo
					? 'text-muted-foreground'
					: '';

	$: monthsShown = pl ? (pl.months ?? []).slice(0, pl.months_through ?? 12) : [];

	// Dense report table: 13px, 6px row padding, 12px at the outer edges (design system → Reports).
	const TABLE =
		'text-[13px] [&_td]:py-1.5 [&_td:first-child]:pl-3 [&_th:first-child]:pl-3 [&_td:last-child]:pr-3 [&_th:last-child]:pr-3';
</script>

{#snippet unmappedAlert(unmapped: any[])}
	<Alert.Root variant="warning">
		<TriangleAlert />
		<Alert.Title class="whitespace-normal"
			>{$i18n.t('Accounts with no dedicated line, included under an "other" line:')}</Alert.Title
		>
		<Alert.Description class="font-mono text-[13px]">
			{unmapped.map((u: any) => `${u.account_code}`).join(', ')}
		</Alert.Description>
	</Alert.Root>
{/snippet}

<div class="flex min-w-0 flex-col gap-4">
	<!-- Controls -->
	<div class="flex flex-wrap items-center gap-x-3 gap-y-2">
		<!-- Which statement: line tabs, so they don't read as one control with the report picker above
		     (bottom padding keeps the underline inside the scrolling list) -->
		<Tabs.Root value={which} onValueChange={(v) => (which = v as Which)} class="max-w-full min-w-0">
			<Tabs.List
				variant="line"
				aria-label={layoutLabel ?? undefined}
				class="max-w-full justify-start overflow-x-auto pb-[6px] [scrollbar-width:none]"
			>
				{#each tabs as t}
					<Tabs.Trigger value={t.id} class="flex-none px-2">{$i18n.t(t.label)}</Tabs.Trigger>
				{/each}
			</Tabs.List>
		</Tabs.Root>

		<div class="flex flex-wrap items-center gap-2">
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
					{#each monthOptions as o}
						<NativeSelect.Option value={o.value}>{o.label}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
			</div>

			<Button variant="outline" size="sm" onclick={doExport} disabled={!active}>
				<Download />
				{$i18n.t('Export Excel')}
			</Button>

			{#if layoutLabel}
				<span class="text-sm text-muted-foreground">{layoutLabel}</span>
			{/if}
		</div>
	</div>

	{#if loading}
		<div class="flex max-w-4xl flex-col gap-2 rounded-md border p-3">
			{#each Array(12) as _}
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
	{:else if which === 'balance-sheet' && bs}
		{#if !bs.is_balanced}
			<Alert.Root variant="destructive">
				<CircleAlert />
				<Alert.Title class="whitespace-normal">
					{$i18n.t(
						'Assets do not equal liabilities plus equity. The ledger detail behind one of the lines needs review.'
					)}
				</Alert.Title>
			</Alert.Root>
		{:else}
			<p class="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
				<Scale class="size-4 shrink-0 text-success" aria-hidden="true" />
				{$i18n.t('Balanced — total assets equal liabilities plus equity in both columns')}
			</p>
		{/if}
		{#if bs.unmapped?.length}
			{@render unmappedAlert(bs.unmapped)}
		{/if}

		<div class={cn('grid min-w-0 grid-cols-1 items-start gap-4', !vertical && 'xl:grid-cols-2')}>
			{#each vertical ? [{ title: `${bs.company_name} — ${$i18n.t('as at')} ${bs.as_of}`, rows: [...visible(bs.assets), ...visible(bs.liabilities), ...visible(bs.equity)] }] : [{ title: $i18n.t('ASSETS'), rows: bs.assets }, { title: $i18n.t('LIABILITIES AND EQUITY'), rows: [...bs.liabilities, ...bs.equity] }] as block}
				<div class={cn('min-w-0 overflow-hidden rounded-md border', vertical && 'max-w-4xl')}>
					<Table.Root class={TABLE}>
						<Table.Header class="bg-muted/50">
							<Table.Row class="hover:bg-transparent">
								<Table.Head class="whitespace-normal">{block.title}</Table.Head>
								<Table.Head class="w-12 text-center"
									>{$i18n.t(vertical ? 'Note' : 'Line', { context: 'gnos3' })}</Table.Head
								>
								{#if vertical}
									<Table.Head class="w-28 min-w-24 text-right tabular-nums">{bs.as_of}</Table.Head>
									<Table.Head class="w-28 min-w-24 text-right tabular-nums"
										>{bs.beginning_date}</Table.Head
									>
								{:else}
									<Table.Head class="w-28 min-w-24 text-right tabular-nums"
										>{bs.beginning_date}</Table.Head
									>
									<Table.Head class="w-28 min-w-24 text-right tabular-nums">{bs.as_of}</Table.Head>
								{/if}
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each block.rows as l}
								<Table.Row class={rowClass(l)}>
									<Table.Cell
										class="min-w-48 whitespace-normal"
										style="padding-left: {0.75 + l.indent * 1}rem">{label(l)}</Table.Cell
									>
									<Table.Cell class="text-center font-normal text-muted-foreground tabular-nums"
										>{l.line_no ?? ''}</Table.Cell
									>
									<Table.Cell class="text-right tabular-nums">
										{#if !l.header}<ReportAmount
												value={vertical ? l.ending : l.beginning}
												{...fxProps}
											/>{/if}
									</Table.Cell>
									<Table.Cell class="text-right tabular-nums">
										{#if !l.header}<ReportAmount
												value={vertical ? l.beginning : l.ending}
												{...fxProps}
											/>{/if}
									</Table.Cell>
								</Table.Row>
							{/each}
						</Table.Body>
					</Table.Root>
				</div>
			{/each}
		</div>
	{:else if which === 'profit-loss' && pl}
		{#if pl.unmapped?.length}
			{@render unmappedAlert(pl.unmapped)}
		{/if}
		<div class="min-w-0 overflow-hidden rounded-md border">
			<Table.Root class={TABLE}>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						<Table.Head>{$i18n.t('Item')}</Table.Head>
						<Table.Head class="w-12 text-center">{$i18n.t(hk ? 'Note' : 'Line', { context: 'gnos3' })}</Table.Head>
						{#each monthsShown as m}
							<Table.Head class="w-28 min-w-28 text-right tabular-nums">{monthHeader(m)}</Table.Head
							>
						{/each}
						<Table.Head class="w-32 min-w-28 text-right font-semibold tabular-nums"
							>YTD {pl.fiscal_year}</Table.Head
						>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each visible(pl.lines) as l}
						<Table.Row class={rowClass(l)}>
							<Table.Cell
								class="min-w-48 whitespace-normal"
								style="padding-left: {0.75 + l.indent * 1}rem">{label(l)}</Table.Cell
							>
							<Table.Cell class="text-center font-normal text-muted-foreground tabular-nums"
								>{l.line_no ?? ''}</Table.Cell
							>
							{#each monthsShown as m}
								<Table.Cell class="text-right tabular-nums">
									<ReportAmount value={l.months?.[m]} {...fxProps} />
								</Table.Cell>
							{/each}
							<Table.Cell class="text-right font-semibold tabular-nums">
								<ReportAmount value={l.ytd} {...fxProps} />
							</Table.Cell>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</div>
	{:else}
		<Empty.Root class="max-w-4xl border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><FileSpreadsheet /></Empty.Media>
				<Empty.Description>{$i18n.t('Select a period to build the statement.')}</Empty.Description>
			</Empty.Header>
		</Empty.Root>
	{/if}
</div>
