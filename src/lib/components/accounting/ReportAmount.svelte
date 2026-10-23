<script lang="ts">
	// Renders a report money amount. When a display currency (≠ base) is selected it
	// shows the converted amount on top with the original base-currency amount in
	// small muted text underneath as reference — matching the tables/bank views.
	//
	// `value` is the raw amount in `baseCcy`. `factor` is the base→display multiplier
	// (null = no rate available: falls back to the base amount + a warning).
	import { getContext } from 'svelte';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';

	const i18n: any = getContext('i18n');

	export let value: any;
	export let factor: number | null = 1;
	export let converting = false;
	export let displayCcy = '';
	export let baseCcy = '';
	export let abs = false; // show absolute value (for split debit/credit columns)
	export let zeroText: string | null = ''; // shown for a zero value; null = format 0 normally
	export let minFrac = 2;
	export let maxFrac = 2;
	export let locale: string | undefined = undefined;

	const toNum = (v: any): number => {
		const n = typeof v === 'string' ? parseFloat(v) : (v ?? 0);
		return isNaN(n) ? 0 : n;
	};
	const f = (n: number): string => {
		const x = abs ? Math.abs(n) : n;
		if (x === 0 && zeroText !== null) return zeroText;
		return x.toLocaleString(locale, {
			minimumFractionDigits: minFrac,
			maximumFractionDigits: maxFrac
		});
	};

	$: base = toNum(value);
	$: hasRate = factor != null;
	$: topStr = converting && hasRate ? f(base * (factor as number)) : f(base);
	$: origStr = f(base);
</script>

{#if !converting}
	{f(base)}
{:else}
	{#key displayCcy}
		{#if hasRate}
			<span
				>{topStr}{#if topStr}{' '}<span class="text-[10px] font-normal text-muted-foreground"
						>{displayCcy}</span
					>{/if}</span
			>
			{#if origStr}<span class="block text-[10px] font-normal text-muted-foreground"
					>{origStr} {baseCcy}</span
				>{/if}
		{:else}
			<span
				>{origStr}{#if origStr}{' '}<span class="text-[10px] font-normal text-muted-foreground"
						>{baseCcy}</span
					>{/if}</span
			>
			<span title={$i18n.t('No exchange rate available')} class="inline-flex align-[-2px]"
				><TriangleAlert
					class="size-3 text-warning"
					aria-label={$i18n.t('No exchange rate available')}
				/></span
			>
		{/if}
	{/key}
{/if}
