<script lang="ts">
	// AR or AP aging buckets (donut), from /reports/ar-aging | /reports/ap-aging.
	// Buckets carry an ordinal severity ramp (recent → overdue); the legend names each bucket.
	import { onMount, getContext } from 'svelte';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import { theme } from '$lib/stores';
	import { getARAging, getAPAging } from '$lib/apis/accounting';
	import EChart from '../EChart.svelte';
	import WidgetState from '../WidgetState.svelte';
	import {
		chartTheme,
		pageIsDark,
		tooltipStyle,
		legendStyle,
		tooltipHtml,
		donutLayout
	} from '../palette';
	import { fmtNumber, fmtCompact } from '../format';

	export let companyId: number;
	export let options: { kind?: 'ar' | 'ap' } = {};

	const i18n: any = getContext('i18n');
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);
	$: t = chartTheme(pageIsDark($theme));

	let summary: any = null;
	let loading = true;
	let error = false;

	$: kind = options?.kind ?? 'ar';

	onMount(load);
	async function load() {
		loading = true;
		error = false;
		try {
			const res =
				kind === 'ap'
					? await getAPAging({ company_id: companyId })
					: await getARAging({ company_id: companyId });
			summary = res?.summary ?? null;
		} catch {
			summary = null;
			error = true;
		}
		loading = false;
	}

	$: buckets = summary
		? [
				{ name: T('Current'), value: summary.current ?? 0, color: t.series[0] },
				{ name: '31–60d', value: summary.days_31_60 ?? 0, color: t.warning },
				{ name: '61–90d', value: summary.days_61_90 ?? 0, color: t.serious ?? t.expenses },
				{ name: '90d+', value: summary.over_90 ?? 0, color: t.critical }
			].filter((b) => b.value > 0)
		: [];

	$: total = buckets.reduce((s, b) => s + b.value, 0);

	const layout = donutLayout(['54%', '78%']);
	$: option = {
		baseOption: {
			tooltip: {
				trigger: 'item',
				...tooltipStyle(t),
				formatter: (p: any) =>
					tooltipHtml(t, '', [{ color: p.color, name: p.name, value: fmtNumber(p.value) }])
			},
			legend: { ...legendStyle(t), orient: 'vertical', right: 0, top: 'middle', itemGap: 8 },
			series: [
				{
					type: 'pie',
					...layout.wide,
					// 2px surface gap between slices
					itemStyle: { borderColor: t.surface, borderWidth: 2 },
					label: {
						show: true,
						position: 'center',
						formatter: () => (total ? fmtCompact(total) : ''),
						color: t.primary,
						fontSize: 14,
						fontWeight: 600
					},
					emphasis: { label: { show: true } },
					data: buckets.map((b) => ({
						name: b.name,
						value: b.value,
						itemStyle: { color: b.color }
					}))
				}
			]
		},
		media: [layout.narrow]
	};
	$: label = buckets.map((b) => `${b.name} ${fmtNumber(b.value)}`).join(', ');
</script>

{#if loading}
	<WidgetState state="loading" />
{:else if error}
	<WidgetState state="error" onretry={load} />
{:else if buckets.length === 0}
	<WidgetState state="empty" icon={CircleCheck} message={T('Nothing outstanding')} />
{:else}
	<EChart {option} {label} />
{/if}
