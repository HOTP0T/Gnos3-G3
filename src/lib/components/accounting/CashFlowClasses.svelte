<!--
	Company → Settings → Cash Flow Classes: operating / investing / financing for
	each balance-sheet account. The cash flow statement and Finances read them, so
	a loan received or share capital paid in never reads as revenue.
	An account left on "Default" follows the suggestion shown (or its parent's
	choice); only explicit choices are saved.
-->
<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';

	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import Landmark from '@lucide/svelte/icons/landmark';
	import Search from '@lucide/svelte/icons/search';

	import {
		getCashFlowClasses,
		updateCashFlowClasses,
		type CashFlowClass,
		type CashFlowClassAccount
	} from '$lib/apis/accounting';

	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';

	const i18n: any = getContext('i18n');

	let { companyId }: { companyId: number } = $props();

	const CLASS_LABEL: Record<string, string> = {
		operating: 'Operating',
		investing: 'Investing',
		financing: 'Financing'
	};
	const GROUPS = [
		{ type: 'asset', label: 'Assets' },
		{ type: 'liability', label: 'Liabilities' },
		{ type: 'equity', label: 'Equity' }
	] as const;

	let loading = $state(true);
	let loadError = $state('');
	let saving = $state(false);
	let accounts = $state<CashFlowClassAccount[]>([]);
	let query = $state('');
	/** account id → explicit choice ('' = back to default), only for rows the user touched. */
	let draft = $state<Record<number, CashFlowClass | ''>>({});

	const byId = $derived(new Map(accounts.map((a) => [a.id, a])));

	function stored(a: CashFlowClassAccount): CashFlowClass | '' {
		return a.source === 'set' ? (a.value as CashFlowClass) : '';
	}
	function chosen(a: CashFlowClassAccount): CashFlowClass | '' {
		return a.id in draft ? draft[a.id] : stored(a);
	}
	/** The nearest parent's explicit choice, drafts included. */
	function fromParent(a: CashFlowClassAccount): CashFlowClass | '' {
		const seen = new Set([a.id]);
		let parent = a.parent_id ? byId.get(a.parent_id) : undefined;
		while (parent && !seen.has(parent.id)) {
			const own = chosen(parent);
			if (own) return own;
			seen.add(parent.id);
			parent = parent.parent_id ? byId.get(parent.parent_id) : undefined;
		}
		return '';
	}
	function automaticLabel(a: CashFlowClassAccount): string {
		const inherited = fromParent(a);
		return inherited
			? $i18n.t('As parent ({{class}})', { class: $i18n.t(CLASS_LABEL[inherited]) })
			: $i18n.t('Default ({{class}})', { class: $i18n.t(CLASS_LABEL[a.default] ?? a.default) });
	}

	const changes = $derived(
		Object.fromEntries(
			Object.entries(draft)
				.filter(([id, v]) => {
					const a = byId.get(Number(id));
					return a && v !== stored(a);
				})
				.map(([id, v]) => [Number(id), v === '' ? null : v])
		) as Record<number, CashFlowClass | null>
	);
	const changeCount = $derived(Object.keys(changes).length);

	const visible = $derived.by(() => {
		const q = query.trim().toLowerCase();
		if (!q) return accounts;
		return accounts.filter(
			(a) => a.code.toLowerCase().includes(q) || a.name.toLowerCase().includes(q)
		);
	});

	/** The API client rejects with the server's JSON (`{ detail }`) or an Error. */
	function errorText(err: unknown): string {
		const detail = (err as { detail?: unknown } | null)?.detail;
		return String(detail ?? err);
	}

	async function load() {
		loading = true;
		loadError = '';
		try {
			accounts = (await getCashFlowClasses(companyId)).accounts;
			draft = {};
		} catch (err) {
			loadError = `${$i18n.t('Failed to load')}: ${errorText(err)}`;
		}
		loading = false;
	}

	async function save() {
		saving = true;
		try {
			accounts = (await updateCashFlowClasses(companyId, changes)).accounts;
			draft = {};
			toast.success($i18n.t('Cash flow classes saved'));
		} catch (err) {
			toast.error(`${$i18n.t('Failed to save')}: ${errorText(err)}`);
		}
		saving = false;
	}

	onMount(load);
