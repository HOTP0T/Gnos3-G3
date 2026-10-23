<!--
	The count and pager under a table (design system → page recipe "List"):
	"Showing 51–100 of 342" on the left, Previous / Next on the right.
-->
<script lang="ts">
	import { getContext } from 'svelte';
	import ChevronLeft from '@lucide/svelte/icons/chevron-left';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import { Button } from '$lib/components/ui/button/index.js';
	import { cn } from '$lib/utils/shadcn.js';

	const i18n: any = getContext('i18n');

	let {
		page = $bindable(1),
		count,
		perPage,
		class: className = ''
	}: { page?: number; count: number; perPage: number; class?: string } = $props();

	const pages = $derived(Math.max(1, Math.ceil(count / perPage)));
	const from = $derived(count === 0 ? 0 : (page - 1) * perPage + 1);
	const to = $derived(Math.min(count, page * perPage));
</script>

<div class={cn('flex flex-wrap items-center justify-between gap-2 text-sm', className)}>
	<span class="text-muted-foreground tabular-nums">
		{$i18n.t('Showing {{from}}–{{to}} of {{count}}', { from, to, count })}
	</span>
	{#if pages > 1}
		<div class="flex items-center gap-2">
			<span class="text-muted-foreground tabular-nums">{page} / {pages}</span>
			<Button variant="outline" size="sm" disabled={page <= 1} onclick={() => (page = page - 1)}>
				<ChevronLeft />{$i18n.t('Previous')}
			</Button>
			<Button
				variant="outline"
				size="sm"
				disabled={page >= pages}
				onclick={() => (page = page + 1)}
			>
				{$i18n.t('Next')}<ChevronRight />
			</Button>
		</div>
	{/if}
</div>
