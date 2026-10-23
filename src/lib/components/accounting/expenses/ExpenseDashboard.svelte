<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';
	import Info from '@lucide/svelte/icons/info';

	import { getExpenseStats, type ExpenseStats } from '$lib/apis/expenses';

	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import KpiCard from '$lib/components/gnos3-ui/KpiCard.svelte';

	const i18n: any = getContext('i18n');

	export let companyId: number;

	let loading = true;
	let loadError = '';
	let stats: ExpenseStats | null = null;

	function fmtCur(byCur: Record<string, number>): string {
		const entries = Object.entries(byCur || {}).filter(([, v]) => v);
		if (!entries.length) return '—';
		return entries
			.map(
				([c, v]) =>
					`${c} ${v.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
			)
			.join(' · ');
	}
	const total = (byCur: Record<string, number>) =>
		Object.values(byCur || {}).reduce((a, b) => a + b, 0);

	$: statusOf = (k: string) => stats?.by_status?.[k] ?? { count: 0, by_currency: {} };
	$: catMax = Math.max(1, ...(stats?.by_category ?? []).map((c) => total(c.by_currency)));
	$: empMax = Math.max(1, ...(stats?.by_employee ?? []).map((e) => total(e.by_currency)));
	$: groups = [
		{
			title: 'Spend by category',
			max: catMax,
			rows: (stats?.by_category ?? []).map((c) => ({
				key: c.category_id ?? 0,
				label: c.label ?? '—',
				count: c.count,
				by_currency: c.by_currency
			}))
		},
		{
			title: 'Spend by employee',
			max: empMax,
			rows: (stats?.by_employee ?? []).map((e) => ({
				key: e.employee_id ?? 0,
				label: e.name ?? '—',
				count: e.count,
				by_currency: e.by_currency
			}))
		}
	];

	async function load() {
		loading = true;
		loadError = '';
		try {
			stats = await getExpenseStats(companyId);
		} catch (e: any) {
			loadError = e?.message ?? 'Failed to load stats';
			toast.error(loadError);
		} finally {
			loading = false;
		}
	}
	onMount(load);

	const TILES = [
		{ key: 'submitted', label: 'Pending review' },
		{ key: 'approved', label: 'To reimburse' },
		{ key: 'reimbursed', label: 'Reimbursed' },
		{ key: 'rejected', label: 'Rejected' }
	];
</script>

{#if loading}
	<div class="flex flex-col gap-4">
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(12.5rem,100%),1fr))] gap-4">
			{#each Array(4) as _}<Skeleton class="h-[118px] rounded-xl" />{/each}
		</div>
		<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
			<Skeleton class="h-56 rounded-xl" />
			<Skeleton class="h-56 rounded-xl" />
		</div>
	</div>
{:else if loadError}
	<Alert.Root variant="destructive">
		<CircleAlert />
		<Alert.Title>{$i18n.t('Could not load the expense overview.')}</Alert.Title>
		<Alert.Description>
			<p>{loadError}</p>
			<Button variant="outline" size="sm" class="mt-2" onclick={load}>
				<RefreshCw />{$i18n.t('Retry')}
			</Button>
		</Alert.Description>
	</Alert.Root>
{:else if stats}
	<div class="flex flex-col gap-4">
		<!-- KPI cards: count, then the amounts per currency -->
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(12.5rem,100%),1fr))] gap-4">
			{#each TILES as t}
				{@const b = statusOf(t.key)}
				<KpiCard label={$i18n.t(t.label)} value={b.count}>
					{#snippet footer()}
						<span class="tabular-nums">{fmtCur(b.by_currency)}</span>
					{/snippet}
				</KpiCard>
			{/each}
		</div>

		<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
			{#each groups as group (group.title)}
				<Card.Root>
					<Card.Header>
						<Card.Title>{$i18n.t(group.title)}</Card.Title>
					</Card.Header>
					<Card.Content>
						{#if !group.rows.length}
							<p class="text-sm text-muted-foreground">{$i18n.t('No data.')}</p>
						{:else}
							<ul class="flex flex-col gap-3">
								{#each group.rows as row (row.key)}
									<li>
										<div class="mb-1.5 flex items-center justify-between gap-3 text-sm">
											<span class="min-w-0 truncate"
												>{row.label}
												<span class="text-muted-foreground tabular-nums">· {row.count}</span></span
											>
											<span class="shrink-0 text-right font-medium tabular-nums"
												>{fmtCur(row.by_currency)}</span
											>
										</div>
										<div class="h-2 overflow-hidden rounded-full bg-muted">
											<div
												class="h-full rounded-full bg-chart-1"
												style="width:{Math.max(3, (total(row.by_currency) / group.max) * 100)}%"
											></div>
										</div>
									</li>
								{/each}
							</ul>
						{/if}
					</Card.Content>
				</Card.Root>
			{/each}
		</div>

		{#if stats.by_category.some((c) => Object.keys(c.by_currency).length > 1) || Object.values(stats.by_status).some((s) => Object.keys(s.by_currency).length > 1)}
			<p class="flex items-start gap-1.5 text-sm text-muted-foreground">
				<Info class="mt-0.5 size-4 shrink-0" />
				{$i18n.t(
					'Amounts are grouped by currency; bar lengths are approximate across currencies until FX conversion is enabled.'
				)}
			</p>
		{/if}
	</div>
{/if}
