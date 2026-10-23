<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import type { Component } from 'svelte';
	import Plus from '@lucide/svelte/icons/plus';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import CircleSlash from '@lucide/svelte/icons/circle-slash';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Dot from '@lucide/svelte/icons/dot';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';

	import { getAuditTrail } from '$lib/apis/accounting';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';

	const i18n: any = getContext('i18n');

	let {
		companyId,
		entityType = undefined,
		entityId = undefined,
		limit = 20
	}: {
		companyId: number;
		entityType?: string;
		entityId?: number;
		limit?: number;
	} = $props();

	let entries = $state<any[]>([]);
	let total = $state(0);
	let loading = $state(true);
	let failed = $state(false);

	const load = async () => {
		loading = true;
		failed = false;
		try {
			const res = await getAuditTrail({
				company_id: companyId,
				entity_type: entityType,
				entity_id: entityId,
				limit
			});
			entries = res.entries ?? [];
			total = res.total ?? 0;
		} catch (err) {
			console.error(err);
			failed = true;
		}
		loading = false;
	};

	onMount(load);

	// Icon + word for each action (never colour alone); colour only where it carries meaning.
	const ACTIONS: Record<string, { icon: Component; tone?: string }> = {
		created: { icon: Plus },
		posted: { icon: CircleCheck, tone: 'text-success' },
		voided: { icon: CircleSlash },
		deleted: { icon: Trash2, tone: 'text-destructive' },
		updated: { icon: Pencil }
	};

	const formatTime = (ts: string) => {
		if (!ts) return '';
		const d = new Date(ts);
		return d.toLocaleString(undefined, {
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	};
</script>

{#if loading}
	<div class="grid gap-2" aria-busy="true">
		{#each Array(4) as _}
			<Skeleton class="h-4 w-full" />
		{/each}
	</div>
{:else if failed}
	<div class="flex items-center gap-2 text-sm text-muted-foreground">
		<CircleAlert class="size-4 shrink-0 text-destructive" />
		{$i18n.t('Failed to load activity')}
		<Button variant="link" size="sm" onclick={load}>{$i18n.t('Retry')}</Button>
	</div>
{:else if entries.length === 0}
	<p class="text-sm text-muted-foreground">{$i18n.t('No activity yet')}</p>
{:else}
	<ul class="grid gap-2">
		{#each entries as entry}
			{@const spec = ACTIONS[entry.action] ?? { icon: Dot }}
			<li class="flex items-start gap-2 text-[13px] leading-5">
				<spec.icon class="mt-0.5 size-3.5 shrink-0 {spec.tone ?? 'text-muted-foreground'}" />
				<div class="min-w-0 flex-1">
					<span class="font-medium {entry.action === 'voided' ? 'line-through' : ''}"
						>{$i18n.t(entry.action)}</span
					>
					<span class="text-muted-foreground">
						{entry.entity_type}
						<span class="font-mono">#{entry.entity_id}</span>
					</span>
					{#if entry.changes && typeof entry.changes === 'object'}
						<span class="text-muted-foreground">· {Object.keys(entry.changes).join(', ')}</span>
					{/if}
				</div>
				<span class="text-xs whitespace-nowrap text-muted-foreground tabular-nums">
					{formatTime(entry.timestamp)}
				</span>
			</li>
		{/each}
	</ul>
	{#if total > entries.length}
		<p class="mt-2 text-xs text-muted-foreground tabular-nums">
			{$i18n.t('Showing')}
			{entries.length} / {total}
		</p>
	{/if}
{/if}
