<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';

	import { getCompany, updateCompany, getAccounts } from '$lib/apis/accounting';

	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';

	const i18n: any = getContext('i18n');

	export let companyId: number;

	let loading = true;
	let loadError = '';
	let saving = false;
	let accounts: any[] = [];
	let apId: number | '' = '';
	let arId: number | '' = '';
	let savedAp: number | '' = '';
	let savedAr: number | '' = '';
	// Exchange differences: gain (revenue), loss (expense), and the clearing
	// account a base-currency amount passes through when paid from a
	// foreign-currency bank. Unset → the difference is a gap, never dropped.
	let gainId: number | '' = '';
	let lossId: number | '' = '';
	let clearingId: number | '' = '';
	let savedGain: number | '' = '';
	let savedLoss: number | '' = '';
	let savedClearing: number | '' = '';

	$: parentIds = new Set(accounts.map((a: any) => a.parent_id).filter(Boolean));
	$: leaf = accounts.filter((a: any) => !parentIds.has(a.id));
	$: liabilities = leaf.filter((a: any) => a.account_type === 'liability');
	$: assets = leaf.filter((a: any) => a.account_type === 'asset');
	$: revenues = leaf.filter((a: any) => a.account_type === 'revenue');
	$: expenses = leaf.filter((a: any) => a.account_type === 'expense');
	$: dirty =
		apId !== savedAp ||
		arId !== savedAr ||
		gainId !== savedGain ||
		lossId !== savedLoss ||
		clearingId !== savedClearing;

	const load = async () => {
		loading = true;
		loadError = '';
		try {
			const [co, accts] = await Promise.all([
				getCompany(companyId),
				getAccounts({ company_id: companyId, active: true })
			]);
			accounts = Array.isArray(accts) ? accts : (accts?.items ?? accts?.accounts ?? []);
			apId = savedAp = co?.default_ap_account_id ?? '';
			arId = savedAr = co?.default_ar_account_id ?? '';
			gainId = savedGain = co?.fx_gain_account_id ?? '';
			lossId = savedLoss = co?.fx_loss_account_id ?? '';
			clearingId = savedClearing = co?.fx_clearing_account_id ?? '';
		} catch (err: any) {
			loadError = `${$i18n.t('Failed to load')}: ${err?.detail ?? err}`;
		}
		loading = false;
	};

	onMount(load);

	const save = async () => {
		saving = true;
		try {
			await updateCompany(companyId, {
				default_ap_account_id: apId === '' ? null : Number(apId),
				default_ar_account_id: arId === '' ? null : Number(arId),
				fx_gain_account_id: gainId === '' ? null : Number(gainId),
				fx_loss_account_id: lossId === '' ? null : Number(lossId),
				fx_clearing_account_id: clearingId === '' ? null : Number(clearingId)
			});
			savedAp = apId;
			savedAr = arId;
			savedGain = gainId;
			savedLoss = lossId;
			savedClearing = clearingId;
			toast.success($i18n.t('Booking defaults saved'));
		} catch (err: any) {
			toast.error(`${$i18n.t('Failed to save')}: ${err?.detail ?? err}`);
		}
		saving = false;
	};
</script>

