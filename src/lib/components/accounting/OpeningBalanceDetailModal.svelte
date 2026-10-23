<script lang="ts">
	import { getContext, createEventDispatcher } from 'svelte';
	import { toast } from 'svelte-sonner';

	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';
	import Download from '@lucide/svelte/icons/download';
	import Upload from '@lucide/svelte/icons/upload';
	import Scale from '@lucide/svelte/icons/scale';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import BookOpen from '@lucide/svelte/icons/book-open';

	import {
		getArApAccounts,
		getOpeningBalanceDetails,
		setOpeningBalanceDetails,
		importOpeningBalanceDetails,
		downloadOpeningBalanceDetailTemplate
	} from '$lib/apis/accounting';

	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;
	export let companyId: number;

	let loading = false;
	let saving = false;
	let importing = false;
	let arApAccounts: any[] = []; // flattened ar + ap with side
	let selectedAccountId: number | null = null;
	let rows: any[] = [];
	let fileInput: HTMLInputElement;

	$: selectedAccount = arApAccounts.find((a) => a.id === selectedAccountId) ?? null;
	$: detailTotal = rows.reduce((s, r) => s + (parseFloat(r.amount) || 0), 0);
	$: openingLump = selectedAccount ? Number(selectedAccount.opening) : 0;
	$: delta = Math.round((detailTotal - openingLump) * 100) / 100;

	$: if (show && companyId && arApAccounts.length === 0) loadAccounts();

	const fmt = (n: number) =>
		n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

	const loadAccounts = async () => {
		loading = true;
		try {
			const res = await getArApAccounts(companyId);
			arApAccounts = [
				...(res.ar ?? []).map((a: any) => ({ ...a, side: 'ar' })),
				...(res.ap ?? []).map((a: any) => ({ ...a, side: 'ap' }))
			];
			if (arApAccounts.length && selectedAccountId == null) {
				selectedAccountId = arApAccounts[0].id;
				await loadDetails();
			}
		} catch (err) {
			toast.error(`${err}`);
		}
		loading = false;
	};

	const loadDetails = async () => {
		if (!selectedAccountId) return;
		loading = true;
		try {
			const res = await getOpeningBalanceDetails(companyId, selectedAccountId);
			rows = (res ?? []).map((d: any) => ({
				party_name: d.party_name,
				reference: d.reference ?? '',
				amount: d.amount,
				item_date: d.item_date ?? '',
				due_date: d.due_date ?? ''
			}));
		} catch (err) {
			toast.error(`${err}`);
		}
		loading = false;
	};

	const onAccountChange = () => loadDetails();

	const addRow = () =>
		(rows = [
			...rows,
			{ party_name: '', reference: '', amount: null, item_date: '', due_date: '' }
		]);
	const removeRow = (i: number) => (rows = rows.filter((_, idx) => idx !== i));

	const save = async () => {
		if (!selectedAccountId) return;
		const clean = rows
			.filter((r) => r.party_name && parseFloat(r.amount) > 0)
			.map((r) => ({
				party_name: r.party_name,
				reference: r.reference || null,
				amount: parseFloat(r.amount),
				item_date: r.item_date || null,
				due_date: r.due_date || null
			}));
		saving = true;
		try {
			await setOpeningBalanceDetails(companyId, selectedAccountId, clean);
			toast.success($i18n.t('Opening balance detail saved'));
			await loadAccounts();
			dispatch('save');
		} catch (err) {
			toast.error(`${err}`);
		}
		saving = false;
	};

	const onImport = async (e: Event) => {
		const file = (e.target as HTMLInputElement).files?.[0];
		if (!file) return;
		importing = true;
		try {
			const res = await importOpeningBalanceDetails(companyId, file);
			toast.success(
				$i18n.t('Imported') + `: ${res.imported}, ` + $i18n.t('skipped') + `: ${res.skipped}`
			);
			arApAccounts = [];
			await loadAccounts();
			await loadDetails();
		} catch (err) {
			toast.error(`${err}`);
		}
		importing = false;
		if (fileInput) fileInput.value = '';
	};
</script>

