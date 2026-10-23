<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { uiLocale } from '$lib/utils/uiLocale';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';

	import {
		getFixedAssets,
		createFixedAsset,
		deleteFixedAsset,
		generateDepreciation,
		getAccounts,
		getPeriods,
		getCompany,
		updateCompany,
		downloadAssetImportTemplate
	} from '$lib/apis/accounting';

	import Plus from '@lucide/svelte/icons/plus';
	import Upload from '@lucide/svelte/icons/upload';
	import Download from '@lucide/svelte/icons/download';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Package from '@lucide/svelte/icons/package';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';
	import CalendarCheck from '@lucide/svelte/icons/calendar-check';
	import Save from '@lucide/svelte/icons/save';

	import ExcelImportModal from './ExcelImportModal.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';

	const i18n: any = getContext('i18n');

	export let companyId: number;

	// State
	let loading = true;
	let loadError = '';
	let assets: any[] = [];
	let accounts: any[] = [];

	// "As of" month for the accumulated-depreciation / book-value view (YYYY-MM)
	let asOfMonth = '';

	// Company default fixed-asset accounts (customizable) + Excel import
	let defaultAssetAccountId: number | '' = '';
	let defaultDepreciationAccountId: number | '' = '';
	let defaultExpenseAccountId: number | '' = '';
	let savingDefaults = false;
	let showImportModal = false;

	// Create form
	let showAddForm = false;
	let creating = false;
	let newName = '';
	let newDescription = '';
	let newAssetAccountId: number | '' = '';
	let newDepreciationAccountId: number | '' = '';
	let newExpenseAccountId: number | '' = '';
	let newAcquisitionDate = '';
	let newValue = '';
	let newSalvageValue = '0';
	let newUsefulLife = '';
	let newMethod = 'linear';

	// Depreciation generation
	let generatingDep = false;
	let depMonth = '';
	let monthOptions: Array<{ value: string; label: string; to: string }> = [];

	// Delete confirmation
	let showDeleteConfirm = false;
	let deleteTarget: any = null;

	// ─── Helpers ────────────────────────────────────────────────────────────────

	const formatDate = (val: any) => {
		if (!val) return '-';
		return dayjs(val).format('YYYY-MM-DD');
	};

	const fmt = (v: any): string => {
		const n = typeof v === 'string' ? parseFloat(v) : (v ?? 0);
		if (n === 0) return '0.00';
		return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	};

	// The "as of" date = last day of the chosen month (undefined → backend uses today)
	const asOfEndDate = (): string | undefined => {
		if (!asOfMonth) return undefined;
		const [y, m] = asOfMonth.split('-').map(Number);
		const last = new Date(y, m, 0).getDate();
		return `${asOfMonth}-${String(last).padStart(2, '0')}`;
	};

	function buildMonthOptions(periods: any[]) {
		const options: typeof monthOptions = [];
		for (const p of periods) {
			const start = new Date(p.start_date);
			const end = new Date(p.end_date);
			let cursor = new Date(start.getFullYear(), start.getMonth(), 1);
			while (cursor <= end) {
				const y = cursor.getFullYear();
				const m = cursor.getMonth();
				const lastDay = new Date(y, m + 1, 0).getDate();
				const to = `${y}-${String(m + 1).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;
				const label = cursor.toLocaleDateString(uiLocale(), { year: 'numeric', month: 'long' });
				options.push({ value: `${y}-${String(m + 1).padStart(2, '0')}`, label, to });
				cursor = new Date(y, m + 1, 1);
			}
		}
		const seen = new Map<string, (typeof options)[0]>();
		for (const o of options) seen.set(o.value, o);
		return Array.from(seen.values()).sort((a, b) => b.value.localeCompare(a.value));
	}

	// Account filters — by account TYPE so they work across charts (French PCG,
	// Chinese GAAP, US…) instead of guessing from code prefixes. Asset cost and
	// accumulated depreciation both live under the "asset" type; the depreciation
	// charge is an "expense". Accounts missing a type are shown in all lists.
	$: assetAccounts = accounts.filter((a: any) => !a.account_type || a.account_type === 'asset');
	$: depreciationAccounts = accounts.filter(
		(a: any) => !a.account_type || a.account_type === 'asset'
	);
	$: expenseAccounts = accounts.filter((a: any) => !a.account_type || a.account_type === 'expense');

	// ─── Data loading ───────────────────────────────────────────────────────────

	const loadAssets = async () => {
		loading = true;
		loadError = '';
		try {
			const res = await getFixedAssets(companyId, asOfEndDate());
			assets = Array.isArray(res) ? res : (res?.items ?? []);
		} catch (err) {
			loadError = `${err}`;
			toast.error(`${$i18n.t('Failed to load fixed assets')}: ${err}`);
		}
		loading = false;
	};

	onMount(async () => {
		const now0 = new Date();
		asOfMonth = `${now0.getFullYear()}-${String(now0.getMonth() + 1).padStart(2, '0')}`;
		try {
			const [, acctRes, periodRes, companyRes] = await Promise.all([
				loadAssets(),
				getAccounts({ company_id: companyId }),
				getPeriods({ company_id: companyId }),
				getCompany(companyId)
			]);
			accounts = Array.isArray(acctRes) ? acctRes : (acctRes?.items ?? acctRes?.accounts ?? []);
			const periods = periodRes.periods ?? periodRes ?? [];
			monthOptions = buildMonthOptions(periods);

			defaultAssetAccountId = companyRes?.fixed_asset_account_id ?? '';
			defaultDepreciationAccountId = companyRes?.accumulated_depreciation_account_id ?? '';
			defaultExpenseAccountId = companyRes?.depreciation_expense_account_id ?? '';
			applyDefaultsToForm();

			const now = new Date();
			const curKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
			const match = monthOptions.find((o) => o.value === curKey);
			if (match) {
				depMonth = match.value;
			} else if (monthOptions.length > 0) {
				depMonth = monthOptions[0].value;
			}
		} catch (err) {
			console.error('Failed to load accounts/periods:', err);
		}
	});

	// ─── Default accounts + import ───────────────────────────────────────────────

	function applyDefaultsToForm() {
		if (!newAssetAccountId && defaultAssetAccountId)
			newAssetAccountId = Number(defaultAssetAccountId);
		if (!newDepreciationAccountId && defaultDepreciationAccountId)
			newDepreciationAccountId = Number(defaultDepreciationAccountId);
		if (!newExpenseAccountId && defaultExpenseAccountId)
			newExpenseAccountId = Number(defaultExpenseAccountId);
	}

	const saveDefaults = async () => {
		savingDefaults = true;
		try {
			await updateCompany(companyId, {
				fixed_asset_account_id: defaultAssetAccountId ? Number(defaultAssetAccountId) : null,
				accumulated_depreciation_account_id: defaultDepreciationAccountId
					? Number(defaultDepreciationAccountId)
					: null,
				depreciation_expense_account_id: defaultExpenseAccountId
					? Number(defaultExpenseAccountId)
					: null
			});
			toast.success($i18n.t('Default fixed-asset accounts saved'));
			applyDefaultsToForm();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to save default accounts') + ': ' + msg);
		}
		savingDefaults = false;
	};

	const handleAssetsImported = async () => {
		showImportModal = false;
		await loadAssets();
	};

	const handleDownloadTemplate = async () => {
		try {
			await downloadAssetImportTemplate();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to download template') + ': ' + msg);
		}
	};

	// ─── Create ─────────────────────────────────────────────────────────────────

	const handleCreate = async () => {
		if (!newName || !newAssetAccountId || !newAcquisitionDate || !newValue || !newUsefulLife) {
			toast.error($i18n.t('Please fill in all required fields'));
			return;
		}
		const valueNum = parseFloat(newValue);
		const salvageNum = parseFloat(newSalvageValue) || 0;
		const lifeNum = parseInt(String(newUsefulLife), 10);
		if (isNaN(valueNum) || valueNum <= 0) {
			toast.error($i18n.t('Value must be a positive number'));
			return;
		}
		if (isNaN(lifeNum) || lifeNum <= 0) {
			toast.error($i18n.t('Useful life must be a positive number'));
			return;
		}

		creating = true;
		try {
			await createFixedAsset(companyId, {
				name: newName,
				description: newDescription,
				asset_account_id: Number(newAssetAccountId),
				depreciation_account_id: newDepreciationAccountId
					? Number(newDepreciationAccountId)
					: undefined,
				expense_account_id: newExpenseAccountId ? Number(newExpenseAccountId) : undefined,
				acquisition_date: newAcquisitionDate,
				acquisition_value: valueNum,
				salvage_value: salvageNum,
				useful_life_months: lifeNum,
				method: newMethod
			});
			toast.success($i18n.t('Fixed asset created'));
			showAddForm = false;
			newName = '';
			newDescription = '';
			newAssetAccountId = '';
			newDepreciationAccountId = '';
			newExpenseAccountId = '';
			newAcquisitionDate = '';
			newValue = '';
			newSalvageValue = '0';
			newUsefulLife = '';
			newMethod = 'linear';
			await loadAssets();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to create fixed asset') + ': ' + msg);
		}
		creating = false;
	};

	// ─── Delete ─────────────────────────────────────────────────────────────────

	const confirmDelete = (asset: any) => {
		deleteTarget = asset;
		showDeleteConfirm = true;
	};

	const handleDelete = async () => {
		if (!deleteTarget) return;
		try {
			await deleteFixedAsset(deleteTarget.id);
			toast.success($i18n.t('Fixed asset deleted'));
			await loadAssets();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to delete fixed asset') + ': ' + msg);
		}
		deleteTarget = null;
	};

	// ─── Generate Depreciation ──────────────────────────────────────────────────

	const handleGenerateDepreciation = async () => {
		const opt = monthOptions.find((o) => o.value === depMonth);
		if (!opt) {
			toast.error($i18n.t('Please select a month'));
			return;
		}
		generatingDep = true;
		try {
			const result = await generateDepreciation(companyId, opt.to);
			const count = result?.entries_created ?? result?.count ?? 0;
			toast.success(`${count} ${$i18n.t('depreciation entries created as Draft')}`);
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to generate depreciation') + ': ' + msg);
		}
		generatingDep = false;
	};

	// Per-row figures (the register's arithmetic) and the column totals.
	const rowFigures = (asset: any) => {
		const acqValue = parseFloat(asset.acquisition_value ?? asset.value ?? 0);
		const salvage = parseFloat(asset.salvage_value ?? 0);
		const lifeMonths = asset.useful_life_months ?? asset.useful_life ?? 1;
		const monthlyDep = lifeMonths > 0 ? (acqValue - salvage) / lifeMonths : 0;
		const accumulated = parseFloat(asset.accumulated_depreciation ?? 0);
		const bookValue =
			asset.book_value !== undefined ? parseFloat(asset.book_value) : acqValue - accumulated;
		return { acqValue, lifeMonths, monthlyDep, accumulated, bookValue };
	};
	$: totals = assets.reduce(
		(t, a) => {
			const r = rowFigures(a);
			t.acqValue += r.acqValue || 0;
			t.monthlyDep += r.monthlyDep || 0;
			t.accumulated += r.accumulated || 0;
			t.bookValue += r.bookValue || 0;
			return t;
		},
		{ acqValue: 0, monthlyDep: 0, accumulated: 0, bookValue: 0 }
	);

	const openAddForm = () => {
		applyDefaultsToForm();
		showAddForm = true;
	};
</script>

<ConfirmDialog
	bind:open={showDeleteConfirm}
	title={$i18n.t('Delete fixed asset?')}
	description={`${deleteTarget?.name ? `${deleteTarget.name} — ` : ''}${$i18n.t(
		'Are you sure you want to delete this fixed asset? This action cannot be undone.'
	)}`}
	confirmLabel={$i18n.t('Delete')}
	destructive
	onconfirm={handleDelete}
	oncancel={() => (deleteTarget = null)}
/>

<ExcelImportModal
	bind:show={showImportModal}
	type="asset"
	{companyId}
	on:imported={handleAssetsImported}
/>

<div class="flex flex-col gap-4">
	<!-- Header: title, count and the register's actions -->
	<div class="flex flex-wrap items-start justify-between gap-3">
		<div class="flex min-w-0 flex-col gap-1">
			<h2 class="flex items-center gap-2 text-lg font-semibold">
				{$i18n.t('Fixed Assets')}
				{#if !loading || assets.length > 0}<Badge variant="count">{assets.length}</Badge>{/if}
			</h2>
			<p class="text-sm text-muted-foreground">
				{$i18n.t('Manage fixed assets and generate monthly depreciation entries.')}
			</p>
		</div>
		<div class="flex flex-wrap gap-2">
			<Button variant="outline" size="sm" onclick={handleDownloadTemplate}>
				<Download />{$i18n.t('Download Template')}
			</Button>
			<Button variant="outline" size="sm" onclick={() => (showImportModal = true)}>
				<Upload />{$i18n.t('Import from Excel')}
			</Button>
			<Button size="sm" onclick={openAddForm}>
				<Plus />{$i18n.t('Add Asset')}
			</Button>
		</div>
	</div>

	<!-- Asset register -->
	<div class="flex flex-col gap-2">
		<div class="flex flex-wrap items-center justify-between gap-2">
			<h3 class="text-sm font-medium">{$i18n.t('Asset Register')}</h3>
			<div class="flex items-center gap-2">
				<Label for="asset-asof" class="font-normal text-muted-foreground">
					{$i18n.t('Accumulated depreciation as of')}
				</Label>
				<Input
					id="asset-asof"
					type="month"
					class="h-8 w-auto"
					bind:value={asOfMonth}
					onchange={loadAssets}
				/>
			</div>
		</div>

		{#if loading && assets.length === 0}
			<div class="flex flex-col gap-2 rounded-md border p-3">
				{#each Array(4) as _}<Skeleton class="h-8 w-full" />{/each}
			</div>
		{:else if loadError && assets.length === 0}
			<Alert.Root variant="destructive">
				<CircleAlert />
				<Alert.Title>{$i18n.t('Failed to load fixed assets')}</Alert.Title>
				<Alert.Description>
					<p>{loadError}</p>
					<Button variant="outline" size="sm" class="mt-2" onclick={loadAssets}>
						<RotateCcw />{$i18n.t('Retry')}
					</Button>
				</Alert.Description>
			</Alert.Root>
		{:else if assets.length === 0}
			<Empty.Root class="border border-dashed">
				<Empty.Header>
					<Empty.Media variant="icon"><Package /></Empty.Media>
					<Empty.Title>{$i18n.t('No fixed assets registered')}</Empty.Title>
					<Empty.Description>
						{$i18n.t('Add fixed assets to track depreciation and generate monthly entries.')}
					</Empty.Description>
				</Empty.Header>
				<Empty.Content>
					<Button variant="outline" size="sm" onclick={openAddForm}
						><Plus />{$i18n.t('Add Asset')}</Button
					>
				</Empty.Content>
			</Empty.Root>
		{:else}
			<div class="overflow-hidden rounded-md border" class:opacity-60={loading}>
				<Table.Root>
					<Table.Header class="bg-muted/50">
						<Table.Row class="hover:bg-transparent">
							<Table.Head class="min-w-48">{$i18n.t('Name', { context: 'gnos3' })}</Table.Head>
							<Table.Head>{$i18n.t('Acquisition Date')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Value')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Useful Life')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Monthly Dep.')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Accumulated')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Book Value')}</Table.Head>
							<Table.Head class="w-12"><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head
							>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each assets as asset (asset.id)}
							{@const r = rowFigures(asset)}
							<Table.Row>
								<Table.Cell class="max-w-[22rem] whitespace-normal">
									<div class="font-medium">{asset.name}</div>
									{#if asset.description}
										<div class="text-xs text-muted-foreground">{asset.description}</div>
									{/if}
								</Table.Cell>
								<Table.Cell class="tabular-nums">{formatDate(asset.acquisition_date)}</Table.Cell>
								<Table.Cell class="text-right tabular-nums">{fmt(r.acqValue)}</Table.Cell>
								<Table.Cell class="text-right tabular-nums"
									>{r.lifeMonths} {$i18n.t('mo.')}</Table.Cell
								>
								<Table.Cell class="text-right tabular-nums">{fmt(r.monthlyDep)}</Table.Cell>
								<Table.Cell class="text-right tabular-nums">{fmt(r.accumulated)}</Table.Cell>
								<Table.Cell class="text-right font-medium tabular-nums"
									>{fmt(r.bookValue)}</Table.Cell
								>
								<Table.Cell class="text-right">
									<Tip content={$i18n.t('Delete this fixed asset')}>
										<Button
											variant="ghost"
											size="icon-xs"
											aria-label={$i18n.t('Delete this fixed asset')}
											onclick={() => confirmDelete(asset)}
										>
											<Trash2 />
										</Button>
									</Tip>
								</Table.Cell>
							</Table.Row>
						{/each}
					</Table.Body>
					<Table.Footer>
						<Table.Row class="hover:bg-transparent">
							<Table.Cell colspan={2}>{$i18n.t('Total')}</Table.Cell>
							<Table.Cell class="text-right tabular-nums">{fmt(totals.acqValue)}</Table.Cell>
							<Table.Cell></Table.Cell>
							<Table.Cell class="text-right tabular-nums">{fmt(totals.monthlyDep)}</Table.Cell>
							<Table.Cell class="text-right tabular-nums">{fmt(totals.accumulated)}</Table.Cell>
							<Table.Cell class="text-right tabular-nums">{fmt(totals.bookValue)}</Table.Cell>
							<Table.Cell></Table.Cell>
						</Table.Row>
					</Table.Footer>
				</Table.Root>
			</div>
		{/if}
	</div>

	<div class="grid items-start gap-4 lg:grid-cols-2">
		<!-- Generate monthly depreciation -->
		<Card.Root>
			<Card.Header>
				<Card.Title>{$i18n.t('Generate Monthly Depreciation')}</Card.Title>
				<Card.Description
					>{$i18n.t("Creates the month's depreciation entries as drafts.")}</Card.Description
				>
			</Card.Header>
			<Card.Content class="flex flex-wrap items-end gap-3">
				<div class="grid gap-2">
					<Label for="dep-month">{$i18n.t('Month')}</Label>
					{#if monthOptions.length > 0}
						<NativeSelect.Root id="dep-month" class="min-w-44" bind:value={depMonth}>
							{#each monthOptions as opt}
								<NativeSelect.Option value={opt.value}>{opt.label}</NativeSelect.Option>
							{/each}
						</NativeSelect.Root>
					{:else}
						<span class="flex h-9 items-center text-sm text-muted-foreground">
							{$i18n.t('No accounting periods defined')}
						</span>
					{/if}
				</div>
				<Button
					variant="outline"
					disabled={!depMonth || generatingDep}
					onclick={handleGenerateDepreciation}
				>
					{#if generatingDep}<Spinner />{:else}<CalendarCheck />{/if}
					{$i18n.t('Generate', { context: 'gnos3' })}
				</Button>
				{#if generatingDep}
					<span class="flex h-9 items-center text-sm text-muted-foreground" role="status">
						{$i18n.t('Generating depreciation entries...')}
					</span>
				{/if}
			</Card.Content>
		</Card.Root>

		<!-- Default accounts -->
		<Card.Root>
			<Card.Header>
				<Card.Title>{$i18n.t('Default Fixed-Asset Accounts')}</Card.Title>
				<Card.Description>
					{$i18n.t(
						'These accounts pre-fill new assets and are used when importing an asset register. Leave blank to choose per asset.'
					)}
				</Card.Description>
			</Card.Header>
			<Card.Content class="grid gap-4">
				<div class="grid gap-2">
					<Label for="default-asset-account">{$i18n.t('Asset Account')}</Label>
					<NativeSelect.Root
						id="default-asset-account"
						class="w-full"
						bind:value={defaultAssetAccountId}
					>
						<NativeSelect.Option value="">{$i18n.t('Not set')}</NativeSelect.Option>
						{#each assetAccounts as acct}
							<NativeSelect.Option value={acct.id}>{acct.code} - {acct.name}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
				<div class="grid gap-2">
					<Label for="default-dep-account">{$i18n.t('Depreciation Account')}</Label>
					<NativeSelect.Root
						id="default-dep-account"
						class="w-full"
						bind:value={defaultDepreciationAccountId}
					>
						<NativeSelect.Option value="">{$i18n.t('Not set')}</NativeSelect.Option>
						{#each depreciationAccounts as acct}
							<NativeSelect.Option value={acct.id}>{acct.code} - {acct.name}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
				<div class="grid gap-2">
					<Label for="default-expense-account">{$i18n.t('Expense Account')}</Label>
					<NativeSelect.Root
						id="default-expense-account"
						class="w-full"
						bind:value={defaultExpenseAccountId}
					>
						<NativeSelect.Option value="">{$i18n.t('Not set')}</NativeSelect.Option>
						{#each expenseAccounts as acct}
							<NativeSelect.Option value={acct.id}>{acct.code} - {acct.name}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
			</Card.Content>
			<Card.Footer class="justify-end">
				<Button variant="outline" disabled={savingDefaults} onclick={saveDefaults}>
					{#if savingDefaults}<Spinner />{:else}<Save />{/if}
					{savingDefaults ? $i18n.t('Saving...') : $i18n.t('Save Defaults')}
				</Button>
			</Card.Footer>
		</Card.Root>
	</div>
</div>

<!-- Add asset -->
<Dialog.Root bind:open={showAddForm}>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Add Fixed Asset')}</Dialog.Title>
			<Dialog.Description>{$i18n.t('Fields marked * are required.')}</Dialog.Description>
		</Dialog.Header>

		<div class="grid gap-4 sm:grid-cols-2">
			<div class="grid gap-2">
				<Label for="asset-name">{$i18n.t('Name', { context: 'gnos3' })} *</Label>
				<Input
					id="asset-name"
					type="text"
					bind:value={newName}
					placeholder={$i18n.t('e.g. Office Computer')}
				/>
			</div>
			<div class="grid gap-2">
				<Label for="asset-description">{$i18n.t('Description')}</Label>
				<Input id="asset-description" type="text" bind:value={newDescription} />
			</div>
			<div class="grid gap-2">
				<Label for="asset-account">{$i18n.t('Asset Account')} *</Label>
				<NativeSelect.Root id="asset-account" class="w-full" bind:value={newAssetAccountId}>
					<NativeSelect.Option value="">{$i18n.t('Select account...')}</NativeSelect.Option>
					{#each assetAccounts as acct}
						<NativeSelect.Option value={acct.id}>{acct.code} - {acct.name}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
			</div>
			<div class="grid gap-2">
				<Label for="depreciation-account">{$i18n.t('Depreciation Account')}</Label>
				<NativeSelect.Root
					id="depreciation-account"
					class="w-full"
					bind:value={newDepreciationAccountId}
				>
					<NativeSelect.Option value="">{$i18n.t('Select account...')}</NativeSelect.Option>
					{#each depreciationAccounts as acct}
						<NativeSelect.Option value={acct.id}>{acct.code} - {acct.name}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
			</div>
			<div class="grid gap-2">
				<Label for="expense-account">{$i18n.t('Expense Account')}</Label>
				<NativeSelect.Root id="expense-account" class="w-full" bind:value={newExpenseAccountId}>
					<NativeSelect.Option value="">{$i18n.t('Select account...')}</NativeSelect.Option>
					{#each expenseAccounts as acct}
						<NativeSelect.Option value={acct.id}>{acct.code} - {acct.name}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
			</div>
			<div class="grid gap-2">
				<Label for="asset-method">{$i18n.t('Method')}</Label>
				<NativeSelect.Root id="asset-method" class="w-full" bind:value={newMethod}>
					<NativeSelect.Option value="linear">{$i18n.t('Linear')}</NativeSelect.Option>
					<NativeSelect.Option value="declining">{$i18n.t('Declining')}</NativeSelect.Option>
				</NativeSelect.Root>
			</div>
			<div class="grid gap-2">
				<Label for="asset-acquisition-date">{$i18n.t('Acquisition Date')} *</Label>
				<Input id="asset-acquisition-date" type="date" bind:value={newAcquisitionDate} />
			</div>
			<div class="grid gap-2">
				<Label for="asset-value">{$i18n.t('Value')} *</Label>
				<Input
					id="asset-value"
					type="number"
					step="0.01"
					min="0"
					class="text-right tabular-nums"
					bind:value={newValue}
					placeholder="10000.00"
				/>
			</div>
			<div class="grid gap-2">
				<Label for="asset-salvage">{$i18n.t('Salvage Value')}</Label>
				<Input
					id="asset-salvage"
					type="number"
					step="0.01"
					min="0"
					class="text-right tabular-nums"
					bind:value={newSalvageValue}
					placeholder="0"
				/>
			</div>
			<div class="grid gap-2">
				<Label for="asset-useful-life">{$i18n.t('Useful Life (months)')} *</Label>
				<Input
					id="asset-useful-life"
					type="number"
					step="1"
					min="1"
					class="text-right tabular-nums"
					bind:value={newUsefulLife}
					placeholder="60"
				/>
			</div>
		</div>

		<Dialog.Footer>
			<Button variant="outline" onclick={() => (showAddForm = false)}>{$i18n.t('Cancel')}</Button>
			<Button
				onclick={handleCreate}
				disabled={creating ||
					!newName ||
					!newAssetAccountId ||
					!newAcquisitionDate ||
					!newValue ||
					!newUsefulLife}
			>
				{#if creating}<Spinner />{/if}
				{creating ? $i18n.t('Saving...') : $i18n.t('Save')}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
