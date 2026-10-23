<script lang="ts">
	import { getContext, createEventDispatcher } from 'svelte';
	import { toast } from 'svelte-sonner';

	import { createAccount, updateAccount } from '$lib/apis/accounting';

	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;
	export let account: any = null;
	export let accounts: any[] = [];
	export let companyId: number;

	const ACCOUNT_TYPES = ['asset', 'liability', 'equity', 'revenue', 'expense'];

	// Form state
	let code = '';
	let name = '';
	let account_type = 'asset';
	// '' = top level (a null option value does not survive the select wrapper)
	let parent_id: number | '' = '';
	let description = '';
	let opening_debit: number | null = null;
	let opening_credit: number | null = null;
	let submitting = false;

	$: if (show) {
		initForm();
	}

	$: filteredParents = accounts.filter(
		(a) => a.account_type === account_type && a.is_active && (!account || a.id !== account.id)
	);

	const initForm = () => {
		if (account) {
			code = account.code || '';
			name = account.name || '';
			account_type = account.account_type || 'asset';
			parent_id = account.parent_id || '';
			description = account.description || '';
			opening_debit = parseFloat(account.opening_debit) || null;
			opening_credit = parseFloat(account.opening_credit) || null;
		} else {
			code = '';
			name = '';
			account_type = 'asset';
			parent_id = '';
			description = '';
			opening_debit = null;
			opening_credit = null;
		}
	};

	const handleSubmit = async (e?: Event) => {
		e?.preventDefault();
		if (!code.trim() || !name.trim()) {
			toast.error($i18n.t('Code and Name are required'));
			return;
		}

		submitting = true;
		try {
			const payload: Record<string, any> = {
				code: code.trim(),
				name: name.trim(),
				account_type,
				description: description.trim() || null,
				opening_debit: opening_debit || 0,
				opening_credit: opening_credit || 0
			};
			if (parent_id) {
				payload.parent_id = parent_id;
			}

			let result;
			if (account) {
				result = await updateAccount(account.id, payload);
				toast.success($i18n.t('Account updated'));
			} else {
				result = await createAccount(payload, companyId);
				toast.success($i18n.t('Account created'));
			}
			dispatch('save', result);
			show = false;
		} catch (err: any) {
			toast.error(err?.detail || `${err}`);
		} finally {
			submitting = false;
		}
	};
</script>

<Dialog.Root bind:open={show}>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-lg">
		<Dialog.Header>
			<Dialog.Title>
				{account ? $i18n.t('Edit Account') : $i18n.t('Add Account')}
			</Dialog.Title>
			{#if account}
				<Dialog.Description>
					<span class="font-mono text-[13px]">{account.code}</span>
					{account.name}
				</Dialog.Description>
			{/if}
		</Dialog.Header>

		<form id="account-form" class="grid gap-4" onsubmit={handleSubmit}>
			<div class="grid gap-4 sm:grid-cols-[10rem_1fr]">
				<div class="grid gap-2">
					<Label for="account-code">{$i18n.t('Code')}</Label>
					<Input
						id="account-code"
						type="text"
						bind:value={code}
						placeholder={$i18n.t('e.g. 1000')}
						class="font-mono text-[13px]"
						required
					/>
				</div>
				<div class="grid gap-2">
					<Label for="account-name">{$i18n.t('Name', { context: 'gnos3' })}</Label>
					<Input
						id="account-name"
						type="text"
						bind:value={name}
						placeholder={$i18n.t('e.g. Cash')}
						required
					/>
				</div>
			</div>

			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2">
					<Label for="account-type">{$i18n.t('Account Type')}</Label>
					<NativeSelect.Root
						id="account-type"
						class="w-full"
						bind:value={account_type}
						onchange={() => {
							parent_id = '';
						}}
					>
						{#each ACCOUNT_TYPES as t}
							<NativeSelect.Option value={t}
								>{$i18n.t(t.charAt(0).toUpperCase() + t.slice(1))}</NativeSelect.Option
							>
						{/each}
					</NativeSelect.Root>
				</div>
				<div class="grid gap-2">
					<Label for="account-parent">{$i18n.t('Parent Account')}</Label>
					<NativeSelect.Root id="account-parent" class="w-full" bind:value={parent_id}>
						<NativeSelect.Option value="">{$i18n.t('None (top-level)')}</NativeSelect.Option>
						{#each filteredParents as p}
							<NativeSelect.Option value={p.id}>{p.code} - {p.name}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
			</div>

			<div class="grid gap-2">
				<Label for="account-description">{$i18n.t('Description')}</Label>
				<Textarea
					id="account-description"
					bind:value={description}
					placeholder={$i18n.t('Optional description')}
					rows={2}
					class="resize-none"
				/>
			</div>

			<fieldset class="grid gap-2">
				<legend class="mb-2 text-sm font-medium">{$i18n.t('Opening Balance')}</legend>
				<div class="grid grid-cols-2 gap-4">
					<div class="grid gap-1.5">
						<Label for="ob-debit" class="font-normal text-muted-foreground"
							>{$i18n.t('Debit')}</Label
						>
						<Input
							id="ob-debit"
							type="number"
							step="0.01"
							min="0"
							bind:value={opening_debit}
							placeholder="0.00"
							class="text-right tabular-nums"
						/>
					</div>
					<div class="grid gap-1.5">
						<Label for="ob-credit" class="font-normal text-muted-foreground"
							>{$i18n.t('Credit')}</Label
						>
						<Input
							id="ob-credit"
							type="number"
							step="0.01"
							min="0"
							bind:value={opening_credit}
							placeholder="0.00"
							class="text-right tabular-nums"
						/>
					</div>
				</div>
			</fieldset>
		</form>

		<Dialog.Footer>
			<Button variant="outline" onclick={() => (show = false)}>{$i18n.t('Cancel')}</Button>
			<Button type="submit" form="account-form" disabled={submitting}>
				{#if submitting}<Spinner />{/if}
				{submitting ? $i18n.t('Saving...') : account ? $i18n.t('Update') : $i18n.t('Create')}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
