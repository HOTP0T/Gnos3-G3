<script lang="ts">
	import { getContext } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import ExpenseSheetsList from '$lib/components/accounting/expenses/ExpenseSheetsList.svelte';
	import ExpenseSubmissions from '$lib/components/accounting/expenses/ExpenseSubmissions.svelte';
	import ExpenseDashboard from '$lib/components/accounting/expenses/ExpenseDashboard.svelte';
	import * as Tabs from '$lib/components/ui/tabs/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { getPendingCount } from '$lib/apis/expenses';

	const i18n: any = getContext('i18n');

	$: companyId = parseInt($page.params.id ?? '0', 10);

	// Overview | employee-submitted items (portal) | accountant-assembled sheets.
	// The tab lives in the URL (?tab=), so a sheet's "All sheets" link and the
	// browser's back button return to it.
	const TABS = ['overview', 'submissions', 'sheets'];
	// Overview and submissions need the approver role (accountant) on the
	// company; a viewer only gets the sheets.
	let restricted = false;
	$: allowed = restricted ? ['sheets'] : TABS;
	$: urlTab = $page.url.searchParams.get('tab') ?? '';
	$: tab = allowed.includes(urlTab) ? urlTab : allowed[0];

	const setTab = (value: string) => {
		if (!value || value === urlTab) return;
		const url = new URL($page.url);
		url.searchParams.set('tab', value);
		goto(url, { replaceState: true, noScroll: true, keepFocus: true });
	};

	const forbidden = () => {
		restricted = true;
	};

	let pending = 0;
	const refreshPending = async (id: number) => {
		try {
			pending = (await getPendingCount(id)).count;
		} catch (e: any) {
			pending = 0;
			if (e?.status === 403) forbidden();
		}
	};
	$: if (companyId) {
		restricted = false;
		refreshPending(companyId);
	}
</script>

<Tabs.Root value={tab} onValueChange={setTab} class="gap-4">
	<Tabs.List
		class="max-w-full justify-start overflow-x-auto"
		aria-label={$i18n.t('Expenses', { context: 'tab' })}
	>
		{#if !restricted}
			<Tabs.Trigger value="overview" class="flex-none px-3">{$i18n.t('Overview')}</Tabs.Trigger>
			<Tabs.Trigger value="submissions" class="flex-none px-3">
				{$i18n.t('Employee submissions')}
				{#if pending > 0}
					<Badge variant="count" aria-label="{pending} {$i18n.t('to review')}"
						>{pending > 99 ? '99+' : pending}</Badge
					>
				{/if}
			</Tabs.Trigger>
		{/if}
		<Tabs.Trigger value="sheets" class="flex-none px-3">{$i18n.t('Expense sheets')}</Tabs.Trigger>
	</Tabs.List>

	{#key companyId}
		{#if tab === 'overview'}
			<ExpenseDashboard {companyId} onForbidden={forbidden} />
		{:else if tab === 'submissions'}
			<ExpenseSubmissions
				{companyId}
				onChanged={() => refreshPending(companyId)}
				onForbidden={forbidden}
			/>
		{:else}
			<ExpenseSheetsList {companyId} />
		{/if}
	{/key}
</Tabs.Root>