</script>

<div class="flex flex-col gap-4">
	<div class="space-y-1">
		<h2 class="text-lg font-semibold">{$i18n.t('Cash Flow Classes')}</h2>
		<p class="text-sm text-muted-foreground">
			{$i18n.t(
				'Where each balance-sheet account belongs in the cash flow statement and in Finances: running the business (operating), long-term assets (investing), or loans and capital (financing). Revenue and expense accounts are always operating.'
			)}
		</p>
	</div>

	{#if loading}
		<Card.Root>
			<Card.Content class="grid gap-4">
				{#each [0, 1, 2, 3, 4, 5] as row (row)}
					<div class="flex items-center justify-between gap-6">
						<Skeleton class="h-4 w-64" />
						<Skeleton class="h-9 w-56" />
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
		<div class="relative w-full sm:max-w-xs">
			<Search
				class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
				aria-hidden="true"
			/>
			<Input
				type="search"
				class="pl-8"
				placeholder={$i18n.t('Search accounts')}
				aria-label={$i18n.t('Search accounts')}
				bind:value={query}
			/>
		</div>

		{#if visible.length === 0}
			<p class="text-sm text-muted-foreground">{$i18n.t('No accounts found')}</p>
		{/if}

		{#each GROUPS as group (group.type)}
			{@const rows = visible.filter((a) => a.account_type === group.type)}
			{#if rows.length}
				<Card.Root>
					<Card.Header>
						<Card.Title>{$i18n.t(group.label)}</Card.Title>
					</Card.Header>
					<Card.Content class="divide-y">
						{#each rows as a (a.id)}
							<div
								class="flex flex-col gap-2 py-2.5 first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between sm:gap-6"
							>
								<div
									class="flex min-w-0 items-baseline gap-2"
									style={query ? '' : `padding-left: ${Math.min(a.level ?? 0, 4) * 1.25}rem`}
								>
									<span class="shrink-0 font-mono text-xs text-muted-foreground">{a.code}</span>
									<span class="min-w-0 truncate text-sm" class:text-muted-foreground={!a.is_active}
										>{a.name}</span
									>
								</div>
								{#if a.value === 'cash'}
									<Badge variant="secondary" class="w-fit shrink-0">
										<Landmark aria-hidden="true" />{$i18n.t('Cash and bank')}
									</Badge>
								{:else}
									<NativeSelect.Root
										class="w-full sm:w-64 sm:shrink-0"
										aria-label={`${a.code} ${a.name}`}
										value={chosen(a)}
										onchange={(e: Event) => {
											draft[a.id] = (e.currentTarget as HTMLSelectElement).value as
												| CashFlowClass
												| '';
										}}
									>
										<NativeSelect.Option value="">{automaticLabel(a)}</NativeSelect.Option>
										{#each ['operating', 'investing', 'financing'] as c}
											<NativeSelect.Option value={c}>{$i18n.t(CLASS_LABEL[c])}</NativeSelect.Option>
										{/each}
									</NativeSelect.Root>
								{/if}
							</div>
						{/each}
					</Card.Content>
				</Card.Root>
			{/if}
		{/each}

		<div
			class="sticky bottom-0 flex flex-wrap items-center justify-end gap-3 border-t bg-background py-3"
		>
			{#if changeCount}
				<span class="text-sm text-muted-foreground"
					>{$i18n.t('{{count}} unsaved change(s)', { count: changeCount })}</span
				>
				<Button variant="outline" disabled={saving} onclick={() => (draft = {})}
					>{$i18n.t('Discard')}</Button
				>
			{/if}
			<Button disabled={saving || !changeCount} onclick={save}>
				{#if saving}<Spinner />{/if}
				{saving ? $i18n.t('Saving...') : $i18n.t('Save')}
			</Button>
		</div>
	{/if}
</div>
