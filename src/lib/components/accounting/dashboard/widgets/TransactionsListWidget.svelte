<script lang="ts">
	// Recent transactions (or drafts, via options.status). Scrollable dense table; a row opens the
	// entry (click or Enter).
	import { onMount, getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import { goto } from '$app/navigation';
	import dayjs from 'dayjs';
	import Receipt from '@lucide/svelte/icons/receipt';
	import { getTransactions } from '$lib/apis/accounting';
	import * as Table from '$lib/components/ui/table/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';
	import WidgetState from '../WidgetState.svelte';
	import { rowMoney } from '../format';

	export let companyId: number;
	export let options: { status?: 'all' | 'draft'; limit?: number } = {};

	const i18n: any = getContext('i18n');
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);
	const displayCurrency = getContext<Writable<string>>('displayCurrency');
	const exchangeRates = getContext<Writable<any[]>>('exchangeRates');
	const companyCurrencyCtx = getContext<Writable<string>>('companyCurrency');
	$: nativeCurrency = ($companyCurrencyCtx as any) || 'EUR';

	let rows: any[] = [];
	let loading = true;
	let error = false;
	$: status = options?.status ?? 'all';
	$: limit = options?.limit ?? 20;

	onMount(load);
	async function load() {
		loading = true;
		error = false;
		try {
			const res = await getTransactions({
				company_id: companyId,
				limit,
				...(status === 'draft' ? { status: 'draft' } : {})
			});
			rows = Array.isArray(res) ? res : (res?.transactions ?? res?.items ?? []);
		} catch {
			rows = [];
			error = true;
		}
		loading = false;
	}

	const open = (tx: any) => goto(`/accounting/company/${companyId}/entries?id=${tx.id}`);
	const typeLabel = (tt: string | null | undefined) => (tt ? tt.replace(/_/g, ' ') : '—');
</script>

{#if loading}
	<WidgetState state="loading" rows={6} class="px-4 pb-4" />
{:else if error}
	<WidgetState state="error" onretry={load} class="px-4 pb-4" />
{:else if rows.length === 0}
	<WidgetState state="empty" icon={Receipt} message={T('No transactions')} class="px-4 pb-4" />
{:else}
	<!-- The body scrolls; the inner table container must not, so the header can stick. -->
	<div class="h-full overflow-y-auto border-t [&_[data-slot=table-container]]:overflow-visible">
		<Table.Root class="text-[13px]">
			<Table.Header class="sticky top-0 z-10 bg-card shadow-[inset_0_-1px_0_var(--border)]">
				<Table.Row class="border-0 hover:bg-transparent">
					<Table.Head class="h-8 pl-4 text-muted-foreground">{T('Date')}</Table.Head>
					<Table.Head class="h-8 text-muted-foreground">{T('Type')}</Table.Head>
					<Table.Head class="h-8 text-muted-foreground">{T('Description')}</Table.Head>
					<Table.Head class="h-8 text-right text-muted-foreground">{T('Total')}</Table.Head>
					<Table.Head class="h-8 pr-4 text-muted-foreground">{T('Status')}</Table.Head>
				</Table.Row>
			</Table.Header>
			<Table.Body>
				{#each rows as tx (tx.id)}
					{@const mv = rowMoney(
						tx.total ?? tx.amount ?? 0,
						tx.currency,
						nativeCurrency,
						$displayCurrency,
						$exchangeRates ?? [],
						tx.transaction_date,
						tx.exchange_rate
					)}
					<Table.Row
						class="cursor-pointer"
						tabindex={0}
						onclick={() => open(tx)}
						onkeydown={(e: KeyboardEvent) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								open(tx);
							}
						}}
					>
						<Table.Cell class="py-1.5 pl-4 tabular-nums">
							{tx.transaction_date ? dayjs(tx.transaction_date).format('YYYY-MM-DD') : '—'}
						</Table.Cell>
						<Table.Cell class="py-1.5">
							<Badge variant="outline" class="font-normal">{typeLabel(tx.transaction_type)}</Badge>
						</Table.Cell>
						<Table.Cell
							class="max-w-[14rem] truncate py-1.5"
							title={tx.description ?? tx.memo ?? ''}
						>
							{tx.description ?? tx.memo ?? '—'}
						</Table.Cell>
						<Table.Cell class="py-1.5 text-right tabular-nums">
							{#if mv.converting && mv.hasRate}
								{mv.display} <span class="text-xs text-muted-foreground">{mv.to}</span>
							{:else}
								{mv.original} <span class="text-xs text-muted-foreground">{mv.from}</span>
							{/if}
						</Table.Cell>
						<Table.Cell class="py-1.5 pr-4">
							<StatusBadge kind="entry" status={tx.status ?? 'draft'} />
						</Table.Cell>
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</div>
{/if}
