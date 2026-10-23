<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { uiLocale } from '$lib/utils/uiLocale';
	import { toast } from 'svelte-sonner';
	import { page } from '$app/stores';
	import { replaceState } from '$app/navigation';

	import Plus from '@lucide/svelte/icons/plus';
	import Upload from '@lucide/svelte/icons/upload';
	import Download from '@lucide/svelte/icons/download';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import X from '@lucide/svelte/icons/x';
	import BookOpen from '@lucide/svelte/icons/book-open';
	import CalendarRange from '@lucide/svelte/icons/calendar-range';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';

	import {
		getChartTemplates,
		getPeriodTemplates,
		createPeriodTemplate,
		deleteChartTemplate,
		deletePeriodTemplate,
		downloadChartImportTemplate,
		downloadPeriodImportTemplate
	} from '$lib/apis/accounting';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Tabs from '$lib/components/ui/tabs/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';
	import ExcelImportModal from '$lib/components/accounting/ExcelImportModal.svelte';
	import CountryConfigManager from '$lib/components/accounting/CountryConfigManager.svelte';
	import GlobalExchangeRates from '$lib/components/accounting/GlobalExchangeRates.svelte';

	const i18n: any = getContext('i18n');

	// Tab state (kept in ?tab= so a section can be linked to)
	type Tab = 'chart' | 'period' | 'countries' | 'rates';
	const TABS: Tab[] = ['chart', 'period', 'countries', 'rates'];
	let activeTab: Tab = 'chart';

	const setTab = (value: string) => {
		if (!TABS.includes(value as Tab)) return;
		activeTab = value as Tab;
		try {
			const url = new URL($page.url);
			if (activeTab === 'chart') url.searchParams.delete('tab');
			else url.searchParams.set('tab', activeTab);
			replaceState(url, $page.state);
		} catch {}
	};

	// Data
	let chartTemplates: any[] = [];
	let periodTemplates: any[] = [];
	let loadingCharts = true;
	let loadingPeriods = true;
	let chartError = '';
	let periodError = '';

	// Expanded template (by id)
	let expandedChartId: number | null = null;
	let expandedPeriodId: number | null = null;

	// Collapsed type sections within expanded template
	let collapsedTypes: Set<string> = new Set();
	const toggleTypeSection = (type: string) => {
		if (collapsedTypes.has(type)) collapsedTypes.delete(type);
		else collapsedTypes.add(type);
		collapsedTypes = collapsedTypes;
	};

	const ACCOUNT_TYPES = [
		{ key: 'asset', label: 'Assets' },
		{ key: 'liability', label: 'Liabilities' },
		{ key: 'equity', label: 'Equity' },
		{ key: 'revenue', label: 'Revenue' },
		{ key: 'expense', label: 'Expenses' }
	];

	const groupTemplateAccounts = (accounts: any[]) => {
		return ACCOUNT_TYPES.map((type) => ({
			...type,
			accounts: accounts
				.filter((a: any) => (a.account_type ?? a.type ?? '').toLowerCase() === type.key)
				.sort((a: any, b: any) => (a.code ?? '').localeCompare(b.code ?? ''))
		})).filter((g) => g.accounts.length > 0);
	};

	const getIndentLevel = (acct: any): number => {
		if (acct.parent_code) return acct.parent_code.split('.').length;
		const dots = (acct.code ?? '').split('.').length - 1;
		return dots;
	};

	// Create chart template dialog
	let showCreateForm = false;
	let newTemplateName = '';
	let newTemplateCountry = '';
	let creatingTemplate = false;

	// Period template create dialog
	let showPeriodCreateForm = false;
	let newPeriodTemplateName = '';
	let newPeriodTemplateDesc = '';
	let periodEntries: Array<{ name: string; start_date: string; end_date: string }> = [];
	let creatingPeriodTemplate = false;

	// Excel import modal
	let showImportModal = false;
	let importType: 'chart' | 'period' = 'chart';

	// Delete confirmation
	let showDeleteConfirm = false;
	let deleteTarget: { kind: 'chart' | 'period'; id: number; name: string } | null = null;

	const askDelete = (kind: 'chart' | 'period', template: any) => {
		deleteTarget = { kind, id: template.id, name: template.name ?? '' };
		showDeleteConfirm = true;
	};

	const confirmDelete = async () => {
		if (!deleteTarget) return;
		if (deleteTarget.kind === 'chart') await handleDeleteChart(deleteTarget.id);
		else await handleDeletePeriod(deleteTarget.id);
	};

	// ─── Chart Templates ───────────────────────────────────────────────────────

	const loadChartTemplates = async () => {
		loadingCharts = true;
		chartError = '';
		try {
			const res = await getChartTemplates();
			chartTemplates = Array.isArray(res) ? res : (res?.templates ?? []);
		} catch (err) {
			chartError = `${err}`;
			toast.error(`${$i18n.t('Failed to load chart templates')}: ${err}`);
		}
		loadingCharts = false;
	};

	const handleDeleteChart = async (id: number) => {
		try {
			await deleteChartTemplate(id);
			toast.success($i18n.t('Chart template deleted'));
			await loadChartTemplates();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to delete template') + ': ' + msg);
		}
	};

	const toggleChartExpand = (id: number) => {
		expandedChartId = expandedChartId === id ? null : id;
	};

	const resetChartForm = () => {
		showCreateForm = false;
		newTemplateName = '';
		newTemplateCountry = '';
	};

	// ─── Period Templates ──────────────────────────────────────────────────────

	const loadPeriodTemplates = async () => {
		loadingPeriods = true;
		periodError = '';
		try {
			const res = await getPeriodTemplates();
			periodTemplates = Array.isArray(res) ? res : (res?.templates ?? []);
		} catch (err) {
			periodError = `${err}`;
			toast.error(`${$i18n.t('Failed to load period templates')}: ${err}`);
		}
		loadingPeriods = false;
	};

	const handleDeletePeriod = async (id: number) => {
		try {
			await deletePeriodTemplate(id);
			toast.success($i18n.t('Period template deleted'));
			await loadPeriodTemplates();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to delete template') + ': ' + msg);
		}
	};

	const togglePeriodExpand = (id: number) => {
		expandedPeriodId = expandedPeriodId === id ? null : id;
	};

	// ─── Period Template Manual Create ────────────────────────────────────────

	const addPeriodEntry = () => {
		periodEntries = [...periodEntries, { name: '', start_date: '', end_date: '' }];
	};

	const removePeriodEntry = (index: number) => {
		periodEntries = periodEntries.filter((_, i) => i !== index);
	};

	const autoSuggestPeriodName = (index: number) => {
		const entry = periodEntries[index];
		if (entry.start_date && !entry.name) {
			const d = new Date(entry.start_date);
			const monthName = d.toLocaleString(uiLocale(), { month: 'long' });
			periodEntries[index].name = `${monthName} ${d.getFullYear()}`;
			periodEntries = [...periodEntries];
		}
	};

	const handleCreatePeriodTemplate = async () => {
		if (!newPeriodTemplateName.trim()) return;
		const validEntries = periodEntries.filter((e) => e.name && e.start_date && e.end_date);
		if (validEntries.length === 0) {
			toast.error($i18n.t('Add at least one period entry'));
			return;
		}

		creatingPeriodTemplate = true;
		try {
			await createPeriodTemplate({
				name: newPeriodTemplateName.trim(),
				description: newPeriodTemplateDesc.trim() || undefined,
				entries: validEntries.map((e, i) => ({
					name: e.name,
					start_date: e.start_date,
					end_date: e.end_date,
					sort_order: i
				}))
			});
			toast.success($i18n.t('Period template created'));
			showPeriodCreateForm = false;
			newPeriodTemplateName = '';
			newPeriodTemplateDesc = '';
			periodEntries = [];
			await loadPeriodTemplates();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to create template') + ': ' + msg);
		}
		creatingPeriodTemplate = false;
	};

	const resetPeriodForm = () => {
		showPeriodCreateForm = false;
		newPeriodTemplateName = '';
		newPeriodTemplateDesc = '';
		periodEntries = [];
	};

	const openPeriodCreate = () => {
		if (periodEntries.length === 0) addPeriodEntry();
		showPeriodCreateForm = true;
	};

	// ─── Import ────────────────────────────────────────────────────────────────

	const openImportModal = (type: 'chart' | 'period') => {
		importType = type;
		showImportModal = true;
	};

	const handleImported = () => {
		if (importType === 'chart') {
			loadChartTemplates();
		} else {
			loadPeriodTemplates();
		}
	};

	// ─── Lifecycle ─────────────────────────────────────────────────────────────

	onMount(async () => {
		const tab = $page.url.searchParams.get('tab');
		if (tab && TABS.includes(tab as Tab)) activeTab = tab as Tab;
		await Promise.all([loadChartTemplates(), loadPeriodTemplates()]);
	});
