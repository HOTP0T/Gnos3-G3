<script lang="ts">
	import { getContext } from 'svelte';
	import { page } from '$app/stores';
	import ExpenseSheetsList from '$lib/components/accounting/expenses/ExpenseSheetsList.svelte';
	import ExpenseSubmissions from '$lib/components/accounting/expenses/ExpenseSubmissions.svelte';
	import ExpenseDashboard from '$lib/components/accounting/expenses/ExpenseDashboard.svelte';
	import * as Tabs from '$lib/components/ui/tabs/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { getPendingCount } from '$lib/apis/expenses';

	const i18n: any = getContext('i18n');

	$: companyId = parseInt($page.params.id ?? '0', 10);

	// Overview | employee-submitted items (portal) | accountant-assembled sheets.
	let tab: string = 'overview';
	let pending = 0;

	const refreshPending = async (id: number) => {
		try {
			pending = (await getPendingCount(id)).count;
		} catch {
			pending = 0;
		}
	};
	$: if (companyId) refreshPending(companyId);
</script>

<Tabs.Root bind:value={tab} class="gap-4">
	<Tabs.List class="max-w-full justify-start overflow-x-auto" aria-label={$i18n.t('Expenses', { context: 'tab' })}>
		<Tabs.Trigger value="overview" class="flex-none px-3">{$i18n.t('Overview')}</Tabs.Trigger>
		<Tabs.Trigger value="submissions" class="flex-none px-3">
			{$i18n.t('Employee submissions')}
			{#if pending > 0}
				<Badge variant="count" aria-label="{pending} {$i18n.t('to review')}"
					>{pending > 99 ? '99+' : pending}</Badge
				>
			{/if}
		</Tabs.Trigger>
		<Tabs.Trigger value="sheets" class="flex-none px-3">{$i18n.t('Expense sheets')}</Tabs.Trigger>
	</Tabs.List>

	{#if tab === 'overview'}
		<ExpenseDashboard {companyId} />
	{:else if tab === 'submissions'}
		<ExpenseSubmissions {companyId} />
	{:else}
		<ExpenseSheetsList {companyId} />
	{/if}
</Tabs.Root>
