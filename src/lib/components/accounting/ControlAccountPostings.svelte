<script lang="ts">
	import { onMount, getContext, createEventDispatcher } from 'svelte';
	import { toast } from 'svelte-sonner';

	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import ScanSearch from '@lucide/svelte/icons/scan-search';
	import ArrowRightLeft from '@lucide/svelte/icons/arrow-right-left';

	import { getControlAccountPostings, applyReclassification } from '$lib/apis/accounting';

	import * as Table from '$lib/components/ui/table/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let companyId: number;

	let loading = true;
	let loadError = '';
	let working = false;
	let data: any = null;
	// line_id → chosen target code. Nothing is pre-filled: the human decides.
	let targets: Record<number, string> = {};
	let perAccount: Record<string, string> = {};
	let preview: any = null;

	const fmt = (v: any) => {
		const n = typeof v === 'string' ? parseFloat(v) : (v ?? 0);
		return n
			? n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
			: '';
	};

	const load = async () => {
		loading = true;
		loadError = '';
		preview = null;
		try {
			data = await getControlAccountPostings(companyId);
			targets = {};
			perAccount = {};
		} catch (err: any) {
			loadError = `${$i18n.t('Failed to load')}: ${err?.detail ?? err}`;
			data = null;
		}
		loading = false;
	};
	onMount(load);

	$: groups = (data?.by_account ?? []) as any[];
	$: postingsByAccount = (code: string) =>
		(data?.postings ?? []).filter((p: any) => p.account_code === code);
	$: chosen = Object.entries(targets).filter(([, v]) => !!v).length;

	const applyToAccount = (code: string) => {
		const t = perAccount[code];
		if (!t) return;
		for (const p of postingsByAccount(code)) targets[p.line_id] = t;
		targets = { ...targets };
		preview = null;
	};

	const mappings = () =>
		Object.entries(targets)
			.filter(([, v]) => !!v)
			.map(([line_id, target_code]) => ({ line_id: Number(line_id), target_code }));

	const run = async (dryRun: boolean) => {
		if (chosen === 0) return;
		working = true;
		try {
			const res = await applyReclassification(companyId, mappings(), dryRun);
			if (dryRun) {
				preview = res;
				if (res.errors?.length)
					toast.error(
						$i18n.t('{{n}} line(s) cannot be moved — see below', { n: res.errors.length })
					);
				else toast.success($i18n.t('{{n}} line(s) ready to move', { n: res.changes?.length ?? 0 }));
			} else {
				toast.success($i18n.t('{{n}} line(s) moved', { n: res.applied ?? 0 }));
				await load();
				dispatch('applied');
			}
		} catch (err: any) {
			toast.error(`${err?.detail ?? err}`);
		}
		working = false;
	};
</script>

