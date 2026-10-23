<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';

	import Search from '@lucide/svelte/icons/search';
	import Plus from '@lucide/svelte/icons/plus';
	import Ellipsis from '@lucide/svelte/icons/ellipsis';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Copy from '@lucide/svelte/icons/copy';
	import Ban from '@lucide/svelte/icons/ban';
	import Building from '@lucide/svelte/icons/building';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import RotateCw from '@lucide/svelte/icons/rotate-cw';
	import LayoutGrid from '@lucide/svelte/icons/layout-grid';
	import List from '@lucide/svelte/icons/list';

	import {
		getCompanies,
		createCompany,
		updateCompany,
		deleteCompany,
		duplicateCompany,
		getChartTemplates,
		getPeriodTemplates
	} from '$lib/apis/accounting';

	import * as Card from '$lib/components/ui/card/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as ToggleGroup from '$lib/components/ui/toggle-group/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';
	import CompanyFormModal from '$lib/components/accounting/CompanyFormModal.svelte';
	import CompanyLogo from '$lib/components/accounting/CompanyLogo.svelte';
	import { user, isAdmin } from '$lib/stores';

	const i18n: any = getContext('i18n');

	// RBAC: Add Company creates a new company → requires modules.accounting.admin
	// (the user must have global admin on the accounting module). Admins bypass.
	$: canCreateCompany = $isAdmin || Boolean($user?.permissions?.modules?.accounting?.admin);

	let loading = true;
	let loadError = '';
	let companies: any[] = [];
	let query = '';

	// Cards or a compact list; remembered in this browser.
	const VIEW_KEY = 'accounting-companies-view';
	let view: 'grid' | 'list' = 'grid';

	const setView = (v: string) => {
		if (v !== 'grid' && v !== 'list') return; // clicking the pressed item reports ''
		view = v;
		try {
			localStorage.setItem(VIEW_KEY, view);
		} catch {}
	};

	// Modal state
	let showFormModal = false;
	let editingCompany: any = null;

	// Duplicate modal state
	let showDuplicateModal = false;
	let duplicatingCompany: any = null;
	let duplicateName = '';
	let duplicating = false;

	// Deactivate confirm state
	let showDeactivateConfirm = false;
	let deactivatingCompany: any = null;
	let deactivating = false;

	$: filteredCompanies = companies.filter((c) =>
		c.name.toLowerCase().includes(query.toLowerCase())
	);
	$: activeCount = companies.filter((c) => c.is_active).length;
	$: inactiveCount = companies.length - activeCount;

	const loadCompanies = async () => {
		loading = true;
		loadError = '';
		try {
			const res = await getCompanies();
			const list = Array.isArray(res) ? res : (res?.companies ?? []);
			companies = list;
		} catch (err: any) {
			loadError = err?.detail || `${err}`;
			toast.error(loadError);
		}
		loading = false;
	};

	const handleAddCompany = () => {
		editingCompany = null;
		showFormModal = true;
	};

	const handleEditCompany = (company: any) => {
		editingCompany = company;
		showFormModal = true;
	};

	const handleDuplicateCompany = (company: any) => {
		duplicatingCompany = company;
		duplicateName = `${company.name} (Copy)`;
		showDuplicateModal = true;
	};

	const confirmDuplicate = async () => {
		if (!duplicateName.trim()) {
			toast.error($i18n.t('Name is required'));
			return;
		}
		duplicating = true;
		try {
			await duplicateCompany(duplicatingCompany.id, { name: duplicateName.trim() });
			toast.success($i18n.t('Company duplicated successfully'));
			showDuplicateModal = false;
			duplicatingCompany = null;
			duplicateName = '';
			await loadCompanies();
		} catch (err: any) {
			toast.error(err?.detail || `${err}`);
		}
		duplicating = false;
	};

	const handleDeactivate = (company: any) => {
		deactivatingCompany = company;
		showDeactivateConfirm = true;
	};

	const confirmDeactivate = async () => {
		deactivating = true;
		try {
			await updateCompany(deactivatingCompany.id, { is_active: false });
			toast.success($i18n.t('Company deactivated'));
			showDeactivateConfirm = false;
			deactivatingCompany = null;
			await loadCompanies();
		} catch (err: any) {
			toast.error(err?.detail || `${err}`);
		}
		deactivating = false;
	};

	const handleFormSave = async () => {
		showFormModal = false;
		editingCompany = null;
		await loadCompanies();
	};

	const companyHref = (company: any) => `/accounting/company/${company.id}/dashboard`;

	// A click anywhere on a list row opens the company; the link and the menu keep their own.
	const openFromRow = (e: MouseEvent, company: any) => {
		if ((e.target as HTMLElement).closest('a, button')) return;
		goto(companyHref(company));
	};

	const fiscalStart = (company: any) => Number(company.fiscal_year_start_month ?? 1) || 1;

	// "31 Mar": the last day of the fiscal year.
	const fiscalYearEnd = (company: any) =>
		dayjs()
			.month(fiscalStart(company) - 2)
			.endOf('month')
			.format('D MMM');

	// "China · CNY", plus "FY to 31 Mar" when the fiscal year is not the calendar year.
	const companyMeta = (company: any) => {
		const parts = [company.country, company.currency].filter(Boolean);
		if (fiscalStart(company) !== 1) parts.push(`${$i18n.t('FY to')} ${fiscalYearEnd(company)}`);
		return parts.join(' · ');
	};

	onMount(() => {
		try {
			const v = localStorage.getItem(VIEW_KEY);
			if (v === 'grid' || v === 'list') view = v;
		} catch {}
		loadCompanies();
	});
