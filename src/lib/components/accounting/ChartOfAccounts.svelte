<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	import Plus from '@lucide/svelte/icons/plus';
	import Upload from '@lucide/svelte/icons/upload';
	import Download from '@lucide/svelte/icons/download';
	import FileSpreadsheet from '@lucide/svelte/icons/file-spreadsheet';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import Search from '@lucide/svelte/icons/search';
	import Archive from '@lucide/svelte/icons/archive';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import CircleSlash from '@lucide/svelte/icons/circle-slash';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import ListTree from '@lucide/svelte/icons/list-tree';
	import Save from '@lucide/svelte/icons/save';

	import {
		getAccounts,
		deleteAccount,
		getOpeningBalances,
		updateOpeningBalances,
		updateCompany,
		downloadChartImportTemplate
	} from '$lib/apis/accounting';
	import { user, isAdmin } from '$lib/stores';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';
	import AccountFormModal from '$lib/components/accounting/AccountFormModal.svelte';
	import OpeningBalanceDetailModal from '$lib/components/accounting/OpeningBalanceDetailModal.svelte';
	import ExcelImportModal from '$lib/components/accounting/ExcelImportModal.svelte';
	import { cn } from '$lib/utils/shadcn.js';

	const i18n: any = getContext('i18n');

	export let companyId: number;

	// Permissions (UX gating; backend enforces the real check)
	$: canWrite = $isAdmin || Boolean($user?.permissions?.modules?.accounting?.write);
	$: canDelete = $isAdmin || Boolean($user?.permissions?.modules?.accounting?.admin);

	// Data
	let accounts: any[] = [];
	let openingBalances: Record<number, { debit: number; credit: number }> = {};
	let editedBalances: Record<number, { debit: number; credit: number }> = {};
	let savingBalances = false;
	let loading = true;
	let loadError = '';

	// Opening balance date
	let openingBalanceDate = '';
	let originalObDate = '';

	$: isDateDirty = openingBalanceDate !== originalObDate;
	$: isDirty = Object.keys(editedBalances).length > 0 || isDateDirty;

	// Modal state
	let showFormModal = false;
	let editingAccount: any = null;
	let showObDetail = false;
	let showImportModal = false;

	// Delete confirmation
	let showDeleteConfirm = false;
	let deleteTarget: any = null;

	// Collapsible sections: closed on arrival; a search opens every section with a match
	let expandedSections: Set<string> = new Set();
	let searchCollapsed: Set<string> = new Set(); // closed by hand during the current search

	// Search (code, name or description)
	let query = '';
	$: q = query.trim().toLowerCase();

	const ACCOUNT_TYPES = [
		{ key: 'asset', label: 'Assets' },
		{ key: 'liability', label: 'Liabilities' },
		{ key: 'equity', label: 'Equity' },
		{ key: 'revenue', label: 'Revenue' },
		{ key: 'expense', label: 'Expenses' }
	] as const;

	// Singular type name, as the account form shows it ("Asset", "Liability"…)
	const typeLabel = (t: string) => (t ? t.charAt(0).toUpperCase() + t.slice(1) : '—');

	// Accounts with sub-accounts read as headings
	$: parentIds = new Set(accounts.map((a) => a.parent_id).filter(Boolean));

	const matches = (a: any, q: string) =>
		[a.code, a.name, a.description].some((v) => `${v ?? ''}`.toLowerCase().includes(q));

	$: groupedAccounts = ACCOUNT_TYPES.map((type) => ({
		...type,
		accounts: accounts
			.filter((a) => a.account_type === type.key && (!q || matches(a, q)))
			.sort((a, b) => a.code.localeCompare(b.code))
	}));
	$: matchCount = groupedAccounts.reduce((n, g) => n + g.accounts.length, 0);

	const loadAccounts = async () => {
		loading = true;
		loadError = '';
		try {
			const res = await getAccounts({ company_id: companyId });
			if (res) {
				accounts = Array.isArray(res) ? res : (res.accounts ?? []);
			}
		} catch (err: any) {
			loadError = err?.detail ?? `${err}`;
		}
		loading = false;
	};

	const loadOpeningBalances = async () => {
		try {
			const res = await getOpeningBalances(companyId);
			const obj: Record<number, { debit: number; credit: number }> = {};
			if (res?.balances) {
				for (const [idStr, val] of Object.entries(res.balances)) {
					const v = val as { debit: number; credit: number };
					obj[Number(idStr)] = { debit: v.debit ?? 0, credit: v.credit ?? 0 };
				}
			}
			openingBalances = obj;
			if (res?.opening_balance_date) {
				openingBalanceDate = res.opening_balance_date;
				originalObDate = res.opening_balance_date;
			}
		} catch (err) {
			// Opening balances are non-critical, silently fail
		}
	};

	const reload = async () => {
		await loadAccounts();
		await loadOpeningBalances();
	};

	const getBalanceForAccount = (accountId: number): { debit: number; credit: number } => {
		if (editedBalances[accountId]) {
			return editedBalances[accountId];
		}
		return openingBalances[accountId] ?? { debit: 0, credit: 0 };
	};

	const handleBalanceInput = (accountId: number, field: 'debit' | 'credit', value: string) => {
		const current = getBalanceForAccount(accountId);
		const numVal = parseFloat(value) || 0;
		const updated = { ...current, [field]: numVal };
		editedBalances = { ...editedBalances, [accountId]: updated };
	};

	const saveOpeningBalances = async () => {
		if (Object.keys(editedBalances).length === 0 && !isDateDirty) return;
		savingBalances = true;
		try {
			// Persist OB date change first
			if (isDateDirty && openingBalanceDate) {
				await updateCompany(companyId, { opening_balance_date: openingBalanceDate });
				originalObDate = openingBalanceDate;
			}
			// Save balance entries
			if (Object.keys(editedBalances).length > 0) {
				const entries = Object.entries(editedBalances).map(([accountId, bal]) => ({
					account_id: Number(accountId),
					debit: bal.debit,
					credit: bal.credit
				}));
				await updateOpeningBalances(companyId, entries);
				openingBalances = { ...openingBalances, ...editedBalances };
				editedBalances = {};
			}
			toast.success($i18n.t('Opening balances saved'));
		} catch (err: any) {
			toast.error(err?.detail || `${err}`);
		}
		savingBalances = false;
	};

	const toggled = (set: Set<string>, key: string) => {
		const next = new Set(set);
		if (next.has(key)) next.delete(key);
		else next.add(key);
		return next;
	};

	const toggleSection = (key: string) => {
		if (q) searchCollapsed = toggled(searchCollapsed, key);
		else expandedSections = toggled(expandedSections, key);
	};

	const openAddModal = () => {
		editingAccount = null;
		showFormModal = true;
	};

	const openEditModal = (account: any) => {
		editingAccount = account;
		showFormModal = true;
	};

	// Row click / Enter opens the account; clicks and keys inside its inputs and buttons don't.
	const activateRow = (e: Event, account: any) => {
		const target = e.target as HTMLElement;
		if (target.closest('input, button, a')) return;
		if (e instanceof KeyboardEvent) {
			if (e.key !== 'Enter' && e.key !== ' ') return;
			e.preventDefault();
		}
		openEditModal(account);
	};

	const confirmDeactivate = (account: any) => {
		deleteTarget = account;
		showDeleteConfirm = true;
	};

	const handleDeactivate = async () => {
		if (!deleteTarget) return;
		try {
			await deleteAccount(deleteTarget.id);
			toast.success($i18n.t('Account deactivated'));
			await loadAccounts();
			await loadOpeningBalances();
		} catch (err: any) {
			toast.error(err?.detail || `${err}`);
		}
		deleteTarget = null;
	};

	const handleSave = async () => {
		await loadAccounts();
		await loadOpeningBalances();
	};

	const handleImported = async () => {
		toast.success($i18n.t('Accounts imported successfully'));
		await reload();
	};

	onMount(reload);
