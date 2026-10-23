<script lang="ts">
	import { onMount, getContext, createEventDispatcher } from 'svelte';
	import { toast } from 'svelte-sonner';

	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import Info from '@lucide/svelte/icons/info';
	import Pencil from '@lucide/svelte/icons/pencil';
	import X from '@lucide/svelte/icons/x';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';

	import { getTaxAccounts, updateTaxAccounts, getAccounts } from '$lib/apis/accounting';
	import { CIT_KIND_TERMS, TAX_KIND_TERMS } from '$lib/utils/taxTerms';

	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let companyId: number;

	type Acct = {
		id: number;
		code: string;
		name: string;
		account_type?: string;
		parent_id?: number | null;
	};
	type Role = {
		role: string;
		label: string;
		group: string;
		multi: boolean;
		account_type: string | null;
		source: 'mapped' | 'default' | 'missing';
		accounts: Acct[];
		applicable?: boolean; // false = the role does not exist in this jurisdiction (VAT in Hong Kong)
	};

	let loading = true;
	let loadError = '';
	let saving = false;
	let country = '';
	// i18n keys for the group titles, from what the taxes are (VAT / GST…,
	// corporate income tax / Profits Tax) — never the country's own labels.
	let taxLabel = 'VAT';
	let citLabel = 'Corporate income tax';
	let roles: Role[] = [];
	let accounts: Acct[] = [];
	// Working copy: role → account ids. Only roles the user touched are sent.
	let draft: Record<string, number[]> = {};
	let dirty: Set<string> = new Set();
	// Per-role "add another" picker value (multi roles)
	let adder: Record<string, number | ''> = {};

	$: GROUPS = [
		{
			id: 'vat',
			label: taxLabel,
			hint: 'Accounts the return reads (output / input) and the settlement entry posts to.'
		},
		{
			id: 'surcharges',
			label: 'VAT surcharges',
			hint: "Only used where the country levies surcharges on VAT payable (e.g. China's urban construction tax and education surcharges)."
		},
		{
			id: 'cit',
			label: citLabel,
			hint: 'Accrual entry (expense / payable), the account the tax payment debits, and — where the tax office bills prepayments — the prepaid-tax asset.'
		},
		{ id: 'iit', label: 'Individual income tax', hint: 'Account the IIT payment debits.' },
		{
			id: 'payroll',
			label: 'MPF (Mandatory Provident Fund)',
			hint: 'Payable to the trustee by the 10th of the following month (employee 5% withheld + employer 5%), and the employer contribution expense.'
		}
	] as Array<{ id: string; label: string; hint: string }>;

	$: parentIds = new Set(accounts.map((a) => a.parent_id).filter(Boolean));
	$: leafAccounts = accounts.filter((a) => !parentIds.has(a.id));
	$: byId = new Map(accounts.map((a) => [a.id, a]));

	const candidates = (role: Role): Acct[] => {
		// Prefer the role's account type; fall back to every leaf so an unusual chart still works.
		const typed = role.account_type
			? leafAccounts.filter((a) => a.account_type === role.account_type)
			: [];
		return typed.length ? typed : leafAccounts;
	};

	const load = async () => {
		loading = true;
		loadError = '';
		try {
			const [map, accts] = await Promise.all([
				getTaxAccounts(companyId),
				getAccounts({ company_id: companyId, active: true })
			]);
			country = map.country ?? '';
			taxLabel = TAX_KIND_TERMS[map.tax_kind] ?? 'VAT';
			citLabel = CIT_KIND_TERMS[map.cit_kind] ?? 'Corporate income tax';
			// Roles that do not exist in this jurisdiction are not offered at all.
			roles = (map.roles ?? []).filter((r: Role) => r.applicable !== false);
			accounts = Array.isArray(accts) ? accts : (accts?.items ?? accts?.accounts ?? []);
			draft = Object.fromEntries(roles.map((r) => [r.role, r.accounts.map((a) => a.id)]));
			dirty = new Set();
			adder = {};
		} catch (err: any) {
			loadError = `${$i18n.t('Failed to load tax accounts')}: ${err?.detail ?? err}`;
		}
		loading = false;
	};

	onMount(load);

	const touch = (role: string) => {
		dirty = new Set(dirty).add(role);
		draft = { ...draft };
	};

	const setSingle = (role: string, value: number | '') => {
		draft[role] = value === '' ? [] : [Number(value)];
		touch(role);
	};

	const addMulti = (role: string) => {
		const v = adder[role];
		if (v === '' || v === undefined) return;
		const id = Number(v);
		if (!draft[role].includes(id)) draft[role] = [...draft[role], id];
		adder[role] = '';
		touch(role);
	};

	const removeMulti = (role: string, id: number) => {
		draft[role] = draft[role].filter((x) => x !== id);
		touch(role);
	};

	const resetRole = (role: string) => {
		draft[role] = [];
		touch(role);
	};

	const save = async () => {
		if (dirty.size === 0) return;
		saving = true;
		try {
			const mappings: Record<string, number[]> = {};
			for (const r of dirty) mappings[r] = draft[r] ?? [];
			await updateTaxAccounts(companyId, mappings);
			toast.success($i18n.t('Tax accounts saved'));
			await load();
			dispatch('saved');
		} catch (err: any) {
			toast.error(`${$i18n.t('Failed to save tax accounts')}: ${err?.detail ?? err}`);
		}
		saving = false;
	};

	$: missingCount = roles.filter((r) => r.source === 'missing').length;
	$: defaultCount = roles.filter((r) => r.source === 'default').length;

	// Defaults are deterministic but unconfirmed: automation only uses mapped
	// accounts. One click turns every current default into an explicit mapping.
	const confirmDefaults = async () => {
		const mappings: Record<string, number[]> = {};
		for (const r of roles)
			if (r.source === 'default') mappings[r.role] = r.accounts.map((a) => a.id);
		if (Object.keys(mappings).length === 0) return;
		saving = true;
		try {
			await updateTaxAccounts(companyId, mappings);
			toast.success($i18n.t('Defaults confirmed'));
			await load();
			dispatch('saved');
		} catch (err: any) {
			toast.error(`${$i18n.t('Failed to save tax accounts')}: ${err?.detail ?? err}`);
		}
		saving = false;
	};
