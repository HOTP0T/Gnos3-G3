<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	import Plus from '@lucide/svelte/icons/plus';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Tags from '@lucide/svelte/icons/tags';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import CircleSlash from '@lucide/svelte/icons/circle-slash';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';

	import {
		getExpenseCategories,
		createExpenseCategory,
		updateExpenseCategory,
		deleteExpenseCategory,
		instantiateDefaultExpenseCategories,
		getAccounts
	} from '$lib/apis/accounting';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';

	const i18n: any = getContext('i18n');
	export let companyId: number;

	let categories: any[] = [];
	let accounts: any[] = [];
	let loading = true;
	let loadError = '';
	let showForm = false;
	let editingId: number | null = null;
	let editingIsBuiltin = false;

	// Delete confirmation
	let showDeleteConfirm = false;
	let deleteTarget: any = null;

	const emptyForm = () => ({
		key: '',
		label: '',
		description: '',
		default_account_id: null as number | null,
		sort_order: 0,
		is_active: true
	});

	let form = emptyForm();

	const load = async () => {
		loading = true;
		loadError = '';
		try {
			const [catData, acctData] = await Promise.all([
				getExpenseCategories(companyId),
				getAccounts({ company_id: companyId })
			]);
			categories = catData?.categories ?? [];
			const accts = acctData?.accounts ?? acctData ?? [];
			accounts = Array.isArray(accts) ? accts : [];
		} catch (err: any) {
			loadError = `${err?.detail ?? err}`;
			toast.error(err?.detail ?? `${err}`);
		}
		loading = false;
	};

	onMount(load);

	const resetForm = () => {
		form = emptyForm();
		editingId = null;
		editingIsBuiltin = false;
		showForm = false;
	};

	const openNew = () => {
		form = emptyForm();
		editingId = null;
		editingIsBuiltin = false;
		showForm = true;
	};

	const openEdit = (cat: any) => {
		form = {
			key: cat.key,
			label: cat.label,
			description: cat.description ?? '',
			default_account_id: cat.default_account_id,
			sort_order: cat.sort_order,
			is_active: cat.is_active
		};
		editingId = cat.id;
		editingIsBuiltin = cat.is_builtin;
		showForm = true;
	};

	const handleSubmit = async () => {
		if (!form.label.trim()) {
			toast.error($i18n.t('Label is required'));
			return;
		}
		if (!editingId && !form.key.trim()) {
			toast.error($i18n.t('Key is required'));
			return;
		}
		try {
			if (editingId) {
				await updateExpenseCategory(editingId, {
					label: form.label.trim(),
					description: form.description.trim() || null,
					default_account_id: form.default_account_id ?? null,
					sort_order: form.sort_order,
					is_active: form.is_active
				});
				toast.success($i18n.t('Category updated'));
			} else {
				await createExpenseCategory(companyId, {
					key: form.key.trim().toLowerCase(),
					label: form.label.trim(),
					description: form.description.trim() || null,
					default_account_id: form.default_account_id ?? null,
					sort_order: form.sort_order,
					is_active: form.is_active
				});
				toast.success($i18n.t('Category created'));
			}
			resetForm();
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const handleDelete = async (cat: any) => {
		if (cat.is_builtin) {
			toast.error($i18n.t('Built-in categories cannot be deleted — deactivate instead'));
			return;
		}
		try {
			await deleteExpenseCategory(cat.id);
			toast.success($i18n.t('Category deleted'));
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const askDelete = (cat: any) => {
		deleteTarget = cat;
		showDeleteConfirm = true;
	};

	const handleInstantiateDefaults = async () => {
		try {
			await instantiateDefaultExpenseCategories(companyId);
			toast.success($i18n.t('Default categories restored'));
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const accountLabel = (id: number | null) => {
		if (!id) return '';
		const a = accounts.find((x) => x.id === id);
		return a ? `${a.code} — ${a.name}` : '';
	};
</script>

<div class="flex flex-col gap-4">
	<!-- Header -->
	<div class="flex flex-wrap items-start justify-between gap-x-4 gap-y-3">
		<div class="min-w-0 space-y-1">
			<h2 class="text-lg font-semibold">
				{$i18n.t('Expense Categories')}
				{#if !loading}<span class="ml-1 font-normal text-muted-foreground tabular-nums"
						>{categories.length}</span
					>{/if}
			</h2>
			<p class="max-w-2xl text-sm text-muted-foreground">
				{$i18n.t(
					'What an expense receipt can be filed under. Each category can point to a default expense account.'
				)}
			</p>
		</div>
		<div class="flex flex-wrap items-center gap-2">
			<Tip content={$i18n.t('Re-seed any missing built-in categories')}>
				<Button variant="outline" size="sm" onclick={handleInstantiateDefaults}>
					<RotateCcw />{$i18n.t('Restore Defaults')}
				</Button>
			</Tip>
			<Button size="sm" onclick={openNew}>
				<Plus />{$i18n.t('New Category')}
			</Button>
		</div>
	</div>

	{#if loading}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(4) as _}
				<Skeleton class="h-8 w-full" />
			{/each}
		</div>
	{:else if loadError}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Failed to load expense categories')}</Alert.Title>
			<Alert.Description>
				<p>{loadError}</p>
				<Button variant="outline" size="sm" class="mt-2" onclick={load}>
					<RotateCcw />{$i18n.t('Retry')}
				</Button>
			</Alert.Description>
		</Alert.Root>
	{:else if categories.length === 0}
		<Empty.Root class="border">
			<Empty.Header>
				<Empty.Media variant="icon"><Tags /></Empty.Media>
				<Empty.Title
					>{$i18n.t(
						'No expense categories. Click Restore Defaults to seed the built-in taxonomy.'
					)}</Empty.Title
				>
			</Empty.Header>
			<Empty.Content>
				<Button variant="outline" size="sm" onclick={handleInstantiateDefaults}>
					<RotateCcw />{$i18n.t('Restore Defaults')}
				</Button>
			</Empty.Content>
		</Empty.Root>
	{:else}
		<div class="overflow-hidden rounded-md border">
			<Table.Root>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						<Table.Head>{$i18n.t('Key')}</Table.Head>
						<Table.Head>{$i18n.t('Label')}</Table.Head>
						<Table.Head>{$i18n.t('Default Account')}</Table.Head>
						<Table.Head>{$i18n.t('Description')}</Table.Head>
						<Table.Head>{$i18n.t('Status')}</Table.Head>
						<Table.Head class="w-20"><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each categories as cat}
						<Table.Row>
							<Table.Cell class="py-1.5">
								<span class="inline-flex items-center gap-2">
									<span class="font-mono text-[13px]">{cat.key}</span>
									{#if cat.is_builtin}
										<Badge variant="secondary">{$i18n.t('built-in')}</Badge>
									{/if}
								</span>
							</Table.Cell>
							<Table.Cell class="py-1.5 font-medium">{cat.label}</Table.Cell>
							<Table.Cell class="py-1.5 text-muted-foreground">
								{accountLabel(cat.default_account_id) || '—'}
							</Table.Cell>
							<Table.Cell
								class="max-w-[22rem] truncate py-1.5 text-muted-foreground"
								title={cat.description ?? ''}
							>
								{cat.description || '—'}
							</Table.Cell>
							<Table.Cell class="py-1.5">
								{#if cat.is_active}
									<Badge variant="status"
										><CircleCheck class="text-success" aria-hidden="true" />{$i18n.t('Active', { context: 'gnos3' })}</Badge
									>
								{:else}
									<Badge variant="status"
										><CircleSlash aria-hidden="true" />{$i18n.t('Inactive')}</Badge
									>
								{/if}
							</Table.Cell>
							<Table.Cell class="py-1.5 text-right">
								<div class="inline-flex items-center gap-0.5">
									<Tip content={$i18n.t('Edit')}>
										<Button
											variant="ghost"
											size="icon-xs"
											aria-label={$i18n.t('Edit')}
											onclick={() => openEdit(cat)}
										>
											<Pencil />
										</Button>
									</Tip>
									{#if !cat.is_builtin}
										<Tip content={$i18n.t('Delete')}>
											<Button
												variant="ghost"
												size="icon-xs"
												class="text-muted-foreground hover:text-destructive"
												aria-label={$i18n.t('Delete')}
												onclick={() => askDelete(cat)}
											>
												<Trash2 />
											</Button>
										</Tip>
									{:else}
										<span class="size-7" aria-hidden="true"></span>
									{/if}
								</div>
							</Table.Cell>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</div>
	{/if}
</div>

<!-- New / edit category -->
<Dialog.Root bind:open={showForm}>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
		<Dialog.Header>
			<Dialog.Title>{editingId ? $i18n.t('Edit Category') : $i18n.t('New Category')}</Dialog.Title>
			{#if editingId}
				<Dialog.Description>{$i18n.t('The key cannot be changed once created.')}</Dialog.Description
				>
			{/if}
		</Dialog.Header>
		<div class="grid gap-4 sm:grid-cols-[1fr_1fr_8rem]">
			<div class="grid gap-2">
				<Label for="cat-key">{$i18n.t('Key')}{editingId ? '' : ' *'}</Label>
				<Input
					id="cat-key"
					class="font-mono"
					bind:value={form.key}
					placeholder="accommodation"
					disabled={editingId !== null}
				/>
			</div>
			<div class="grid gap-2">
				<Label for="cat-label">{$i18n.t('Label')} *</Label>
				<Input id="cat-label" bind:value={form.label} placeholder={$i18n.t('Accommodation')} />
			</div>
			<div class="grid gap-2">
				<Label for="cat-sort">{$i18n.t('Sort Order')}</Label>
				<Input
					id="cat-sort"
					type="number"
					class="text-right tabular-nums"
					bind:value={form.sort_order}
				/>
			</div>
			<div class="grid gap-2 sm:col-span-3">
				<Label for="cat-desc">{$i18n.t('Description')}</Label>
				<Input id="cat-desc" bind:value={form.description} />
			</div>
			<div class="grid gap-2 sm:col-span-3">
				<Label for="cat-account">{$i18n.t('Default Expense Account')}</Label>
				<NativeSelect.Root id="cat-account" class="w-full" bind:value={form.default_account_id}>
					<option value={null} class="bg-[Canvas] text-[CanvasText]">{$i18n.t('None')}</option>
					{#each accounts.filter((a) => a.account_type === 'expense') as acct}
						<NativeSelect.Option value={acct.id}>{acct.code} — {acct.name}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
			</div>
			<div class="flex items-center gap-2 sm:col-span-3">
				<Checkbox id="cat-active" bind:checked={form.is_active} />
				<Label for="cat-active">{$i18n.t('Active', { context: 'gnos3' })}</Label>
			</div>
		</div>
		<Dialog.Footer>
			<Button variant="outline" onclick={resetForm}>{$i18n.t('Cancel')}</Button>
			<Button onclick={handleSubmit}>
				{editingId ? $i18n.t('Update') : $i18n.t('Create')}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<ConfirmDialog
	bind:open={showDeleteConfirm}
	title={$i18n.t('Delete category?')}
	description={deleteTarget
		? $i18n.t('"{{name}}" will be removed. This cannot be undone.', {
				name: deleteTarget.label ?? deleteTarget.key ?? ''
			})
		: ''}
	confirmLabel={$i18n.t('Delete')}
	destructive
	onconfirm={() => handleDelete(deleteTarget)}
/>
