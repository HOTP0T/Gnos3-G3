<!--
	Company → Settings: a left nav of sections (a select on narrow screens) and the chosen section.
	The section is kept in the URL (?section=…) so a link can open it directly.
-->
<script lang="ts">
	import { getContext, type Component } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	import ListTree from '@lucide/svelte/icons/list-tree';
	import CalendarRange from '@lucide/svelte/icons/calendar-range';
	import Coins from '@lucide/svelte/icons/coins';
	import Building from '@lucide/svelte/icons/building';
	import BookCheck from '@lucide/svelte/icons/book-check';
	import ListFilter from '@lucide/svelte/icons/list-filter';
	import Repeat from '@lucide/svelte/icons/repeat';
	import Split from '@lucide/svelte/icons/split';
	import Users from '@lucide/svelte/icons/users';
	import Tags from '@lucide/svelte/icons/tags';

	import ChartOfAccounts from '$lib/components/accounting/ChartOfAccounts.svelte';
	import AccountingPeriods from '$lib/components/accounting/AccountingPeriods.svelte';
	import CategorizationRules from '$lib/components/accounting/CategorizationRules.svelte';
	import BookingDefaults from '$lib/components/accounting/BookingDefaults.svelte';
	import ControlAccountPostings from '$lib/components/accounting/ControlAccountPostings.svelte';
	import ExchangeRates from '$lib/components/accounting/ExchangeRates.svelte';
	import FixedAssets from '$lib/components/accounting/FixedAssets.svelte';
	import RecurringTemplates from '$lib/components/accounting/RecurringTemplates.svelte';
	import EmployeesManager from '$lib/components/accounting/EmployeesManager.svelte';
	import ExpenseCategoriesManager from '$lib/components/accounting/ExpenseCategoriesManager.svelte';

	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import { cn } from '$lib/utils/shadcn.js';

	const i18n: any = getContext('i18n');

	let { companyId }: { companyId: number } = $props();

	type Section = { key: string; label: string; icon: Component };

	const GROUPS: { label: string; sections: Section[] }[] = [
		{
			label: 'Ledger',
			sections: [
				{ key: 'chart', label: 'Chart of Accounts', icon: ListTree },
				{ key: 'periods', label: 'Accounting Periods', icon: CalendarRange },
				{ key: 'exchange', label: 'Exchange Rates', icon: Coins },
				{ key: 'assets', label: 'Fixed Assets', icon: Building }
			]
		},
		{
			label: 'Booking',
			sections: [
				{ key: 'booking', label: 'Booking Defaults', icon: BookCheck },
				{ key: 'categorization', label: 'Categorization Rules', icon: ListFilter },
				{ key: 'recurring', label: 'Recurring Transactions', icon: Repeat },
				{ key: 'reclassify', label: 'Postings on Control Accounts', icon: Split }
			]
		},
		{
			label: 'Expenses',
			sections: [
				{ key: 'employees', label: 'Employees', icon: Users },
				{ key: 'expenseCategories', label: 'Expense Categories', icon: Tags }
			]
		}
	];
	const KEYS = GROUPS.flatMap((g) => g.sections.map((s) => s.key));

	const active = $derived.by(() => {
		const s = $page.url.searchParams.get('section');
		return s && KEYS.includes(s) ? s : 'chart';
	});

	function select(key: string) {
		if (key === active) return;
		const url = new URL($page.url);
		url.searchParams.set('section', key);
		goto(`${url.pathname}${url.search}`, { replaceState: true, noScroll: true, keepFocus: true });
		document.getElementById('accounting-container')?.scrollTo({ top: 0 });
	}
</script>

<div class="@container">
	<div class="grid gap-6 @4xl:grid-cols-[15rem_minmax(0,1fr)]">
		<!-- Section nav: a list from 896px of content width, a select below -->
		<nav
			aria-label={$i18n.t('Settings')}
			class="hidden content-start gap-4 self-start @4xl:sticky @4xl:top-0 @4xl:grid"
		>
			{#each GROUPS as group}
				<div class="grid gap-0.5">
					<div class="px-2 pb-1 text-xs font-medium text-muted-foreground">
						{$i18n.t(group.label, { context: 'tab' })}
					</div>
					{#each group.sections as s (s.key)}
						<button
							type="button"
							aria-current={active === s.key ? 'page' : undefined}
							class={cn(
								'flex h-8 items-center gap-2 rounded-md px-2 text-left text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none',
								active === s.key && 'bg-accent font-medium text-foreground'
							)}
							onclick={() => select(s.key)}
						>
							<s.icon class="size-4 shrink-0" aria-hidden="true" />
							<span class="min-w-0 truncate">{$i18n.t(s.label)}</span>
						</button>
					{/each}
				</div>
			{/each}
		</nav>

		<div class="@4xl:hidden">
			<label for="settings-section" class="sr-only">{$i18n.t('Section')}</label>
			<NativeSelect.Root
				id="settings-section"
				class="w-full"
				value={active}
				onchange={(e: Event) => select((e.currentTarget as HTMLSelectElement).value)}
			>
				{#each GROUPS as group}
					<NativeSelect.OptGroup label={$i18n.t(group.label, { context: 'tab' })}>
						{#each group.sections as s (s.key)}
							<NativeSelect.Option value={s.key}>{$i18n.t(s.label)}</NativeSelect.Option>
						{/each}
					</NativeSelect.OptGroup>
				{/each}
			</NativeSelect.Root>
		</div>

		<section class="min-w-0">
			{#key `${companyId}-${active}`}
				{#if active === 'chart'}
					<ChartOfAccounts {companyId} />
				{:else if active === 'periods'}
					<AccountingPeriods {companyId} />
				{:else if active === 'exchange'}
					<ExchangeRates {companyId} />
				{:else if active === 'assets'}
					<FixedAssets {companyId} />
				{:else if active === 'booking'}
					<BookingDefaults {companyId} />
				{:else if active === 'categorization'}
					<CategorizationRules {companyId} />
				{:else if active === 'recurring'}
					<RecurringTemplates {companyId} />
				{:else if active === 'reclassify'}
					<ControlAccountPostings {companyId} />
				{:else if active === 'employees'}
					<EmployeesManager {companyId} />
				{:else if active === 'expenseCategories'}
					<ExpenseCategoriesManager {companyId} />
				{/if}
			{/key}
		</section>
	</div>
</div>