</script>

<!-- Where the role's account comes from: mapped ✓, a default to confirm, or missing -->
{#snippet sourceBadge(r: Role, isDirty: boolean)}
	{#if isDirty}
		<Badge variant="status"><Pencil aria-hidden="true" />{$i18n.t('unsaved')}</Badge>
	{:else if r.source === 'mapped'}
		<Badge variant="status">
			<CircleCheck class="text-success" aria-hidden="true" />{$i18n.t('mapped')}
		</Badge>
	{:else if r.source === 'default'}
		<Badge variant="info"><Info aria-hidden="true" />{$i18n.t('Default — confirm')}</Badge>
	{:else}
		<Badge variant="warning"><TriangleAlert aria-hidden="true" />{$i18n.t('missing')}</Badge>
	{/if}
{/snippet}

<div class="flex flex-col gap-4">
	<div class="space-y-1">
		<h2 class="flex flex-wrap items-center gap-2 text-lg font-semibold">
			{$i18n.t('Tax accounts')}
			{#if country}
				<Badge variant="outline">{country}</Badge>
			{/if}
		</h2>
		<p class="text-sm text-muted-foreground">
			{$i18n.t(
				'Which GL accounts play each tax role for this company. "default" is resolved from the country config and the chart; map an account to override it. Only detail (leaf) accounts can be mapped.'
			)}
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
		{#if missingCount > 0}
			<Alert.Root variant="warning">
				<TriangleAlert />
				<Alert.Title>
					{$i18n.t(
						'{{count}} role(s) have no account. Declarations still compute, but settlement entries and payments that need them are blocked until mapped.',
						{ count: missingCount }
					)}
				</Alert.Title>
			</Alert.Root>
		{/if}
		{#if defaultCount > 0}
			<Alert.Root variant="info">
				<Info />
				<Alert.Title>
					{$i18n.t(
						'{{count}} role(s) are resolved from the country defaults but not confirmed. Automatic booking (rules, expense sheets) only uses confirmed accounts.',
						{ count: defaultCount }
					)}
				</Alert.Title>
				<Alert.Description>
					<Button
						variant="outline"
						size="sm"
						class="mt-2"
						disabled={saving}
						onclick={confirmDefaults}
					>
						<CircleCheck />{$i18n.t('Confirm all defaults')}
					</Button>
				</Alert.Description>
			</Alert.Root>
		{/if}

		{#each GROUPS as g}
			{@const groupRoles = roles.filter((r) => r.group === g.id)}
			{#if groupRoles.length}
				<Card.Root>
					<Card.Header>
						<Card.Title>{$i18n.t(g.label)}</Card.Title>
						<Card.Description>{$i18n.t(g.hint)}</Card.Description>
					</Card.Header>
					<Card.Content class="divide-y">
						{#each groupRoles as r (r.role)}
							{@const ids = draft[r.role] ?? []}
							<div
								class="flex flex-col gap-2 py-3 first:pt-0 last:pb-0 md:flex-row md:items-start md:justify-between md:gap-6"
							>
								<div class="grid min-w-0 gap-1.5 md:pt-1.5">
									<label for="tax-role-{r.role}" class="text-sm font-medium"
										>{$i18n.t(r.label)}</label
									>
									{@render sourceBadge(r, dirty.has(r.role))}
								</div>
								<div class="flex w-full min-w-0 flex-col gap-2 md:w-96 md:shrink-0">
									{#if r.multi}
										{#if ids.length}
											<div class="flex flex-wrap gap-1.5">
												{#each ids as id (id)}
													{@const a = byId.get(id)}
													<Badge variant="outline" class="h-7 gap-1.5 pr-0.5 text-sm font-normal">
														{#if a}
															<span class="font-mono text-[13px]">{a.code}</span>
															<span class="truncate">{a.name}</span>
														{:else}
															<span class="font-mono text-[13px]">#{id}</span>
														{/if}
														<Tip content={$i18n.t('Remove')}>
															<Button
																variant="ghost"
																size="icon-xs"
																class="size-6"
																aria-label="{$i18n.t('Remove')} {a?.code ?? id}"
																onclick={() => removeMulti(r.role, id)}
															>
																<X />
															</Button>
														</Tip>
													</Badge>
												{/each}
											</div>
										{/if}
										<NativeSelect.Root
											id="tax-role-{r.role}"
											class="w-full"
											bind:value={adder[r.role]}
											onchange={() => addMulti(r.role)}
										>
											<NativeSelect.Option value="">{$i18n.t('Add account...')}</NativeSelect.Option
											>
											{#each candidates(r) as a}
												{#if !ids.includes(a.id)}
													<NativeSelect.Option value={a.id}>{a.code} - {a.name}</NativeSelect.Option
													>
												{/if}
											{/each}
										</NativeSelect.Root>
									{:else}
										<NativeSelect.Root
											id="tax-role-{r.role}"
											class="w-full"
											value={ids[0] ?? ''}
											onchange={(e: Event) => {
												const v = (e.currentTarget as HTMLSelectElement).value;
												setSingle(r.role, v === '' ? '' : Number(v));
											}}
										>
											<NativeSelect.Option value="">{$i18n.t('— not mapped —')}</NativeSelect.Option
											>
											{#each candidates(r) as a}
												<NativeSelect.Option value={a.id}>{a.code} - {a.name}</NativeSelect.Option>
											{/each}
										</NativeSelect.Root>
									{/if}
									{#if ids.length > 0 || r.source === 'mapped'}
										<Button
											variant="ghost"
											size="xs"
											class="self-start text-muted-foreground"
											onclick={() => resetRole(r.role)}
										>
											<RotateCcw />{$i18n.t('Reset to default')}
										</Button>
									{/if}
								</div>
							</div>
						{/each}
					</Card.Content>
				</Card.Root>
			{/if}
		{/each}

		<div class="flex flex-wrap items-center justify-end gap-3">
			{#if dirty.size > 0}
				<span class="text-sm text-muted-foreground">
					{$i18n.t('{{count}} unsaved change(s)', { count: dirty.size })}
				</span>
				<Button variant="outline" onclick={load}>{$i18n.t('Discard')}</Button>
			{/if}
			<Button disabled={saving || dirty.size === 0} onclick={save}>
				{#if saving}<Spinner />{/if}
				{saving ? $i18n.t('Saving...') : $i18n.t('Save')}
			</Button>
		</div>
	{/if}
</div>
