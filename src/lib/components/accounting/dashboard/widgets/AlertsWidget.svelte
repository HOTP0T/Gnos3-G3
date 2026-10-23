<script lang="ts">
	// Actionable alerts (drafts / unmatched bank lines / overdue invoices) as a checklist:
	// icon + what needs doing + an outline button that opens the page where it is fixed.
	// Reads the shared common-data store so it doesn't refetch stats.
	import { getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { COMMON_DATA_CTX, type CommonData } from '../store';

	export let companyId: number;
	export let options: Record<string, any> = {}; // unused; part of widget contract
	const i18n: any = getContext('i18n');
	const common = getContext<Writable<CommonData>>(COMMON_DATA_CTX);
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);

	$: stats = $common.stats ?? {};
	$: drafts = stats.draft_count ?? 0;
	$: unmatched = stats.unmatched_bank_lines ?? 0;
	$: overdue = stats.overdue_invoices ?? 0;
	$: anyAlerts = drafts > 0 || unmatched > 0 || overdue > 0;
	$: base = `/accounting/company/${companyId}`;
</script>

<div class="h-full overflow-y-auto">
	{#if $common.loading}
		<div class="flex flex-col gap-2" aria-busy="true">
			{#each Array(3) as _}<Skeleton class="h-7 w-full" />{/each}
		</div>
	{:else if !anyAlerts}
		<div class="flex h-full items-center gap-2">
			<CircleCheck class="size-4 shrink-0 text-success" aria-hidden="true" />
			<span>{T('All clear — nothing needs attention')}</span>
		</div>
	{:else}
		<ul class="divide-y">
			{#if drafts > 0}
				<li class="flex items-center gap-3 py-1.5 first:pt-0 last:pb-0">
					<TriangleAlert class="size-4 shrink-0 text-warning" aria-hidden="true" />
					<span class="min-w-0 flex-1 truncate font-medium"
						><span class="tabular-nums">{drafts}</span> {T('draft entries awaiting review')}</span
					>
					<Button variant="outline" size="xs" href="{base}/entries">{T('View')}</Button>
				</li>
			{/if}
			{#if unmatched > 0}
				<li class="flex items-center gap-3 py-1.5 first:pt-0 last:pb-0">
					<TriangleAlert class="size-4 shrink-0 text-warning" aria-hidden="true" />
					<span class="min-w-0 flex-1 truncate font-medium"
						><span class="tabular-nums">{unmatched}</span> {T('unmatched bank lines')}</span
					>
					<Button variant="outline" size="xs" href="{base}/bank">{T('Reconcile')}</Button>
				</li>
			{/if}
			{#if overdue > 0}
				<li class="flex items-center gap-3 py-1.5 first:pt-0 last:pb-0">
					<CircleAlert class="size-4 shrink-0 text-destructive" aria-hidden="true" />
					<span class="min-w-0 flex-1 truncate font-medium"
						><span class="tabular-nums">{overdue}</span> {T('overdue invoices')}</span
					>
					<Button variant="outline" size="xs" href="{base}/invoices">{T('View')}</Button>
				</li>
			{/if}
		</ul>
	{/if}
</div>