</script>

<ExcelImportModal bind:show={showImportModal} type={importType} on:imported={handleImported} />

<div class="flex flex-col gap-6">
	<div class="flex flex-col gap-1">
		<h1 class="text-2xl font-semibold tracking-tight">{$i18n.t('Accounting Settings')}</h1>
		<p class="text-sm text-muted-foreground">
			{$i18n.t('Templates, tax rules and exchange rates shared by every company.')}
		</p>
	</div>

	<Tabs.Root value={activeTab} onValueChange={setTab} class="flex-col gap-6">
		<Tabs.List class="h-9 max-w-full justify-start overflow-x-auto [scrollbar-width:none]">
			<Tabs.Trigger value="chart" class="flex-none px-2.5"
				>{$i18n.t('Chart Templates')}</Tabs.Trigger
			>
			<Tabs.Trigger value="period" class="flex-none px-2.5"
				>{$i18n.t('Period Templates')}</Tabs.Trigger
			>
			<Tabs.Trigger value="countries" class="flex-none px-2.5">{$i18n.t('Countries')}</Tabs.Trigger>
			<Tabs.Trigger value="rates" class="flex-none px-2.5">{$i18n.t('Exchange Rates')}</Tabs.Trigger
			>
		</Tabs.List>

		<!-- Chart Templates -->
		<Tabs.Content value="chart" class="flex flex-col gap-4">
			{#if activeTab === 'chart'}
				<div class="flex flex-wrap items-start justify-between gap-x-4 gap-y-3">
					<div class="min-w-0 max-w-2xl space-y-1">
						<h2 class="text-lg font-semibold">{$i18n.t('Chart Templates')}</h2>
						<p class="text-sm text-muted-foreground">
							{$i18n.t(
								'Charts of accounts a new company can start from. The company gets its own copy, so later edits never change the template.'
							)}
						</p>
					</div>
					<div class="flex flex-wrap items-center gap-2">
						<Button variant="ghost" size="sm" onclick={() => downloadChartImportTemplate()}>
							<Download />{$i18n.t('Download Template')}
						</Button>
						<Button variant="outline" size="sm" onclick={() => (showCreateForm = true)}>
							<Plus />{$i18n.t('Create Template')}
						</Button>
						<Button size="sm" onclick={() => openImportModal('chart')}>
							<Upload />{$i18n.t('Import from Excel')}
						</Button>
					</div>
				</div>

				{#if loadingCharts}
					<Card.Root class="gap-0 py-0">
						{#each Array(5) as _}
							<div class="flex items-center gap-3 border-b px-4 py-3.5 last:border-b-0">
								<Skeleton class="size-4" />
								<Skeleton class="h-4 w-56" />
								<Skeleton class="ml-auto h-4 w-20" />
							</div>
						{/each}
					</Card.Root>
				{:else if chartError}
					<Alert.Root variant="destructive">
						<CircleAlert />
						<Alert.Title>{$i18n.t('Failed to load chart templates')}</Alert.Title>
						<Alert.Description>
							<p>{chartError}</p>
							<Button variant="outline" size="sm" class="mt-2" onclick={loadChartTemplates}>
								<RotateCcw />{$i18n.t('Retry')}
							</Button>
						</Alert.Description>
					</Alert.Root>
				{:else if chartTemplates.length === 0}
					<Empty.Root class="border">
						<Empty.Header>
							<Empty.Media variant="icon"><BookOpen /></Empty.Media>
							<Empty.Title
								>{$i18n.t(
									'No chart templates found. Import one from Excel to get started.'
								)}</Empty.Title
							>
						</Empty.Header>
						<Empty.Content>
							<Button variant="outline" size="sm" onclick={() => openImportModal('chart')}>
								<Upload />{$i18n.t('Import from Excel')}
							</Button>
						</Empty.Content>
					</Empty.Root>
				{:else}
					<Card.Root class="gap-0 overflow-hidden py-0">
						{#each chartTemplates as template (template.id)}
							{@const open = expandedChartId === template.id}
							<div class="border-b last:border-b-0">
								<div class="flex items-center gap-1 pr-2 transition-colors hover:bg-muted/50">
									<button
										type="button"
										class="flex min-w-0 flex-1 items-center gap-3 rounded-md py-3 pl-4 text-left outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
										aria-expanded={open}
										onclick={() => toggleChartExpand(template.id)}
									>
										<ChevronRight
											class="size-4 shrink-0 text-muted-foreground transition-transform motion-reduce:transition-none {open
												? 'rotate-90'
												: ''}"
										/>
										<span class="flex min-w-0 flex-1 flex-wrap items-center gap-x-2 gap-y-1">
											<span class="truncate font-medium">{template.name}</span>
											{#if template.country}
												<span class="text-sm text-muted-foreground">{template.country}</span>
											{/if}
											{#if template.is_builtin}
												<Badge variant="secondary">{$i18n.t('Built-in')}</Badge>
											{/if}
										</span>
										<span class="shrink-0 pr-1 text-sm text-muted-foreground tabular-nums">
											{template.accounts?.length ?? template.account_count ?? 0}
											{$i18n.t('accounts')}
										</span>
									</button>
									{#if template.is_builtin}
										<span class="size-8 shrink-0" aria-hidden="true"></span>
									{:else}
										<Tip content={$i18n.t('Delete')}>
											<Button
												variant="ghost"
												size="icon-sm"
												class="text-muted-foreground hover:text-destructive"
												aria-label={$i18n.t('Delete')}
												onclick={() => askDelete('chart', template)}
											>
												<Trash2 />
											</Button>
										</Tip>
									{/if}
								</div>

								<!-- Expanded: the template's accounts, grouped by type -->
								{#if open}
									<div class="border-t bg-muted/30 px-4 py-3">
										{#if template.accounts?.length > 0}
											<div class="flex flex-col gap-3">
												{#each groupTemplateAccounts(template.accounts) as group}
													{@const groupKey = template.id + '-' + group.key}
													{@const groupOpen = !collapsedTypes.has(groupKey)}
													<div class="overflow-hidden rounded-md border bg-card">
														<button
															type="button"
															class="flex w-full items-center gap-2 px-3 py-2 text-left text-sm font-medium outline-none hover:bg-muted/50 focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:ring-inset"
															aria-expanded={groupOpen}
															onclick={() => toggleTypeSection(groupKey)}
														>
															<ChevronRight
																class="size-3.5 text-muted-foreground transition-transform motion-reduce:transition-none {groupOpen
																	? 'rotate-90'
																	: ''}"
															/>
															{$i18n.t(group.label)}
															<Badge variant="count">{group.accounts.length}</Badge>
														</button>
														{#if groupOpen}
															<div class="border-t">
																<Table.Root class="min-w-[34rem] table-fixed">
																	<colgroup>
																		<col class="w-28" />
																		<col />
																		<col class="w-24" />
																		<col class="w-28" />
																	</colgroup>
																	<Table.Header class="bg-muted/50">
																		<Table.Row class="hover:bg-transparent">
																			<Table.Head class="h-9">{$i18n.t('Code')}</Table.Head>
																			<Table.Head class="h-9">{$i18n.t('Name', { context: 'gnos3' })}</Table.Head>
																			<Table.Head class="h-9">{$i18n.t('Balance')}</Table.Head>
																			<Table.Head class="h-9">{$i18n.t('Parent')}</Table.Head>
																		</Table.Row>
																	</Table.Header>
																	<Table.Body>
																		{#each group.accounts as acct}
																			<Table.Row>
																				<Table.Cell class="py-1.5 font-mono text-[13px]"
																					>{acct.code}</Table.Cell
																				>
																				<Table.Cell
																					class="truncate py-1.5"
																					style="padding-left: {8 + getIndentLevel(acct) * 14}px"
																					title={acct.description
																						? `${acct.name} — ${acct.description}`
																						: acct.name}
																				>
																					{acct.name}
																					{#if acct.description}
																						<span class="ml-1 text-xs text-muted-foreground"
																							>— {acct.description}</span
																						>
																					{/if}
																				</Table.Cell>
																				<Table.Cell class="py-1.5 text-muted-foreground capitalize">
																					{acct.normal_balance ?? '—'}
																				</Table.Cell>
																				<Table.Cell
																					class="py-1.5 font-mono text-[13px] text-muted-foreground"
																				>
																					{acct.parent_code ?? '—'}
																				</Table.Cell>
																			</Table.Row>
																		{/each}
																	</Table.Body>
																</Table.Root>
															</div>
														{/if}
													</div>
												{/each}
											</div>
										{:else}
											<p class="text-sm text-muted-foreground">
												{$i18n.t('No accounts in this template.')}
											</p>
										{/if}
									</div>
								{/if}
							</div>
						{/each}
					</Card.Root>
				{/if}
			{/if}
		</Tabs.Content>

		<!-- Period Templates -->
		<Tabs.Content value="period" class="flex flex-col gap-4">
			{#if activeTab === 'period'}
				<div class="flex flex-wrap items-start justify-between gap-x-4 gap-y-3">
					<div class="min-w-0 max-w-2xl space-y-1">
						<h2 class="text-lg font-semibold">{$i18n.t('Period Templates')}</h2>
						<p class="text-sm text-muted-foreground">
							{$i18n.t(
								'Accounting period calendars a new company can start from, such as the twelve months of a fiscal year.'
							)}
						</p>
					</div>
					<div class="flex flex-wrap items-center gap-2">
						<Button variant="ghost" size="sm" onclick={() => downloadPeriodImportTemplate()}>
							<Download />{$i18n.t('Download Template')}
						</Button>
						<Button variant="outline" size="sm" onclick={() => openImportModal('period')}>
							<Upload />{$i18n.t('Import from Excel')}
						</Button>
						<Button size="sm" onclick={openPeriodCreate}>
							<Plus />{$i18n.t('Create Template')}
						</Button>
					</div>
				</div>

				{#if loadingPeriods}
					<Card.Root class="gap-0 py-0">
						{#each Array(4) as _}
							<div class="flex items-center gap-3 border-b px-4 py-3.5 last:border-b-0">
								<Skeleton class="size-4" />
								<Skeleton class="h-4 w-56" />
								<Skeleton class="ml-auto h-4 w-20" />
							</div>
						{/each}
					</Card.Root>
				{:else if periodError}
					<Alert.Root variant="destructive">
						<CircleAlert />
						<Alert.Title>{$i18n.t('Failed to load period templates')}</Alert.Title>
						<Alert.Description>
							<p>{periodError}</p>
							<Button variant="outline" size="sm" class="mt-2" onclick={loadPeriodTemplates}>
								<RotateCcw />{$i18n.t('Retry')}
							</Button>
						</Alert.Description>
					</Alert.Root>
				{:else if periodTemplates.length === 0}
					<Empty.Root class="border">
						<Empty.Header>
							<Empty.Media variant="icon"><CalendarRange /></Empty.Media>
							<Empty.Title
								>{$i18n.t(
									'No period templates found. Create one manually or import from Excel.'
								)}</Empty.Title
							>
						</Empty.Header>
						<Empty.Content>
							<Button variant="outline" size="sm" onclick={openPeriodCreate}>
								<Plus />{$i18n.t('Create Template')}
							</Button>
						</Empty.Content>
					</Empty.Root>
				{:else}
					<Card.Root class="gap-0 overflow-hidden py-0">
						{#each periodTemplates as template (template.id)}
							{@const open = expandedPeriodId === template.id}
							<div class="border-b last:border-b-0">
								<div class="flex items-center gap-1 pr-2 transition-colors hover:bg-muted/50">
									<button
										type="button"
										class="flex min-w-0 flex-1 items-center gap-3 rounded-md py-3 pl-4 text-left outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
										aria-expanded={open}
										onclick={() => togglePeriodExpand(template.id)}
									>
										<ChevronRight
											class="size-4 shrink-0 text-muted-foreground transition-transform motion-reduce:transition-none {open
												? 'rotate-90'
												: ''}"
										/>
										<span class="min-w-0 flex-1 truncate font-medium">{template.name}</span>
										<span class="shrink-0 pr-1 text-sm text-muted-foreground tabular-nums">
											{template.entries?.length ?? template.entry_count ?? 0}
											{$i18n.t('entries')}
										</span>
									</button>
									<Tip content={$i18n.t('Delete')}>
										<Button
											variant="ghost"
											size="icon-sm"
											class="text-muted-foreground hover:text-destructive"
											aria-label={$i18n.t('Delete')}
											onclick={() => askDelete('period', template)}
										>
											<Trash2 />
										</Button>
									</Tip>
								</div>

								{#if open}
									<div class="border-t bg-muted/30 px-4 py-3">
										{#if template.entries?.length > 0}
											<div class="overflow-hidden rounded-md border bg-card">
												<Table.Root>
													<Table.Header class="bg-muted/50">
														<Table.Row class="hover:bg-transparent">
															<Table.Head class="h-9">{$i18n.t('Name', { context: 'gnos3' })}</Table.Head>
															<Table.Head class="h-9 w-36">{$i18n.t('Start Date')}</Table.Head>
															<Table.Head class="h-9 w-36">{$i18n.t('End Date')}</Table.Head>
														</Table.Row>
													</Table.Header>
													<Table.Body>
														{#each template.entries as entry}
															<Table.Row>
																<Table.Cell class="py-1.5">{entry.name}</Table.Cell>
																<Table.Cell class="py-1.5 tabular-nums"
																	>{entry.start_date}</Table.Cell
																>
																<Table.Cell class="py-1.5 tabular-nums">{entry.end_date}</Table.Cell
																>
															</Table.Row>
														{/each}
													</Table.Body>
												</Table.Root>
											</div>
										{:else}
											<p class="text-sm text-muted-foreground">
												{$i18n.t('No entries in this template.')}
											</p>
										{/if}
									</div>
								{/if}
							</div>
						{/each}
					</Card.Root>
				{/if}
			{/if}
		</Tabs.Content>

		<!-- Countries -->
		<Tabs.Content value="countries">
			{#if activeTab === 'countries'}
				<CountryConfigManager />
			{/if}
		</Tabs.Content>

		<!-- Exchange Rates -->
		<Tabs.Content value="rates">
			{#if activeTab === 'rates'}
				<GlobalExchangeRates />
			{/if}
		</Tabs.Content>
	</Tabs.Root>
</div>

<!-- Create chart template: the accounts come from an Excel file -->
<Dialog.Root bind:open={showCreateForm}>
	<Dialog.Content class="sm:max-w-lg">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Create New Chart Template')}</Dialog.Title>
			<Dialog.Description>
				{$i18n.t('Chart templates are imported from an Excel file.')}
			</Dialog.Description>
		</Dialog.Header>
		<div class="grid gap-4 sm:grid-cols-2">
			<div class="grid gap-2">
				<Label for="template-name">{$i18n.t('Name', { context: 'gnos3' })} *</Label>
				<Input
					id="template-name"
					bind:value={newTemplateName}
					placeholder={$i18n.t('e.g. French PCG')}
				/>
			</div>
			<div class="grid gap-2">
				<Label for="template-country">{$i18n.t('Country')}</Label>
				<Input
					id="template-country"
					bind:value={newTemplateCountry}
					placeholder={$i18n.t('e.g. FR')}
				/>
			</div>
		</div>
		<Dialog.Footer>
			<Button variant="outline" onclick={resetChartForm}>{$i18n.t('Cancel')}</Button>
			<Button
				disabled={!newTemplateName || creatingTemplate}
				onclick={() => {
					showCreateForm = false;
					openImportModal('chart');
				}}
			>
				<Upload />{$i18n.t('Import Excel')}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Create period template by hand -->
<Dialog.Root bind:open={showPeriodCreateForm}>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-3xl">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Create New Period Template')}</Dialog.Title>
			<Dialog.Description>
				{$i18n.t('Add one line per accounting period. Choosing a start date names an empty line.')}
			</Dialog.Description>
		</Dialog.Header>

		<div class="grid gap-4 sm:grid-cols-2">
			<div class="grid gap-2">
				<Label for="period-template-name">{$i18n.t('Template Name')} *</Label>
				<Input
					id="period-template-name"
					bind:value={newPeriodTemplateName}
					placeholder={$i18n.t('e.g. Calendar Year 2025 Monthly')}
				/>
			</div>
			<div class="grid gap-2">
				<Label for="period-template-desc">{$i18n.t('Description')}</Label>
				<Input
					id="period-template-desc"
					bind:value={newPeriodTemplateDesc}
					placeholder={$i18n.t('Optional description')}
				/>
			</div>
		</div>

		<div class="grid gap-2">
			<span class="text-sm font-medium">{$i18n.t('Period Entries')}</span>
			<div
				class="hidden grid-cols-[1fr_9.5rem_9.5rem_2rem] gap-2 text-sm text-muted-foreground sm:grid"
			>
				<span>{$i18n.t('Period name')}</span>
				<span>{$i18n.t('Start Date')}</span>
				<span>{$i18n.t('End Date')}</span>
			</div>
			{#each periodEntries as entry, idx}
				<div
					class="grid grid-cols-[1fr_1fr_2rem] items-center gap-2 border-b pb-2 last:border-b-0 sm:grid-cols-[1fr_9.5rem_9.5rem_2rem] sm:border-b-0 sm:pb-0"
				>
					<Input
						class="col-span-2 sm:col-span-1"
						bind:value={entry.name}
						placeholder={$i18n.t('Period name')}
						aria-label={$i18n.t('Period name')}
					/>
					<Input
						type="date"
						class="order-3 tabular-nums sm:order-none"
						bind:value={entry.start_date}
						onchange={() => autoSuggestPeriodName(idx)}
						aria-label={$i18n.t('Start Date')}
					/>
					<Input
						type="date"
						class="order-4 tabular-nums sm:order-none"
						bind:value={entry.end_date}
						aria-label={$i18n.t('End Date')}
					/>
					<Tip content={$i18n.t('Remove')}>
						<Button
							variant="ghost"
							size="icon-sm"
							aria-label={$i18n.t('Remove')}
							onclick={() => removePeriodEntry(idx)}
						>
							<X />
						</Button>
					</Tip>
				</div>
			{/each}
			<div>
				<Button variant="outline" size="sm" onclick={addPeriodEntry}>
					<Plus />{$i18n.t('Add Period')}
				</Button>
			</div>
		</div>

		<Dialog.Footer>
			<Button variant="outline" onclick={resetPeriodForm}>{$i18n.t('Cancel')}</Button>
			<Button
				disabled={!newPeriodTemplateName.trim() ||
					periodEntries.length === 0 ||
					creatingPeriodTemplate}
				onclick={handleCreatePeriodTemplate}
			>
				{#if creatingPeriodTemplate}<Spinner />{/if}
				{creatingPeriodTemplate ? $i18n.t('Creating...') : $i18n.t('Create Template')}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<ConfirmDialog
	bind:open={showDeleteConfirm}
	title={deleteTarget?.kind === 'period'
		? $i18n.t('Delete period template?')
		: $i18n.t('Delete chart template?')}
	description={$i18n.t('"{{name}}" will be removed. This cannot be undone.', {
		name: deleteTarget?.name ?? ''
	})}
	confirmLabel={$i18n.t('Delete')}
	destructive
	onconfirm={confirmDelete}
/>
