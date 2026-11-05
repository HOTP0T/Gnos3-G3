<!--
	A month calendar for daily notes: days that have one are marked; clicking a day opens its note,
	or creates it from the vault's daily-note template.
-->
<script lang="ts">
	import { getContext } from 'svelte';
	import ChevronLeft from '@lucide/svelte/icons/chevron-left';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import { Button } from '$lib/components/ui/button/index.js';
	import dayjs from '$lib/dayjs';
	import { uiLocale } from '$lib/utils/uiLocale';
	import { currentVault, normalizeTitle, tree } from '../vault';

	const i18n: any = getContext('i18n');

	let { onPick }: { onPick: (date: Date) => void } = $props();

	let month = $state(dayjs().startOf('month'));

	const daily = $derived(
		$currentVault?.settings?.daily ?? {
			folder: 'Daily notes',
			format: 'YYYY-MM-DD',
			template_id: null
		}
	);

	const existing = $derived.by(() => {
		const set = new Set<string>();
		for (const n of $tree?.notes ?? []) {
			if (n.folder === daily.folder || !daily.folder) set.add(normalizeTitle(n.title));
		}
		return set;
	});

	const days = $derived.by(() => {
		const start = month.startOf('month');
		// Weeks start on Monday.
		const offset = (start.day() + 6) % 7;
		const first = start.subtract(offset, 'day');
		return Array.from({ length: 42 }, (_, i) => first.add(i, 'day'));
	});

	// Month and weekday names in the UI language (uiLocale), Monday first.
	const weekdays = $derived.by(() => {
		$i18n.language;
		const fmt = new Intl.DateTimeFormat(uiLocale(), { weekday: 'narrow' });
		const monday = dayjs('2024-01-01'); // a Monday
		return Array.from({ length: 7 }, (_, i) => fmt.format(monday.add(i, 'day').toDate()));
	});
	const monthLabel = $derived.by(() => {
		$i18n.language;
		return new Intl.DateTimeFormat(uiLocale(), { month: 'long', year: 'numeric' }).format(
			month.toDate()
		);
	});
</script>

<div class="w-64 select-none">
	<div class="mb-2 flex items-center justify-between">
		<Button
			variant="ghost"
			size="icon-xs"
			onclick={() => (month = month.subtract(1, 'month'))}
			aria-label={$i18n.t('Previous month')}><ChevronLeft /></Button
		>
		<button
			type="button"
			class="text-sm font-medium capitalize hover:underline"
			onclick={() => (month = dayjs().startOf('month'))}
		>
			{monthLabel}
		</button>
		<Button
			variant="ghost"
			size="icon-xs"
			onclick={() => (month = month.add(1, 'month'))}
			aria-label={$i18n.t('Next month')}><ChevronRight /></Button
		>
	</div>
	<div class="grid grid-cols-7 gap-0.5 text-center">
		{#each weekdays as w}<div class="py-1 text-[11px] text-muted-foreground uppercase">
				{w}
			</div>{/each}
		{#each days as d (d.valueOf())}
			{@const has = existing.has(normalizeTitle(d.format(daily.format || 'YYYY-MM-DD')))}
			{@const today = d.isSame(dayjs(), 'day')}
			<button
				type="button"
				class="relative h-8 rounded-md text-sm tabular-nums hover:bg-accent {d.month() !==
				month.month()
					? 'text-muted-foreground/50'
					: ''} {today ? 'font-semibold text-link ring-1 ring-primary/40' : ''}"
				onclick={() => onPick(d.toDate())}
			>
				{d.date()}
				{#if has}<span
						class="absolute bottom-1 left-1/2 size-1 -translate-x-1/2 rounded-full bg-primary"
					></span>{/if}
			</button>
		{/each}
	</div>
</div>
