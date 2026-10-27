<script lang="ts">
	import { onMount, onDestroy, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import {
		getExpenseSheets,
		getEmployees,
		generateExpenseSheet,
		createExpenseSheet,
		getExpenseSheetCandidates,
		getPendingReimbursableInvoices,
		downloadExpenseSheetsPdf
	} from '$lib/apis/accounting';
	import dayjs from 'dayjs';

	import Plus from '@lucide/svelte/icons/plus';
	import FileDown from '@lucide/svelte/icons/file-down';
	import Search from '@lucide/svelte/icons/search';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';
	import FileSpreadsheet from '@lucide/svelte/icons/file-spreadsheet';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import TablePagination from '$lib/components/gnos3-ui/TablePagination.svelte';
	import ExpenseSheetStatusBadge from './ExpenseSheetStatusBadge.svelte';

	const i18n: any = getContext('i18n');
	export let companyId: number;

	let sheets: any[] = [];
	let employees: any[] = [];
	let pendingGroups: any[] = [];
	let pendingTotal = 0;
	let loading = true;
	let loadError = '';
	let showGenerate = false;
	let generating = false;
	let exporting = false;

	let statusFilter = '';
	let employeeFilter: number | '' = '';
	let dateFrom = '';
	let dateTo = '';
	let search = '';

	// This month, in local dates (toISOString() is UTC: a day off east of UTC).
	const defaultPeriod = () => ({
		start: dayjs().startOf('month').format('YYYY-MM-DD'),
		end: dayjs().endOf('month').format('YYYY-MM-DD')
	});

	let genForm = (() => {
		const p = defaultPeriod();
		return {
			employee_id: 0,
			period_start: p.start,
			period_end: p.end,
			title: '',
			include_uncategorized: true,
			// Start empty: create the sheet now and attach receipts afterwards,
			// instead of auto-pulling every eligible invoice in the period.
			start_empty: false
		};
	})();
	let candidatePreview: { total: number } | null = null;

	// Filters can change faster than the server answers: only the latest
	// request is applied.
	let loadSeq = 0;
	const load = async () => {
		const seq = ++loadSeq;
		loading = true;
		loadError = '';
		try {
			const [sheetData, empData, pendingData] = await Promise.all([
				getExpenseSheets(companyId, {
					status: statusFilter || undefined,
					employee_id: typeof employeeFilter === 'number' ? employeeFilter : undefined,
					date_from: dateFrom || undefined,
					date_to: dateTo || undefined,
					search: search || undefined
				}),
				getEmployees(companyId, { active: true }),
				getPendingReimbursableInvoices(companyId)
			]);
			if (seq !== loadSeq) return;
			sheets = sheetData?.sheets ?? [];
			employees = empData?.employees ?? [];
			pendingGroups = pendingData?.groups ?? [];
			pendingTotal = pendingData?.total_invoices ?? 0;
		} catch (err: any) {
			if (seq !== loadSeq) return;
			loadError = err?.detail ?? `${err}`;
			toast.error(loadError);
		}
		loading = false;
	};

	// Search as you type, once the typing pauses.
	let searchTimer: ReturnType<typeof setTimeout> | undefined;
	const searchLater = () => {
		clearTimeout(searchTimer);
		searchTimer = setTimeout(load, 300);
	};
	onDestroy(() => clearTimeout(searchTimer));

	const openSheet = (id: number) => goto(`/accounting/company/${companyId}/expenses/${id}`);
	const valueOf = (e: Event) => (e.currentTarget as HTMLInputElement).value;

	const generateForEmployee = async (group: any) => {
		const periodStart = group.earliest_date ?? defaultPeriod().start;
		const periodEnd = group.latest_date ?? defaultPeriod().end;
		generating = true;
		try {
			const sheet = await generateExpenseSheet(companyId, {
				employee_id: group.employee_id,
				period_start: periodStart,
				period_end: periodEnd,
				include_uncategorized: true
			});
			toast.success($i18n.t('Expense sheet created'));
			goto(`/accounting/company/${companyId}/expenses/${sheet.id}`);
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		generating = false;
	};

	const exportPdf = async () => {
		if (exporting) return;
		exporting = true;
		try {
			await downloadExpenseSheetsPdf(companyId, {
				status: statusFilter || undefined,
				employee_id: typeof employeeFilter === 'number' ? employeeFilter : undefined,
				date_from: dateFrom || undefined,
				date_to: dateTo || undefined,
				search: search || undefined
			});
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		exporting = false;
	};

	onMount(load);

	const openGenerate = () => {
		showGenerate = true;
		candidatePreview = null;
		if (employees.length && !genForm.employee_id) {
			genForm.employee_id = employees[0].id;
		}
	};

	const previewCandidates = async () => {
		if (!genForm.employee_id) {
			toast.error($i18n.t('Pick an employee first'));
			return;
		}
		try {
			candidatePreview = await getExpenseSheetCandidates(companyId, {
				employee_id: genForm.employee_id,
				period_start: genForm.period_start,
				period_end: genForm.period_end
			});
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const handleGenerate = async () => {
		if (!genForm.employee_id) {
			toast.error($i18n.t('Pick an employee'));
			return;
		}
		generating = true;
		try {
			// Two different endpoints: /generate auto-populates from the period,
			// while the plain create with auto_populate:false leaves it empty.
			const sheet = genForm.start_empty
				? await createExpenseSheet(companyId, {
						employee_id: genForm.employee_id,
						period_start: genForm.period_start,
						period_end: genForm.period_end,
						title: genForm.title || undefined,
						auto_populate: false
					})
				: await generateExpenseSheet(companyId, {
						employee_id: genForm.employee_id,
						period_start: genForm.period_start,
						period_end: genForm.period_end,
						title: genForm.title || undefined,
						include_uncategorized: genForm.include_uncategorized
					});
			toast.success($i18n.t('Expense sheet created'));
			showGenerate = false;
			goto(`/accounting/company/${companyId}/expenses/${sheet.id}`);
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		generating = false;
	};

	const money = (amount: any, currency: string) => {
		if (amount == null) return '';
		const n = typeof amount === 'number' ? amount : parseFloat(amount);
		if (!isFinite(n)) return '';
		try {
			return new Intl.NumberFormat(undefined, {
				style: 'currency',
				currency: currency || 'USD'
			}).format(n);
		} catch {
			return `${currency} ${n.toFixed(2)}`;
		}
	};
</script>

<div class="flex flex-col gap-4">
	<!-- Header with the primary action -->
	<div class="flex flex-wrap items-start justify-between gap-3">
		<div class="min-w-0">
			<h2 class="text-lg font-semibold">{$i18n.t('Expense Sheets')}</h2>
			<p class="text-sm text-muted-foreground">
				{$i18n.t(
					'Employee expense reports. Generate a sheet, submit for approval, then mark as paid.'
				)}
			</p>
		</div>
		<div class="flex items-center gap-2">
			<Button
				variant="outline"
				size="sm"
				disabled={exporting || loading || sheets.length === 0}
				title={$i18n.t('Export the sheets matching the current filters as a PDF')}
				onclick={exportPdf}
			>
				{#if exporting}<Spinner />{:else}<FileDown />{/if}
				{exporting ? $i18n.t('Exporting...') : $i18n.t('Export PDF')}
			</Button>
			<Button size="sm" onclick={openGenerate}>
				<Plus />{$i18n.t('New Sheet')}
			</Button>
		</div>
	</div>

	<!-- Pending receipts -->
	{#if pendingTotal > 0}
		<Alert.Root variant="warning">
			<TriangleAlert />
			<Alert.Title>
				{pendingTotal}
				{$i18n.t('reimbursable receipt(s) waiting to be sheeted')}
			</Alert.Title>
			<Alert.Description>
				<p>
					{$i18n.t('These have an employee assigned but are not on any active expense sheet yet.')}
				</p>
				<ul class="mt-2 grid w-full gap-2 sm:grid-cols-2 xl:grid-cols-3">
					{#each pendingGroups as g}
						<li class="flex items-center justify-between gap-3 rounded-md border bg-card px-3 py-2">
							<div class="min-w-0">
								<div class="truncate text-sm font-medium text-foreground">
									{g.employee_name}
									<span class="font-normal text-muted-foreground">({g.employee_code})</span>
								</div>
								<div class="text-[13px] text-muted-foreground tabular-nums">
									{g.count}
									{$i18n.t('receipts')} · {money(g.total, g.currency || 'USD')}
									{#if g.earliest_date && g.latest_date}
										· {g.earliest_date} → {g.latest_date}
									{/if}
								</div>
							</div>
							<Button
								variant="outline"
								size="xs"
								disabled={generating}
								onclick={() => generateForEmployee(g)}
							>
								{$i18n.t('Generate', { context: 'gnos3' })}
							</Button>
						</li>
					{/each}
				</ul>
			</Alert.Description>
		</Alert.Root>
	{/if}

	<!-- Toolbar: search and filters -->
	<div class="flex flex-wrap items-center gap-2">
		<div class="relative w-full sm:w-56">
			<Search
				class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
			/>
			<Input
				type="search"
				class="h-8 pl-8"
				aria-label={$i18n.t('Search')}
				placeholder="ES-2026-0001"
				value={search}
				oninput={(e) => {
					search = valueOf(e);
					searchLater();
				}}
			/>
		</div>
		<NativeSelect.Root
			size="sm"
			aria-label={$i18n.t('Status')}
			value={statusFilter}
			onchange={(e: Event) => {
				statusFilter = valueOf(e);
				load();
			}}
		>
			<NativeSelect.Option value="">{$i18n.t('Any status')}</NativeSelect.Option>
			<NativeSelect.Option value="draft">{$i18n.t('Draft')}</NativeSelect.Option>
			<NativeSelect.Option value="submitted">{$i18n.t('Submitted')}</NativeSelect.Option>
			<NativeSelect.Option value="approved">{$i18n.t('Approved')}</NativeSelect.Option>
			<NativeSelect.Option value="paid">{$i18n.t('Paid')}</NativeSelect.Option>
			<NativeSelect.Option value="rejected">{$i18n.t('Rejected')}</NativeSelect.Option>
		</NativeSelect.Root>
		<NativeSelect.Root
			size="sm"
			class="max-w-56"
			aria-label={$i18n.t('Employee')}
			value={String(employeeFilter)}
			onchange={(e: Event) => {
				const v = valueOf(e);
				employeeFilter = v === '' ? '' : Number(v);
				load();
			}}
		>
			<NativeSelect.Option value="">{$i18n.t('All employees')}</NativeSelect.Option>
			{#each employees as emp}
				<NativeSelect.Option value={String(emp.id)}>{emp.full_name}</NativeSelect.Option>
			{/each}
		</NativeSelect.Root>
		<div class="flex items-center gap-1.5">
			<Label for="es-filter-from" class="font-normal text-muted-foreground">{$i18n.t('From')}</Label
			>
			<Input
				id="es-filter-from"
				type="date"
				class="h-8 w-auto"
				value={dateFrom}
				onchange={(e) => {
					dateFrom = valueOf(e);
					load();
				}}
			/>
		</div>
		<div class="flex items-center gap-1.5">
			<Label for="es-filter-to" class="font-normal text-muted-foreground">{$i18n.t('To')}</Label>
			<Input
				id="es-filter-to"
				type="date"
				class="h-8 w-auto"
				value={dateTo}
				onchange={(e) => {
					dateTo = valueOf(e);
					load();
				}}
			/>
		</div>
	</div>

	{#if loadError && !loading}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Could not load the expense sheets.')}</Alert.Title>
			<Alert.Description>
				<p>{loadError}</p>
				<Button variant="outline" size="sm" class="mt-2" onclick={load}>
					<RefreshCw />{$i18n.t('Retry')}
				</Button>
			</Alert.Description>
		</Alert.Root>
	{:else if loading && sheets.length === 0}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(5) as _}<Skeleton class="h-8 w-full" />{/each}
		</div>
	{:else if sheets.length === 0}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><FileSpreadsheet /></Empty.Media>
				<Empty.Title>{$i18n.t('No expense sheets yet. Click New Sheet to create one.')}</Empty.Title
				>
			</Empty.Header>
			<Empty.Content>
				<Button size="sm" onclick={openGenerate}><Plus />{$i18n.t('New Sheet')}</Button>
			</Empty.Content>
		</Empty.Root>
	{:else}
		<div class="overflow-hidden rounded-md border">
			<Table.Root>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						<Table.Head>{$i18n.t('Reference')}</Table.Head>
						<Table.Head>{$i18n.t('Employee')}</Table.Head>
						<Table.Head>{$i18n.t('Period')}</Table.Head>
						<Table.Head class="text-right">{$i18n.t('Total')}</Table.Head>
						<Table.Head class="text-right">{$i18n.t('Lines')}</Table.Head>
						<Table.Head>{$i18n.t('Status')}</Table.Head>
						<Table.Head>{$i18n.t('Created')}</Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each sheets as s}
						<Table.Row
							class="cursor-pointer"
							tabindex={0}
							onclick={() => openSheet(s.id)}
							onkeydown={(e: KeyboardEvent) => {
								if (e.key === 'Enter') openSheet(s.id);
							}}
						>
							<Table.Cell class="font-mono text-[13px]">{s.reference}</Table.Cell>
							<Table.Cell>
								{s.employee_name ?? `#${s.employee_id}`}
								{#if s.employee_code}
									<span class="ml-1 text-muted-foreground">({s.employee_code})</span>
								{/if}
							</Table.Cell>
							<Table.Cell class="text-muted-foreground tabular-nums">
								{s.period_start} → {s.period_end}
							</Table.Cell>
							<Table.Cell class="text-right font-medium tabular-nums"
								>{money(s.total_amount, s.currency) || '—'}</Table.Cell
							>
							<Table.Cell class="text-right tabular-nums">{s.line_count}</Table.Cell>
							<Table.Cell>
								<ExpenseSheetStatusBadge status={s.status} />
							</Table.Cell>
							<Table.Cell class="text-muted-foreground tabular-nums"
								>{s.created_at ? dayjs(s.created_at).format('YYYY-MM-DD') : '—'}</Table.Cell
							>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</div>
		<TablePagination page={1} count={sheets.length} perPage={Math.max(1, sheets.length)} />
	{/if}
</div>

<!-- New sheet -->
<Dialog.Root bind:open={showGenerate}>
	<Dialog.Content class="sm:max-w-lg">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Generate Sheet')}</Dialog.Title>
			<Dialog.Description
				>{$i18n.t('Create a sheet for one employee and period.')}</Dialog.Description
			>
		</Dialog.Header>

		<div class="grid gap-4">
			<div class="grid gap-1.5">
				<Label for="es-gen-employee">{$i18n.t('Employee')}</Label>
				<NativeSelect.Root
					id="es-gen-employee"
					class="w-full"
					value={String(genForm.employee_id)}
					onchange={(e: Event) => {
						genForm.employee_id = Number(valueOf(e));
						candidatePreview = null;
					}}
				>
					<NativeSelect.Option value="0">{$i18n.t('Select...')}</NativeSelect.Option>
					{#each employees as emp}
						<NativeSelect.Option value={String(emp.id)}>{emp.full_name}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
			</div>
			<div class="grid grid-cols-2 gap-3">
				<div class="grid gap-1.5">
					<Label for="es-gen-from">{$i18n.t('From')}</Label>
					<Input
						id="es-gen-from"
						type="date"
						value={genForm.period_start}
						onchange={(e) => {
							genForm.period_start = valueOf(e);
							candidatePreview = null;
						}}
					/>
				</div>
				<div class="grid gap-1.5">
					<Label for="es-gen-to">{$i18n.t('To')}</Label>
					<Input
						id="es-gen-to"
						type="date"
						value={genForm.period_end}
						onchange={(e) => {
							genForm.period_end = valueOf(e);
							candidatePreview = null;
						}}
					/>
				</div>
			</div>
			<div class="grid gap-1.5">
				<Label for="es-gen-title">{$i18n.t('Title (optional)')}</Label>
				<Input id="es-gen-title" bind:value={genForm.title} />
			</div>
			<div class="grid gap-3">
				<div class="flex items-center gap-2">
					<Checkbox
						id="es-gen-uncat"
						checked={genForm.include_uncategorized}
						disabled={genForm.start_empty}
						onCheckedChange={(v) => (genForm.include_uncategorized = v === true)}
					/>
					<Label for="es-gen-uncat" class="font-normal {genForm.start_empty ? 'opacity-50' : ''}">
						{$i18n.t('Include uncategorized invoices')}
					</Label>
				</div>
				<div class="flex items-center gap-2">
					<Checkbox
						id="es-gen-empty"
						checked={genForm.start_empty}
						onCheckedChange={(v) => {
							genForm.start_empty = v === true;
							candidatePreview = null;
						}}
					/>
					<Label for="es-gen-empty" class="font-normal">
						{$i18n.t('Start empty — add receipts after creating the sheet')}
					</Label>
				</div>
			</div>
			{#if !genForm.start_empty}
				<div class="flex flex-wrap items-center gap-3">
					<Button variant="outline" size="sm" onclick={previewCandidates}>
						{$i18n.t('Preview Candidates')}
					</Button>
					{#if candidatePreview}
						<span class="text-sm text-muted-foreground tabular-nums">
							{candidatePreview.total}
							{$i18n.t('invoice(s) will be included')}
						</span>
					{/if}
				</div>
			{/if}
		</div>

		<Dialog.Footer>
			<Button variant="outline" onclick={() => (showGenerate = false)}>{$i18n.t('Cancel')}</Button>
			<Button disabled={generating} onclick={handleGenerate}>
				{#if generating}<Spinner />{/if}
				{generating
					? $i18n.t('Generating...')
					: genForm.start_empty
						? $i18n.t('Create empty sheet')
						: $i18n.t('Generate', { context: 'gnos3' })}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
