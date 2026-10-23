<script lang="ts">
	import { onMount, getContext } from 'svelte';

	import * as Tabs from '$lib/components/ui/tabs/index.js';
	import GeneralLedger from './GeneralLedger.svelte';
	import TrialBalance from './TrialBalance.svelte';
	import ProfitLoss from './ProfitLoss.svelte';
	import BalanceSheet from './BalanceSheet.svelte';
	import CashFlow from './CashFlow.svelte';
	import AgingReport from './AgingReport.svelte';
	import StatutoryStatements from './StatutoryStatements.svelte';
	import { getStatementLayout, type StatementLayout } from '$lib/apis/accounting';

	const i18n: any = getContext('i18n');

	export let companyId: number;

	type ReportTab =
		| 'statements'
		| 'general-ledger'
		| 'trial-balance'
		| 'profit-loss'
		| 'balance-sheet'
		| 'cash-flow'
		| 'ap-aging'
		| 'ar-aging';

	let activeReport: ReportTab = 'general-ledger';

	// A company whose country has a prescribed filing layout (today: China,
	// 小企业会计准则) gets an extra tab holding those statements, and opens on it —
	// that is the form its accountant actually files.
	let statementLayout: StatementLayout | null = null;
	$: hasStatements = !!statementLayout?.layout;

	onMount(async () => {
		try {
			statementLayout = await getStatementLayout(companyId);
			if (statementLayout?.layout) activeReport = 'statements';
		} catch (err) {
			console.error('Failed to resolve statement layout:', err);
		}
	});

	const baseTabs: Array<{ id: ReportTab; label: string }> = [
		{ id: 'general-ledger', label: 'General Ledger' },
		{ id: 'trial-balance', label: 'Trial Balance' },
		{ id: 'profit-loss', label: 'P&L' },
		{ id: 'balance-sheet', label: 'Balance Sheet' },
		{ id: 'cash-flow', label: 'Cash Flow' },
		{ id: 'ap-aging', label: 'AP Aging' },
		{ id: 'ar-aging', label: 'AR Aging' }
	];

	$: tabs = hasStatements
		? [{ id: 'statements' as ReportTab, label: 'Statutory Statements' }, ...baseTabs]
		: baseTabs;
</script>

<!-- Report picker: segmented tabs (views of the same books); only the active report mounts. -->
<Tabs.Root
	value={activeReport}
	onValueChange={(v) => (activeReport = v as ReportTab)}
	class="min-w-0 gap-4"
>
	<Tabs.List
		aria-label={$i18n.t('Reports')}
		class="max-w-full justify-start overflow-x-auto [scrollbar-width:none]"
	>
		{#each tabs as tab (tab.id)}
			<Tabs.Trigger value={tab.id} class="flex-[1_0_auto] px-2.5">{$i18n.t(tab.label)}</Tabs.Trigger
			>
		{/each}
	</Tabs.List>

	{#if hasStatements}
		<Tabs.Content value="statements" class="min-w-0">
			{#if activeReport === 'statements'}
				<StatutoryStatements
					{companyId}
					layoutLabel={statementLayout?.label_en ? $i18n.t(statementLayout.label_en) : null}
					layoutKey={statementLayout?.layout ?? null}
					presentation={statementLayout?.presentation ?? null}
				/>
			{/if}
		</Tabs.Content>
	{/if}
	<Tabs.Content value="general-ledger" class="min-w-0">
		{#if activeReport === 'general-ledger'}<GeneralLedger {companyId} />{/if}
	</Tabs.Content>
	<Tabs.Content value="trial-balance" class="min-w-0">
		{#if activeReport === 'trial-balance'}<TrialBalance {companyId} />{/if}
	</Tabs.Content>
	<Tabs.Content value="profit-loss" class="min-w-0">
		{#if activeReport === 'profit-loss'}<ProfitLoss {companyId} />{/if}
	</Tabs.Content>
	<Tabs.Content value="balance-sheet" class="min-w-0">
		{#if activeReport === 'balance-sheet'}<BalanceSheet {companyId} />{/if}
	</Tabs.Content>
	<Tabs.Content value="cash-flow" class="min-w-0">
		{#if activeReport === 'cash-flow'}<CashFlow {companyId} />{/if}
	</Tabs.Content>
	<Tabs.Content value="ap-aging" class="min-w-0">
		{#if activeReport === 'ap-aging'}<AgingReport {companyId} reportType="ap" />{/if}
	</Tabs.Content>
	<Tabs.Content value="ar-aging" class="min-w-0">
		{#if activeReport === 'ar-aging'}<AgingReport {companyId} reportType="ar" />{/if}
	</Tabs.Content>
</Tabs.Root>