<Dialog.Root bind:open={show}>
	<Dialog.Content class="max-h-[90vh] gap-5 overflow-y-auto sm:max-w-3xl">
		<Dialog.Header>
			<Dialog.Title>
				{$i18n.t('Opening Balance Detail (AR/AP)')}
			</Dialog.Title>
			<Dialog.Description>
				{$i18n.t(
					'Break an AR/AP account opening balance into per-customer/vendor lines so they appear individually in the aging report.'
				)}
			</Dialog.Description>
		</Dialog.Header>

		{#if loading && arApAccounts.length === 0}
			<div class="grid gap-2">
				{#each Array(4) as _}
					<Skeleton class="h-8 w-full" />
				{/each}
			</div>
		{:else if arApAccounts.length === 0}
			<Empty.Root class="border border-dashed">
				<Empty.Header>
					<Empty.Media variant="icon"><BookOpen /></Empty.Media>
					<Empty.Title>{$i18n.t('No AR/AP accounts found for this company.')}</Empty.Title>
					<Empty.Description>
						{$i18n.t('Add receivable or payable accounts in the chart of accounts first.')}
					</Empty.Description>
				</Empty.Header>
			</Empty.Root>
		{:else}
			<div class="flex flex-wrap items-end gap-2">
				<div class="grid min-w-[16rem] flex-1 gap-2">
					<Label for="ob-account">{$i18n.t('Account', { context: 'gnos3' })}</Label>
					<NativeSelect.Root
						id="ob-account"
						class="w-full"
						bind:value={selectedAccountId}
						onchange={onAccountChange}
					>
						{#each arApAccounts as a}
							<NativeSelect.Option value={a.id}
								>{a.side.toUpperCase()} · {a.code} — {a.name}</NativeSelect.Option
							>
						{/each}
					</NativeSelect.Root>
				</div>
				<Button variant="ghost" onclick={downloadOpeningBalanceDetailTemplate}>
					<Download />{$i18n.t('Download template')}
				</Button>
				<Button variant="outline" disabled={importing} onclick={() => fileInput?.click()}>
					{#if importing}<Spinner />{:else}<Upload />{/if}
					{$i18n.t('Import Excel')}
				</Button>
				<input
					type="file"
					accept=".xlsx,.xls"
					class="hidden"
					bind:this={fileInput}
					onchange={onImport}
				/>
			</div>

			<!-- Reconciliation: detail lines against the account's opening balance -->
			<Alert.Root variant={Math.abs(delta) < 0.01 ? 'default' : 'warning'}>
				{#if Math.abs(delta) < 0.01}
					<Scale class="text-success!" />
				{:else}
					<TriangleAlert />
				{/if}
				<Alert.Title class="flex flex-wrap gap-x-4 gap-y-1 tabular-nums">
					<span>{$i18n.t('Account opening')}: <b>{fmt(openingLump)}</b></span>
					<span>{$i18n.t('Detail total')}: <b>{fmt(detailTotal)}</b></span>
					<span>{$i18n.t('Δ')}: <b>{fmt(delta)}</b></span>
				</Alert.Title>
				{#if Math.abs(delta) >= 0.01}
					<Alert.Description>
						{$i18n.t('Detail lines should sum to the account opening balance.')}
					</Alert.Description>
				{/if}
			</Alert.Root>

			<div class="overflow-hidden rounded-md border {loading ? 'opacity-60' : ''}">
				<Table.Root>
					<Table.Header class="bg-muted/50">
						<Table.Row class="hover:bg-transparent">
							<Table.Head class="min-w-[10rem]">{$i18n.t('Customer / Vendor')}</Table.Head>
							<Table.Head class="min-w-[8rem]">{$i18n.t('Reference')}</Table.Head>
							<Table.Head class="w-32 text-right">{$i18n.t('Amount')}</Table.Head>
							<Table.Head>{$i18n.t('Item Date')}</Table.Head>
							<Table.Head>{$i18n.t('Due Date')}</Table.Head>
							<Table.Head class="w-10"><span class="sr-only">{$i18n.t('Remove')}</span></Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each rows as r, i}
							<Table.Row class="hover:bg-transparent">
								<Table.Cell>
									<Input
										class="h-8"
										aria-label={$i18n.t('Customer / Vendor')}
										bind:value={r.party_name}
									/>
								</Table.Cell>
								<Table.Cell>
									<Input
										class="h-8 font-mono"
										aria-label={$i18n.t('Reference')}
										bind:value={r.reference}
									/>
								</Table.Cell>
								<Table.Cell>
									<Input
										type="number"
										step="0.01"
										class="h-8 min-w-24 text-right tabular-nums"
										aria-label={$i18n.t('Amount')}
										bind:value={r.amount}
									/>
								</Table.Cell>
								<Table.Cell>
									<Input
										type="date"
										class="h-8 tabular-nums"
										aria-label={$i18n.t('Item Date')}
										bind:value={r.item_date}
									/>
								</Table.Cell>
								<Table.Cell>
									<Input
										type="date"
										class="h-8 tabular-nums"
										aria-label={$i18n.t('Due Date')}
										bind:value={r.due_date}
									/>
								</Table.Cell>
								<Table.Cell>
									<Tip content={$i18n.t('Remove line')}>
										<Button
											variant="ghost"
											size="icon-xs"
											aria-label={$i18n.t('Remove line')}
											onclick={() => removeRow(i)}
										>
											<X />
										</Button>
									</Tip>
								</Table.Cell>
							</Table.Row>
						{:else}
							<Table.Row class="hover:bg-transparent">
								<Table.Cell colspan={6} class="py-6 text-center text-muted-foreground">
									{$i18n.t('No detail lines yet.')}
								</Table.Cell>
							</Table.Row>
						{/each}
					</Table.Body>
				</Table.Root>
			</div>

			<div>
				<Button variant="ghost" size="sm" onclick={addRow}>
					<Plus />{$i18n.t('Add line')}
				</Button>
			</div>
		{/if}

		<Dialog.Footer>
			<Button variant="outline" onclick={() => (show = false)}>{$i18n.t('Close')}</Button>
			{#if arApAccounts.length > 0}
				<Button disabled={saving} onclick={save}>
					{#if saving}<Spinner />{/if}
					{$i18n.t('Save')}
				</Button>
			{/if}
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
