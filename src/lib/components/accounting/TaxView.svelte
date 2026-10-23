<script lang="ts">
	import { getContext, onMount } from 'svelte';

	import { getTaxAccounts, getTaxConfig } from '$lib/apis/accounting';
	import { citTerm, taxTerm } from '$lib/utils/taxTerms';
	import TaxDeclaration from './TaxDeclaration.svelte';
	import IsDeclaration from './IsDeclaration.svelte';
	import IrDeclaration from './IrDeclaration.svelte';
	import TaxAccountsSettings from './TaxAccountsSettings.svelte';

	import * as Tabs from '$lib/components/ui/tabs/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';

	const i18n: any = getContext('i18n');

	export let companyId: number;

	type TaxTab = 'vat' | 'is' | 'ir' | 'accounts';
	let activeTab: TaxTab = 'vat';

	// The country decides which taxes exist: Hong Kong has no VAT and no salary
	// withholding, so those tabs are not shown at all. Tabs are named in the UI
	// language from what the tax is (VAT / GST…, corporate income tax / Profits Tax).
	// undefined = still loading (nothing rendered), null = could not load (all tabs shown).
	let cfg: any = undefined;
	$: hasVat = cfg ? cfg.has_vat !== false : true;
	$: withholdsIit = cfg ? cfg.withholds_iit !== false : true;
	$: tabs = [
		...(hasVat ? [{ id: 'vat' as TaxTab, label: taxTerm($i18n.t, cfg) }] : []),
		{ id: 'is' as TaxTab, label: citTerm($i18n.t, cfg) },
		...(withholdsIit
			? [{ id: 'ir' as TaxTab, label: $i18n.t('Individual income tax') }]
			: []),
		{ id: 'accounts' as TaxTab, label: $i18n.t('Accounts') }
	];
	$: if (cfg && !tabs.some((t) => t.id === activeTab)) activeTab = tabs[0].id;

	// Count of unmapped roles that exist in this jurisdiction — shown on the
	// Accounts tab so a blocked settlement entry has an obvious place to go.
	let missing = 0;
	const refreshMissing = async () => {
		try {
			const map = await getTaxAccounts(companyId);
			missing = (map.roles ?? []).filter(
				(r: any) => r.source === 'missing' && r.applicable !== false
			).length;
		} catch {
			missing = 0;
		}
	};
	onMount(async () => {
		try {
			cfg = await getTaxConfig(companyId);
			if (cfg?.has_vat === false) activeTab = 'is';
		} catch {
			cfg = null;
		}
		await refreshMissing();
	});

	// Remount the declaration tabs after a mapping change so they re-resolve.
	let mapVersion = 0;
	const onSaved = () => {
		mapVersion += 1;
		refreshMissing();
	};
	const gotoAccounts = () => (activeTab = 'accounts');
</script>

<div class="flex flex-col gap-4">
	{#if cfg === undefined}
		<Skeleton class="h-9 w-72 max-w-full" />
		<Skeleton class="h-40 w-full rounded-xl" />
	{:else}
		<Tabs.Root value={activeTab} onValueChange={(v) => (activeTab = v as TaxTab)} class="gap-4">
			<div class="flex max-w-full overflow-x-auto">
				<Tabs.List>
					{#each tabs as tab (tab.id)}
						<Tabs.Trigger value={tab.id} class="px-3">
							{tab.label}
							{#if tab.id === 'accounts' && missing > 0}
								<Badge
									variant="danger"
									class="h-[18px] min-w-[18px] rounded-full px-1 tabular-nums"
									title={$i18n.t('Unmapped tax roles')}
								>
									{missing}<span class="sr-only">{$i18n.t('Unmapped tax roles')}</span>
								</Badge>
							{/if}
						</Tabs.Trigger>
					{/each}
				</Tabs.List>
			</div>

			{#if cfg && (!hasVat || !withholdsIit)}
				<p class="text-sm text-muted-foreground">
					{#if !hasVat}
						{$i18n.t(
							'{{country}} levies no VAT / GST: there is no VAT return, and any tax printed on a supplier bill is booked as part of the cost.',
							{ country: cfg.country }
						)}
					{/if}
					{#if !withholdsIit}
						{$i18n.t(
							"Employers do not withhold Salaries Tax — employees settle it themselves; the employer files the yearly Employer's Return (BIR56A / IR56B) in April."
						)}
					{/if}
				</p>
			{/if}

			<Tabs.Content value={activeTab}>
				{#key mapVersion}
					{#if activeTab === 'vat'}
						<TaxDeclaration {companyId} on:gotoAccounts={gotoAccounts} />
					{:else if activeTab === 'is'}
						<IsDeclaration {companyId} on:gotoAccounts={gotoAccounts} />
					{:else if activeTab === 'ir'}
						<IrDeclaration {companyId} on:gotoAccounts={gotoAccounts} />
					{:else if activeTab === 'accounts'}
						<TaxAccountsSettings {companyId} on:saved={onSaved} />
					{/if}
				{/key}
			</Tabs.Content>
		</Tabs.Root>
	{/if}
</div>
