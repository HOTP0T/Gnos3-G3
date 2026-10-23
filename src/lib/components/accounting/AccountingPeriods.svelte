<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';

	import Plus from '@lucide/svelte/icons/plus';
	import Upload from '@lucide/svelte/icons/upload';
	import Download from '@lucide/svelte/icons/download';
	import FileSpreadsheet from '@lucide/svelte/icons/file-spreadsheet';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import Lock from '@lucide/svelte/icons/lock';
	import LockOpen from '@lucide/svelte/icons/lock-open';
	import CalendarRange from '@lucide/svelte/icons/calendar-range';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';

	import {
		getPeriods,
		createPeriod,
		closePeriod,
		reopenPeriod,
		downloadPeriodImportTemplate
	} from '$lib/apis/accounting';

	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';
	import ExcelImportModal from '$lib/components/accounting/ExcelImportModal.svelte';

	const i18n: any = getContext('i18n');

	export let companyId: number;

	let loading = true;
	let loadError = '';
	let periods: any[] = [];

	// Create form
	let showCreateForm = false;
	let newName = '';
	let newStartDate = '';
	let newEndDate = '';
	let creating = false;

	// Confirm dialogs
	let showCloseConfirm = false;
	let closeTarget: any = null;
	let showReopenConfirm = false;
	let reopenTarget: any = null;

	let showImportModal = false;

	const loadPeriods = async () => {
		loading = true;
		loadError = '';
		try {
			const res = await getPeriods({ company_id: companyId });
			periods = Array.isArray(res) ? res : (res?.items ?? []);
		} catch (err: any) {
			loadError = err?.detail ?? `${err}`;
		}
		loading = false;
	};

	const openCreateForm = () => {
		newName = '';
		newStartDate = '';
		newEndDate = '';
		showCreateForm = true;
	};

	const handleCreate = async (e?: Event) => {
		e?.preventDefault();
		if (!newName || !newStartDate || !newEndDate) {
			toast.error($i18n.t('Please fill in all fields'));
			return;
		}
		if (newEndDate < newStartDate) {
			toast.error($i18n.t('End date must be after start date'));
			return;
		}

		creating = true;
		try {
			await createPeriod(
				{
					name: newName,
					start_date: newStartDate,
					end_date: newEndDate
				},
				companyId
			);
			toast.success($i18n.t('Period created'));
			showCreateForm = false;
			newName = '';
			newStartDate = '';
			newEndDate = '';
			await loadPeriods();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to create period') + ': ' + msg);
		}
		creating = false;
	};

	const confirmClose = (period: any) => {
		closeTarget = period;
		showCloseConfirm = true;
	};

	const handleClose = async () => {
		if (!closeTarget) return;
		try {
			await closePeriod(closeTarget.id);
			toast.success($i18n.t('Period closed'));
			await loadPeriods();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to close period') + ': ' + msg);
		}
		closeTarget = null;
	};

	const confirmReopen = (period: any) => {
		reopenTarget = period;
		showReopenConfirm = true;
	};

	const handleReopen = async () => {
		if (!reopenTarget) return;
		try {
			await reopenPeriod(reopenTarget.id);
			toast.success($i18n.t('Period reopened'));
			await loadPeriods();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to reopen period') + ': ' + msg);
		}
		reopenTarget = null;
	};

	const suggestName = () => {
		if (newStartDate && !newName) {
			const d = dayjs(newStartDate);
			newName = d.format('MMMM YYYY');
		}
	};

	const handleImported = async () => {
		toast.success($i18n.t('Periods imported successfully'));
		await loadPeriods();
	};

	onMount(() => {
		loadPeriods();
	});
</script>

<ConfirmDialog
	bind:open={showCloseConfirm}
	title={$i18n.t('Close Period')}
	description={$i18n.t(
		'Closing this period will prevent any new transactions from being posted within its date range. Continue?'
	)}
	confirmLabel={$i18n.t('Close')}
	onconfirm={handleClose}
/>

<ConfirmDialog
	bind:open={showReopenConfirm}
	title={$i18n.t('Reopen Period')}
	description={$i18n.t(
		'Reopening this period will allow transactions to be posted within its date range again. Continue?'
	)}
	confirmLabel={$i18n.t('Reopen')}
	onconfirm={handleReopen}
/>

<ExcelImportModal
	bind:show={showImportModal}
	type="period"
	{companyId}
	on:imported={handleImported}
/>

