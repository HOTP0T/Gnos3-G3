<script lang="ts">
	// Thin, theme-aware ECharts wrapper. Lazy-imports echarts on first mount so
	// the ~1MB library is only paid for when a chart widget is actually shown.
	// Re-renders on `option` change and resizes with its container (gridstack).
	import { onMount, onDestroy } from 'svelte';

	export let option: any = null;
	export let height = '100%';
	/** What the chart shows, for screen readers (the canvas itself is not readable). */
	export let label = '';

	let el: HTMLDivElement;
	let chart: any = null;
	let echarts: any = null;
	let ro: ResizeObserver | null = null;
	let mounted = false;

	// Canvas text ignores CSS fonts and is not redrawn when a web font arrives, so
	// hand ECharts the page's font stack and wait for Geist before the first draw.
	let fontFamily = 'sans-serif';
	const withFont = (o: typeof option) =>
		o.baseOption
			? // responsive option ({ baseOption, media }): the font goes on the base
				{
					...o,
					baseOption: { ...o.baseOption, textStyle: { fontFamily, ...o.baseOption.textStyle } }
				}
			: { ...o, textStyle: { fontFamily, ...o.textStyle } };

	onMount(async () => {
		fontFamily = getComputedStyle(el).fontFamily || fontFamily;
		const [mod] = await Promise.all([
			import('echarts'),
			document.fonts?.load('12px Geist').catch(() => {})
		]);
		echarts = mod;
		chart = echarts.init(el, null, { renderer: 'canvas' });
		if (option) chart.setOption(withFont(option), true);
		ro = new ResizeObserver(() => {
			if (chart) chart.resize();
		});
		ro.observe(el);
		mounted = true;
	});

	// notMerge=true so a full option swap (e.g. theme change) replaces cleanly.
	$: if (mounted && chart && option) chart.setOption(withFont(option), true);

	onDestroy(() => {
		ro?.disconnect();
		ro = null;
		if (chart) {
			chart.dispose();
			chart = null;
		}
	});
</script>

<div
	bind:this={el}
	role={label ? 'img' : undefined}
	aria-label={label || undefined}
	style="width:100%;height:{height};min-height:0;"
></div>
