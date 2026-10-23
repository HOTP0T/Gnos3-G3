<script lang="ts">
	// Top vendors (by billed) or customers (by invoiced) — horizontal bars, one series, so no
	// legend (the card title names it). Vendors take the expenses colour, customers revenue's.
	// Backed by /reports/top-parties.
	import { onMount, getContext } from 'svelte';
	import Users from '@lucide/svelte/icons/users';
	import { theme } from '$lib/stores';
	import { getTopParties, type TopPartyRow } from '$lib/apis/accounting';
	import EChart from '../EChart.svelte';
	import WidgetState from '../WidgetState.svelte';
	import { chartTheme, pageIsDark, tooltipStyle, tooltipHtml } from '../palette';
	import { fmtNumber, fmtCompact } from '../format';

	export let companyId: number;
	export let options: { direction?: 'vendors' | 'customers'; limit?: number } = {};

	const i18n: any = getContext('i18n');
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);
	$: t = chartTheme(pageIsDark($theme));

	let rows: TopPartyRow[] = [];
	let currency = '';
	let loading = true;
	let error = false;

	$: direction = options?.direction ?? 'vendors';
	$: limit = options?.limit ?? 8;

	onMount(load);
	async function load() {
		loading = true;
		error = false;
		try {
			const res = await getTopParties({ company_id: companyId, direction, limit });
			rows = res.rows ?? [];
			currency = res.currency ?? '';
		} catch {
			rows = [];
			error = true;
		}
		loading = false;
	}

	// echarts category axis draws bottom→top, so reverse for descending top-down.
	$: ordered = [...rows].reverse();
	$: barColor = direction === 'vendors' ? t.expenses : t.revenue;

	$: option = {
		grid: { left: 6, right: 40, top: 4, bottom: 0, containLabel: true },
		tooltip: {
			trigger: 'axis',
			axisPointer: { type: 'shadow', shadowStyle: { color: t.band, opacity: 0.8 } },
			...tooltipStyle(t),
			formatter: (params: any[]) => {
				const r = ordered[params[0]?.dataIndex ?? 0];
				return tooltipHtml(t, r?.name ?? '', [
					{
						color: barColor,
						name: T('Total'),
						value: `${fmtNumber(r?.total_amount ?? 0)} ${currency}`.trim()
					},
					{ name: T('Invoices'), value: String(r?.invoice_count ?? '') }
				]);
			}
		},
		xAxis: {
			type: 'value',
			splitNumber: 3,
			splitLine: { lineStyle: { color: t.grid } },
			axisLabel: { color: t.muted, fontSize: 11, formatter: (v: number) => fmtCompact(v) }
		},
		yAxis: {
			type: 'category',
			data: ordered.map((r) => r.name),
			axisLine: { show: false },
			axisTick: { show: false },
			axisLabel: {
				color: t.secondary,
				fontSize: 11,
				width: 110,
				overflow: 'truncate'
			}
		},
		series: [
			{
				type: 'bar',
				data: ordered.map((r) => +r.total_amount.toFixed(2)),
				itemStyle: { color: barColor, borderRadius: [0, 4, 4, 0] },
				barMaxWidth: 16,
				// values at the bar ends (the colour is light on white; the label carries the figure)
				label: {
					show: true,
					position: 'right',
					color: t.secondary,
					fontSize: 11,
					formatter: (p: any) => fmtCompact(p.value)
				}
			}
		]
	};
</script>

{#if loading}
	<WidgetState state="loading" />
{:else if error}
	<WidgetState state="error" onretry={load} />
{:else if rows.length === 0}
	<WidgetState state="empty" icon={Users} message={T('No data')} />
{:else}
	<EChart {option} label={rows.map((r) => `${r.name} ${fmtNumber(r.total_amount)}`).join(', ')} />
{/if}
