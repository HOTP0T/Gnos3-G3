<script lang="ts">
	import { onMount, getContext, setContext } from 'svelte';
	import { writable } from 'svelte/store';
	import { page } from '$app/state';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import X from '@lucide/svelte/icons/x';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import Clock from '@lucide/svelte/icons/clock';
	import { WEBUI_NAME } from '$lib/stores';
	import { getCompany, getExchangeRates, getGlobalExchangeRates } from '$lib/apis/accounting';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import ModuleShell from '$lib/components/gnos3-ui/ModuleShell.svelte';
	import NavTabs from '$lib/components/gnos3-ui/NavTabs.svelte';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import { cn } from '$lib/utils/shadcn.js';

	let { children } = $props();

	const i18n: any = getContext('i18n');

	let loaded = $state(false);
	let companyName = $state('');
	let companyCurrency = $state('EUR');

	// Global display currency — shared via context to all child components
	const displayCurrency = writable('');
	const exchangeRates = writable<any[]>([]);
	const ratesLoaded = writable(false);
	const companyCurrencyStore = writable('EUR');
	const companyNameStore = writable('');
	setContext('displayCurrency', displayCurrency);
	setContext('exchangeRates', exchangeRates);
	setContext('ratesLoaded', ratesLoaded);
	setContext('companyCurrency', companyCurrencyStore);
	setContext('companyName', companyNameStore);

	// $app/state, not the store: the store still holds the previous page during this layout's first render.
	const companyId = $derived(parseInt(page.params.id ?? '', 10));
	const basePath = $derived(`/accounting/company/${page.params.id}`);

	setContext('companyId', {
		get id() {
			return companyId;
		}
	});

	const CURRENCIES = ['EUR', 'USD', 'GBP', 'CNY', 'JPY', 'CAD', 'AUD', 'CHF', 'BRL', 'INR', 'KRW', 'MXN', 'SGD', 'HKD', 'MAD'];

	const defaultTabs = [
		{ key: 'dashboard', label: 'Dashboard' },
		{ key: 'bank', label: 'Bank' },
		{ key: 'invoices', label: 'Invoices' },
		{ key: 'entries', label: 'Entries' },
		{ key: 'payments', label: 'Payments' },
		{ key: 'expenses', label: 'Expenses' },
		{ key: 'reports', label: 'Reports' },
		{ key: 'tax', label: 'Tax' },
		{ key: 'assets', label: 'Fixed Assets' },
		{ key: 'closing', label: 'Closing' },
		{ key: 'settings', label: 'Settings' }
	];

	// Tab order is per company and survives reloads. Until 2026-10 one order was saved for every
	// company under "…-undefined" (the key was built before the id was known); read it as a fallback.
	const tabOrderKey = () => `accounting-tab-order-${companyId}`;
	const LEGACY_TAB_ORDER_KEY = 'accounting-tab-order-undefined';
	let tabs = $state(defaultTabs);

	function loadTabOrder() {
		try {
			const saved = localStorage.getItem(tabOrderKey()) ?? localStorage.getItem(LEGACY_TAB_ORDER_KEY);
			if (!saved) return;
			const savedKeys: string[] = JSON.parse(saved);
			const tabMap = new Map(defaultTabs.map((t) => [t.key, t]));
			const ordered: typeof defaultTabs = [];
			for (const key of savedKeys) {
				const tab = tabMap.get(key);
				if (tab) {
					ordered.push(tab);
					tabMap.delete(key);
				}
			}
			// Tabs added since the order was saved go at the end
			tabs = [...ordered, ...tabMap.values()];
		} catch {}
	}

	function reorderTabs(from: number, to: number) {
		const next = [...tabs];
		const [moved] = next.splice(from, 1);
		next.splice(to, 0, moved);
		tabs = next;
		try {
			localStorage.setItem(tabOrderKey(), JSON.stringify(tabs.map((t) => t.key)));
		} catch {}
	}

	// Any rate for the selected pair
	const hasRatesForDisplay = $derived(
		$displayCurrency && $displayCurrency !== companyCurrency && $exchangeRates.length > 0
			? $exchangeRates.some(
					(r) =>
						(r.from_currency === companyCurrency && r.to_currency === $displayCurrency) ||
						(r.from_currency === $displayCurrency && r.to_currency === companyCurrency)
				)
			: true
	);

	// A rate for the current month specifically
	const currentMonthKey = new Date().toISOString().slice(0, 7); // "2026-03"
	const hasCurrentMonthRate = $derived(
		!($displayCurrency && $displayCurrency !== companyCurrency) ||
			$exchangeRates.some(
				(r) =>
					r.effective_date?.startsWith(currentMonthKey) &&
					((r.from_currency === companyCurrency && r.to_currency === $displayCurrency) ||
						(r.from_currency === $displayCurrency && r.to_currency === companyCurrency))
			)
	);
	const converted = $derived(!!$displayCurrency && $displayCurrency !== companyCurrency);

	async function loadCompanyData() {
		try {
			const data = await getCompany(companyId);
			companyName = data.name || '';
			companyCurrency = data.currency || 'EUR';
			companyNameStore.set(companyName);
			companyCurrencyStore.set(companyCurrency);
			displayCurrency.set(companyCurrency);

			// Exchange rates: the full shared global set plus any company-specific overrides.
			// Overrides go first so they win on ties in convertAmount's nearest-date search. The
			// full set (not just this company's base) is loaded so consumers that convert from a
			// non-base currency — e.g. bank reconciliation, whose amounts are in the bank
			// account's currency — resolve.
			try {
				const [companyRates, globalRates] = await Promise.all([
					getExchangeRates({ company_id: companyId }).catch(() => []),
					getGlobalExchangeRates().catch(() => [])
				]);
				exchangeRates.set([
					...(Array.isArray(companyRates) ? companyRates : []),
					...(Array.isArray(globalRates) ? globalRates : [])
				]);
				ratesLoaded.set(true);
			} catch {
				exchangeRates.set([]);
				ratesLoaded.set(true);
			}
		} catch (err) {
			console.error('Failed to load company:', err);
		}
	}

	onMount(async () => {
		loadTabOrder();
		await loadCompanyData();
		loaded = true;
	});
