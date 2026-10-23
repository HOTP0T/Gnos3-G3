<script lang="ts">
	// Cash-flow waterfall: Opening → Operating → Investing → Financing → Closing.
	// Backed by /reports/cash-flow (indirect method), YTD by default. Every bar carries its signed
	// value, so an inflow and an outflow never differ by colour alone.
	import { onMount, getContext } from 'svelte';
	import Landmark from '@lucide/svelte/icons/landmark';
	import { theme } from '$lib/stores';
	import { getCashFlow } from '$lib/apis/accounting';
	import EChart from '../EChart.svelte';
	import WidgetState from '../WidgetState.svelte';
	import { chartTheme, pageIsDark, tooltipStyle, tooltipHtml } from '../palette';
	import { fmtNumber, fmtCompact } from '../format';

	export let companyId: number;
	export let options: { range?: 'ytd' | 'mtd' } = {};

	const i18n: any = getContext('i18n');
	const T = (k: string, o?: Record<string, unknown>) => ($i18n?.t ? $i18n.t(k, o) : k);
	$: t = chartTheme(pageIsDark($theme));

	let cf: any = null;
	let loading = true;
	let error = false;
	$: range = options?.range ?? 'ytd';

	onMount(load);
	async function load() {
		loading = true;
		error = false;
		try {
			const now = new Date();
			const y = now.getFullYear();
			const m = String(now.getMonth() + 1).padStart(2, '0');
			const d = String(now.getDate()).padStart(2, '0');
			const date_to = `${y}-${m}-${d}`;
			const date_from = range === 'mtd' ? `${y}-${m}-01` : `${y}-01-01`;
			cf = await getCashFlow({ company_id: companyId, date_from, date_to });
		} catch {
			error = true;
		}
		loading = false;
	}

	$: cats = [T('Opening'), T('Operating'), T('Investing'), T('Financing'), T('Closing', { context: 'balance' })];

	// t is passed so a theme change recolours the bars
	$: built = buildWaterfall(cf, t);
	function buildWaterfall(cf: any, t: any) {
		if (!cf) return { placeholder: [], bars: [], deltas: [], hasData: false };
		const opening = +(cf.opening_cash ?? 0);
		const op = +(cf.cash_from_operations ?? 0);
		const inv = +(cf.cash_from_investing ?? 0);
		const fin = +(cf.cash_from_financing ?? 0);
		const closing = +(cf.closing_cash ?? opening + op + inv + fin);

		const placeholder: number[] = [];
		const bars: any[] = [];
		const deltas: number[] = [opening, op, inv, fin, closing];

		const totalColor = t.series[0];
		const signed = (v: number) => (v > 0 ? '+' : v < 0 ? '−' : '') + fmtCompact(Math.abs(v));
		const pushDelta = (base: number, delta: number) => {
			const b = delta >= 0 ? base : base + delta;
			placeholder.push(b);
			bars.push({
				value: Math.abs(delta),
				itemStyle: { color: delta >= 0 ? t.good : t.critical, borderRadius: 4 },
				label: {
					show: true,
					position: 'top',
					color: t.primary,
					fontSize: 11,
					formatter: () => signed(delta)
				}
			});
		};
		const totalBar = (v: number) => ({
			value: v,
			itemStyle: { color: totalColor, borderRadius: 4 },
			label: {
				show: true,
				position: 'top',
				color: t.primary,
				fontSize: 11,
				fontWeight: 500,
				formatter: () => fmtCompact(v)
			}
		});

		// Opening (total from 0)
		placeholder.push(0);
		bars.push(totalBar(opening));
		let running = opening;
		pushDelta(running, op);
		running += op;
		pushDelta(running, inv);
		running += inv;
		pushDelta(running, fin);
		running += fin;
		// Closing (total from 0)
		placeholder.push(0);
		bars.push(totalBar(closing));

		const hasData = [opening, op, inv, fin, closing].some((v) => v !== 0);
		return { placeholder, bars, deltas, hasData };
	}

	$: option = {
		grid: { left: 6, right: 8, top: 20, bottom: 0, containLabel: true },
		tooltip: {
			trigger: 'axis',
			axisPointer: { type: 'shadow', shadowStyle: { color: t.band, opacity: 0.8 } },
			...tooltipStyle(t),
			formatter: (params: any[]) => {
				const i = params[0].dataIndex;
				const val = built.deltas[i] ?? 0;
				const sign = i === 0 || i === 4 ? '' : val >= 0 ? '+' : '−';
				return tooltipHtml(t, cats[i], [{ name: '', value: `${sign}${fmtNumber(Math.abs(val))}` }]);
			}
		},
		xAxis: {
			type: 'category',
			data: cats,
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
				type: 'bar',
				stack: 'wf',
				itemStyle: { color: 'transparent' },
				emphasis: { itemStyle: { color: 'transparent' } },
				data: built.placeholder,
				silent: true
			},
			{ type: 'bar', stack: 'wf', barMaxWidth: 34, data: built.bars }
		]
	};
</script>

{#if loading}
	<WidgetState state="loading" />
{:else if error}
	<WidgetState state="error" onretry={load} />
{:else if !built.hasData}
	<WidgetState state="empty" icon={Landmark} message={T('No data')} />
{:else}
	<EChart
		{option}
		label={cats.map((c, i) => `${c} ${fmtNumber(built.deltas[i] ?? 0)}`).join(', ')}
	/>
{/if}