</script>

<ConfirmDialog
	bind:open={showDeleteConfirm}
	title={$i18n.t('Deactivate Account')}
	description={$i18n.t(
		'Are you sure you want to deactivate this account? It will no longer appear in active listings.'
	)}
	confirmLabel={$i18n.t('Deactivate')}
	destructive
	onconfirm={handleDeactivate}
/>

<AccountFormModal
	bind:show={showFormModal}
	account={editingAccount}
	{accounts}
	{companyId}
	on:save={handleSave}
/>

<OpeningBalanceDetailModal bind:show={showObDetail} {companyId} />

<ExcelImportModal
	bind:show={showImportModal}
	type="chart"
	{companyId}
	on:imported={handleImported}
/>

<div class="flex flex-col gap-4">
	<!-- Header -->
	<div class="flex flex-wrap items-start justify-between gap-x-4 gap-y-3">
		<div class="min-w-0 space-y-1">
			<h2 class="text-lg font-semibold">
				{$i18n.t('Chart of Accounts')}
				<span class="ml-1 font-normal text-muted-foreground tabular-nums">{accounts.length}</span>
			</h2>
			<p class="text-sm text-muted-foreground">
				{$i18n.t(
					'Click an account to edit it. Opening balances are typed in the table and saved together.'
				)}
			</p>
		</div>
		<div class="flex flex-wrap items-center gap-2">
			<DropdownMenu.Root>
				<DropdownMenu.Trigger>
					{#snippet child({ props })}
						<Button {...props} variant="outline" size="sm">
							<FileSpreadsheet />{$i18n.t('Excel')}<ChevronDown class="text-muted-foreground" />
						</Button>
					{/snippet}
				</DropdownMenu.Trigger>
				<DropdownMenu.Content align="end" class="w-52">
					<DropdownMenu.Item onSelect={() => (showImportModal = true)}>
						<Upload />{$i18n.t('Import from Excel')}
					</DropdownMenu.Item>
					<DropdownMenu.Item onSelect={() => downloadChartImportTemplate()}>
						<Download />{$i18n.t('Download Template')}
					</DropdownMenu.Item>
				</DropdownMenu.Content>
			</DropdownMenu.Root>
			{#if canWrite}
				<Tip content={$i18n.t('Split AR/AP opening balances by customer/vendor')}>
					<Button variant="outline" size="sm" onclick={() => (showObDetail = true)}>
						{$i18n.t('AR/AP Opening Detail')}
					</Button>
				</Tip>
				<Button size="sm" variant={isDirty ? 'outline' : 'default'} onclick={openAddModal}>
					<Plus />{$i18n.t('Add Account')}
				</Button>
			{/if}
		</div>
	</div>

	<!-- Opening balance date (saved with the balances typed in the table) -->
	<div
		class="flex flex-col gap-3 rounded-xl border bg-card px-4 py-3 shadow-sm sm:flex-row sm:items-center sm:justify-between"
	>
		<div class="grid min-w-0 gap-0.5">
			<Label for="ob-date">{$i18n.t('OB Date')}</Label>
			<p class="text-sm text-muted-foreground">
				{#if isDirty}
					{$i18n.t('Unsaved opening balance changes.')}
				{:else}
					{$i18n.t('The date the opening balances are stated at.')}
				{/if}
			</p>
		</div>
		<div class="flex flex-wrap items-center gap-2">
			<Input
				id="ob-date"
				type="date"
				class={cn('w-40 tabular-nums dark:scheme-dark', isDateDirty && 'border-ring')}
				bind:value={openingBalanceDate}
			/>
			{#if isDirty}
				<Button onclick={saveOpeningBalances} disabled={savingBalances}>
					{#if savingBalances}<Spinner />{:else}<Save />{/if}
					{$i18n.t('Save Opening Balances')}
				</Button>
			{/if}
		</div>
	</div>

	<!-- Content -->
	{#if loading && accounts.length === 0}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(8) as _}
				<Skeleton class="h-8 w-full" />
			{/each}
		</div>
	{:else if loadError && accounts.length === 0}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Failed to load accounts')}</Alert.Title>
			<Alert.Description>{loadError}</Alert.Description>
			<Alert.Action>
				<Button variant="outline" size="sm" onclick={reload}>{$i18n.t('Retry')}</Button>
			</Alert.Action>
		</Alert.Root>
	{:else if accounts.length === 0}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><ListTree /></Empty.Media>
				<Empty.Title>{$i18n.t('No accounts found')}</Empty.Title>
				<Empty.Description>
					{$i18n.t('Add accounts one by one, or import a chart from Excel.')}
				</Empty.Description>
			</Empty.Header>
			{#if canWrite}
				<Empty.Content class="flex-row justify-center gap-2">
					<Button variant="outline" size="sm" onclick={() => (showImportModal = true)}>
						<Upload />{$i18n.t('Import from Excel')}
					</Button>
					<Button size="sm" onclick={openAddModal}><Plus />{$i18n.t('Add Account')}</Button>
				</Empty.Content>
			{/if}
		</Empty.Root>
	{:else}
		<div class="relative w-full sm:w-72">
			<Search
				class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
			/>
			<Input
				type="search"
				class="h-8 pl-8"
				bind:value={query}
				oninput={() => (searchCollapsed = new Set())}
				aria-label={$i18n.t('Search accounts')}
				placeholder={$i18n.t('Search by code or name...')}
			/>
		</div>

		{#if q && matchCount === 0}
			<Empty.Root class="border border-dashed">
				<Empty.Header>
					<Empty.Media variant="icon"><ListTree /></Empty.Media>
					<Empty.Title>{$i18n.t('No accounts match your search')}</Empty.Title>
				</Empty.Header>
				<Empty.Content>
					<Button variant="outline" size="sm" onclick={() => (query = '')}>
						{$i18n.t('Clear search')}
					</Button>
				</Empty.Content>
			</Empty.Root>
		{/if}

		{#each groupedAccounts as group (group.key)}
			{#if group.accounts.length > 0}
				{@const open = q ? !searchCollapsed.has(group.key) : expandedSections.has(group.key)}
				<div class="overflow-hidden rounded-md border">
					<button
						type="button"
						class="flex w-full items-center gap-2 bg-muted/50 px-3 py-2 text-left text-sm font-medium transition-colors hover:bg-muted focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
						aria-expanded={open}
						onclick={() => toggleSection(group.key)}
					>
						<ChevronDown
							class={cn('size-4 text-muted-foreground transition-transform', !open && '-rotate-90')}
						/>
						{$i18n.t(group.label)}
						<Badge variant="count">{group.accounts.length}</Badge>
					</button>

					{#if open}
						<Table.Root class="border-t">
							<Table.Header>
								<Table.Row class="hover:bg-transparent">
									<Table.Head class="w-36">{$i18n.t('Code')}</Table.Head>
									<Table.Head class="min-w-56">{$i18n.t('Name', { context: 'gnos3' })}</Table.Head>
									<Table.Head class="w-28">{$i18n.t('Type')}</Table.Head>
									<Table.Head class="w-32 text-right">{$i18n.t('Opening DR')}</Table.Head>
									<Table.Head class="w-32 text-right">{$i18n.t('Opening CR')}</Table.Head>
									<Table.Head class="w-28">{$i18n.t('Status')}</Table.Head>
									<Table.Head class="w-12"
										><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head
									>
								</Table.Row>
							</Table.Header>
							<Table.Body>
								{#each group.accounts as acct (acct.id)}
									{@const indent = `padding-left: ${0.5 + (acct.level ?? 0) * 1.25}rem`}
									<Table.Row
										class="cursor-pointer"
										tabindex={0}
										onclick={(e: MouseEvent) => activateRow(e, acct)}
										onkeydown={(e: KeyboardEvent) => activateRow(e, acct)}
									>
										<Table.Cell class="py-1.5 font-mono text-[13px]" style={indent}>
											{acct.code}
										</Table.Cell>
										<Table.Cell class="py-1.5 whitespace-normal" style={indent}>
											<span class={parentIds.has(acct.id) ? 'font-medium' : ''}>{acct.name}</span>
											{#if acct.description}
												<span class="ml-1 text-muted-foreground">— {acct.description}</span>
											{/if}
										</Table.Cell>
										<Table.Cell class="py-1.5">
											<Badge variant="outline">{$i18n.t(typeLabel(acct.account_type))}</Badge>
										</Table.Cell>
										<Table.Cell class="py-1 text-right">
											<Input
												type="number"
												step="0.01"
												aria-label="{$i18n.t('Opening DR')} {acct.code}"
												class={cn(
													'ml-auto h-8 w-28 text-right tabular-nums',
													editedBalances[acct.id] && 'border-ring'
												)}
												value={(editedBalances[acct.id] ?? openingBalances[acct.id] ?? { debit: 0 })
													.debit || ''}
												oninput={(e: Event) =>
													handleBalanceInput(
														acct.id,
														'debit',
														(e.currentTarget as HTMLInputElement).value
													)}
											/>
										</Table.Cell>
										<Table.Cell class="py-1 text-right">
											<Input
												type="number"
												step="0.01"
												aria-label="{$i18n.t('Opening CR')} {acct.code}"
												class={cn(
													'ml-auto h-8 w-28 text-right tabular-nums',
													editedBalances[acct.id] && 'border-ring'
												)}
												value={(
													editedBalances[acct.id] ??
													openingBalances[acct.id] ?? { credit: 0 }
												).credit || ''}
												oninput={(e: Event) =>
													handleBalanceInput(
														acct.id,
														'credit',
														(e.currentTarget as HTMLInputElement).value
													)}
											/>
										</Table.Cell>
										<Table.Cell class="py-1.5">
											{#if acct.is_active}
												<Badge variant="status">
													<CircleCheck class="text-success" aria-hidden="true" />{$i18n.t('Active', { context: 'gnos3' })}
												</Badge>
											{:else}
												<Badge variant="status">
													<CircleSlash aria-hidden="true" />{$i18n.t('Inactive')}
												</Badge>
											{/if}
										</Table.Cell>
										<Table.Cell class="py-1.5 text-right">
											{#if acct.is_active && canDelete}
												<Tip content={$i18n.t('Deactivate')}>
													<Button
														variant="ghost"
														size="icon-xs"
														class="text-muted-foreground hover:text-destructive"
														aria-label="{$i18n.t('Deactivate')} {acct.code}"
														onclick={() => confirmDeactivate(acct)}
													>
														<Archive />
													</Button>
												</Tip>
											{/if}
										</Table.Cell>
									</Table.Row>
								{/each}
							</Table.Body>
						</Table.Root>
					{/if}
				</div>
			{/if}
		{/each}
	{/if}
</div>
