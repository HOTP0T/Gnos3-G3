<script lang="ts">
	// Upcoming recurring entries, ordered by next run date. From /recurring.
	// A run date in the past gets an alert icon, one within a week a clock (icon + date, never
	// colour alone). A row opens the recurring entries page (click or Enter).
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import dayjs from 'dayjs';
	import Repeat from '@lucide/svelte/icons/repeat';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import Clock from '@lucide/svelte/icons/clock';
	import { getRecurringTemplates } from '$lib/apis/accounting';
	import * as Table from '$lib/components/ui/table/index.js';
	import WidgetState from '../WidgetState.svelte';

	export let companyId: number;
	export let options: { limit?: number } = {};
	const i18n: any = getContext('i18n');
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);
	$: limit = options?.limit ?? 12;

	let rows: any[] = [];
	let loading = true;
	let error = false;

	onMount(load);
	async function load() {
		loading = true;
		error = false;
		try {
			const res = await getRecurringTemplates(companyId);
			const list = Array.isArray(res) ? res : (res?.items ?? []);
			rows = list
				.filter((r: any) => r.is_active !== false)
				.sort((a: any, b: any) =>
					String(a.next_run_date ?? '9999').localeCompare(String(b.next_run_date ?? '9999'))
				)
				.slice(0, limit);
		} catch {
			rows = [];
			error = true;
		}
		loading = false;
	}

	const due = (d?: string): 'overdue' | 'soon' | null => {
		if (!d) return null;
		const days = dayjs(d).diff(dayjs(), 'day');
		if (days < 0) return 'overdue';
		if (days <= 7) return 'soon';
		return null;
	};
	const open = () => goto(`/accounting/company/${companyId}/recurring`);
</script>

{#if loading}
	<WidgetState state="loading" rows={6} class="px-4 pb-4" />
{:else if error}
	<WidgetState state="error" onretry={load} class="px-4 pb-4" />
{:else if rows.length === 0}
	<WidgetState state="empty" icon={Repeat} message={T('No recurring entries')} class="px-4 pb-4" />
{:else}
	<div class="h-full overflow-y-auto border-t [&_[data-slot=table-container]]:overflow-visible">
		<Table.Root class="text-[13px]">
			<Table.Body>
				{#each rows as r}
					{@const d = due(r.next_run_date)}
					<Table.Row
						class="cursor-pointer"
						tabindex={0}
						onclick={open}
						onkeydown={(e: KeyboardEvent) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								open();
							}
						}}
					>
						<Table.Cell class="max-w-[10rem] truncate py-1.5 pl-4 font-medium" title={r.name ?? ''}
							>{r.name ?? '—'}</Table.Cell
						>
						<Table.Cell class="py-1.5 text-muted-foreground">{r.frequency ?? ''}</Table.Cell>
						<Table.Cell class="py-1.5 pr-4 text-right tabular-nums">
							<span class="inline-flex items-center gap-1.5">
								{#if d === 'overdue'}
									<CircleAlert class="size-3.5 text-destructive" aria-label={T('Overdue')} />
								{:else if d === 'soon'}
									<Clock class="size-3.5 text-warning" aria-label={T('Due this week')} />
								{/if}
								{r.next_run_date ? dayjs(r.next_run_date).format('YYYY-MM-DD') : '—'}
							</span>
						</Table.Cell>
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</div>
{/if}
