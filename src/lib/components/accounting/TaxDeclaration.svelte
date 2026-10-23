<script lang="ts">
	import { onMount, getContext, createEventDispatcher } from 'svelte';
	import { uiLocale } from '$lib/utils/uiLocale';
	import { toast } from 'svelte-sonner';

	import {
		getTaxConfig,
		getTaxDeclaration,
		createTaxEntry,
		saveTaxFiling,
		exportTaxWorksheet,
		getPeriods
	} from '$lib/apis/accounting';

	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import Download from '@lucide/svelte/icons/download';
	import Save from '@lucide/svelte/icons/save';
	import Calculator from '@lucide/svelte/icons/calculator';

	import TaxFilingsList from './TaxFilingsList.svelte';
	import { taxTerm } from '$lib/utils/taxTerms';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import KpiCard from '$lib/components/gnos3-ui/KpiCard.svelte';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let companyId: number;

	// State
	let loading = false;
	let calculating = false;
	let creating = false;
	let saving = false;
	let taxConfig: any = null;
	let declaration: any = null;
	let filingsList: any;

	// Credit brought forward from the previous return.
	// Blank = taken from the previous filing (or recomputed); a value overrides it.
	let openingCreditInput: string | number | null = '';
	// A number input yields a number (or null) once typed into — never call string methods on it.
	const blank = (v: any) => v === '' || v === null || v === undefined;

	// Month selector
	let selectedMonth = '';
	let monthOptions: Array<{ value: string; label: string; from: string; to: string }> = [];

	// ─── Helpers ────────────────────────────────────────────────────────────────

	const fmt = (v: any): string => {
		const n = typeof v === 'string' ? parseFloat(v) : (v ?? 0);
		if (n === 0) return '0.00';
		return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	};

	// Period options follow the country's filing frequency: one entry per
	// month, quarter or fiscal period, spanning the company's accounting periods.
	function buildPeriodOptions(periods: any[], frequency: string) {
		const options: typeof monthOptions = [];
		const pad = (n: number) => String(n).padStart(2, '0');
		const lastDay = (y: number, m: number) => new Date(y, m + 1, 0).getDate();
		for (const p of periods) {
			const start = new Date(p.start_date);
			const end = new Date(p.end_date);
			if (frequency === 'yearly') {
				options.push({
					value: `${p.start_date}_${p.end_date}`,
					label: p.name ?? `${p.start_date} → ${p.end_date}`,
					from: p.start_date,
					to: p.end_date
				});
				continue;
			}
			const step = frequency === 'quarterly' ? 3 : 1;
			let cursor = new Date(start.getFullYear(), Math.floor(start.getMonth() / step) * step, 1);
			while (cursor <= end) {
				const y = cursor.getFullYear();
				const m = cursor.getMonth();
				const mEnd = m + step - 1;
				const from = `${y}-${pad(m + 1)}-01`;
				const to = `${y}-${pad(mEnd + 1)}-${pad(lastDay(y, mEnd))}`;
				const label =
					step === 3
						? `Q${m / 3 + 1} ${y}`
						: cursor.toLocaleDateString(uiLocale(), { year: 'numeric', month: 'long' });
				const value = step === 3 ? `${y}-Q${m / 3 + 1}` : `${y}-${pad(m + 1)}`;
				options.push({ value, label, from, to });
				cursor = new Date(y, m + step, 1);
			}
		}
		const seen = new Map<string, (typeof options)[0]>();
		for (const o of options) seen.set(o.value, o);
		return Array.from(seen.values()).sort((a, b) => b.from.localeCompare(a.from));
	}

	// ─── Data loading ───────────────────────────────────────────────────────────

	onMount(async () => {
		loading = true;
		try {
			const [config, res] = await Promise.all([
				getTaxConfig(companyId),
				getPeriods({ company_id: companyId })
			]);
			taxConfig = config;
			const periods = res.periods ?? res ?? [];
			monthOptions = buildPeriodOptions(periods, config?.filing_frequency ?? 'monthly');

			// Default to the period containing today, else the latest one.
			const today = new Date().toISOString().slice(0, 10);
			const match = monthOptions.find((o) => o.from <= today && today <= o.to);
			selectedMonth = match?.value ?? monthOptions[0]?.value ?? '';
		} catch (err) {
			toast.error(`${$i18n.t('Failed to load tax configuration')}: ${err}`);
		}
		loading = false;
	});

	// ─── Calculate ──────────────────────────────────────────────────────────────

	const handleCalculate = async () => {
		const opt = monthOptions.find((o) => o.value === selectedMonth);
		if (!opt) {
			toast.error($i18n.t('Please select a period'));
			return;
		}
		calculating = true;
		declaration = null;
		try {
			declaration = await getTaxDeclaration({
				company_id: companyId,
				period_start: opt.from,
				period_end: opt.to,
				opening_credit: blank(openingCreditInput)
					? undefined
					: parseFloat(String(openingCreditInput)) || 0
			});
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to calculate tax declaration') + ': ' + msg);
		}
		calculating = false;
	};

	// ─── Create settlement entry ──────────────────────────────────────────────────

	const handleCreateEntry = async () => {
		if (!declaration?.suggested_entry) return;
		creating = true;
		try {
			const result = await createTaxEntry(companyId, {
				tax_type: 'vat',
				period_start: declaration.period_start,
				period_end: declaration.period_end,
				entry: declaration.suggested_entry,
				tax_amount: declaration.grand_total ?? declaration.payable ?? 0,
				currency: declaration.currency,
				details: declaration
			});
			const txId = result?.transaction_id ?? '';
			toast.success(
				$i18n.t('Settlement entry created as Draft and linked to the filing') +
					(txId ? ` (ID: ${txId})` : '')
			);
			filingsList?.reload();
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Failed to create settlement entry') + ': ' + msg);
		}
		creating = false;
	};

	// ─── Save filing + export ─────────────────────────────────────────────────────

	const handleSaveFiling = async () => {
		if (!declaration) return;
		saving = true;
		try {
			await saveTaxFiling(companyId, {
				tax_type: 'vat',
				period_start: declaration.period_start,
				period_end: declaration.period_end,
				tax_amount: declaration.grand_total ?? declaration.payable ?? 0,
				currency: declaration.currency,
				details: declaration
			});
			toast.success($i18n.t('Filing saved'));
			filingsList?.reload();
		} catch (err: any) {
			toast.error(`${$i18n.t('Failed to save filing')}: ${err?.detail ?? err}`);
		}
		saving = false;
	};

	const handleExport = async () => {
		if (!declaration) return;
		try {
			await exportTaxWorksheet({
				company_id: companyId,
				tax_type: 'vat',
				period_start: declaration.period_start,
				period_end: declaration.period_end,
				opening_credit: blank(openingCreditInput)
					? undefined
					: parseFloat(String(openingCreditInput)) || 0
			});
		} catch (err: any) {
			toast.error(`${$i18n.t('Failed to export')}: ${err?.detail ?? err}`);
		}
	};

	// Named in the UI language from the kind of tax (VAT, GST…), never with the
	// country's own labels.
	$: taxName = taxTerm($i18n.t, taxConfig);
	$: collectedLabel = $i18n.t('Output {{tax}}', { tax: taxName });
	$: deductibleLabel = $i18n.t('Input {{tax}}', { tax: taxName });
	$: payableLabel = $i18n.t('{{tax}} payable', { tax: taxName });
	$: hasSurcharges = !!declaration && (declaration.surcharges ?? []).length > 0;
	$: periodLabel =
		taxConfig?.filing_frequency === 'quarterly'
			? $i18n.t('Quarter')
			: taxConfig?.filing_frequency === 'yearly'
				? $i18n.t('Fiscal period')
				: $i18n.t('Month');
	$: creditSourceText = (() => {
		const src: string = declaration?.opening_credit_source ?? 'none';
		if (src === 'manual') return $i18n.t('entered manually');
		if (src.startsWith('filing:')) return `${$i18n.t('from the filing ending')} ${src.slice(7)}`;
		if (src.startsWith('computed:'))
			return `${$i18n.t('recomputed from the period ending')} ${src.slice(9)} (${$i18n.t('no filing saved')})`;
		return $i18n.t('no previous period');
	})();
	$: ccy = declaration?.currency ?? '';
	$: hasEntry =
		(declaration?.entry_blockers ?? []).length === 0 &&
		declaration?.suggested_entry?.lines?.length > 0;
	const sum = (lines: any[], key: 'debit' | 'credit') =>
		(lines ?? []).reduce((t, l) => t + (Number(l?.[key]) || 0), 0);
