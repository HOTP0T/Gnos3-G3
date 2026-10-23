<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';

	import Plus from '@lucide/svelte/icons/plus';
	import Upload from '@lucide/svelte/icons/upload';
	import Download from '@lucide/svelte/icons/download';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Info from '@lucide/svelte/icons/info';
	import ArrowLeftRight from '@lucide/svelte/icons/arrow-left-right';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';

	import {
		getExchangeRates,
		createExchangeRate,
		deleteExchangeRate,
		bulkImportExchangeRates,
		downloadExchangeRateTemplate
	} from '$lib/apis/accounting';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';

	const i18n: any = getContext('i18n');

	export let companyId: number;

	const CURRENCIES = [
		'EUR',
		'USD',
		'GBP',
		'CNY',
		'JPY',
		'CAD',
		'AUD',
		'CHF',
		'BRL',
		'INR',
		'KRW',
		'MXN',
		'SGD',
		'HKD',
		'MAD'
	];

	// State
	let loading = true;
	let loadError = '';
	let rates: any[] = [];

	// Create form (company overrides only — stored on the day given, and holding
	// from that day until a later override supersedes it)
	let showAddForm = false;
	let newFromCurrency = 'USD';
	let newToCurrency = 'EUR';
	let newRate = '';
	let newEffectiveDate = '';
	let creating = false;

	// Import
	let importingCsv = false;
	let fileInput: HTMLInputElement;

	// Delete confirmation
	let showDeleteConfirm = false;
	let deleteTarget: any = null;

	const AUTO_SOURCES = ['frankfurter', 'erapi', 'ecb', 'exchangerate'];

	// ─── Helpers ────────────────────────────────────────────────────────────────

	const formatRate = (val: any) => {
		if (val === null || val === undefined) return '—';
		return parseFloat(val).toLocaleString(undefined, {
			minimumFractionDigits: 4,
			maximumFractionDigits: 6
		});
	};

	const formatDate = (val: any) => {
		if (!val) return '—';
		return dayjs(val).format('YYYY-MM-DD');
	};

	// ─── Data loading ───────────────────────────────────────────────────────────

	const loadRates = async () => {
		loading = true;
		loadError = '';
		try {
			const res = await getExchangeRates({ company_id: companyId });
			rates = Array.isArray(res) ? res : (res?.items ?? []);
			// Sort by effective_date descending
			rates.sort(
				(a: any, b: any) =>
					new Date(b.effective_date).getTime() - new Date(a.effective_date).getTime()
			);
		} catch (err) {
			loadError = `${err}`;
			toast.error(`${$i18n.t('Failed to load exchange rates')}: ${err}`);
		}
		loading = false;
	};

	// ─── Create ─────────────────────────────────────────────────────────────────

	const handleCreate = async () => {
		if (!newFromCurrency || !newToCurrency || !newRate || !newEffectiveDate) {
			toast.error($i18n.t('Please fill in all fields'));
			return;
		}
		if (newFromCurrency === newToCurrency) {
			toast.error($i18n.t('From and To currencies must be different'));
			return;
		}
		const rateVal = parseFloat(newRate);
		if (isNaN(rateVal) || rateVal <= 0) {
			toast.error($i18n.t('Rate must be a positive number'));
			return;
		}

		creating = true;
		try {
			await createExchangeRate(companyId, {
				from_currency: newFromCurrency,
				to_currency: newToCurrency,
				rate: rateVal,
				effective_date: newEffectiveDate
			});
			toast.success($i18n.t('Exchange rate created'));
			showAddForm = false;
			newRate = '';
			newEffectiveDate = '';
			await loadRates();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to create exchange rate') + ': ' + msg);
		}
		creating = false;
	};

	// ─── Delete ─────────────────────────────────────────────────────────────────

	const confirmDelete = (rate: any) => {
		deleteTarget = rate;
		showDeleteConfirm = true;
	};

	const handleDelete = async () => {
		if (!deleteTarget) return;
		try {
			await deleteExchangeRate(deleteTarget.id);
			toast.success($i18n.t('Exchange rate deleted'));
			await loadRates();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to delete exchange rate') + ': ' + msg);
		}
	};

	// ─── CSV Import ────────────────────────────────────────────────────────────

	const handleFileImport = async (event: Event) => {
		const input = event.target as HTMLInputElement;
		const file = input?.files?.[0];
		if (!file) return;

		importingCsv = true;
		try {
			const text = await file.text();
			const lines = text
				.split(/\r?\n/)
				.map((l) => l.trim())
				.filter((l) => l.length > 0);
			if (lines.length < 2) {
				toast.error($i18n.t('File must have a header row and at least one data row'));
				importingCsv = false;
				return;
			}

			// Parse header to find column indices
			const header = lines[0]
				.split(/[,;\t]/)
				.map((h) => h.trim().toLowerCase().replace(/['"]/g, ''));
			const dateIdx = header.findIndex(
				(h) => h === 'date' || h === 'effective_date' || h === 'effective date'
			);
			const fromIdx = header.findIndex(
				(h) => h === 'from' || h === 'from_currency' || h === 'from currency'
			);
			const toIdx = header.findIndex(
				(h) => h === 'to' || h === 'to_currency' || h === 'to currency'
			);
			const rateIdx = header.findIndex(
				(h) => h === 'rate' || h === 'exchange_rate' || h === 'exchange rate'
			);

			if (dateIdx < 0 || fromIdx < 0 || toIdx < 0 || rateIdx < 0) {
				toast.error($i18n.t('CSV must have columns: Date, From, To, Rate'));
				importingCsv = false;
				return;
			}

			const rates: any[] = [];
			for (let i = 1; i < lines.length; i++) {
				const cols = lines[i].split(/[,;\t]/).map((c) => c.trim().replace(/['"]/g, ''));
				const dateVal = cols[dateIdx];
				const fromVal = cols[fromIdx]?.toUpperCase();
				const toVal = cols[toIdx]?.toUpperCase();
				const rateVal = parseFloat(cols[rateIdx]);

				if (!dateVal || !fromVal || !toVal || isNaN(rateVal) || rateVal <= 0) continue;

				rates.push({
					effective_date: dateVal,
					from_currency: fromVal,
					to_currency: toVal,
					rate: rateVal
				});
			}

			if (rates.length === 0) {
				toast.error($i18n.t('No valid rates found in file'));
				importingCsv = false;
				return;
			}

			await bulkImportExchangeRates(companyId, rates);
			toast.success($i18n.t('Imported {{count}} exchange rates', { count: rates.length }));
			await loadRates();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Import failed') + ': ' + msg);
		}
		importingCsv = false;
		// Reset input so same file can be re-selected
		if (input) input.value = '';
	};

	onMount(() => {
		loadRates();
	});
</script>

<input
	type="file"
	accept=".csv,.txt"
	class="hidden"
	bind:this={fileInput}
	on:change={handleFileImport}
/>

<div class="flex flex-col gap-4">
	<!-- Header: what this list is, then its actions -->
	<div class="flex flex-wrap items-start justify-between gap-x-4 gap-y-3">
		<div class="min-w-0 space-y-1">
			<h2 class="text-lg font-semibold">
				{$i18n.t('Exchange Rates')}
				{#if !loading}<span class="ml-1 font-normal text-muted-foreground tabular-nums"
						>{rates.length}</span
					>{/if}
			</h2>
			<p class="max-w-2xl text-sm text-muted-foreground">
				{$i18n.t(
					'Monthly exchange rates for converting foreign currency transactions to your company currency.'
				)}
			</p>
		</div>
		<div class="flex flex-wrap items-center gap-2">
			<Tip content={$i18n.t('Download CSV template with example monthly rates')}>
				<Button variant="ghost" size="sm" onclick={() => downloadExchangeRateTemplate()}>
					<Download />{$i18n.t('Template')}
				</Button>
			</Tip>
			<Button
				variant="outline"
				size="sm"
				disabled={importingCsv}
				onclick={() => fileInput?.click()}
			>
				{#if importingCsv}<Spinner />{:else}<Upload />{/if}
				{importingCsv ? $i18n.t('Importing...') : $i18n.t('Import CSV')}
			</Button>
			<Button size="sm" onclick={() => (showAddForm = true)}>
				<Plus />{$i18n.t('Add Rate')}
			</Button>
		</div>
	</div>

	<!-- Company overrides fall back to the shared global rates -->
	<Alert.Root variant="info">
		<Info />
		<Alert.Description>
			{$i18n.t(
				'This company uses the shared platform rates (Accounting → Settings → Exchange Rates) unless you add an override below. An override applies from its date onward, until a later one replaces it.'
			)}
			<a
				href="/accounting/settings?tab=rates"
				class="font-medium text-link underline-offset-4 hover:underline"
				>{$i18n.t('Open shared rates')}</a
			>
		</Alert.Description>
	</Alert.Root>

	<!-- Rates Table -->
	{#if loading}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(4) as _}
				<Skeleton class="h-8 w-full" />
			{/each}
		</div>
	{:else if loadError}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Failed to load exchange rates')}</Alert.Title>
			<Alert.Description>
				<p>{loadError}</p>
				<Button variant="outline" size="sm" class="mt-2" onclick={loadRates}>
					<RotateCcw />{$i18n.t('Retry')}
				</Button>
			</Alert.Description>
		</Alert.Root>
	{:else if rates.length === 0}
		<Empty.Root class="border">
			<Empty.Header>
				<Empty.Media variant="icon"><ArrowLeftRight /></Empty.Media>
				<Empty.Title>{$i18n.t('No exchange rates defined yet.')}</Empty.Title>
				<Empty.Description>
					{$i18n.t(
						'Add exchange rates to convert foreign currency transactions to your company currency.'
					)}
				</Empty.Description>
			</Empty.Header>
			<Empty.Content>
				<Button variant="outline" size="sm" onclick={() => (showAddForm = true)}>
					<Plus />{$i18n.t('Add Rate')}
				</Button>
			</Empty.Content>
		</Empty.Root>
	{:else}
		<div class="overflow-hidden rounded-md border">
			<Table.Root>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						<Table.Head>{$i18n.t('Effective Date')}</Table.Head>
						<Table.Head>{$i18n.t('From', { context: 'currency' })}</Table.Head>
						<Table.Head>{$i18n.t('To', { context: 'currency' })}</Table.Head>
						<Table.Head class="text-right">{$i18n.t('Rate')}</Table.Head>
						<Table.Head>{$i18n.t('Source')}</Table.Head>
						<Table.Head class="w-12"><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each rates as rate (rate.id)}
						<Table.Row>
							<Table.Cell class="py-1.5 tabular-nums">{formatDate(rate.effective_date)}</Table.Cell>
							<Table.Cell class="py-1.5 font-medium">{rate.from_currency}</Table.Cell>
							<Table.Cell class="py-1.5 font-medium">{rate.to_currency}</Table.Cell>
							<Table.Cell class="py-1.5 text-right tabular-nums">{formatRate(rate.rate)}</Table.Cell
							>
							<Table.Cell class="py-1.5">
								{#if rate.source === 'manual' || rate.source === 'Manual'}
									<Badge variant="outline">{$i18n.t('Manual')}</Badge>
								{:else if AUTO_SOURCES.includes(rate.source)}
									<Badge variant="secondary">{$i18n.t('Auto')}</Badge>
								{:else}
									<Badge variant="outline" class="capitalize"
										>{rate.source ? $i18n.t(rate.source) : $i18n.t('Import')}</Badge
									>
								{/if}
							</Table.Cell>
							<Table.Cell class="py-1.5 text-right">
								<Tip content={$i18n.t('Delete this exchange rate')}>
									<Button
										variant="ghost"
										size="icon-xs"
										class="text-muted-foreground hover:text-destructive"
										aria-label={$i18n.t('Delete this exchange rate')}
										onclick={() => confirmDelete(rate)}
									>
										<Trash2 />
									</Button>
								</Tip>
							</Table.Cell>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</div>
	{/if}
</div>

<!-- Add a company override -->
<Dialog.Root bind:open={showAddForm}>
	<Dialog.Content class="sm:max-w-lg">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Add Exchange Rate')}</Dialog.Title>
			<Dialog.Description>
				{$i18n.t('An override applies from its date onward, until a later one replaces it.')}
			</Dialog.Description>
		</Dialog.Header>
		<div class="grid gap-4 sm:grid-cols-2">
			<div class="grid gap-2">
				<Label for="rate-from-currency">{$i18n.t('From Currency')} *</Label>
				<NativeSelect.Root id="rate-from-currency" class="w-full" bind:value={newFromCurrency}>
					{#each CURRENCIES as cur}
						<NativeSelect.Option value={cur}>{cur}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
			</div>
			<div class="grid gap-2">
				<Label for="rate-to-currency">{$i18n.t('To Currency')} *</Label>
				<NativeSelect.Root id="rate-to-currency" class="w-full" bind:value={newToCurrency}>
					{#each CURRENCIES as cur}
						<NativeSelect.Option value={cur}>{cur}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
			</div>
			<div class="grid gap-2">
				<Label for="rate-value">{$i18n.t('Rate')} *</Label>
				<Input
					id="rate-value"
					type="number"
					step="0.000001"
					min="0"
					class="text-right tabular-nums"
					bind:value={newRate}
					placeholder="1.0850"
				/>
			</div>
			<div class="grid gap-2">
				<Label for="rate-effective-date">{$i18n.t('Effective Date')} *</Label>
				<Input
					id="rate-effective-date"
					type="date"
					class="tabular-nums"
					bind:value={newEffectiveDate}
				/>
			</div>
		</div>
		<Dialog.Footer>
			<Button variant="outline" onclick={() => (showAddForm = false)}>{$i18n.t('Cancel')}</Button>
			<Button
				onclick={handleCreate}
				disabled={creating || !newFromCurrency || !newToCurrency || !newRate || !newEffectiveDate}
			>
				{#if creating}<Spinner />{/if}
				{creating ? $i18n.t('Saving...') : $i18n.t('Save')}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<ConfirmDialog
	bind:open={showDeleteConfirm}
	title={$i18n.t('Delete Exchange Rate')}
	description={$i18n.t(
		'Are you sure you want to delete this exchange rate? This action cannot be undone.'
	)}
	confirmLabel={$i18n.t('Delete')}
	destructive
	onconfirm={handleDelete}
/>
