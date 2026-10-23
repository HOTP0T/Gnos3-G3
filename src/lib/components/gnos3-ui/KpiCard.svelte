<!--
	A KPI card (design system → Cards & KPIs): label, a 28px tabular figure, optional badge
	or action at the top right, and a footer line. Link the card to the page that explains it.

	<KpiCard label="Needs review" value="12" href="/business-cards/data?needs_review=true">
		{#snippet footer()}Open the queue{/snippet}
	</KpiCard>
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { cn } from '$lib/utils/shadcn.js';

	let {
		label,
		value,
		href = undefined,
		action = undefined,
		footer = undefined,
		class: className = ''
	}: {
		label: string;
		value: string | number;
		href?: string;
		action?: Snippet;
		footer?: Snippet;
		class?: string;
	} = $props();
</script>

<svelte:element
	this={href ? 'a' : 'div'}
	{href}
	data-slot="kpi-card"
	class={cn(
		'flex min-w-0 flex-col gap-3 rounded-xl border bg-card py-5 text-card-foreground shadow-sm',
		href &&
			'transition-colors hover:bg-accent/40 focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50',
		className
	)}
>
	<div class="grid grid-cols-[1fr_auto] items-start gap-x-3 gap-y-2 px-5">
		<div class="text-sm text-muted-foreground">{label}</div>
		{#if action}<div class="row-span-2 justify-self-end">{@render action()}</div>{/if}
		<div
			class="col-start-1 text-[28px] leading-8 font-semibold tracking-[-0.01em] whitespace-nowrap tabular-nums"
		>
			{value}
		</div>
	</div>
	{#if footer}
		<div class="flex flex-col items-start gap-1 px-5 text-[13px] text-muted-foreground">
			{@render footer()}
		</div>
	{/if}
</svelte:element>