<!-- Settings row: label and what an empty value means on the left, the account on the right -->
{#snippet label(id: string, text: string, unset: boolean, unsetText: string)}
	<div class="grid min-w-0 gap-1.5">
		<Label for={id}>{text}</Label>
		{#if unset}
			<Badge variant="warning" class="whitespace-normal">
				<TriangleAlert aria-hidden="true" />{unsetText}
			</Badge>
		{/if}
	</div>
{/snippet}

<div class="flex flex-col gap-4">
	<div class="space-y-1">
		<h2 class="text-lg font-semibold">{$i18n.t('Booking Defaults')}</h2>
		<p class="text-sm text-muted-foreground">
			{$i18n.t('Accounts the booking engine uses when nothing more specific names one.')}
		</p>
	</div>

	{#if loading}
		<Card.Root>
			<Card.Content class="grid gap-4">
				{#each Array(5) as _}
					<div class="flex items-center justify-between gap-6">
						<Skeleton class="h-4 w-56" />
						<Skeleton class="h-9 w-80" />
					</div>
				{/each}
			</Card.Content>
		</Card.Root>
	{:else if loadError}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{loadError}</Alert.Title>
			<Alert.Action>
				<Button variant="outline" size="sm" onclick={load}>{$i18n.t('Retry')}</Button>
			</Alert.Action>
		</Alert.Root>
	{:else}
		<Card.Root>
			<Card.Header>
				<Card.Title>{$i18n.t('Counterparty accounts')}</Card.Title>
				<Card.Description>
					{$i18n.t(
						'Counterparty accounts used when an invoice is booked and no categorisation rule names one for the vendor. Nothing is guessed: with no rule and no default, the entry is created with the counterparty line left open for you to fill.'
					)}
				</Card.Description>
			</Card.Header>
			<Card.Content class="divide-y">
				<div
					class="flex flex-col gap-2 py-3 first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between sm:gap-6"
				>
					{@render label(
						'bd-ap',
						$i18n.t('Default supplier (AP) account — purchases'),
						apId === '',
						$i18n.t('Not set: purchase entries keep an open counterparty line')
					)}
					<NativeSelect.Root id="bd-ap" class="w-full sm:w-80 sm:shrink-0" bind:value={apId}>
						<NativeSelect.Option value="">{$i18n.t('— none: ask every time —')}</NativeSelect.Option
						>
						{#each liabilities as a}
							<NativeSelect.Option value={a.id}>{a.code} - {a.name}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
				<div
					class="flex flex-col gap-2 py-3 first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between sm:gap-6"
				>
					{@render label(
						'bd-ar',
						$i18n.t('Default customer (AR) account — sales'),
						arId === '',
						$i18n.t('Not set: sales entries keep an open counterparty line')
					)}
					<NativeSelect.Root id="bd-ar" class="w-full sm:w-80 sm:shrink-0" bind:value={arId}>
						<NativeSelect.Option value="">{$i18n.t('— none: ask every time —')}</NativeSelect.Option
						>
						{#each assets as a}
							<NativeSelect.Option value={a.id}>{a.code} - {a.name}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Header>
				<Card.Title>{$i18n.t('Exchange differences')}</Card.Title>
				<Card.Description>
					{$i18n.t(
						'Exchange differences — a USD bill paid at a later rate, or a HKD tax paid from a USD account — are booked to the gain / loss accounts below. A base-currency amount paid from a foreign-currency bank passes through the clearing account so the obligation clears to the cent. Unset: the difference stays as a gap on a draft.'
					)}
				</Card.Description>
			</Card.Header>
			<Card.Content class="divide-y">
				<div
					class="flex flex-col gap-2 py-3 first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between sm:gap-6"
				>
					{@render label(
						'bd-gain',
						$i18n.t('Exchange gain account'),
						gainId === '',
						$i18n.t('Not set: gains stay as a gap on a draft')
					)}
					<NativeSelect.Root id="bd-gain" class="w-full sm:w-80 sm:shrink-0" bind:value={gainId}>
						<NativeSelect.Option value="">{$i18n.t('— none —')}</NativeSelect.Option>
						{#each revenues as a}
							<NativeSelect.Option value={a.id}>{a.code} - {a.name}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
				<div
					class="flex flex-col gap-2 py-3 first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between sm:gap-6"
				>
					{@render label(
						'bd-loss',
						$i18n.t('Exchange loss account'),
						lossId === '',
						$i18n.t('Not set: losses stay as a gap on a draft')
					)}
					<NativeSelect.Root id="bd-loss" class="w-full sm:w-80 sm:shrink-0" bind:value={lossId}>
						<NativeSelect.Option value="">{$i18n.t('— none —')}</NativeSelect.Option>
						{#each expenses as a}
							<NativeSelect.Option value={a.id}>{a.code} - {a.name}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
				<div
					class="flex flex-col gap-2 py-3 first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between sm:gap-6"
				>
					{@render label(
						'bd-clearing',
						$i18n.t('Exchange clearing account'),
						clearingId === '',
						$i18n.t('Not set: foreign-bank payments of base-currency amounts stay as a gap')
					)}
					<NativeSelect.Root
						id="bd-clearing"
						class="w-full sm:w-80 sm:shrink-0"
						bind:value={clearingId}
					>
						<NativeSelect.Option value="">{$i18n.t('— none —')}</NativeSelect.Option>
						{#each [...assets, ...liabilities] as a}
							<NativeSelect.Option value={a.id}>{a.code} - {a.name}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
			</Card.Content>
		</Card.Root>

		<div class="flex flex-wrap items-center justify-end gap-3">
			{#if dirty}
				<span class="text-sm text-muted-foreground">{$i18n.t('Unsaved changes')}</span>
			{/if}
			<Button disabled={saving || !dirty} onclick={save}>
				{#if saving}<Spinner />{/if}
				{saving ? $i18n.t('Saving...') : $i18n.t('Save')}
			</Button>
		</div>
	{/if}
</div>
