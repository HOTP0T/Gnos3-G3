<script lang="ts">
	// Current accounting period summary. Loads its own periods list.
	import { onMount, getContext } from 'svelte';
	import dayjs from 'dayjs';
	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import Circle from '@lucide/svelte/icons/circle';
	import Lock from '@lucide/svelte/icons/lock';
	import { getPeriods } from '$lib/apis/accounting';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import WidgetState from '../WidgetState.svelte';

	export let companyId: number;
	export let options: Record<string, any> = {}; // unused; part of widget contract
	const i18n: any = getContext('i18n');
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);

	let period: any = null;
	let loading = true;
	let error = false;

	onMount(load);
	async function load() {
		loading = true;
		error = false;
		try {
			const res = await getPeriods({ company_id: companyId });
			const list = Array.isArray(res) ? res : (res?.items ?? []);
			period = list.find((p: any) => !p.is_closed) ?? list[0] ?? null;
		} catch {
			period = null;
			error = true;
		}
		loading = false;
	}
</script>

<div class="flex h-full flex-col justify-center">
	{#if loading}
		<div class="flex flex-col gap-2" aria-busy="true">
			<Skeleton class="h-5 w-1/2" />
			<Skeleton class="h-4 w-2/3" />
		</div>
	{:else if error}
		<WidgetState state="error" onretry={load} />
	{:else if !period}
		<WidgetState state="empty" icon={CalendarDays} message={T('No periods defined')} />
	{:else}
		<div class="flex flex-wrap items-center gap-2">
			<span class="font-medium">
				{period.name ?? `${period.start_date} – ${period.end_date}`}
			</span>
			<Badge variant="status">
				{#if !period.is_closed}
					<Circle class="text-success" aria-hidden="true" />{T('Open')}
				{:else}
					<Lock aria-hidden="true" />{T('Closed')}
				{/if}
			</Badge>
		</div>
		{#if period.start_date && period.end_date}
			<div class="mt-1 text-sm text-muted-foreground tabular-nums">
				{dayjs(period.start_date).format('YYYY-MM-DD')} — {dayjs(period.end_date).format(
					'YYYY-MM-DD'
				)}
			</div>
		{/if}
	{/if}
</div>
