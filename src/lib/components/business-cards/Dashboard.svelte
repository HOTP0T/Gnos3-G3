<script lang="ts">
	import { onMount, onDestroy, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';

	import RefreshCw from '@lucide/svelte/icons/refresh-cw';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import ExternalLink from '@lucide/svelte/icons/external-link';
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import IdCard from '@lucide/svelte/icons/id-card';

	import {
		getBusinessCards,
		getBusinessCardStats,
		type BusinessCard,
		type BusinessCardStats
	} from '$lib/apis/business-cards';
	import { k4miDocHref } from '$lib/apis/k4mi';

	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import KpiCard from '$lib/components/gnos3-ui/KpiCard.svelte';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';

	const i18n: any = getContext('i18n');

	let loading = $state(true);
	let stats = $state<BusinessCardStats | null>(null);
	let recentCards = $state<BusinessCard[]>([]);
	let reviewCards = $state<BusinessCard[]>([]);
	let refreshInterval: ReturnType<typeof setInterval> | null = null;

	const loadData = async () => {
		loading = true;
		try {
			const [statsResp, recent, review] = await Promise.all([
				getBusinessCardStats(localStorage.token),
				getBusinessCards(localStorage.token, { sort_by: 'created_at', sort_dir: 'desc', limit: 10 }),
				getBusinessCards(localStorage.token, {
					needs_review: true,
					sort_by: 'created_at',
					sort_dir: 'desc',
					limit: 10
				})
			]);

			stats = statsResp;
			recentCards = recent.business_cards ?? [];
			reviewCards = review.business_cards ?? [];

			if ((stats?.processing ?? 0) > 0 && !refreshInterval) {
				refreshInterval = setInterval(() => loadData(), 5000);
			} else if ((stats?.processing ?? 0) === 0 && refreshInterval) {
				clearInterval(refreshInterval);
				refreshInterval = null;
			}
		} catch (err) {
			toast.error(`${err}`);
		}
		loading = false;
	};

	onMount(loadData);
	onDestroy(() => {
		if (refreshInterval) clearInterval(refreshInterval);
	});

	const maxCompany = $derived(Math.max(1, ...(stats?.by_company ?? []).map((c) => c.count)));
</script>

<div class="flex flex-col gap-4">
	<div class="flex items-center justify-between gap-2">
		<h1 class="text-2xl font-semibold tracking-tight">{$i18n.t('Business cards')}</h1>
		<Button variant="outline" size="sm" onclick={loadData} disabled={loading}>
			{#if loading}<Spinner />{:else}<RefreshCw />{/if}
			{$i18n.t('Refresh')}
		</Button>
	</div>

	{#if loading && !stats}
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(12.5rem,100%),1fr))] gap-4">
			{#each Array(4) as _}<Skeleton class="h-[118px] rounded-xl" />{/each}
		</div>
		<Skeleton class="h-64 rounded-xl" />
	{:else if stats}
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(12.5rem,100%),1fr))] gap-4">
			<KpiCard label={$i18n.t('Total')} value={stats.total} />
			<KpiCard label={$i18n.t('Completed')} value={stats.completed} />
			<KpiCard
				label={$i18n.t('Needs review')}
				value={stats.needs_review}
				href="/business-cards/data?needs_review=true"
			>
				{#snippet action()}
					{#if stats && stats.needs_review > 0}<Badge variant="warning">{$i18n.t('Review')}</Badge>{/if}
				{/snippet}
				{#snippet footer()}
					<span class="inline-flex items-center gap-1 text-link"
						>{$i18n.t('Open the review list')}<ArrowRight class="size-3.5" /></span
					>
				{/snippet}
			</KpiCard>
			<KpiCard label={$i18n.t('Added in last 30 days')} value={stats.recent_added_30d} />
		</div>

		{#if stats.processing > 0}
			<Alert.Root>
				<LoaderCircle class="animate-spin motion-reduce:animate-none" />
				<Alert.Title>
					{stats.processing}
					{$i18n.t('cards still processing')}
				</Alert.Title>
				<Alert.Description>{$i18n.t('This page will update automatically.')}</Alert.Description>
			</Alert.Root>
		{/if}

		<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
			<Card.Root>
				<Card.Header>
					<Card.Title>{$i18n.t('Top companies')}</Card.Title>
					<Card.Description>{$i18n.t('Cards per company')}</Card.Description>
				</Card.Header>
				<Card.Content>
					{#if stats.by_company.length === 0}
						<p class="text-sm text-muted-foreground">{$i18n.t('No company data yet.')}</p>
					{:else}
						<ul class="grid gap-2.5">
							{#each stats.by_company as row}
								<li class="grid grid-cols-[minmax(0,10rem)_1fr_2.5rem] items-center gap-3 text-sm">
									<span class="truncate" title={row.company_name}>{row.company_name}</span>
									<div class="h-2 overflow-hidden rounded-full bg-muted">
										<div
											class="h-full rounded-full bg-chart-1"
											style="width: {(row.count / maxCompany) * 100}%"
										></div>
									</div>
									<span class="text-right tabular-nums">{row.count}</span>
								</li>
							{/each}
						</ul>
					{/if}
				</Card.Content>
			</Card.Root>

			<Card.Root>
				<Card.Header>
					<Card.Title>{$i18n.t('Recent additions')}</Card.Title>
					<Card.Action>
						<Button variant="link" size="sm" href="/business-cards/data">{$i18n.t('View all')}</Button>
					</Card.Action>
				</Card.Header>
				<Card.Content>
					{#if recentCards.length === 0}
						<Empty.Root class="p-6">
							<Empty.Header>
								<Empty.Media variant="icon"><IdCard /></Empty.Media>
								<Empty.Title>{$i18n.t('No business cards yet.')}</Empty.Title>
								<Empty.Description>
									{$i18n.t('Tag a K4mi document with')} <code>business_card</code>
									{$i18n.t('to get started.')}
								</Empty.Description>
							</Empty.Header>
						</Empty.Root>
					{:else}
						<ul class="divide-y">
							{#each recentCards as card}
								<li class="flex items-center gap-3 py-2 first:pt-0 last:pb-0">
									<div class="min-w-0 flex-1">
										<div class="truncate text-sm font-medium">
											{card.full_name || $i18n.t('Untitled card')}
										</div>
										<div class="truncate text-sm text-muted-foreground">
											{[card.job_title, card.company_name].filter(Boolean).join(' · ') || '—'}
										</div>
									</div>
									<span class="text-sm text-muted-foreground tabular-nums">
										{card.created_at ? dayjs(card.created_at).format('YYYY-MM-DD') : ''}
									</span>
									{#if card.k4mi_document_id}
										<Button
											variant="ghost"
											size="icon-xs"
											href={k4miDocHref(card.k4mi_document_id)}
											target="_blank"
											rel="noopener noreferrer"
											aria-label={$i18n.t('Open in K4mi')}
											title={$i18n.t('Open in K4mi')}
										>
											<ExternalLink />
										</Button>
									{/if}
								</li>
							{/each}
						</ul>
					{/if}
				</Card.Content>
			</Card.Root>
		</div>

		{#if reviewCards.length > 0}
			<Card.Root>
				<Card.Header>
					<Card.Title>{$i18n.t('Needs review')}</Card.Title>
					<Card.Description>{$i18n.t('Low-confidence extractions to check against the card')}</Card.Description>
					<Card.Action>
						<Button variant="link" size="sm" href="/business-cards/data?needs_review=true"
							>{$i18n.t('Review all')}</Button
						>
					</Card.Action>
				</Card.Header>
				<Card.Content>
					<ul class="divide-y">
						{#each reviewCards as card}
							<li class="flex items-center gap-3 py-2 text-sm first:pt-0 last:pb-0">
								<span class="min-w-0 flex-1 truncate">{card.full_name || $i18n.t('Untitled card')}</span>
								{#if card.confidence_score !== null && card.confidence_score !== undefined}
									<StatusBadge kind="confidence" status={card.confidence_score} />
								{/if}
								{#if card.k4mi_document_id}
									<Button
										variant="ghost"
										size="icon-xs"
										href={k4miDocHref(card.k4mi_document_id)}
										target="_blank"
										rel="noopener noreferrer"
										aria-label={$i18n.t('Open in K4mi')}
										title={$i18n.t('Open in K4mi')}
									>
										<ExternalLink />
									</Button>
								{/if}
							</li>
						{/each}
					</ul>
				</Card.Content>
			</Card.Root>
		{/if}
	{/if}
</div>
