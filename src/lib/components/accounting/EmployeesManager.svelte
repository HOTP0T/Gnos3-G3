<script lang="ts">
	import { onMount, onDestroy, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	import Plus from '@lucide/svelte/icons/plus';
	import Search from '@lucide/svelte/icons/search';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';
	import Pencil from '@lucide/svelte/icons/pencil';
	import UserX from '@lucide/svelte/icons/user-x';
	import UserCheck from '@lucide/svelte/icons/user-check';
	import Users from '@lucide/svelte/icons/users';
	import Link from '@lucide/svelte/icons/link';
	import Copy from '@lucide/svelte/icons/copy';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import CircleSlash from '@lucide/svelte/icons/circle-slash';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';

	import {
		getEmployees,
		createEmployee,
		updateEmployee,
		restoreEmployee,
		provisionEmployeeLogin,
		syncEmployeesToK4mi,
		getAccounts,
		getExpenseCategories
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
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';

	const i18n: any = getContext('i18n');
	export let companyId: number;

	// Shown once when a new portal login is created — finance hands these to the
	// employee (the password can't be retrieved again).
	let credential: { email: string; password: string } | null = null;

	let employees: any[] = [];
	let accounts: any[] = [];
	let categories: any[] = [];
	let loading = true;
	let loadError = '';
	let showForm = false;
	let editingId: number | null = null;
	let showInactive = false;
	let searchTerm = '';

	const emptyForm = () => ({
		code: '',
		full_name: '',
		email: '',
		department: '',
		reimbursement_account_id: null as number | null,
		default_expense_category_id: null as number | null,
		is_active: true
	});

	let form = emptyForm();
	let saving = false;

	// The account the employee is owed on. There is no company-wide fallback:
	// a sheet can't be approved until the employee has an active one.
	const isActiveLiability = (a: any) => a.account_type === 'liability' && a.is_active !== false;
	$: reimbursementOk = (id: number | null) => {
		if (!id) return false;
		const a = accounts.find((x) => x.id === id);
		return !!a && isActiveLiability(a);
	};
	// The current choice stays listed even if it was deactivated since.
	$: reimbursementOptions = accounts.filter(
		(a) =>
			isActiveLiability(a) ||
			(a.id === form.reimbursement_account_id && a.account_type === 'liability')
	);

	// Typing in the search box can outrun the server: only the latest answer is applied.
	let loadSeq = 0;
	const load = async () => {
		const seq = ++loadSeq;
		loading = true;
		loadError = '';
		try {
			const [empData, acctData, catData] = await Promise.all([
				getEmployees(companyId, {
					active: showInactive ? undefined : true,
					search: searchTerm || undefined
				}),
				getAccounts({ company_id: companyId }),
				getExpenseCategories(companyId)
			]);
			if (seq !== loadSeq) return;
			employees = empData?.employees ?? [];
			const accts = acctData?.accounts ?? acctData ?? [];
			accounts = Array.isArray(accts) ? accts : [];
			categories = catData?.categories ?? [];
		} catch (err: any) {
			if (seq !== loadSeq) return;
			loadError = `${err?.detail ?? err}`;
			toast.error(err?.detail ?? `${err}`);
		}
		loading = false;
	};

	onMount(load);

	let searchTimer: ReturnType<typeof setTimeout> | undefined;
	const searchLater = () => {
		clearTimeout(searchTimer);
		searchTimer = setTimeout(load, 300);
	};
	onDestroy(() => clearTimeout(searchTimer));

	const resetForm = () => {
		form = emptyForm();
		editingId = null;
		showForm = false;
	};

	const openNew = () => {
		form = emptyForm();
		editingId = null;
		showForm = true;
	};

	const openEdit = (emp: any) => {
		form = {
			code: emp.code,
			full_name: emp.full_name,
			email: emp.email ?? '',
			department: emp.department ?? '',
			reimbursement_account_id: emp.reimbursement_account_id,
			default_expense_category_id: emp.default_expense_category_id,
			is_active: emp.is_active
		};
		editingId = emp.id;
		showForm = true;
	};

	const handleSubmit = async () => {
		if (saving) return;
		if (!form.code.trim() || !form.full_name.trim()) {
			toast.error($i18n.t('Code and full name are required'));
			return;
		}
		const payload: Record<string, any> = {
			code: form.code.trim(),
			full_name: form.full_name.trim(),
			email: form.email.trim() || null,
			department: form.department.trim() || null,
			reimbursement_account_id: form.reimbursement_account_id ?? null,
			default_expense_category_id: form.default_expense_category_id ?? null,
			is_active: form.is_active
		};
		saving = true;
		try {
			if (editingId) {
				await updateEmployee(editingId, payload);
				toast.success($i18n.t('Employee updated'));
			} else {
				const res = await createEmployee(companyId, payload);
				toast.success($i18n.t('Employee created'));
				const login = res?.login;
				if (login?.created && login?.temp_password) {
					credential = { email: payload.email, password: login.temp_password };
				} else if (login?.error && payload.email) {
					toast.error(`${$i18n.t('Login not created')}: ${login.error}`);
				}
			}
			resetForm();
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		} finally {
			saving = false;
		}
	};

	const handleProvisionLogin = async (emp: any) => {
		try {
			const res = await provisionEmployeeLogin(emp.id);
			if (res?.created && res?.temp_password) {
				credential = { email: emp.email, password: res.temp_password };
			} else {
				toast.success($i18n.t('Portal login linked'));
			}
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	// Deactivate asks first. It goes through the same update as the form's
	// "Active" box (accountants may do it); the DELETE route needs an admin.
	let deactivateTarget: any = null;
	let showDeactivateConfirm = false;
	const askDeactivate = (emp: any) => {
		deactivateTarget = emp;
		showDeactivateConfirm = true;
	};
	const handleDeactivate = async () => {
		const emp = deactivateTarget;
		if (!emp) return;
		try {
			await updateEmployee(emp.id, { is_active: false });
			toast.success($i18n.t('Employee deactivated'));
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	// Copy the one-time login. Appliances serve plain HTTP, where
	// navigator.clipboard does not exist: fall back on a hidden textarea inside
	// the dialog (outside it, the dialog's focus trap would steal the selection).
	let copyHost: HTMLElement | null = null;
	const copyText = async (text: string): Promise<boolean> => {
		if (window.isSecureContext && navigator.clipboard?.writeText) {
			try {
				await navigator.clipboard.writeText(text);
				return true;
			} catch {
				/* fall back below */
			}
		}
		const ta = document.createElement('textarea');
		ta.value = text;
		ta.setAttribute('readonly', '');
		ta.style.position = 'fixed';
		ta.style.top = '0';
		ta.style.left = '0';
		ta.style.opacity = '0';
		(copyHost ?? document.body).appendChild(ta);
		try {
			ta.focus();
			ta.select();
			return document.execCommand('copy');
		} catch {
			return false;
		} finally {
			ta.remove();
		}
	};
	const copyCredential = async () => {
		if (!credential) return;
		const ok = await copyText(
			`${$i18n.t('Email')}: ${credential.email}\n${$i18n.t('Temporary password')}: ${credential.password}`
		);
		if (ok) toast.success($i18n.t('Copied'));
		else toast.error($i18n.t('Could not copy. Select the password and copy it by hand.'));
	};

	const handleRestore = async (id: number) => {
		try {
			await restoreEmployee(id);
			toast.success($i18n.t('Employee restored'));
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const handleSyncK4mi = async () => {
		try {
			await syncEmployeesToK4mi(companyId);
			toast.success($i18n.t('K4mi Employee field synced'));
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const reload = async () => {
		await load();
	};

	const accountLabel = (id: number | null) => {
		if (!id) return '';
		const a = accounts.find((x) => x.id === id);
		return a ? `${a.code} — ${a.name}` : '';
	};

	const categoryLabel = (id: number | null) => {
		if (!id) return '';
		const c = categories.find((x) => x.id === id);
		return c ? c.label : '';
	};
</script>

<div class="flex flex-col gap-4">
	<!-- Header -->
	<div class="flex flex-wrap items-start justify-between gap-x-4 gap-y-3">
		<div class="min-w-0 space-y-1">
			<h2 class="text-lg font-semibold">
				{$i18n.t('Employees')}
				{#if !loading}<span class="ml-1 font-normal text-muted-foreground tabular-nums"
						>{employees.length}</span
					>{/if}
			</h2>
			<p class="max-w-2xl text-sm text-muted-foreground">
				{$i18n.t(
					'People who submit expense receipts. One with an email can sign in to the expense portal.'
				)}
			</p>
		</div>
		<div class="flex flex-wrap items-center gap-2">
			<Tip content={$i18n.t('Force resync of the K4mi Employee select field')}>
				<Button variant="ghost" size="sm" onclick={handleSyncK4mi}>
					<RefreshCw />{$i18n.t('Sync K4mi')}
				</Button>
			</Tip>
			<Button size="sm" onclick={openNew}>
				<Plus />{$i18n.t('New Employee')}
			</Button>
		</div>
	</div>

	<!-- Toolbar -->
	<div class="flex flex-wrap items-center gap-2">
		<div class="relative w-full sm:w-64">
			<Search
				class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
			/>
			<Input
				type="search"
				class="h-8 pl-8"
				bind:value={searchTerm}
				oninput={searchLater}
				placeholder={$i18n.t('Search...')}
				aria-label={$i18n.t('Search...')}
			/>
		</div>
		<div class="flex items-center gap-2">
			<Checkbox
				id="emp-show-inactive-{companyId}"
				checked={showInactive}
				onCheckedChange={(v) => {
					showInactive = v === true;
					reload();
				}}
			/>
			<Label for="emp-show-inactive-{companyId}" class="font-normal"
				>{$i18n.t('Show inactive')}</Label
			>
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
			<Alert.Title>{$i18n.t('Failed to load employees')}</Alert.Title>
			<Alert.Description>
				<p>{loadError}</p>
				<Button variant="outline" size="sm" class="mt-2" onclick={load}>
					<RotateCcw />{$i18n.t('Retry')}
				</Button>
			</Alert.Description>
		</Alert.Root>
	{:else if employees.length === 0}
		<Empty.Root class="border">
			<Empty.Header>
				<Empty.Media variant="icon"><Users /></Empty.Media>
				<Empty.Title
					>{$i18n.t('No employees yet. Add one to start assigning expense receipts.')}</Empty.Title
				>
			</Empty.Header>
			<Empty.Content>
				<Button variant="outline" size="sm" onclick={openNew}>
					<Plus />{$i18n.t('New Employee')}
				</Button>
			</Empty.Content>
		</Empty.Root>
	{:else}
		<div class="overflow-hidden rounded-md border">
			<Table.Root>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						<Table.Head>{$i18n.t('Code')}</Table.Head>
						<Table.Head>{$i18n.t('Name', { context: 'gnos3' })}</Table.Head>
						<Table.Head>{$i18n.t('Email')}</Table.Head>
						<Table.Head>{$i18n.t('Department')}</Table.Head>
						<Table.Head>{$i18n.t('Reimbursement Account')}</Table.Head>
						<Table.Head>{$i18n.t('Default Category')}</Table.Head>
						<Table.Head>{$i18n.t('Status')}</Table.Head>
						<Table.Head>{$i18n.t('Portal login')}</Table.Head>
						<Table.Head class="w-20"><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each employees as emp}
						<Table.Row>
							<Table.Cell class="py-1.5 font-mono text-[13px]">{emp.code}</Table.Cell>
							<Table.Cell class="py-1.5 font-medium">{emp.full_name}</Table.Cell>
							<Table.Cell class="py-1.5 text-muted-foreground">{emp.email || '—'}</Table.Cell>
							<Table.Cell class="py-1.5 text-muted-foreground">{emp.department || '—'}</Table.Cell>
							<Table.Cell class="py-1.5 text-muted-foreground">
								{#if emp.is_active && !reimbursementOk(emp.reimbursement_account_id)}
									<Tip
										content={$i18n.t(
											"Needed to approve this employee's reimbursement sheets: choose an active liability account."
										)}
									>
										<span class="inline-flex items-center gap-1 text-foreground">
											<TriangleAlert class="size-3.5 text-warning" aria-hidden="true" />
											{accountLabel(emp.reimbursement_account_id) || $i18n.t('Not set')}
										</span>
									</Tip>
								{:else}
									{accountLabel(emp.reimbursement_account_id) || '—'}
								{/if}
							</Table.Cell>
							<Table.Cell class="py-1.5 text-muted-foreground">
								{categoryLabel(emp.default_expense_category_id) || '—'}
							</Table.Cell>
							<Table.Cell class="py-1.5">
								{#if emp.is_active}
									<Badge variant="status"
										><CircleCheck class="text-success" aria-hidden="true" />{$i18n.t('Active', {
											context: 'gnos3'
										})}</Badge
									>
								{:else}
									<Badge variant="status"
										><CircleSlash aria-hidden="true" />{$i18n.t('Inactive')}</Badge
									>
								{/if}
							</Table.Cell>
							<Table.Cell class="py-1.5">
								{#if emp.user_id}
									<Badge variant="status"><Link aria-hidden="true" />{$i18n.t('Linked')}</Badge>
								{:else if emp.is_active && emp.email}
									<Button variant="link" size="sm" onclick={() => handleProvisionLogin(emp)}>
										{$i18n.t('Create login')}
									</Button>
								{:else}
									<span class="text-muted-foreground">{$i18n.t('needs email')}</span>
								{/if}
							</Table.Cell>
							<Table.Cell class="py-1.5 text-right">
								<div class="inline-flex items-center gap-0.5">
									<Tip content={$i18n.t('Edit')}>
										<Button
											variant="ghost"
											size="icon-xs"
											aria-label={$i18n.t('Edit')}
											onclick={() => openEdit(emp)}
										>
											<Pencil />
										</Button>
									</Tip>
									{#if emp.is_active}
										<Tip content={$i18n.t('Deactivate')}>
											<Button
												variant="ghost"
												size="icon-xs"
												class="text-muted-foreground hover:text-destructive"
												aria-label={$i18n.t('Deactivate')}
												onclick={() => askDeactivate(emp)}
											>
												<UserX />
											</Button>
										</Tip>
									{:else}
										<Tip content={$i18n.t('Restore')}>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label={$i18n.t('Restore')}
												onclick={() => handleRestore(emp.id)}
											>
												<UserCheck />
											</Button>
										</Tip>
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

<!-- New / edit employee -->
<Dialog.Root bind:open={showForm}>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
		<Dialog.Header>
			<Dialog.Title>{editingId ? $i18n.t('Edit Employee') : $i18n.t('New Employee')}</Dialog.Title>
			{#if !editingId}
				<Dialog.Description>
					{$i18n.t('A new employee with an email also gets an expense-portal login.')}
				</Dialog.Description>
			{/if}
		</Dialog.Header>
		<div class="grid gap-4 sm:grid-cols-2">
			<div class="grid gap-2">
				<Label for="emp-code">{$i18n.t('Code')} *</Label>
				<Input id="emp-code" class="font-mono" bind:value={form.code} placeholder="EMP001" />
			</div>
			<div class="grid gap-2">
				<Label for="emp-name">{$i18n.t('Full Name')} *</Label>
				<Input id="emp-name" bind:value={form.full_name} placeholder="Alice Nguyen" />
			</div>
			<div class="grid gap-2">
				<Label for="emp-email">{$i18n.t('Email')}</Label>
				<Input id="emp-email" type="email" bind:value={form.email} />
			</div>
			<div class="grid gap-2">
				<Label for="emp-dept">{$i18n.t('Department')}</Label>
				<Input id="emp-dept" bind:value={form.department} />
			</div>
			<div class="grid gap-2">
				<Label for="emp-reimb">{$i18n.t('Reimbursement Account')}</Label>
				<NativeSelect.Root
					id="emp-reimb"
					class="w-full"
					aria-describedby="emp-reimb-hint"
					bind:value={form.reimbursement_account_id}
				>
					<option value={null} class="bg-[Canvas] text-[CanvasText]"
						>— {$i18n.t('Not set')} —</option
					>
					{#each reimbursementOptions as acct}
						<NativeSelect.Option value={acct.id}
							>{acct.code} — {acct.name}{acct.is_active === false
								? ` (${$i18n.t('Inactive')})`
								: ''}</NativeSelect.Option
						>
					{/each}
				</NativeSelect.Root>
				<p id="emp-reimb-hint" class="text-[13px] text-muted-foreground">
					{$i18n.t(
						"The liability account the employee is owed on. Required to approve the employee's reimbursement sheets."
					)}
				</p>
			</div>
			<div class="grid gap-2">
				<Label for="emp-cat">{$i18n.t('Default Category')}</Label>
				<NativeSelect.Root
					id="emp-cat"
					class="w-full"
					bind:value={form.default_expense_category_id}
				>
					<option value={null} class="bg-[Canvas] text-[CanvasText]">{$i18n.t('None')}</option>
					{#each categories as cat}
						<NativeSelect.Option value={cat.id}>{cat.label}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
			</div>
			<div class="flex items-center gap-2 sm:col-span-2">
				<Checkbox id="emp-active" bind:checked={form.is_active} />
				<Label for="emp-active">{$i18n.t('Active', { context: 'gnos3' })}</Label>
			</div>
		</div>
		<Dialog.Footer>
			<Button variant="outline" onclick={resetForm}>{$i18n.t('Cancel')}</Button>
			<Button disabled={saving} onclick={handleSubmit}>
				{#if saving}<Spinner />{/if}
				{editingId ? $i18n.t('Update') : $i18n.t('Create')}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- The new portal login, shown once: closing it is a deliberate "Done" -->
<Dialog.Root
	open={credential !== null}
	onOpenChange={(v) => {
		if (!v) credential = null;
	}}
>
	<Dialog.Content
		class="sm:max-w-md"
		showCloseButton={false}
		escapeKeydownBehavior="ignore"
		interactOutsideBehavior="ignore"
	>
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Portal login created')}</Dialog.Title>
			<Dialog.Description>
				{$i18n.t(
					"Share these with the employee — the password can't be shown again. They sign in at the expense portal."
				)}
			</Dialog.Description>
		</Dialog.Header>
		{#if credential}
			<div class="grid gap-2" bind:this={copyHost}>
				<div class="grid gap-1 rounded-md border bg-muted/50 px-3 py-2">
					<span class="text-sm text-muted-foreground">{$i18n.t('Email')}</span>
					<span class="font-mono text-[13px] select-all">{credential.email}</span>
				</div>
				<div class="grid gap-1 rounded-md border bg-muted/50 px-3 py-2">
					<span class="text-sm text-muted-foreground">{$i18n.t('Temporary password')}</span>
					<span class="font-mono text-[13px] select-all">{credential.password}</span>
				</div>
			</div>
		{/if}
		<Dialog.Footer>
			<Button variant="outline" onclick={copyCredential}>
				<Copy />{$i18n.t('Copy')}
			</Button>
			<Button onclick={() => (credential = null)}>{$i18n.t('Done')}</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<ConfirmDialog
	bind:open={showDeactivateConfirm}
	title={$i18n.t('Deactivate this employee?')}
	description={deactivateTarget
		? $i18n.t(
				'{{name}} leaves the employee lists and the K4mi Employee field. Their sheets and expenses are kept, and you can restore them later.',
				{ name: deactivateTarget.full_name }
			)
		: ''}
	confirmLabel={$i18n.t('Deactivate')}
	destructive
	onconfirm={handleDeactivate}
	oncancel={() => (deactivateTarget = null)}
/>