</script>

<CompanyFormModal bind:show={showFormModal} company={editingCompany} on:save={handleFormSave} />

{#snippet companyMenu(company: any)}
	<DropdownMenu.Root>
		<DropdownMenu.Trigger>
			{#snippet child({ props })}
				<Button {...props} variant="ghost" size="icon-xs" aria-label={$i18n.t('Company actions')}>
					<Ellipsis />
				</Button>
			{/snippet}
		</DropdownMenu.Trigger>
		<DropdownMenu.Content align="end" class="w-48">
			<DropdownMenu.Item onSelect={() => handleEditCompany(company)}>
				<Pencil />{$i18n.t('Edit')}
			</DropdownMenu.Item>
			<DropdownMenu.Item onSelect={() => handleDuplicateCompany(company)}>
				<Copy />{$i18n.t('Duplicate')}
			</DropdownMenu.Item>
			{#if company.is_active}
				<DropdownMenu.Separator />
				<DropdownMenu.Item variant="destructive" onSelect={() => handleDeactivate(company)}>
					<Ban />{$i18n.t('Deactivate')}
				</DropdownMenu.Item>
			{/if}
		</DropdownMenu.Content>
	</DropdownMenu.Root>
{/snippet}

<div class="flex flex-col gap-4">
	<!-- Page head: title + counts, search and the one primary action -->
	<div class="flex flex-wrap items-end justify-between gap-3">
		<div class="min-w-0">
			<h1 class="text-2xl font-semibold tracking-tight">{$i18n.t('Companies')}</h1>
			{#if !loading && !loadError}
				<p class="text-sm text-muted-foreground tabular-nums">
					{activeCount}
					{$i18n.t('active')}
					{#if inactiveCount}· {inactiveCount} {$i18n.t('inactive')}{/if}
				</p>
			{/if}
		</div>

		<div class="flex w-full items-center gap-2 sm:w-auto">
			<div class="relative min-w-0 flex-1 sm:w-56 sm:flex-none">
				<Search
					class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
				/>
				<Input
					type="search"
					class="h-8 pl-8"
					bind:value={query}
					aria-label={$i18n.t('Search')}
					placeholder={$i18n.t('Search companies...')}
				/>
			</div>

			<ToggleGroup.Root
				type="single"
				variant="outline"
				size="sm"
				value={view}
				onValueChange={(v) => setView(v)}
				aria-label={$i18n.t('View')}
			>
				<ToggleGroup.Item value="grid" aria-label={$i18n.t('Cards')} title={$i18n.t('Cards')}>
					<LayoutGrid />
				</ToggleGroup.Item>
				<ToggleGroup.Item value="list" aria-label={$i18n.t('List')} title={$i18n.t('List')}>
					<List />
				</ToggleGroup.Item>
			</ToggleGroup.Root>

			<!-- Add Company (accounting admins) -->
			{#if canCreateCompany}
				<Button size="sm" onclick={handleAddCompany}>
					<Plus />{$i18n.t('Add Company')}
				</Button>
			{/if}
		</div>
	</div>

	{#if loading && view === 'list'}
		<div class="flex flex-col gap-px overflow-hidden rounded-md border" aria-busy="true">
			{#each Array(8) as _}<Skeleton class="h-12 rounded-none" />{/each}
		</div>
	{:else if loading}
		<div
			class="grid grid-cols-[repeat(auto-fill,minmax(min(15rem,100%),1fr))] gap-4"
			aria-busy="true"
		>
			{#each Array(6) as _}<Skeleton class="h-[7.5rem] rounded-xl" />{/each}
		</div>
	{:else if loadError}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t("Couldn't load companies.")}</Alert.Title>
			<Alert.Description>
				<p>{loadError}</p>
				<Button variant="outline" size="sm" class="mt-2" onclick={loadCompanies}>
					<RotateCw />{$i18n.t('Retry')}
				</Button>
			</Alert.Description>
		</Alert.Root>
	{:else if filteredCompanies.length === 0}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><Building /></Empty.Media>
				{#if query}
					<Empty.Title>{$i18n.t('No companies match your search')}</Empty.Title>
				{:else}
					<Empty.Title>{$i18n.t('No companies yet')}</Empty.Title>
					<Empty.Description
						>{$i18n.t('Create your first company to get started')}</Empty.Description
					>
				{/if}
			</Empty.Header>
			{#if query}
				<Empty.Content>
					<Button variant="outline" size="sm" onclick={() => (query = '')}>
						{$i18n.t('Clear search')}
					</Button>
				</Empty.Content>
			{:else if canCreateCompany}
				<Empty.Content>
					<Button size="sm" onclick={handleAddCompany}>
						<Plus />{$i18n.t('Add Company')}
					</Button>
				</Empty.Content>
			{/if}
		</Empty.Root>
	{:else if view === 'list'}
		<div class="overflow-hidden rounded-md border">
			<Table.Root>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						<Table.Head>{$i18n.t('Company')}</Table.Head>
						<Table.Head class="hidden md:table-cell">{$i18n.t('Country')}</Table.Head>
						<Table.Head>{$i18n.t('Currency')}</Table.Head>
						<Table.Head class="hidden lg:table-cell">{$i18n.t('Year end')}</Table.Head>
						<Table.Head class="hidden xl:table-cell">{$i18n.t('Chart of Accounts')}</Table.Head>
						<Table.Head class="w-12"><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each filteredCompanies as company (company.id)}
						<Table.Row class="cursor-pointer" onclick={(e) => openFromRow(e, company)}>
							<Table.Cell class="max-w-0 w-full py-1.5">
								<div class="flex min-w-0 items-center gap-3">
									<CompanyLogo {company} size="sm" />
									<div class="flex min-w-0 flex-col">
										<div class="flex min-w-0 items-center gap-2">
											<a
												href={companyHref(company)}
												title={company.name}
												class="truncate font-medium outline-none hover:underline focus-visible:underline"
												>{company.name}</a
											>
											{#if !company.is_active}
												<Badge variant="secondary">{$i18n.t('Inactive')}</Badge>
											{/if}
										</div>
										{#if company.description}
											<span
												class="truncate text-xs text-muted-foreground"
												title={company.description}>{company.description}</span
											>
										{/if}
									</div>
								</div>
							</Table.Cell>
							<Table.Cell class="hidden text-muted-foreground md:table-cell"
								>{company.country || '—'}</Table.Cell
							>
							<Table.Cell class="font-mono text-xs">{company.currency}</Table.Cell>
							<Table.Cell class="hidden text-muted-foreground tabular-nums lg:table-cell"
								>{fiscalYearEnd(company)}</Table.Cell
							>
							<Table.Cell
								class="hidden max-w-[16rem] truncate text-muted-foreground xl:table-cell"
								title={company.chart_template_name ?? ''}
								>{company.chart_template_name || '—'}</Table.Cell
							>
							<Table.Cell class="py-1.5 text-right">{@render companyMenu(company)}</Table.Cell>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</div>
	{:else}
		<div class="grid grid-cols-[repeat(auto-fill,minmax(min(15rem,100%),1fr))] gap-4">
			{#each filteredCompanies as company (company.id)}
				<!-- The name is the link; it stretches over the card so the whole card opens it. -->
				<Card.Root
					size="sm"
					class="relative transition-colors hover:bg-accent/40 has-[a:focus-visible]:ring-[3px] has-[a:focus-visible]:ring-ring/50"
				>
					<Card.Header
						class="gap-x-3 has-data-[slot=card-action]:grid-cols-[auto_minmax(0,1fr)_auto]"
					>
						<CompanyLogo {company} class="row-span-2 self-center" />
						<Card.Title class="col-start-2 min-w-0 truncate leading-5">
							<a
								href={companyHref(company)}
								title={company.name}
								class="outline-none after:absolute after:inset-0 after:rounded-xl after:content-['']"
								>{company.name}</a
							>
						</Card.Title>
						<Card.Description
							class="col-span-2 col-start-2 truncate tabular-nums"
							title={companyMeta(company)}>{companyMeta(company)}</Card.Description
						>
						<!-- one row high, so the description below can use the full width -->
						<Card.Action class="relative z-10 col-start-3 row-span-1 -my-1">
							{@render companyMenu(company)}
						</Card.Action>
					</Card.Header>
					{#if company.description || company.chart_template_name || company.period_template_name || !company.is_active}
						<Card.Content class="flex flex-col gap-2">
							{#if company.description}
								<p class="truncate text-muted-foreground" title={company.description}>
									{company.description}
								</p>
							{/if}
							{#if company.chart_template_name || company.period_template_name || !company.is_active}
								<div class="flex flex-wrap gap-1.5">
									{#if company.chart_template_name}
										<Badge
											variant="outline"
											class="max-w-full truncate"
											title={$i18n.t('Chart of Accounts Template')}
											>{company.chart_template_name}</Badge
										>
									{/if}
									{#if company.period_template_name}
										<Badge
											variant="outline"
											class="max-w-full truncate"
											title={$i18n.t('Accounting Period Template')}
											>{company.period_template_name}</Badge
										>
									{/if}
									{#if !company.is_active}
										<Badge variant="secondary">{$i18n.t('Inactive')}</Badge>
									{/if}
								</div>
							{/if}
						</Card.Content>
					{/if}
				</Card.Root>
			{/each}
		</div>
	{/if}
</div>

<!-- Duplicate Company -->
<Dialog.Root bind:open={showDuplicateModal}>
	<Dialog.Content class="sm:max-w-lg">
		<form class="contents" on:submit|preventDefault={confirmDuplicate}>
			<Dialog.Header>
				<Dialog.Title>{$i18n.t('Duplicate Company')}</Dialog.Title>
				<Dialog.Description>
					{$i18n.t('This will copy the chart of accounts and period configuration from')}
					<span class="font-medium text-foreground">{duplicatingCompany?.name}</span
					>{duplicatingCompany?.name?.endsWith('.') ? '' : '.'}
				</Dialog.Description>
			</Dialog.Header>

			<div class="flex flex-col gap-2">
				<Label for="duplicate-name">{$i18n.t('New Company Name')}</Label>
				<Input
					id="duplicate-name"
					type="text"
					bind:value={duplicateName}
					placeholder={$i18n.t('Enter company name')}
					required
				/>
			</div>

			<Dialog.Footer>
				<Button type="button" variant="outline" onclick={() => (showDuplicateModal = false)}>
					{$i18n.t('Cancel')}
				</Button>
				<Button type="submit" disabled={duplicating}>
					{#if duplicating}<Spinner />{$i18n.t('Duplicating...')}{:else}{$i18n.t('Duplicate')}{/if}
				</Button>
			</Dialog.Footer>
		</form>
	</Dialog.Content>
</Dialog.Root>

<!-- Deactivate Company -->
<ConfirmDialog
	bind:open={showDeactivateConfirm}
	title={$i18n.t('Deactivate Company')}
	description={deactivatingCompany
		? `${$i18n.t('Are you sure you want to deactivate')} ${deactivatingCompany.name}? ${$i18n.t('This company will no longer appear in active views.')}`
		: ''}
	confirmLabel={$i18n.t('Deactivate')}
	destructive
	onconfirm={confirmDeactivate}
	oncancel={() => (deactivatingCompany = null)}
/>
