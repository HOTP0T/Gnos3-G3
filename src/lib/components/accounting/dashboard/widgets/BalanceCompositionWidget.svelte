<script lang="ts">
	// Balance-sheet composition: Assets vs Liabilities + Equity (stacked columns).
	// Fixed entity colours: assets blue, liabilities orange, equity violet; a 2px surface gap
	// separates the stacked segments.
	import { onMount, getContext } from 'svelte';
	import Scale from '@lucide/svelte/icons/scale';
	import { theme } from '$lib/stores';
	import { getBalanceSheet } from '$lib/apis/accounting';
	import EChart from '../EChart.svelte';
	import WidgetState from '../WidgetState.svelte';
	import { chartTheme, pageIsDark, tooltipStyle, legendStyle, tooltipHtml, SLOT } from '../palette';
	import { fmtNumber, fmtCompact } from '../format';

	export let companyId: number;
	export let options: Record<string, any> = {}; // unused; part of widget contract

	const i18n: any = getContext('i18n');
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);
	$: t = chartTheme(pageIsDark($theme));

	let bs: any = null;
	let currency = '';
	let loading = true;
	let error = false;

	onMount(load);
	async function load() {
		loading = true;
		error = false;
		try {
			bs = await getBalanceSheet({ company_id: companyId });
			currency = bs?.currency ?? '';
		} catch {
			bs = null;
			error = true;
		}
		loading = false;
	}

	$: assets = bs?.total_assets ?? 0;
	$: liabilities = bs?.total_liabilities ?? 0;
	$: equity = bs?.total_equity ?? 0;
	$: hasData = assets || liabilities || equity;

	$: names = { assets: T('Assets'), liabilities: T('Liabilities'), equity: T('Equity') };
	$: segment = (color: string) => ({
		color,
		borderColor: t.surface,
		borderWidth: 1,
		borderRadius: 4
	});

	$: option = {
		grid: { left: 6, right: 8, top: 36, bottom: 0, containLabel: true },
		tooltip: {
			trigger: 'axis',
			axisPointer: { type: 'shadow', shadowStyle: { color: t.band, opacity: 0.8 } },
			...tooltipStyle(t),
			formatter: (params: any[]) =>
				tooltipHtml(
					t,
					params[0]?.axisValueLabel ?? '',
					params
						.filter((p) => Number.isFinite(+p.value) && +p.value !== 0)
						.map((p) => ({
							color: p.color,
							name: p.seriesName,
							value: `${fmtNumber(p.value)} ${currency}`.trim()
						}))
				)
		},
		legend: { ...legendStyle(t), top: 0, left: 0 },
		xAxis: {
			type: 'category',
			data: [names.assets, `${names.liabilities} + ${names.equity}`],
			axisLine: { show: false },
			axisTick: { show: false },
			axisLabel: { color: t.muted, fontSize: 11 }
		},
		yAxis: {
			type: 'value',
			splitNumber: 3,
			splitLine: { lineStyle: { color: t.grid } },
			axisLabel: { color: t.muted, fontSize: 11, formatter: (v: number) => fmtCompact(v) }
		},
		series: [
			{
				name: names.assets,
				type: 'bar',
				stack: 'total',
				barMaxWidth: 56,
				data: [+assets, '-'],
				itemStyle: segment(t.series[SLOT.blue])
			},
			{
				name: names.liabilities,
				type: 'bar',
				stack: 'total',
				barMaxWidth: 56,
				data: ['-', +liabilities],
				itemStyle: segment(t.series[SLOT.orange])
			},
			{
				name: names.equity,
				type: 'bar',
				stack: 'total',
				barMaxWidth: 56,
				data: ['-', +equity],
				itemStyle: segment(t.series[SLOT.violet])
			}
		]
	};
	$: label = `${names.assets} ${fmtNumber(assets)}, ${names.liabilities} ${fmtNumber(liabilities)}, ${names.equity} ${fmtNumber(equity)} ${currency}`;
</script>

{#if loading}
	<WidgetState state="loading" />
{:else if error}
	<WidgetState state="error" onretry={load} />
{:else if !hasData}
	<WidgetState state="empty" icon={Scale} message={T('No data')} />
{:else}
	<EChart {option} {label} />
{/if}
