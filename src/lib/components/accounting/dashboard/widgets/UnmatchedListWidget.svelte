<script lang="ts">
	// Unmatched bank statement lines — from /companies/{id}/unmatched-bank-lines.
	// A row opens bank reconciliation (click or Enter).
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import dayjs from 'dayjs';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import { getUnmatchedBankLines } from '$lib/apis/accounting';
	import * as Table from '$lib/components/ui/table/index.js';
	import WidgetState from '../WidgetState.svelte';
	import { fmtNumber } from '../format';

	export let companyId: number;
	export let options: { limit?: number } = {};
	const i18n: any = getContext('i18n');
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);
	$: limit = options?.limit ?? 20;

	let rows: any[] = [];
	let loading = true;
	let error = false;

	onMount(load);
	async function load() {
		loading = true;
		error = false;
		try {
			const res = await getUnmatchedBankLines(companyId, { limit });
			rows = Array.isArray(res) ? res : (res?.items ?? []);
		} catch {
			rows = [];
			error = true;
		}
		loading = false;
	}

	const open = () => goto(`/accounting/company/${companyId}/bank`);
</script>

{#if loading}
	<WidgetState state="loading" rows={6} class="px-4 pb-4" />
{:else if error}
	<WidgetState state="error" onretry={load} class="px-4 pb-4" />
{:else if rows.length === 0}
	<WidgetState
		state="empty"
		icon={CircleCheck}
		message={T('All bank lines reconciled')}
		class="px-4 pb-4"
	/>
{:else}
	<div class="h-full overflow-y-auto border-t [&_[data-slot=table-container]]:overflow-visible">
		<Table.Root class="text-[13px]">
			<Table.Body>
				{#each rows as line}
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
						<Table.Cell class="py-1.5 pl-4 text-muted-foreground tabular-nums">
							{line.transaction_date ? dayjs(line.transaction_date).format('YYYY-MM-DD') : '—'}
						</Table.Cell>
						<Table.Cell
							class="max-w-[12rem] truncate py-1.5"
							title={line.description ?? line.reference ?? ''}
						>
							{line.description ?? line.reference ?? '—'}
						</Table.Cell>
						<Table.Cell class="py-1.5 pr-4 text-right tabular-nums">
							{fmtNumber(line.amount ?? 0)}
						</Table.Cell>
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</div>
{/if}