<!-- New period -->
<Dialog.Root bind:open={showCreateForm}>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-lg">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Create New Period')}</Dialog.Title>
			<Dialog.Description>
				{$i18n.t(
					'Create periods to control when transactions can be posted. Closing a period prevents changes to transactions in that date range.'
				)}
			</Dialog.Description>
		</Dialog.Header>
		<form id="period-form" class="grid gap-4" onsubmit={handleCreate}>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2">
					<Label for="period-start">{$i18n.t('Start Date')} *</Label>
					<Input
						id="period-start"
						type="date"
						class="tabular-nums dark:scheme-dark"
						bind:value={newStartDate}
						onchange={suggestName}
					/>
				</div>
				<div class="grid gap-2">
					<Label for="period-end">{$i18n.t('End Date')} *</Label>
					<Input
						id="period-end"
						type="date"
						class="tabular-nums dark:scheme-dark"
						bind:value={newEndDate}
					/>
				</div>
			</div>
			<div class="grid gap-2">
				<Label for="period-name">{$i18n.t('Name', { context: 'gnos3' })} *</Label>
				<Input
					id="period-name"
					type="text"
					bind:value={newName}
					placeholder={$i18n.t('e.g. March 2026')}
				/>
			</div>
		</form>
		<Dialog.Footer>
			<Button variant="outline" onclick={() => (showCreateForm = false)}>{$i18n.t('Cancel')}</Button
			>
			<Button
				type="submit"
				form="period-form"
				disabled={creating || !newName || !newStartDate || !newEndDate}
			>
				{#if creating}<Spinner />{/if}
				{creating ? $i18n.t('Creating...') : $i18n.t('Create')}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<div class="flex flex-col gap-4">
	<!-- Header -->
	<div class="flex flex-wrap items-start justify-between gap-x-4 gap-y-3">
		<div class="min-w-0 space-y-1">
			<h2 class="text-lg font-semibold">
				{$i18n.t('Accounting Periods')}
				<span class="ml-1 font-normal text-muted-foreground tabular-nums">{periods.length}</span>
			</h2>
			<p class="text-sm text-muted-foreground">
				{$i18n.t('A closed period accepts no new postings in its date range.')}
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
					<DropdownMenu.Item onSelect={() => downloadPeriodImportTemplate()}>
						<Download />{$i18n.t('Download Template')}
					</DropdownMenu.Item>
				</DropdownMenu.Content>
			</DropdownMenu.Root>
			<Button size="sm" onclick={openCreateForm}><Plus />{$i18n.t('New Period')}</Button>
		</div>
	</div>

	<!-- Periods Table -->
	{#if loading}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(4) as _}
				<Skeleton class="h-8 w-full" />
			{/each}
		</div>
	{:else if loadError}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Failed to load periods')}</Alert.Title>
			<Alert.Description>{loadError}</Alert.Description>
			<Alert.Action>
				<Button variant="outline" size="sm" onclick={loadPeriods}>{$i18n.t('Retry')}</Button>
			</Alert.Action>
		</Alert.Root>
	{:else if periods.length === 0}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><CalendarRange /></Empty.Media>
				<Empty.Title>{$i18n.t('No accounting periods defined yet.')}</Empty.Title>
				<Empty.Description>
					{$i18n.t(
						'Create periods to control when transactions can be posted. Closing a period prevents changes to transactions in that date range.'
					)}
				</Empty.Description>
			</Empty.Header>
			<Empty.Content>
				<Button size="sm" onclick={openCreateForm}><Plus />{$i18n.t('New Period')}</Button>
			</Empty.Content>
		</Empty.Root>
	{:else}
		<div class="overflow-hidden rounded-md border">
			<Table.Root>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						<Table.Head>{$i18n.t('Name', { context: 'gnos3' })}</Table.Head>
						<Table.Head>{$i18n.t('Start Date')}</Table.Head>
						<Table.Head>{$i18n.t('End Date')}</Table.Head>
						<Table.Head>{$i18n.t('Status')}</Table.Head>
						<Table.Head>{$i18n.t('Closed At')}</Table.Head>
						<Table.Head class="text-right"
							><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head
						>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each periods as period (period.id)}
						<Table.Row>
							<Table.Cell class="font-medium">{period.name}</Table.Cell>
							<Table.Cell class="tabular-nums">
								{dayjs(period.start_date).format('YYYY-MM-DD')}
							</Table.Cell>
							<Table.Cell class="tabular-nums">
								{dayjs(period.end_date).format('YYYY-MM-DD')}
							</Table.Cell>
							<Table.Cell>
								{#if period.is_closed}
									<Badge variant="status"><Lock aria-hidden="true" />{$i18n.t('Closed')}</Badge>
								{:else}
									<Badge variant="status">
										<LockOpen class="text-success" aria-hidden="true" />{$i18n.t('Open')}
									</Badge>
								{/if}
							</Table.Cell>
							<Table.Cell class="text-muted-foreground tabular-nums">
								{period.closed_at ? dayjs(period.closed_at).format('YYYY-MM-DD HH:mm') : '—'}
							</Table.Cell>
							<Table.Cell class="text-right">
								{#if period.is_closed}
									<Tip content={$i18n.t('Reopen this period')}>
										<Button variant="outline" size="xs" onclick={() => confirmReopen(period)}>
											<LockOpen />{$i18n.t('Reopen')}
										</Button>
									</Tip>
								{:else}
									<Tip content={$i18n.t('Close this period to prevent changes')}>
										<Button variant="outline" size="xs" onclick={() => confirmClose(period)}>
											<Lock />{$i18n.t('Close')}
										</Button>
									</Tip>
								{/if}
							</Table.Cell>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</div>
	{/if}
</div>