</script>

<div class="flex flex-col gap-4">
	<div class="flex flex-col gap-1">
		<h2 class="text-lg font-semibold">{$i18n.t('{{tax}} return', { tax: taxName })}</h2>
		<p class="text-sm text-muted-foreground">
			{$i18n.t(
				'Calculate {{tax}} (and surcharges) for a period, save it as a filing, and export the worksheet.',
				{ tax: taxName }
			)}
		</p>
	</div>

	{#if loading}
		<div class="flex flex-wrap items-end gap-3">
			<Skeleton class="h-9 w-44" />
			<Skeleton class="h-9 w-44" />
			<Skeleton class="h-9 w-28" />
		</div>
	{:else}
		<!-- Period + credit brought forward + Calculate -->
		<div class="flex flex-wrap items-end gap-3">
			<div class="grid gap-2">
				<Label for="tax-month">{periodLabel}</Label>
				{#if monthOptions.length > 0}
					<NativeSelect.Root id="tax-month" class="min-w-44" bind:value={selectedMonth}>
						{#each monthOptions as opt}
							<NativeSelect.Option value={opt.value}>{opt.label}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				{:else}
					<span class="flex h-9 items-center text-sm text-muted-foreground">
						{$i18n.t('No accounting periods defined')}
					</span>
				{/if}
			</div>
			<div class="grid gap-2">
				<Label for="tax-opening-credit">{$i18n.t('Credit brought forward')}</Label>
				<Input
					id="tax-opening-credit"
					type="number"
					step="0.01"
					class="w-44 text-right tabular-nums"
					bind:value={openingCreditInput}
					placeholder={$i18n.t('from previous filing')}
				/>
			</div>
			<Button
				variant={hasEntry ? 'outline' : 'default'}
				disabled={!selectedMonth || calculating}
				onclick={handleCalculate}
			>
				{#if calculating}<Spinner />{:else}<Calculator />{/if}
				{$i18n.t('Calculate')}
			</Button>
		</div>

		{#if calculating}
			<div
				class="grid grid-cols-[repeat(auto-fit,minmax(min(12.5rem,100%),1fr))] gap-4"
				aria-busy="true"
			>
				{#each Array(4) as _}<Skeleton class="h-[104px] rounded-xl" />{/each}
			</div>
			<Skeleton class="h-64 w-full rounded-xl" />
			<span class="sr-only">{taxName} {$i18n.t('declaration loading...')}</span>
		{/if}

		{#if declaration && !calculating}
			{#if (declaration.warnings ?? []).length > 0}
				<Alert.Root variant="warning">
					<TriangleAlert />
					<Alert.Description>
						{#each declaration.warnings as w}<p>{$i18n.t(w)}</p>{/each}
						<Button variant="link" size="sm" onclick={() => dispatch('gotoAccounts')}
							>{$i18n.t('Open Tax accounts')}</Button
						>
					</Alert.Description>
				</Alert.Root>
			{/if}

			<!-- Summary -->
			<div class="grid grid-cols-[repeat(auto-fit,minmax(min(12.5rem,100%),1fr))] gap-4">
				<KpiCard label={collectedLabel} value={fmt(declaration.collected ?? 0)} />
				<KpiCard label={deductibleLabel} value={fmt(declaration.deductible ?? 0)} />
				<KpiCard
					label={$i18n.t('Credit brought forward')}
					value={fmt(declaration.opening_credit ?? 0)}
				/>
				<KpiCard
					label={hasSurcharges
						? $i18n.t('Total {{tax}} and surcharges', { tax: taxName })
						: payableLabel}
					value={`${ccy ? `${ccy} ` : ''}${fmt(hasSurcharges ? declaration.grand_total : (declaration.payable ?? 0))}`}
				/>
			</div>

			<div class="grid gap-4 lg:grid-cols-2">
				<!-- VAT computation (the return's own arithmetic) -->
				<Card.Root class="gap-4">
					<Card.Header>
						<Card.Title>{$i18n.t('{{tax}} computation', { tax: taxName })}</Card.Title>
					</Card.Header>
					<Card.Content>
						<Table.Root class="text-[13px]">
							<Table.Body>
								<Table.Row class="hover:bg-transparent">
									<Table.Cell class="whitespace-normal">{collectedLabel}</Table.Cell>
									<Table.Cell class="text-right tabular-nums"
										>{fmt(declaration.collected)}</Table.Cell
									>
								</Table.Row>
								<Table.Row class="hover:bg-transparent">
									<Table.Cell class="whitespace-normal"
										>{$i18n.t('Less')}: {deductibleLabel}</Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										>{fmt(declaration.deductible)}</Table.Cell
									>
								</Table.Row>
								<Table.Row class="font-semibold hover:bg-transparent">
									<Table.Cell class="whitespace-normal">{$i18n.t('Net for the period')}</Table.Cell>
									<Table.Cell class="text-right tabular-nums">{fmt(declaration.net)}</Table.Cell>
								</Table.Row>
								<Table.Row class="hover:bg-transparent">
									<Table.Cell class="whitespace-normal">
										{$i18n.t('Credit brought forward')}
										<span class="text-muted-foreground">({creditSourceText})</span>
									</Table.Cell>
									<Table.Cell class="text-right tabular-nums"
										>{fmt(declaration.opening_credit)}</Table.Cell
									>
								</Table.Row>
								<Table.Row class="hover:bg-transparent">
									<Table.Cell class="whitespace-normal"
										>{$i18n.t('Less')}: {$i18n.t('credit used this period')}</Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										>{fmt(declaration.credit_used)}</Table.Cell
									>
								</Table.Row>
								<Table.Row class="bg-muted/50 font-semibold hover:bg-muted/50">
									<Table.Cell class="whitespace-normal">{payableLabel}</Table.Cell>
									<Table.Cell class="text-right tabular-nums">
										{ccy}
										{fmt(declaration.payable)}
									</Table.Cell>
								</Table.Row>
								<Table.Row class="border-b-0 font-medium hover:bg-transparent">
									<Table.Cell class="whitespace-normal">
										{$i18n.t('Credit carried forward')} → {$i18n.t('next period')}
									</Table.Cell>
									<Table.Cell class="text-right tabular-nums">{fmt(declaration.credit)}</Table.Cell>
								</Table.Row>
							</Table.Body>
						</Table.Root>
					</Card.Content>
				</Card.Root>

				<!-- VAT & Surcharges (only when the country levies surcharges) -->
				{#if hasSurcharges}
					<Card.Root class="gap-4">
						<Card.Header>
							<Card.Title>{$i18n.t('{{tax}} and surcharges', { tax: taxName })}</Card.Title>
						</Card.Header>
						<Card.Content>
							<Table.Root class="text-[13px]">
								<Table.Body>
									<Table.Row class="hover:bg-transparent">
										<Table.Cell class="whitespace-normal">{payableLabel}</Table.Cell>
										<Table.Cell class="text-right tabular-nums"
											>{fmt(declaration.payable)}</Table.Cell
										>
									</Table.Row>
									{#each declaration.surcharges as s}
										<Table.Row class="hover:bg-transparent">
											<Table.Cell class="whitespace-normal">
												{$i18n.t(s.label)}
												<span class="text-muted-foreground tabular-nums"
													>({(s.rate * 100).toFixed(2)}%)</span
												>
												{#if s.payable_account}
													<span class="ml-1 font-mono text-xs text-muted-foreground"
														>→ {s.payable_account.code}</span
													>
												{/if}
											</Table.Cell>
											<Table.Cell class="text-right tabular-nums">{fmt(s.amount)}</Table.Cell>
										</Table.Row>
									{/each}
									<Table.Row class="font-semibold hover:bg-transparent">
										<Table.Cell class="whitespace-normal">{$i18n.t('Total surcharges')}</Table.Cell>
										<Table.Cell class="text-right tabular-nums"
											>{fmt(declaration.surcharge_total)}</Table.Cell
										>
									</Table.Row>
									<Table.Row class="border-b-0 bg-muted/50 font-semibold hover:bg-muted/50">
										<Table.Cell class="whitespace-normal"
											>{$i18n.t('Total {{tax}} and surcharges', { tax: taxName })}</Table.Cell
										>
										<Table.Cell class="text-right tabular-nums">
											{ccy}
											{fmt(declaration.grand_total)}
										</Table.Cell>
									</Table.Row>
								</Table.Body>
							</Table.Root>
						</Card.Content>
					</Card.Root>
				{/if}
			</div>

			<!-- Per-account breakdown -->
			<div class="flex flex-col gap-2">
				<h3 class="text-sm font-medium">{$i18n.t('By account')}</h3>
				<div class="overflow-hidden rounded-md border">
					<Table.Root class="text-[13px]">
						<Table.Header class="bg-muted/50">
							<Table.Row class="hover:bg-transparent">
								<Table.Head>{$i18n.t('Account', { context: 'gnos3' })}</Table.Head>
								<Table.Head>{$i18n.t('Role', { context: 'gnos3' })}</Table.Head>
								<Table.Head class="text-right">{$i18n.t('Debit')}</Table.Head>
								<Table.Head class="text-right">{$i18n.t('Credit')}</Table.Head>
								<Table.Head class="text-right">{$i18n.t('Amount')}</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each declaration.detail_collectee ?? [] as d}
								<Table.Row>
									<Table.Cell>
										<span class="font-mono">{d.account_code}</span>
										<span class="text-muted-foreground">{d.account_name}</span>
									</Table.Cell>
									<Table.Cell>{collectedLabel}</Table.Cell>
									<Table.Cell class="text-right tabular-nums">{fmt(d.debit)}</Table.Cell>
									<Table.Cell class="text-right tabular-nums">{fmt(d.credit)}</Table.Cell>
									<Table.Cell class="text-right tabular-nums">{fmt(d.amount)}</Table.Cell>
								</Table.Row>
							{/each}
							{#each declaration.detail_deductible ?? [] as d}
								<Table.Row>
									<Table.Cell>
										<span class="font-mono">{d.account_code}</span>
										<span class="text-muted-foreground">{d.account_name}</span>
									</Table.Cell>
									<Table.Cell>{deductibleLabel}</Table.Cell>
									<Table.Cell class="text-right tabular-nums">{fmt(d.debit)}</Table.Cell>
									<Table.Cell class="text-right tabular-nums">{fmt(d.credit)}</Table.Cell>
									<Table.Cell class="text-right tabular-nums">{fmt(d.amount)}</Table.Cell>
								</Table.Row>
							{/each}
							{#if (declaration.detail_collectee ?? []).length + (declaration.detail_deductible ?? []).length === 0}
								<Table.Row class="hover:bg-transparent">
									<Table.Cell colspan={5} class="py-6 text-center text-muted-foreground">
										{$i18n.t('No {{tax}} accounts mapped for this company.', { tax: taxName })}
										<Button variant="link" size="sm" onclick={() => dispatch('gotoAccounts')}
											>{$i18n.t('Open Tax accounts')}</Button
										>
									</Table.Cell>
								</Table.Row>
							{/if}
						</Table.Body>
					</Table.Root>
				</div>
			</div>

			<!-- Settlement entry: what is missing, or what it will book -->
			{#if (declaration.entry_blockers ?? []).length > 0}
				<Alert.Root variant="warning">
					<TriangleAlert />
					<Alert.Title>{$i18n.t('Settlement entry not available')}</Alert.Title>
					<Alert.Description>
						<ul class="list-disc pl-4">
							{#each declaration.entry_blockers as b}<li>{$i18n.t(b)}</li>{/each}
						</ul>
						<Button
							variant="outline"
							size="sm"
							class="mt-2"
							onclick={() => dispatch('gotoAccounts')}
						>
							{$i18n.t('Open Tax accounts')}
						</Button>
					</Alert.Description>
				</Alert.Root>
			{:else if declaration.suggested_entry?.lines?.length > 0}
				<div class="flex flex-col gap-2">
					<h3 class="text-sm font-medium">{$i18n.t('Suggested Settlement Entry')}</h3>
					<div class="overflow-hidden rounded-md border">
						<Table.Root class="text-[13px]">
							<Table.Header class="bg-muted/50">
								<Table.Row class="hover:bg-transparent">
									<Table.Head>{$i18n.t('Account Code')}</Table.Head>
									<Table.Head>{$i18n.t('Description')}</Table.Head>
									<Table.Head class="text-right">{$i18n.t('Debit')}</Table.Head>
									<Table.Head class="text-right">{$i18n.t('Credit')}</Table.Head>
								</Table.Row>
							</Table.Header>
							<Table.Body>
								{#each declaration.suggested_entry.lines as line}
									<Table.Row>
										<Table.Cell class="font-mono">{line.account_code ?? ''}</Table.Cell>
										<Table.Cell class="whitespace-normal"
											>{line.description ?? line.account_name ?? ''}</Table.Cell
										>
										<Table.Cell class="text-right tabular-nums"
											>{line.debit ? fmt(line.debit) : ''}</Table.Cell
										>
										<Table.Cell class="text-right tabular-nums"
											>{line.credit ? fmt(line.credit) : ''}</Table.Cell
										>
									</Table.Row>
								{/each}
							</Table.Body>
							<Table.Footer>
								<Table.Row class="hover:bg-transparent">
									<Table.Cell colspan={2}>{$i18n.t('Total')}</Table.Cell>
									<Table.Cell class="text-right tabular-nums"
										>{fmt(sum(declaration.suggested_entry.lines, 'debit'))}</Table.Cell
									>
									<Table.Cell class="text-right tabular-nums"
										>{fmt(sum(declaration.suggested_entry.lines, 'credit'))}</Table.Cell
									>
								</Table.Row>
							</Table.Footer>
						</Table.Root>
					</div>
				</div>
			{/if}

			<!-- Actions -->
			<div class="flex flex-wrap gap-2">
				{#if hasEntry}
					<Button disabled={creating} onclick={handleCreateEntry}>
						{#if creating}<Spinner />{/if}
						{creating ? $i18n.t('Creating...') : $i18n.t('Create Settlement Entry (Draft)')}
					</Button>
				{/if}
				<Button variant="outline" disabled={saving} onclick={handleSaveFiling}>
					{#if saving}<Spinner />{:else}<Save />{/if}
					{saving ? $i18n.t('Saving...') : $i18n.t('Save as Filing')}
				</Button>
				<Button variant="outline" onclick={handleExport}>
					<Download />{$i18n.t('Export Excel')}
				</Button>
			</div>
		{/if}

		<TaxFilingsList {companyId} taxType="vat" bind:this={filingsList} on:gotoAccounts />
	{/if}
</div>