</script>

<svelte:head>
	<title>
		{companyName ? `${companyName} - ` : ''}{$i18n.t('Accounting')} &bull; {$WEBUI_NAME}
	</title>
</svelte:head>

{#if loaded}
	<ModuleShell containerId="accounting-container">
		{#snippet nav()}
			<div class="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 pb-1">
				<div class="flex min-w-0 items-center gap-2.5">
					<Button variant="ghost" size="sm" href="/accounting/companies" class="-ml-2 pl-1.5">
						<ArrowLeft />{$i18n.t('Companies')}
					</Button>
					<Separator orientation="vertical" class="h-4!" />
					{#if companyName}
						<h1 class="truncate text-xl leading-7 font-semibold">{companyName}</h1>
					{/if}
					<Badge variant="outline">{companyCurrency}</Badge>
				</div>

				<!-- Display currency: every amount below converts when it differs from the company's -->
				<div class="flex items-center gap-1.5">
					<label for="display-currency" class="text-sm text-muted-foreground"
						>{$i18n.t('Display')}</label
					>
					<NativeSelect.Root
						id="display-currency"
						size="sm"
						class={cn('w-24', converted && 'border-ring text-link font-medium')}
						value={$displayCurrency}
						title={$i18n.t('View amounts in a different currency')}
						onchange={(e: Event) => displayCurrency.set((e.currentTarget as HTMLSelectElement).value)}
					>
						{#each CURRENCIES as cur}
							<NativeSelect.Option value={cur}
								>{cur}{cur === companyCurrency ? ' ●' : ''}</NativeSelect.Option
							>
						{/each}
					</NativeSelect.Root>
					{#if converted}
						{#if !hasRatesForDisplay}
							<Tip
								content={$i18n.t('No exchange rates found for') +
									` ${companyCurrency}→${$displayCurrency}. ` +
									$i18n.t('Import rates in Settings → Exchange Rates.')}
							>
								<TriangleAlert class="size-4 text-warning" aria-label={$i18n.t('No exchange rates')} />
							</Tip>
						{:else}
							<Badge variant="info" class="tabular-nums">{companyCurrency}→{$displayCurrency}</Badge>
						{/if}
						<Tip content={$i18n.t('Reset to company currency')}>
							<Button
								variant="ghost"
								size="icon-xs"
								aria-label={$i18n.t('Reset to company currency')}
								onclick={() => displayCurrency.set(companyCurrency)}
							>
								<X />
							</Button>
						</Tip>
					{/if}
				</div>
			</div>
			<NavTabs
				label={companyName || $i18n.t('Company')}
				onreorder={reorderTabs}
				items={tabs.map((t) => ({
					href: `${basePath}/${t.key}`,
					// "Tax" here is the tax section; elsewhere it is a tax amount
					label: $i18n.t(t.label, { context: 'tab' }),
					active: page.url.pathname.includes(`${basePath}/${t.key}`)
				}))}
			/>
		{/snippet}

		{#if converted && hasRatesForDisplay && !hasCurrentMonthRate}
			<Alert.Root variant="info" class="mb-4">
				<Clock />
				<Alert.Title>{$i18n.t('No exchange rate for the current month')} ({currentMonthKey})</Alert.Title>
				<Alert.Description>
					{$i18n.t('Conversion uses the most recent available rate.')}
					<a href="{basePath}/settings?section=exchange" class="font-medium text-link underline-offset-4 hover:underline"
						>{$i18n.t('Update rates')}</a
					>
				</Alert.Description>
			</Alert.Root>
		{/if}

		{#if converted && !hasRatesForDisplay}
			<Alert.Root variant="warning" class="mb-4">
				<TriangleAlert />
				<Alert.Title>
					{$i18n.t('No exchange rates found for')}
					{companyCurrency}→{$displayCurrency}
				</Alert.Title>
				<Alert.Description>
					{$i18n.t('Amounts cannot be converted.')}
					<a href="{basePath}/settings?section=exchange" class="font-medium text-link underline-offset-4 hover:underline"
						>{$i18n.t('Import rates in Settings → Exchange Rates')}</a
					>
				</Alert.Description>
			</Alert.Root>
		{/if}

		{@render children?.()}
	</ModuleShell>
{/if}
