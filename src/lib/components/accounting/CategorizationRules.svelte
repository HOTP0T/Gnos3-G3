<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';

	import Plus from '@lucide/svelte/icons/plus';
	import Check from '@lucide/svelte/icons/check';
	import X from '@lucide/svelte/icons/x';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Play from '@lucide/svelte/icons/play';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Ellipsis from '@lucide/svelte/icons/ellipsis';
	import Sparkles from '@lucide/svelte/icons/sparkles';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import ListFilter from '@lucide/svelte/icons/list-filter';

	import {
		getCategorizationRules,
		createCategorizationRule,
		updateCategorizationRule,
		approveCategorizationRule,
		rejectCategorizationRule,
		deleteCategorizationRule,
		applyCategorizationRule,
		getAccounts
	} from '$lib/apis/accounting';

	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as ToggleGroup from '$lib/components/ui/toggle-group/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';

	const i18n: any = getContext('i18n');
	export let companyId: number;

	let rules: any[] = [];
	let accounts: any[] = [];
	let loading = true;
	let loadError = '';
	let showForm = false;

	let newVendor = '';
	let newAccountCode = '';
	let newCounterpartyCode = '';
	let newMatchType = 'contains';
	let newMatchField = 'vendor';
	let newPriority = 0;
	let newDescKeywords = '';
	let newAutoCreateEntry = true;
	let newTaxAccountCode = '';
	let newTaxRate = '';
	let newDefaultDescription = '';
	let newRuleType = 'invoice';

	$: pendingRules = rules.filter((r: any) => r.status === 'pending');
	$: invoiceRules = rules.filter(
		(r: any) => (r.rule_type || 'invoice') === 'invoice' && r.status !== 'pending'
	);
	$: bankFeeRules = rules.filter((r: any) => r.rule_type === 'bank_fee' && r.status !== 'pending');

	// Split of the net across several accounts (invoice rules only).
	// Fixed amounts first, then percentages of the rest; the remainder lands on the main account.
	let newSplitLines: Array<{
		account_code: string;
		percent: string;
		amount: string;
		description: string;
	}> = [];
	const addSplit = () => {
		newSplitLines = [
			...newSplitLines,
			{ account_code: '', percent: '', amount: '', description: '' }
		];
	};
	const splitPayload = () =>
		newSplitLines
			.filter((l) => l.account_code && (l.percent !== '' || l.amount !== ''))
			.map((l) => ({
				account_code: l.account_code,
				percent: l.percent !== '' ? parseFloat(l.percent) : null,
				amount: l.amount !== '' ? parseFloat(l.amount) : null,
				description: l.description || null
			}));
	$: expenseAccounts = accounts.filter((a: any) =>
		['expense', 'revenue', 'liability', 'asset'].includes(a.account_type)
	);

	// Edit mode
	let editingRule: any = null;

	// Remove confirmation
	let showRemoveConfirm = false;
	let removeTarget: any = null;

	const openNew = (ruleType: 'invoice' | 'bank_fee') => {
		editingRule = null;
		newRuleType = ruleType;
		showForm = true;
	};

	const startEdit = (rule: any) => {
		editingRule = { ...rule };
		newVendor = rule.vendor_name_pattern;
		newAccountCode = rule.account_code;
		newCounterpartyCode = rule.counterparty_account_code || '';
		newMatchType = rule.match_type;
		newMatchField = rule.match_field || 'vendor';
		newPriority = rule.priority;
		newDescKeywords = (rule.description_keywords || []).join(', ');
		newAutoCreateEntry = rule.auto_create_entry;
		newTaxAccountCode = rule.tax_account_code || '';
		newTaxRate = rule.tax_rate ? String(rule.tax_rate) : '';
		newDefaultDescription = rule.default_description || '';
		newRuleType = rule.rule_type || 'invoice';
		newSplitLines = (rule.split_lines || []).map((l: any) => ({
			account_code: l.account_code ?? '',
			percent: l.percent ?? '',
			amount: l.amount ?? '',
			description: l.description ?? ''
		}));
		showForm = true;
	};

	const handleSaveEdit = async () => {
		if (!editingRule || !newVendor || !newAccountCode) {
			toast.error($i18n.t('Name pattern and account are required'));
			return;
		}
		try {
			await updateCategorizationRule(editingRule.id, {
				vendor_name_pattern: newVendor,
				account_code: newAccountCode,
				counterparty_account_code: newCounterpartyCode || null,
				match_field: newRuleType === 'bank_fee' ? 'vendor' : newMatchField,
				auto_create_entry: newAutoCreateEntry,
				tax_account_code: newTaxAccountCode || null,
				tax_rate: newTaxRate ? parseFloat(newTaxRate) : null,
				default_description: newDefaultDescription || null,
				split_lines: newRuleType === 'invoice' ? splitPayload() : null,
				match_type: newMatchType,
				priority: newPriority,
				description_keywords: newDescKeywords
					? newDescKeywords
							.split(',')
							.map((k: string) => k.trim())
							.filter(Boolean)
					: null,
				rule_type: newRuleType
			});
			toast.success($i18n.t('Rule updated'));
			editingRule = null;
			showForm = false;
			newVendor = '';
			newAccountCode = '';
			newCounterpartyCode = '';
			newDescKeywords = '';
			newTaxAccountCode = '';
			newTaxRate = '';
			newDefaultDescription = '';
			newSplitLines = [];
			newAutoCreateEntry = true;
			newRuleType = 'invoice';
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const cancelEdit = () => {
		editingRule = null;
		showForm = false;
		newVendor = '';
		newAccountCode = '';
		newCounterpartyCode = '';
		newDescKeywords = '';
		newTaxAccountCode = '';
		newTaxRate = '';
		newDefaultDescription = '';
		newSplitLines = [];
		newAutoCreateEntry = true;
		newRuleType = 'invoice';
	};

	const handleApprove = async (id: number) => {
		try {
			await approveCategorizationRule(id);
			toast.success($i18n.t('Rule approved'));
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const handleReject = async (id: number) => {
		try {
			await rejectCategorizationRule(id);
			toast.success($i18n.t('Rule rejected'));
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const load = async () => {
		loading = true;
		loadError = '';
		try {
			const [rulesData, accountsData] = await Promise.all([
				getCategorizationRules(companyId),
				getAccounts({ company_id: companyId })
			]);
			rules = rulesData ?? [];
			const accts = accountsData?.accounts ?? accountsData ?? [];
			accounts = Array.isArray(accts) ? accts : [];
		} catch (err: any) {
			loadError = err?.detail ?? `${err}`;
		}
		loading = false;
	};

	onMount(load);

	const handleCreate = async () => {
		if (!newVendor || !newAccountCode) {
			toast.error($i18n.t('Name pattern and account are required'));
			return;
		}
		try {
			await createCategorizationRule(companyId, {
				vendor_name_pattern: newVendor,
				account_code: newAccountCode,
				counterparty_account_code: newCounterpartyCode || null,
				match_field: newRuleType === 'bank_fee' ? 'vendor' : newMatchField,
				auto_create_entry: newAutoCreateEntry,
				tax_account_code: newTaxAccountCode || null,
				tax_rate: newTaxRate ? parseFloat(newTaxRate) : null,
				default_description: newDefaultDescription || null,
				split_lines: newRuleType === 'invoice' ? splitPayload() : null,
				match_type: newMatchType,
				priority: newPriority,
				description_keywords: newDescKeywords
					? newDescKeywords
							.split(',')
							.map((k: string) => k.trim())
							.filter(Boolean)
					: null,
				rule_type: newRuleType
			});
			toast.success($i18n.t('Rule created'));
			newVendor = '';
			newAccountCode = '';
			newCounterpartyCode = '';
			newDescKeywords = '';
			newTaxAccountCode = '';
			newTaxRate = '';
			newDefaultDescription = '';
			newSplitLines = [];
			newAutoCreateEntry = true;
			newRuleType = 'invoice';
			showForm = false;
			await load();
		} catch (err) {
			toast.error(`${err}`);
		}
	};

	const handleSubmit = (e: Event) => {
		e.preventDefault();
		editingRule ? handleSaveEdit() : handleCreate();
	};

	const confirmRemove = (rule: any) => {
		removeTarget = rule;
		showRemoveConfirm = true;
	};

	const handleDelete = async (id: number) => {
		try {
			await deleteCategorizationRule(id);
			toast.success($i18n.t('Rule removed'));
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	let applyingRuleId: number | null = null;
	const handleApply = async (rule: any) => {
		applyingRuleId = rule.id;
		try {
			const res = await applyCategorizationRule(rule.id);
			const label = res.rule_type === 'bank_fee' ? $i18n.t('bank lines') : $i18n.t('invoices');
			toast.success(`${$i18n.t('Applied to')} ${res.applied} ${label}`);
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		applyingRuleId = null;
	};

	const accountOf = (code: string) => accounts.find((a: any) => a.code === code);

	const matchTypeLabel = (t: string) =>
		t === 'exact' ? 'Exact' : t === 'prefix' ? 'Prefix' : t === 'contains' ? 'Contains' : t;
</script>

<!-- An account reference: code in mono, then the name -->
{#snippet account(code: string | null | undefined)}
	{#if code}
		{@const a = accountOf(code)}
		<span class="font-mono text-[13px]">{code}</span>
		{#if a}<span class="text-muted-foreground">{a.name}</span>{/if}
	{:else}
		<span class="text-muted-foreground">—</span>
	{/if}
{/snippet}

{#snippet source(createdBy: string, withSystem: boolean)}
	{#if createdBy === 'human'}
		<Badge variant="outline">{$i18n.t('Manual')}</Badge>
	{:else if withSystem && createdBy === 'system'}
		<Badge variant="outline">{$i18n.t('System')}</Badge>
	{:else}
		<Badge variant="outline"><Sparkles aria-hidden="true" />{$i18n.t('AI')}</Badge>
	{/if}
{/snippet}

{#snippet rowMenu(rule: any)}
	<DropdownMenu.Root>
		<DropdownMenu.Trigger>
			{#snippet child({ props })}
				<Button
					{...props}
					variant="ghost"
					size="icon-xs"
					aria-label="{$i18n.t('More actions')} {rule.vendor_name_pattern}"
				>
					{#if applyingRuleId === rule.id}<Spinner />{:else}<Ellipsis />{/if}
				</Button>
			{/snippet}
		</DropdownMenu.Trigger>
		<DropdownMenu.Content align="end" class="w-44">
			<DropdownMenu.Item onSelect={() => startEdit(rule)}>
				<Pencil />{$i18n.t('Edit')}
			</DropdownMenu.Item>
			<DropdownMenu.Item disabled={applyingRuleId === rule.id} onSelect={() => handleApply(rule)}>
				<Play />{applyingRuleId === rule.id ? $i18n.t('Applying...') : $i18n.t('Apply')}
			</DropdownMenu.Item>
			<DropdownMenu.Separator />
			<DropdownMenu.Item variant="destructive" onSelect={() => confirmRemove(rule)}>
				<Trash2 />{$i18n.t('Remove')}
			</DropdownMenu.Item>
		</DropdownMenu.Content>
	</DropdownMenu.Root>
{/snippet}

<ConfirmDialog
	bind:open={showRemoveConfirm}
	title={$i18n.t('Remove this rule?')}
	description={removeTarget?.vendor_name_pattern ?? ''}
	confirmLabel={$i18n.t('Remove')}
	destructive
	onconfirm={async () => {
		if (removeTarget) await handleDelete(removeTarget.id);
		removeTarget = null;
	}}
/>

<!-- New / edit rule -->
<Dialog.Root
	bind:open={showForm}
	onOpenChange={(v) => {
		if (!v) cancelEdit();
	}}
>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-3xl">
		<Dialog.Header>
			<Dialog.Title>
				{#if editingRule}
					{$i18n.t('Edit')}: {editingRule.vendor_name_pattern}
				{:else if newRuleType === 'bank_fee'}
					{$i18n.t('Add Bank Line Rule')}
				{:else}
					{$i18n.t('Add Invoice Rule')}
				{/if}
			</Dialog.Title>
			<Dialog.Description>
				{newRuleType === 'bank_fee'
					? $i18n.t('Matches a bank line by its description or payee.')
					: $i18n.t('Matches an invoice by its vendor or client name.')}
			</Dialog.Description>
		</Dialog.Header>

		<form id="rule-form" class="grid gap-4" onsubmit={handleSubmit}>
			<ToggleGroup.Root
				type="single"
				variant="outline"
				value={newRuleType}
				onValueChange={(v) => {
					if (v) newRuleType = v;
				}}
				aria-label={$i18n.t('Type')}
			>
				<ToggleGroup.Item value="invoice" class="px-3">{$i18n.t('Invoice Rule')}</ToggleGroup.Item>
				<ToggleGroup.Item value="bank_fee" class="px-3"
					>{$i18n.t('Bank Line Rule')}</ToggleGroup.Item
				>
			</ToggleGroup.Root>

			<div class="grid gap-4 sm:grid-cols-[auto_1fr_1fr]">
				{#if newRuleType === 'invoice'}
					<div class="grid gap-2">
						<Label for="rule-match-field">{$i18n.t('Match On')}</Label>
						<NativeSelect.Root id="rule-match-field" class="w-full" bind:value={newMatchField}>
							<NativeSelect.Option value="vendor">{$i18n.t('Vendor')}</NativeSelect.Option>
							<NativeSelect.Option value="client">{$i18n.t('Client')}</NativeSelect.Option>
							<NativeSelect.Option value="both">{$i18n.t('Both')}</NativeSelect.Option>
						</NativeSelect.Root>
					</div>
				{/if}
				<div class="grid gap-2 {newRuleType === 'bank_fee' ? 'sm:col-span-2' : ''}">
					<Label for="rule-pattern">
						{newRuleType === 'bank_fee'
							? $i18n.t('Description Pattern')
							: newMatchField === 'client'
								? $i18n.t('Client Pattern')
								: newMatchField === 'both'
									? $i18n.t('Name Pattern')
									: $i18n.t('Vendor Pattern')}
					</Label>
					<Input
						id="rule-pattern"
						type="text"
						bind:value={newVendor}
						placeholder={newRuleType === 'bank_fee'
							? 'e.g. FRAIS BANCAIRES'
							: newMatchField === 'client'
								? 'e.g. Dupont SARL'
								: 'e.g. amazon'}
					/>
				</div>
				<div class="grid gap-2">
					<Label for="rule-debit">{$i18n.t('Debit Account')}</Label>
					<NativeSelect.Root id="rule-debit" class="w-full" bind:value={newAccountCode}>
						<NativeSelect.Option value="">—</NativeSelect.Option>
						{#each accounts as acct}
							<NativeSelect.Option value={acct.code}>{acct.code} — {acct.name}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
			</div>

			<div class="grid gap-2">
				<Label for="rule-credit">{$i18n.t('Credit Account')}</Label>
				<NativeSelect.Root id="rule-credit" class="w-full" bind:value={newCounterpartyCode}>
					<NativeSelect.Option value="">—</NativeSelect.Option>
					{#each accounts as acct}
						<NativeSelect.Option value={acct.code}>{acct.code} — {acct.name}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
			</div>

			<div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
				<div class="grid gap-2">
					<Label for="rule-match-type">{$i18n.t('Match Type')}</Label>
					<NativeSelect.Root id="rule-match-type" class="w-full" bind:value={newMatchType}>
						<NativeSelect.Option value="exact">{$i18n.t('Exact')}</NativeSelect.Option>
						<NativeSelect.Option value="contains">{$i18n.t('Contains')}</NativeSelect.Option>
						<NativeSelect.Option value="prefix">{$i18n.t('Prefix')}</NativeSelect.Option>
					</NativeSelect.Root>
				</div>
				<div class="grid gap-2">
					<Label for="rule-keywords">{$i18n.t('Keywords')}</Label>
					<Input
						id="rule-keywords"
						type="text"
						bind:value={newDescKeywords}
						placeholder={$i18n.t('office, supplies')}
					/>
				</div>
				<div class="grid gap-2">
					<Label for="rule-tax-account">{$i18n.t('Tax Account')}</Label>
					<NativeSelect.Root id="rule-tax-account" class="w-full" bind:value={newTaxAccountCode}>
						<NativeSelect.Option value="">—</NativeSelect.Option>
						{#each accounts as acct}
							<NativeSelect.Option value={acct.code}>{acct.code} — {acct.name}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
				<div class="grid gap-2">
					<Label for="rule-tax-rate">{$i18n.t('Tax Rate %')}</Label>
					<Input
						id="rule-tax-rate"
						type="number"
						step="0.01"
						bind:value={newTaxRate}
						placeholder="e.g. 20"
						class="text-right tabular-nums"
					/>
				</div>
			</div>

			{#if newRuleType === 'invoice'}
				<!-- Split of the net across accounts -->
				<div class="grid gap-3 rounded-lg border border-dashed p-3">
					<div class="flex flex-wrap items-start justify-between gap-2">
						<span class="text-sm font-medium">
							{$i18n.t('Split the net across accounts')}
							<span class="font-normal text-muted-foreground">
								({$i18n.t('optional — e.g. staffing invoice: salary / IIT withheld / fee')})
							</span>
						</span>
						<Button type="button" variant="outline" size="xs" onclick={addSplit}>
							<Plus />{$i18n.t('Add line')}
						</Button>
					</div>
					{#each newSplitLines as sl, i}
						<div
							class="grid grid-cols-[1fr_1fr_auto] items-center gap-2 border-b pb-3 last-of-type:border-b-0 sm:grid-cols-[1.4fr_5rem_6rem_1fr_auto] sm:border-b-0 sm:pb-0"
						>
							<NativeSelect.Root
								size="sm"
								class="col-span-3 w-full sm:col-span-1"
								aria-label={$i18n.t('— account —')}
								bind:value={sl.account_code}
							>
								<NativeSelect.Option value="">{$i18n.t('— account —')}</NativeSelect.Option>
								{#each expenseAccounts as a}
									<NativeSelect.Option value={a.code}>{a.code} - {a.name}</NativeSelect.Option>
								{/each}
							</NativeSelect.Root>
							<Input
								type="number"
								step="0.01"
								bind:value={sl.percent}
								placeholder="%"
								aria-label="%"
								class="h-8 text-right tabular-nums"
							/>
							<Input
								type="number"
								step="0.01"
								bind:value={sl.amount}
								placeholder={$i18n.t('fixed')}
								aria-label={$i18n.t('fixed')}
								class="h-8 text-right tabular-nums"
							/>
							<Input
								type="text"
								bind:value={sl.description}
								placeholder={$i18n.t('Description')}
								aria-label={$i18n.t('Description')}
								class="col-span-2 h-8 sm:col-span-1"
							/>
							<Tip content={$i18n.t('Remove')}>
								<Button
									type="button"
									variant="ghost"
									size="icon-sm"
									aria-label={$i18n.t('Remove')}
									onclick={() => {
										newSplitLines = newSplitLines.filter((_, j) => j !== i);
									}}
								>
									<X />
								</Button>
							</Tip>
						</div>
					{/each}
					{#if newSplitLines.length}
						<p class="text-sm text-muted-foreground">
							{$i18n.t(
								'Fixed amounts are taken first, percentages apply to what is left, and the remainder goes to the main account above.'
							)}
						</p>
					{/if}
				</div>
			{/if}

			<div class="grid gap-4 sm:grid-cols-[1fr_auto_6rem] sm:items-end">
				<div class="grid gap-2">
					<Label for="rule-default-description">{$i18n.t('Default Description')}</Label>
					<Input
						id="rule-default-description"
						type="text"
						bind:value={newDefaultDescription}
						placeholder={$i18n.t('e.g. Office rent')}
					/>
				</div>
				<div class="flex h-9 items-center gap-2">
					<Checkbox id="rule-auto-entry" bind:checked={newAutoCreateEntry} />
					<Label for="rule-auto-entry" class="font-normal whitespace-nowrap">
						{$i18n.t('Auto-create draft entry')}
					</Label>
				</div>
				<div class="grid gap-2">
					<Label for="rule-priority">{$i18n.t('Priority')}</Label>
					<Input
						id="rule-priority"
						type="number"
						bind:value={newPriority}
						class="text-right tabular-nums"
					/>
				</div>
			</div>
		</form>

		<Dialog.Footer>
			<Button variant="outline" onclick={cancelEdit}>{$i18n.t('Cancel')}</Button>
			<Button type="submit" form="rule-form">
				{editingRule ? $i18n.t('Update Rule') : $i18n.t('Save')}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<div class="flex flex-col gap-4">
	<div class="flex flex-wrap items-start justify-between gap-x-4 gap-y-3">
		<div class="min-w-0 space-y-1">
			<h2 class="flex flex-wrap items-center gap-2 text-lg font-semibold">
				{$i18n.t('Account Categorization Rules')}
				{#if pendingRules.length > 0}
					<Badge variant="warning">
						<TriangleAlert aria-hidden="true" />{pendingRules.length}
						{$i18n.t('pending', { context: 'gnos3' })}
					</Badge>
				{/if}
			</h2>
			<p class="text-sm text-muted-foreground">
				{$i18n.t(
					'Invoice rules map a vendor or client name to the accounts an invoice is booked on. Bank line rules map a pattern in a bank statement description (a fee, a tax payment, a salary run) to the account that line settles. The AI learns invoice rules from your corrections automatically.'
				)}
			</p>
		</div>
		<div class="flex flex-wrap items-center gap-2">
			<Button variant="outline" size="sm" onclick={() => openNew('bank_fee')}>
				<Plus />{$i18n.t('Add Bank Line Rule')}
			</Button>
			<Button size="sm" onclick={() => openNew('invoice')}>
				<Plus />{$i18n.t('Add Invoice Rule')}
			</Button>
		</div>
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
			<Alert.Title>{$i18n.t('Failed to load')}</Alert.Title>
			<Alert.Description>{loadError}</Alert.Description>
			<Alert.Action>
				<Button variant="outline" size="sm" onclick={load}>{$i18n.t('Retry')}</Button>
			</Alert.Action>
		</Alert.Root>
	{:else if rules.length === 0}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><ListFilter /></Empty.Media>
				<Empty.Title>{$i18n.t('No categorization rules')}</Empty.Title>
				<Empty.Description>
					{$i18n.t(
						'No rules yet. Rules are created automatically when you confirm invoice categories.'
					)}
				</Empty.Description>
			</Empty.Header>
			<Empty.Content>
				<Button size="sm" onclick={() => openNew('invoice')}>
					<Plus />{$i18n.t('Add Invoice Rule')}
				</Button>
			</Empty.Content>
		</Empty.Root>
	{:else}
		<!-- Pending Rules -->
		{#if pendingRules.length > 0}
			<section class="grid gap-2">
				<h3 class="flex items-center gap-2 text-sm font-medium">
					<TriangleAlert class="size-4 text-warning" aria-hidden="true" />
					{$i18n.t('Pending Approval')}
					<Badge variant="count">{pendingRules.length}</Badge>
				</h3>
				<div class="overflow-hidden rounded-md border">
					<Table.Root>
						<Table.Header class="bg-muted/50">
							<Table.Row class="hover:bg-transparent">
								<Table.Head>{$i18n.t('Pattern')}</Table.Head>
								<Table.Head>{$i18n.t('Type')}</Table.Head>
								<Table.Head>{$i18n.t('Debit')}</Table.Head>
								<Table.Head>{$i18n.t('Credit')}</Table.Head>
								<Table.Head>{$i18n.t('Match', { context: 'type' })}</Table.Head>
								<Table.Head>{$i18n.t('Source')}</Table.Head>
								<Table.Head class="w-px"
									><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head
								>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each pendingRules as rule (rule.id)}
								<Table.Row>
									<Table.Cell class="font-medium">{rule.vendor_name_pattern}</Table.Cell>
									<Table.Cell>
										<Badge variant="outline">
											{rule.rule_type === 'bank_fee' ? $i18n.t('Bank line') : $i18n.t('Invoice')}
										</Badge>
									</Table.Cell>
									<Table.Cell>{@render account(rule.account_code)}</Table.Cell>
									<Table.Cell>{@render account(rule.counterparty_account_code)}</Table.Cell>
									<Table.Cell>
										<Badge variant="outline">{$i18n.t(matchTypeLabel(rule.match_type))}</Badge>
									</Table.Cell>
									<Table.Cell>{@render source(rule.created_by, false)}</Table.Cell>
									<Table.Cell class="text-right">
										<div class="flex items-center justify-end gap-1">
											<Button variant="outline" size="xs" onclick={() => handleApprove(rule.id)}>
												<Check />{$i18n.t('Approve')}
											</Button>
											<Button variant="outline" size="xs" onclick={() => handleReject(rule.id)}>
												<X />{$i18n.t('Reject')}
											</Button>
											<Tip content={$i18n.t('Edit')}>
												<Button
													variant="ghost"
													size="icon-xs"
													aria-label="{$i18n.t('Edit')} {rule.vendor_name_pattern}"
													onclick={() => startEdit(rule)}
												>
													<Pencil />
												</Button>
											</Tip>
										</div>
									</Table.Cell>
								</Table.Row>
							{/each}
						</Table.Body>
					</Table.Root>
				</div>
			</section>
		{/if}

		<!-- Invoice Rules -->
		{#if invoiceRules.length > 0}
			<section class="grid gap-2">
				<h3 class="flex items-center gap-2 text-sm font-medium">
					{$i18n.t('Invoice Rules')}
					<Badge variant="count">{invoiceRules.length}</Badge>
				</h3>
				<div class="overflow-hidden rounded-md border">
					<Table.Root>
						<Table.Header class="bg-muted/50">
							<Table.Row class="hover:bg-transparent">
								<Table.Head>{$i18n.t('Name Pattern')}</Table.Head>
								<Table.Head>{$i18n.t('Field')}</Table.Head>
								<Table.Head>{$i18n.t('Debit')}</Table.Head>
								<Table.Head>{$i18n.t('Credit')}</Table.Head>
								<Table.Head>{$i18n.t('Match', { context: 'type' })}</Table.Head>
								<Table.Head>{$i18n.t('Auto')}</Table.Head>
								<Table.Head>{$i18n.t('Source')}</Table.Head>
								<Table.Head class="text-right">{$i18n.t('Used')}</Table.Head>
								<Table.Head class="w-12"
									><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head
								>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each invoiceRules as rule (rule.id)}
								<Table.Row>
									<Table.Cell class="min-w-44 font-medium whitespace-normal">
										{rule.vendor_name_pattern}
										{#if rule.description_keywords?.length}
											<div class="text-xs font-normal text-muted-foreground">
												{rule.description_keywords.join(', ')}
											</div>
										{/if}
										{#if rule.split_lines?.length}
											<div class="text-xs font-normal text-muted-foreground">
												{$i18n.t('{{count}} split line(s)', { count: rule.split_lines.length })}
											</div>
										{/if}
									</Table.Cell>
									<Table.Cell>
										<Badge variant="outline">
											{rule.match_field === 'client'
												? $i18n.t('Client')
												: rule.match_field === 'both'
													? $i18n.t('Both')
													: $i18n.t('Vendor')}
										</Badge>
									</Table.Cell>
									<Table.Cell>{@render account(rule.account_code)}</Table.Cell>
									<Table.Cell>{@render account(rule.counterparty_account_code)}</Table.Cell>
									<Table.Cell>
										<Badge variant="outline">{$i18n.t(matchTypeLabel(rule.match_type))}</Badge>
									</Table.Cell>
									<Table.Cell>
										{#if rule.auto_create_entry}
											<Badge variant="status">
												<Check class="text-success" aria-hidden="true" />{$i18n.t('Auto')}
											</Badge>
										{:else}
											<span class="text-muted-foreground">—</span>
										{/if}
									</Table.Cell>
									<Table.Cell>{@render source(rule.created_by, true)}</Table.Cell>
									<Table.Cell class="text-right text-muted-foreground tabular-nums">
										{rule.times_used}×
									</Table.Cell>
									<Table.Cell class="text-right">{@render rowMenu(rule)}</Table.Cell>
								</Table.Row>
							{/each}
						</Table.Body>
					</Table.Root>
				</div>
			</section>
		{/if}

		<!-- Bank Fee Rules -->
		{#if bankFeeRules.length > 0}
			<section class="grid gap-2">
				<div class="grid gap-1">
					<h3 class="flex items-center gap-2 text-sm font-medium">
						{$i18n.t('Bank Line Rules')}
						<Badge variant="count">{bankFeeRules.length}</Badge>
					</h3>
					<p class="text-sm text-muted-foreground">
						{$i18n.t(
							'Match a bank line by its description or payee (e.g. "TAX" → taxes payable, "SALARY" → salaries payable, "FEES" → bank charges) — the debit account is what a payment on such a line settles when no invoice is linked. Also used by the Bank Fee button.'
						)}
					</p>
				</div>
				<div class="overflow-hidden rounded-md border">
					<Table.Root>
						<Table.Header class="bg-muted/50">
							<Table.Row class="hover:bg-transparent">
								<Table.Head>{$i18n.t('Description Pattern')}</Table.Head>
								<Table.Head>{$i18n.t('Debit')}</Table.Head>
								<Table.Head>{$i18n.t('Credit')}</Table.Head>
								<Table.Head>{$i18n.t('Match', { context: 'type' })}</Table.Head>
								<Table.Head>{$i18n.t('Default Description')}</Table.Head>
								<Table.Head class="text-right">{$i18n.t('Used')}</Table.Head>
								<Table.Head class="w-12"
									><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head
								>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each bankFeeRules as rule (rule.id)}
								<Table.Row>
									<Table.Cell class="font-medium">{rule.vendor_name_pattern}</Table.Cell>
									<Table.Cell>{@render account(rule.account_code)}</Table.Cell>
									<Table.Cell>{@render account(rule.counterparty_account_code)}</Table.Cell>
									<Table.Cell>
										<Badge variant="outline">{$i18n.t(matchTypeLabel(rule.match_type))}</Badge>
									</Table.Cell>
									<Table.Cell class="text-muted-foreground"
										>{rule.default_description ?? '—'}</Table.Cell
									>
									<Table.Cell class="text-right text-muted-foreground tabular-nums">
										{rule.times_used}×
									</Table.Cell>
									<Table.Cell class="text-right">{@render rowMenu(rule)}</Table.Cell>
								</Table.Row>
							{/each}
						</Table.Body>
					</Table.Root>
				</div>
			</section>
		{/if}
	{/if}
</div>
