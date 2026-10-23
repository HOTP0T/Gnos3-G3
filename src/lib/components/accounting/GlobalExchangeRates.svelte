<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';

	import Plus from '@lucide/svelte/icons/plus';
	import Upload from '@lucide/svelte/icons/upload';
	import Download from '@lucide/svelte/icons/download';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import ArrowLeftRight from '@lucide/svelte/icons/arrow-left-right';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';

	import {
		getGlobalExchangeRates,
		createGlobalExchangeRate,
		deleteGlobalExchangeRate,
		bulkImportGlobalExchangeRates,
		fetchGlobalRatesNow,
		getGlobalRateCoverage,
		backfillGlobalRates,
		downloadExchangeRateTemplate
	} from '$lib/apis/accounting';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';

	const i18n: any = getContext('i18n');

	// A broad picker for manual entry. The auto-fetch covers whatever the source
	// publishes; this list is only for hand-adding a pair.
	const CURRENCIES = [
		'EUR',
		'USD',
		'GBP',
		'CNY',
		'JPY',
		'CHF',
		'CAD',
		'AUD',
		'NZD',
		'HKD',
		'SGD',
		'KRW',
		'INR',
		'THB',
		'MYR',
		'IDR',
		'PHP',
		'VND',
		'TWD',
		'AED',
		'SAR',
		'QAR',
		'KWD',
		'BHD',
		'ZAR',
		'BRL',
		'MXN',
		'TRY',
		'PLN',
		'CZK',
		'HUF',
		'RON',
		'SEK',
		'NOK',
		'DKK',
		'ILS',
		'RUB',
		'MAD'
	];

	const today = () => dayjs().format('YYYY-MM-DD');

	const thisMonth = () => dayjs().format('YYYY-MM');

	// Rows land one per publish day per pair, so the table is windowed rather
	// than listing everything: a month at a time, newest first.
	const PAGE_LIMIT = 1000;

	// State
	let loading = true;
	let loadError = '';
	let rates: any[] = [];
	// Filters (all applied server-side via the list query).
	let monthFilter = thisMonth(); // YYYY-MM; '' = the most recent PAGE_LIMIT rows
	let filterFrom = ''; // from/base currency
	let filterTo = ''; // to/quote currency

	// Fetch-now controls
	let fetchSource = 'frankfurter';
	let fetchDate = today(); // which day "Fetch now" pulls; never later than today
	let fetching = false;

	// Coverage: how far the set reaches per base currency, and the stretches
	// long enough that an entry landing in one would resolve to a stale rate.
	// Weekends and holidays are not gaps — the ECB does not publish on them.
	let coverage: {
		start?: string;
		end?: string;
		bases?: any[];
		gaps?: any[];
		latest_date?: string | null;
		stale_days?: number | null;
		tolerance_days?: number;
	} | null = null;
	let backfilling = false;

	$: gaps = coverage?.gaps ?? [];
	// The source publishes once a business day, so a rate a day or two old is
	// simply the newest one there is. Only past the tolerance is it worth saying.
	$: ratesAreStale =
		coverage?.stale_days != null && coverage.stale_days > (coverage.tolerance_days ?? 7);

	const loadCoverage = async () => {
		try {
			coverage = await getGlobalRateCoverage();
		} catch {
			coverage = null;
		}
	};

	const handleBackfill = async () => {
		backfilling = true;
		try {
			const res = await backfillGlobalRates({ source: fetchSource });
			const failed: string[] = res?.spans_failed ?? [];
			const notes: string[] = res?.errors ?? [];
			if (res?.fetched)
				toast.success(
					$i18n.t('Filled {{count}} rates from {{start}} to {{end}}', {
						count: res.fetched,
						start: res.start,
						end: res.end
					})
				);
			else if (!failed.length && !notes.length) toast.success($i18n.t('Every day already covered'));
			if (failed.length)
				toast.error(
					$i18n.t('Could not reach the rate source for {{spans}} — add those by hand below.', {
						spans: failed.join(', ')
					})
				);
			else if (notes.length)
				// e.g. a latest-only source asked for history it cannot serve. Not a
				// connectivity failure, so it must not read like one.
				toast.error(notes.slice(0, 3).join('; '));
			await Promise.all([loadRates(), loadCoverage()]);
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		backfilling = false;
	};

	// Create form
	let showAddForm = false;
	let newFromCurrency = 'USD';
	let newToCurrency = 'EUR';
	let newRate = '';
	let newDate = today();
	let creating = false;

	// Import
	let importingCsv = false;
	let fileInput: HTMLInputElement;

	// Delete confirmation
	let showDeleteConfirm = false;
	let deleteTarget: any = null;

	// ─── Helpers ────────────────────────────────────────────────────────────────

	const formatRate = (val: any) => {
		if (val === null || val === undefined) return '—';
		return parseFloat(val).toLocaleString(undefined, {
			minimumFractionDigits: 4,
			maximumFractionDigits: 6
		});
	};

	// Rows carry the day the source published them for.
	const formatDate = (val: any) => (val ? dayjs(val).format('YYYY-MM-DD') : '—');
	const formatDay = (val: any) => (val ? dayjs(val).format('D MMM YYYY') : '-');

	const AUTO_SOURCES = ['frankfurter', 'erapi', 'ecb', 'exchangerate'];

	// ─── Data loading ───────────────────────────────────────────────────────────

	const loadRates = async () => {
		loading = true;
		loadError = '';
		try {
			// Empty strings are dropped by the API client, so this sends only the
			// active filters (server-side narrowing).
			const res = await getGlobalExchangeRates({
				from_currency: filterFrom,
				to_currency: filterTo,
				month: monthFilter,
				limit: PAGE_LIMIT
			});
			rates = Array.isArray(res) ? res : (res?.items ?? []);
		} catch (err) {
			loadError = `${err}`;
			toast.error(`${$i18n.t('Failed to load exchange rates')}: ${err}`);
		}
		loading = false;
	};

	const clearFilters = () => {
		filterFrom = '';
		filterTo = '';
		monthFilter = '';
		loadRates();
	};

	// ─── Fetch now ────────────────────────────────────────────────────────────────

	const handleFetchNow = async () => {
		fetching = true;
		try {
			const res = await fetchGlobalRatesNow({
				source: fetchSource,
				force: true,
				effective_date: fetchDate || undefined
			});
			const fetched = res?.fetched ?? 0;
			const errs: string[] = res?.errors ?? [];
			// The source answers with the day it actually published for — over a
			// weekend that is the preceding business day, not the date asked for.
			const landedOn = res?.effective_date ?? fetchDate;
			if (fetched > 0)
				toast.success(
					$i18n.t('Fetched {{count}} rates for {{date}}', { count: fetched, date: landedOn })
				);
			else if (errs.length === 0)
				toast.success($i18n.t('Rates already on file for {{date}}', { date: landedOn }));
			if (errs.length > 0)
				toast.error(`${$i18n.t('Some bases could not be fetched')}: ${errs.join('; ')}`);
			// Show the month the rates landed in.
			monthFilter = dayjs(landedOn).format('YYYY-MM');
			await loadRates();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		fetching = false;
	};

	// ─── Create ─────────────────────────────────────────────────────────────────

	const handleCreate = async () => {
		if (!newFromCurrency || !newToCurrency || !newRate || !newDate) {
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
			await createGlobalExchangeRate({
				from_currency: newFromCurrency,
				to_currency: newToCurrency,
				rate: rateVal,
				effective_date: newDate
			});
			toast.success($i18n.t('Exchange rate created'));
			showAddForm = false;
			newRate = '';
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
			await deleteGlobalExchangeRate(deleteTarget.id);
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

			const parsed: any[] = [];
			for (let i = 1; i < lines.length; i++) {
				const cols = lines[i].split(/[,;\t]/).map((c) => c.trim().replace(/['"]/g, ''));
				const dateVal = cols[dateIdx];
				const fromVal = cols[fromIdx]?.toUpperCase();
				const toVal = cols[toIdx]?.toUpperCase();
				const rateVal = parseFloat(cols[rateIdx]);
				if (!dateVal || !fromVal || !toVal || isNaN(rateVal) || rateVal <= 0) continue;
				parsed.push({
					effective_date: dateVal,
					from_currency: fromVal,
					to_currency: toVal,
					rate: rateVal
				});
			}

			if (parsed.length === 0) {
				toast.error($i18n.t('No valid rates found in file'));
				importingCsv = false;
				return;
			}

			await bulkImportGlobalExchangeRates(parsed);
			toast.success($i18n.t('Imported {{count}} exchange rates', { count: parsed.length }));
			await loadRates();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Import failed') + ': ' + msg);
		}
		importingCsv = false;
		if (input) input.value = '';
	};

	onMount(() => {
		loadRates();
		loadCoverage();
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
	<div class="grid max-w-3xl gap-1">
		<h2 class="text-lg font-semibold">{$i18n.t('Exchange Rates')}</h2>
		<p class="text-sm text-muted-foreground">
			{$i18n.t(
				'Shared exchange rates for the whole platform, one per publish day. An entry uses the last rate published on or before its date, so weekends and holidays need no rate of their own. Each company uses these unless it overrides a rate in its own settings.'
			)}
		</p>
	</div>

	<!-- Fetch from the live source -->
	<Card.Root class="gap-0 py-0">
		<Card.Header class="border-b py-4 [.border-b]:pb-4">
			<Card.Title>{$i18n.t('Live rates')}</Card.Title>
			<Card.Description>
				{$i18n.t(
					'“Fetch now” pulls that day’s rates, per company base currency. A day the source did not publish on (a weekend, a holiday) lands on the business day before it. Manual rates are never overwritten.'
				)}
			</Card.Description>
		</Card.Header>
		<Card.Content class="divide-y">
			<div class="flex flex-col gap-2 py-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
				<div class="grid min-w-0 gap-1">
					<Label for="global-fetch-source">{$i18n.t('Source')}</Label>
					<p class="text-sm text-muted-foreground">
						{$i18n.t(
							'ECB / Frankfurter covers ~31 major currencies. If a company base currency is outside that set (e.g. AED, TWD, SAR, VND), switch the source to open.er-api or add rates manually.'
						)}
					</p>
				</div>
				<NativeSelect.Root
					id="global-fetch-source"
					class="w-full sm:w-72 sm:shrink-0"
					bind:value={fetchSource}
				>
					<NativeSelect.Option value="frankfurter"
						>{$i18n.t('ECB / Frankfurter — all currencies')}</NativeSelect.Option
					>
					<NativeSelect.Option value="erapi"
						>{$i18n.t('open.er-api — 160+ currencies')}</NativeSelect.Option
					>
				</NativeSelect.Root>
			</div>
			<div class="flex flex-col gap-2 py-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
				<div class="grid min-w-0 gap-1">
					<Label for="global-fetch-day">{$i18n.t('Day')}</Label>
				</div>
				<div class="flex w-full items-center gap-2 sm:w-72 sm:shrink-0">
					<Input
						id="global-fetch-day"
						type="date"
						max={today()}
						class="min-w-0 flex-1 tabular-nums"
						bind:value={fetchDate}
					/>
					<Button disabled={fetching} onclick={handleFetchNow}>
						{#if fetching}<Spinner />{:else}<RefreshCw />{/if}
						{fetching ? $i18n.t('Fetching...') : $i18n.t('Fetch now')}
					</Button>
				</div>
			</div>
		</Card.Content>

		<!-- Rate freshness: which day the numbers on screen actually come from -->
		{#if coverage?.latest_date || (coverage && !gaps.length)}
			<Card.Footer class="flex-col items-start gap-1 border-t py-3 [.border-t]:pt-3">
				{#if coverage?.latest_date}
					{#if ratesAreStale}
						<p class="flex items-start gap-2 text-sm">
							<TriangleAlert class="mt-0.5 size-4 shrink-0 text-warning" />
							{$i18n.t(
								'Live rates last reached {{date}}, {{days}} days ago. Conversions across the platform are using that day’s rate until the source is reachable again.',
								{ date: formatDay(coverage.latest_date), days: coverage.stale_days }
							)}
						</p>
					{:else}
						<p class="flex items-center gap-2 text-sm text-muted-foreground">
							<CircleCheck class="size-4 shrink-0 text-success" />
							{$i18n.t('Rates current to {{date}}.', { date: formatDay(coverage.latest_date) })}
						</p>
					{/if}
				{/if}
				{#if coverage && !gaps.length}
					<p class="text-sm text-muted-foreground">
						{$i18n.t('No gaps between {{start}} and {{end}}.', {
							start: coverage.start,
							end: coverage.end
						})}
						{#if coverage.bases?.length}
							<span class="tabular-nums">
								{#each coverage.bases as b, i}{i ? ' · ' : ''}{b.base}: {$i18n.t(
										'{{count}} day(s)',
										{ count: b.days_covered }
									)}{/each}
							</span>
						{/if}
					</p>
				{/if}
			</Card.Footer>
		{/if}
	</Card.Root>

	<!-- Coverage: stretches with no rates at all, shown where they are filled -->
	{#if gaps.length}
		<Alert.Root variant="warning">
			<TriangleAlert />
			<Alert.Title>
				{$i18n.t('{{count}} stretch(es) with no rates on file', { count: gaps.length })}
			</Alert.Title>
			<Alert.Description>
				<ul class="tabular-nums">
					{#each gaps.slice(0, 6) as gap}
						<li>
							{gap.base} · {gap.start} → {gap.end}
							({$i18n.t('{{count}} day(s)', { count: gap.days })})
						</li>
					{/each}
					{#if gaps.length > 6}<li>…</li>{/if}
				</ul>
				<p class="mt-1">
					{$i18n.t(
						'An entry dated inside one of these has no recent rate to use. Fill the gaps, or add the pair by hand — entries will ask for a rate rather than reach back weeks for one.'
					)}
				</p>
				<Button
					variant="outline"
					size="sm"
					class="mt-2"
					disabled={backfilling}
					onclick={handleBackfill}
				>
					{#if backfilling}<Spinner />{/if}
					{backfilling ? $i18n.t('Filling...') : $i18n.t('Fill gaps')}
				</Button>
			</Alert.Description>
		</Alert.Root>
	{/if}

	<!-- Rates on file -->
	<div class="flex flex-wrap items-center gap-2">
		<NativeSelect.Root
			size="sm"
			value={filterFrom}
			aria-label={$i18n.t('From currency')}
			onchange={(e: Event) => {
				filterFrom = (e.currentTarget as HTMLSelectElement).value;
				loadRates();
			}}
		>
			<NativeSelect.Option value="">{$i18n.t('From: any')}</NativeSelect.Option>
			{#each CURRENCIES as cur}<NativeSelect.Option value={cur}>{cur}</NativeSelect.Option>{/each}
		</NativeSelect.Root>
		<ArrowRight class="size-4 text-muted-foreground" aria-hidden="true" />
		<NativeSelect.Root
			size="sm"
			value={filterTo}
			aria-label={$i18n.t('To currency')}
			onchange={(e: Event) => {
				filterTo = (e.currentTarget as HTMLSelectElement).value;
				loadRates();
			}}
		>
			<NativeSelect.Option value="">{$i18n.t('To: any')}</NativeSelect.Option>
			{#each CURRENCIES as cur}<NativeSelect.Option value={cur}>{cur}</NativeSelect.Option>{/each}
		</NativeSelect.Root>
		<Input
			id="global-rate-month-view"
			type="month"
			max={thisMonth()}
			class="h-8 w-40 tabular-nums"
			aria-label={$i18n.t('Month')}
			bind:value={monthFilter}
			onchange={loadRates}
		/>
		{#if filterFrom || filterTo || monthFilter}
			<Button variant="ghost" size="sm" onclick={clearFilters}>{$i18n.t('Clear filters')}</Button>
		{/if}

		<div class="ml-auto flex flex-wrap items-center gap-2">
			<span class="text-sm text-muted-foreground tabular-nums"
				>{rates.length} {$i18n.t('shown')}</span
			>
			<Tip content={$i18n.t('Download CSV template with example daily rates')}>
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
			<Button variant="outline" size="sm" onclick={() => (showAddForm = true)}>
				<Plus />{$i18n.t('Add Rate')}
			</Button>
		</div>
	</div>

	{#if loading}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(6) as _}
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
						'Nothing for this month. Click "Fetch now" to pull live rates, "Fill gaps" to backfill history, or add them manually.'
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

<!-- Add a rate by hand -->
<Dialog.Root bind:open={showAddForm}>
	<Dialog.Content class="sm:max-w-lg">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Add Exchange Rate')}</Dialog.Title>
			<Dialog.Description>
				{$i18n.t(
					'The rate is stored on this exact day and applies until a later one supersedes it. A rate you enter by hand also holds against the auto-fetch for the rest of its month.'
				)}
			</Dialog.Description>
		</Dialog.Header>
		<div class="grid gap-4 sm:grid-cols-2">
			<div class="grid gap-2">
				<Label for="grate-from">{$i18n.t('From Currency')} *</Label>
				<NativeSelect.Root id="grate-from" class="w-full" bind:value={newFromCurrency}>
					{#each CURRENCIES as cur}<NativeSelect.Option value={cur}>{cur}</NativeSelect.Option
						>{/each}
				</NativeSelect.Root>
			</div>
			<div class="grid gap-2">
				<Label for="grate-to">{$i18n.t('To Currency')} *</Label>
				<NativeSelect.Root id="grate-to" class="w-full" bind:value={newToCurrency}>
					{#each CURRENCIES as cur}<NativeSelect.Option value={cur}>{cur}</NativeSelect.Option
						>{/each}
				</NativeSelect.Root>
			</div>
			<div class="grid gap-2">
				<Label for="grate-value">{$i18n.t('Rate')} *</Label>
				<Input
					id="grate-value"
					type="number"
					step="0.000001"
					min="0"
					class="text-right tabular-nums"
					bind:value={newRate}
					placeholder="1.0850"
				/>
			</div>
			<div class="grid gap-2">
				<Label for="grate-date">{$i18n.t('Effective Date')} *</Label>
				<Input id="grate-date" type="date" class="tabular-nums" bind:value={newDate} />
			</div>
		</div>
		<Dialog.Footer>
			<Button variant="outline" onclick={() => (showAddForm = false)}>{$i18n.t('Cancel')}</Button>
			<Button
				onclick={handleCreate}
				disabled={creating || !newFromCurrency || !newToCurrency || !newRate || !newDate}
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