<div class="flex flex-col gap-4">
	<div class="space-y-1">
		<h2 class="text-lg font-semibold">{$i18n.t('Postings on Control Accounts')}</h2>
		<p class="text-sm text-muted-foreground">
			{$i18n.t(
				'Postings that sit on a control account (one with sub-accounts) never appear in the sub-ledger. Choose the sub-account each line belongs on — per line, or once per account — then preview and apply. Nothing is chosen for you; a voided entry and its reversal should move together.'
			)}
		</p>
	</div>

	{#if loading}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(5) as _}
				<Skeleton class="h-8 w-full" />
			{/each}
		</div>
	{:else if loadError}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{loadError}</Alert.Title>
			<Alert.Action>
				<Button variant="outline" size="sm" onclick={load}>{$i18n.t('Retry')}</Button>
			</Alert.Action>
		</Alert.Root>
	{:else if !data || data.total_lines === 0}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><CircleCheck class="text-success" /></Empty.Media>
				<Empty.Title>{$i18n.t('No postings on control accounts.')}</Empty.Title>
				<Empty.Description>
					{$i18n.t('Every line sits on a detail account; there is nothing to move.')}
				</Empty.Description>
			</Empty.Header>
		</Empty.Root>
	{:else}
		{#each groups as g (g.account_code)}
			<div class="overflow-hidden rounded-md border">
				<div
					class="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 border-b bg-muted/50 px-3 py-2"
				>
					<div class="min-w-0 text-sm">
						<span class="font-mono text-[13px]">{g.account_code}</span>
						<span class="font-medium">{g.account_name}</span>
						<span class="ml-2 text-muted-foreground tabular-nums">
							{g.lines}
							{$i18n.t('line(s)')} · DR {fmt(g.debit) || '—'} · CR {fmt(g.credit) || '—'}
						</span>
					</div>
					<div class="flex flex-wrap items-center gap-2">
						<NativeSelect.Root
							size="sm"
							class="w-64 max-w-full"
							aria-label="{$i18n.t('— sub-account for all lines —')} {g.account_code}"
							bind:value={perAccount[g.account_code]}
						>
							<NativeSelect.Option value=""
								>{$i18n.t('— sub-account for all lines —')}</NativeSelect.Option
							>
							{#each g.sub_accounts ?? [] as sa}
								<NativeSelect.Option value={sa.code}>{sa.code} - {sa.name}</NativeSelect.Option>
							{/each}
						</NativeSelect.Root>
						<Button
							variant="outline"
							size="sm"
							disabled={!perAccount[g.account_code]}
							onclick={() => applyToAccount(g.account_code)}
						>
							{$i18n.t('Apply to all')}
						</Button>
					</div>
				</div>
				<Table.Root class="min-w-[56rem] table-fixed">
					<Table.Header>
						<Table.Row class="hover:bg-transparent">
							<Table.Head class="w-28">{$i18n.t('Entry')}</Table.Head>
							<Table.Head class="w-28">{$i18n.t('Date')}</Table.Head>
							<Table.Head class="w-28">{$i18n.t('Status')}</Table.Head>
							<Table.Head>{$i18n.t('Description')}</Table.Head>
							<Table.Head class="w-28 text-right">{$i18n.t('Debit')}</Table.Head>
							<Table.Head class="w-28 text-right">{$i18n.t('Credit')}</Table.Head>
							<Table.Head class="w-64">{$i18n.t('Move to')}</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each postingsByAccount(g.account_code) as p (p.line_id)}
							<Table.Row class={p.status === 'voided' ? 'text-muted-foreground' : ''}>
								<Table.Cell class="font-mono text-[13px]"
									>{p.entry_number || '#' + p.line_id}</Table.Cell
								>
								<Table.Cell class="tabular-nums">{p.date}</Table.Cell>
								<Table.Cell><StatusBadge kind="entry" status={p.status} /></Table.Cell>
								<Table.Cell class="truncate" title={p.description}>
									{p.counterparty ? p.counterparty + ' · ' : ''}{p.description}
								</Table.Cell>
								<Table.Cell class="text-right tabular-nums">{fmt(p.debit)}</Table.Cell>
								<Table.Cell class="text-right tabular-nums">{fmt(p.credit)}</Table.Cell>
								<Table.Cell class="py-1">
									<NativeSelect.Root
										size="sm"
										class="w-full"
										aria-label="{$i18n.t('Move to')} {p.entry_number || '#' + p.line_id}"
										bind:value={targets[p.line_id]}
										onchange={() => (preview = null)}
									>
										<NativeSelect.Option value="">{$i18n.t('— leave —')}</NativeSelect.Option>
										{#each g.sub_accounts ?? [] as sa}
											<NativeSelect.Option value={sa.code}
												>{sa.code} - {sa.name}</NativeSelect.Option
											>
										{/each}
									</NativeSelect.Root>
								</Table.Cell>
							</Table.Row>
						{/each}
					</Table.Body>
				</Table.Root>
			</div>
		{/each}

		{#if preview}
			{#if preview.errors?.length}
				<Alert.Root variant="destructive">
					<CircleAlert />
					<Alert.Title>
						{$i18n.t('Preview')}: {preview.changes?.length ?? 0}
						{$i18n.t('line(s) will move')}
					</Alert.Title>
					<Alert.Description>
						<ul class="list-inside list-disc space-y-0.5">
							{#each preview.errors as e}<li>{e}</li>{/each}
						</ul>
					</Alert.Description>
				</Alert.Root>
			{:else}
				<Alert.Root>
					<CircleCheck class="text-success" />
					<Alert.Title>
						{$i18n.t('Preview')}: {preview.changes?.length ?? 0}
						{$i18n.t('line(s) will move')}
					</Alert.Title>
				</Alert.Root>
			{/if}
		{/if}

		<div class="flex flex-wrap items-center justify-end gap-x-3 gap-y-2">
			<span class="mr-auto text-sm text-muted-foreground">
				{$i18n.t('Preview first; apply is all-or-nothing and audited.')}
			</span>
			<Button variant="outline" disabled={working || chosen === 0} onclick={() => run(true)}>
				<ScanSearch />{$i18n.t('Preview')}
			</Button>
			<Button
				disabled={working || chosen === 0 || !preview || (preview.errors?.length ?? 0) > 0}
				onclick={() => run(false)}
			>
				{#if working}<Spinner />{:else}<ArrowRightLeft />{/if}
				{working ? $i18n.t('Working...') : $i18n.t('Apply {{n}} move(s)', { n: chosen })}
			</Button>
		</div>
	{/if}
</div>
