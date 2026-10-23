<script lang="ts">
	import { onMount, getContext, createEventDispatcher } from 'svelte';
	import { toast } from 'svelte-sonner';

	import {
		computeCitDeclaration,
		saveTaxFiling,
		exportTaxWorksheet,
		createTaxEntry,
		getTaxConfig,
		getTaxFilings,
		getAccounts,
		recordProvisionalTaxPayment,
		getBankFxContext,
		getTaxAccounts,
		type CitAdjustment
	} from '$lib/apis/accounting';
	import { fiscalYearStart, fiscalYearEnd, fiscalYearLabel } from '$lib/utils/fiscalYear';
	import { citTerm } from '$lib/utils/taxTerms';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import Info from '@lucide/svelte/icons/info';
	import Plus from '@lucide/svelte/icons/plus';
	import Minus from '@lucide/svelte/icons/minus';
	import X from '@lucide/svelte/icons/x';
	import Download from '@lucide/svelte/icons/download';
	import Save from '@lucide/svelte/icons/save';
	import Calculator from '@lucide/svelte/icons/calculator';
	import Landmark from '@lucide/svelte/icons/landmark';

	import TaxFilingsList from './TaxFilingsList.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let companyId: number;

	// ── Country shape ──────────────────────────────────────────────────
	// The country config says how this tax works: what it is (corporate income
	// tax / Profits Tax, named in the UI language), flat or tiered rates, whether
	// the tax office bills a provisional prepayment, and the company's fiscal year.
	let cfg: any = null;
	$: citLabel = citTerm($i18n.t, cfg);
	$: provisional = !!cfg?.cit_provisional;
	$: fyStartMonth = Number(cfg?.fiscal_year_start_month ?? 1) || 1;

	let calculating = false;
	let saving = false;
	let creating = false;
	let periodStart = '';
	let periodEnd = '';
	// Number inputs yield a number (or null) once typed into — keep them typed loosely
	// and never call string methods on them.
	let priorYearLosses: string | number | null = '0';
	// Blank = let the backend net off the CIT filings already paid inside the period.
	let citAlreadyPaid: string | number | null = '';
	// Blank = read the provisional payments recorded for the year.
	let provisionalPaid: string | number | null = '';
	const blank = (v: any) => v === '' || v === null || v === undefined;
	const num = (v: any) => (blank(v) ? undefined : parseFloat(String(v)) || 0);
	// Hong Kong: only one entity of a connected group may elect the two-tiered rates.
	let twoTier = true;
	$: hasTiers = (cfg?.cit_tiers ?? []).length > 1;
	// The accountant's tax computation: nothing here is inferred.
	let adjustments: CitAdjustment[] = [];
	let result: any = null;
	let filingsList: any;
	let savedFilings: any[] = [];

	// Quick period choices: the last three fiscal years plus the current year to date.
	type Choice = { key: string; label: string; start: string; end: string };
	let choices: Choice[] = [];
	let choice = '';

	const today = () => new Date().toISOString().slice(0, 10);

	const buildChoices = () => {
		const t = today();
		const curStart = fiscalYearStart(t, fyStartMonth);
		const out: Choice[] = [];
		let start = curStart;
		for (let i = 0; i < 4; i++) {
			const end = fiscalYearEnd(start, fyStartMonth);
			const label = fiscalYearLabel(start, end);
			out.push({
				key: start,
				label:
					i === 0
						? `${$i18n.t('FY')} ${label} (${$i18n.t('year to date')})`
						: `${$i18n.t('FY')} ${label}`,
				start,
				end: i === 0 ? t : end
			});
			// previous fiscal year
			const [y, m] = start.split('-').map(Number);
			start = `${y - 1}-${String(m).padStart(2, '0')}-01`;
		}
		choices = out;
		// Default: the last completed year while its return is still being prepared
		// (up to 8 months after year-end), otherwise the current year to date.
		const prev = out[1];
		const monthsSincePrevEnd =
			(new Date(t).getFullYear() - new Date(prev.end).getFullYear()) * 12 +
			(new Date(t).getMonth() - new Date(prev.end).getMonth());
		const pick = cfg?.cit_frequency === 'yearly' && monthsSincePrevEnd <= 8 ? prev : out[0];
		choice = pick.key;
		periodStart = pick.start;
		periodEnd = pick.end;
	};

	const onChoice = () => {
		const c = choices.find((x) => x.key === choice);
		if (!c) return;
		periodStart = c.start;
		periodEnd = c.end;
		prefillFromFiling();
	};

	// A saved filing for the same period carries the adjustments typed last time.
	const prefillFromFiling = () => {
		const f = savedFilings.find(
			(x) => x.period_start === periodStart && x.period_end === periodEnd
		);
		const d = f?.details;
		if (!d) return;
		if (Array.isArray(d.adjustments)) {
			adjustments = d.adjustments.map((a: any) => ({
				label: a.label ?? '',
				amount: Number(a.amount) || 0,
				kind: a.kind === 'deduct' ? 'deduct' : 'add'
			}));
		}
		if (d.prior_year_losses) priorYearLosses = String(d.prior_year_losses);
		if (d.provisional_paid_source === 'manual') provisionalPaid = String(d.provisional_paid ?? '');
		if (typeof d.two_tier === 'boolean') twoTier = d.two_tier;
	};

	const fmt = (v: any): string => {
		const n = typeof v === 'string' ? parseFloat(v) : (v ?? 0);
		return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	};
	const pct = (r: any) =>
		r === null || r === undefined ? '—' : `${(Number(r) * 100).toFixed(2).replace(/\.?0+$/, '')}%`;
	// A slice with a ceiling means the tax went through the jurisdiction's tiers: show them,
	// even when the profit only reached the first one (Hong Kong: 8.25% up to HK$2M).
	const tiered = (tiers: any[] | null | undefined) =>
		(tiers ?? []).some((t) => t.up_to !== null && t.up_to !== undefined);

	// ── Bank accounts for the provisional-tax payment ──────────────────
	let accounts: any[] = [];
	$: parentIds = new Set(accounts.map((a: any) => a.parent_id).filter(Boolean));
	$: bankAccounts = accounts.filter(
		(a: any) => !parentIds.has(a.id) && (!a.account_type || a.account_type === 'asset')
	);
	let provAmount: string | number | null = '';
	let provDate = '';
	let provBank: number | '' = '';
	let provRef = '';
	// Fiscal year the instalment relates to (the year printed on the demand note).
	// Pre-selected from the payment date; the IRD's second instalment is paid
	// after that year's end, so the accountant may pick the previous year.
	let provPeriodEnd = '';
	let recording = false;
	let showProvisional = false;
	// Foreign-currency bank account: the amount debited in its currency and the rate.
	let provFx: any = null;
	let provFcAmount: string | number | null = '';
	let provRate: string | number | null = '';
	let provFxTimer: any = null;
	const refreshProvFx = async () => {
		if (!provBank) {
			provFx = null;
			return;
		}
		try {
			provFx = await getBankFxContext(companyId, {
				bank_account_id: Number(provBank),
				on_date: provDate || undefined,
				amount: num(provAmount),
				bank_fc_amount: num(provFcAmount),
				rate: num(provRate)
			});
		} catch {
			provFx = null;
		}
	};
	$: {
		void [provBank, provDate, provAmount, provFcAmount, provRate];
		clearTimeout(provFxTimer);
		provFxTimer = setTimeout(refreshProvFx, 250);
	}
	$: provForeign = !!provFx?.foreign;

	$: provYears = (() => {
		const t = provDate || today();
		const curStart = fiscalYearStart(t, fyStartMonth);
		const out: Array<{ end: string; label: string }> = [];
		let start = curStart;
		// one year ahead, then this year and three back
		{
			const [y, m] = start.split('-').map(Number);
			const next = `${y + 1}-${String(m).padStart(2, '0')}-01`;
			out.push({
				end: fiscalYearEnd(next, fyStartMonth),
				label: fiscalYearLabel(next, fiscalYearEnd(next, fyStartMonth))
			});
		}
		for (let i = 0; i < 4; i++) {
			const end = fiscalYearEnd(start, fyStartMonth);
			out.push({ end, label: fiscalYearLabel(start, end) });
			const [y, m] = start.split('-').map(Number);
			start = `${y - 1}-${String(m).padStart(2, '0')}-01`;
		}
		return out;
	})();
	// Follow the payment date: every time it changes, pre-select the year it falls in —
	// unless the accountant picked a year themselves (the second instalment is paid after
	// the year-end and belongs to the year before). The date starts as today, so a check
	// that only fired when the year left the list never moved it for a date typed in.
	let provYearPicked = false;
	let provYearFrom = '';
	$: if (provDate && `${provDate}|${fyStartMonth}` !== provYearFrom) {
		provYearFrom = `${provDate}|${fyStartMonth}`;
		if (!provYearPicked || !provYears.some((y) => y.end === provPeriodEnd)) {
			provPeriodEnd = fiscalYearEnd(provDate, fyStartMonth);
		}
	}

	onMount(async () => {
		try {
			cfg = await getTaxConfig(companyId);
		} catch {
			cfg = null;
		}
		try {
			savedFilings = await getTaxFilings({ company_id: companyId, tax_type: 'cit' });
		} catch {
			savedFilings = [];
		}
		try {
			const a = await getAccounts({ company_id: companyId, active: true });
			accounts = Array.isArray(a) ? a : (a?.items ?? a?.accounts ?? []);
		} catch {
			accounts = [];
		}
		buildChoices();
		prefillFromFiling();
		provDate = today();
	});

	// ── Adjustments editor ─────────────────────────────────────────────
	const PRESETS: Array<{ label: string; kind: 'add' | 'deduct' }> = [
		{ label: 'Depreciation per accounts', kind: 'add' },
		{ label: 'Non-deductible expenses (fines, private expenses)', kind: 'add' },
		{ label: 'Entertainment over the deductible limit', kind: 'add' },
		{ label: 'General provisions', kind: 'add' },
		{ label: 'Depreciation allowances (tax)', kind: 'deduct' },
		{ label: 'Bank interest income (exempt)', kind: 'deduct' },
		{ label: 'Dividend income (exempt)', kind: 'deduct' },
		{ label: 'Offshore / non-taxable income', kind: 'deduct' },
		{ label: 'Capital gains (not taxable)', kind: 'deduct' }
	];
	let preset = '';
	const addAdjustment = (kind: 'add' | 'deduct', label = '') => {
		adjustments = [...adjustments, { label, amount: 0, kind }];
	};
	const addPreset = () => {
		const p = PRESETS.find((x) => x.label === preset);
		if (p) addAdjustment(p.kind, $i18n.t(p.label));
		preset = '';
	};
	const removeAdjustment = (i: number) => {
		adjustments = adjustments.filter((_, idx) => idx !== i);
	};

	const payload = () => ({
		period_start: periodStart,
		period_end: periodEnd,
		prior_year_losses: num(priorYearLosses) ?? 0,
		cit_already_paid: num(citAlreadyPaid),
		provisional_paid: num(provisionalPaid),
		adjustments: adjustments
			.filter((a) => Number(a.amount))
			.map((a) => ({ ...a, amount: Number(a.amount) })),
		two_tier: hasTiers ? twoTier : true
	});

	const calc = async () => {
		if (!periodStart || !periodEnd) {
			toast.error($i18n.t('Select a period'));
			return;
		}
		calculating = true;
		result = null;
		try {
			result = await computeCitDeclaration(companyId, payload());
		} catch (err: any) {
			toast.error(`${$i18n.t('Failed to calculate')}: ${err?.detail ?? err}`);
		}
		calculating = false;
	};

	const filingDetails = () => ({ ...result, adjustments: payload().adjustments });

	const createEntry = async () => {
		if (!result?.suggested_entry) return;
		creating = true;
		try {
			const r = await createTaxEntry(companyId, {
				tax_type: 'cit',
				period_start: result.period_start,
				period_end: result.period_end,
				entry: result.suggested_entry,
				tax_amount: result.cit_due ?? 0,
				currency: result.currency,
				details: filingDetails()
			});
			toast.success(
				$i18n.t('Accrual entry created as Draft and linked to the filing') +
					(r?.transaction_id ? ` (ID: ${r.transaction_id})` : '')
			);
			filingsList?.reload();
		} catch (err: any) {
			toast.error(`${$i18n.t('Failed to create accrual entry')}: ${err?.detail ?? err}`);
		}
		creating = false;
	};

	const save = async () => {
		if (!result) return;
		saving = true;
		try {
			await saveTaxFiling(companyId, {
				tax_type: 'cit',
				period_start: result.period_start,
				period_end: result.period_end,
				tax_amount: result.cit_due ?? 0,
				currency: result.currency,
				details: filingDetails()
			});
			toast.success($i18n.t('Filing saved'));
			filingsList?.reload();
			savedFilings = await getTaxFilings({ company_id: companyId, tax_type: 'cit' });
		} catch (err: any) {
			toast.error(`${$i18n.t('Failed to save filing')}: ${err?.detail ?? err}`);
		}
		saving = false;
	};

	const doExport = async () => {
		if (!result) return;
		try {
			const p = payload();
			await exportTaxWorksheet({
				company_id: companyId,
				tax_type: 'cit',
				period_start: result.period_start,
				period_end: result.period_end,
				prior_year_losses: p.prior_year_losses,
				cit_already_paid: p.cit_already_paid,
				provisional_paid: p.provisional_paid,
				adjustments: p.adjustments,
				two_tier: p.two_tier
			});
		} catch (err: any) {
			toast.error(`${$i18n.t('Failed to export')}: ${err?.detail ?? err}`);
		}
	};

	const recordProvisional = async () => {
		const amount = num(provAmount) ?? 0;
		if (!amount || amount <= 0 || !provBank) {
			toast.error($i18n.t('Enter the amount and the bank account'));
			return;
		}
		if (!provPeriodEnd) {
			toast.error($i18n.t('Select the fiscal year the instalment relates to'));
			return;
		}
		if (provForeign && num(provFcAmount) === undefined) {
			toast.error($i18n.t('Enter the amount debited in {{ccy}}', { ccy: provFx.bank_currency }));
			return;
		}
		recording = true;
		try {
			const r = await recordProvisionalTaxPayment(companyId, {
				amount,
				bank_account_id: Number(provBank),
				paid_date: provDate || undefined,
				reference: provRef || undefined,
				period_end: provPeriodEnd,
				bank_fc_amount: provForeign ? num(provFcAmount) : undefined,
				rate: provForeign ? num(provRate) : undefined
			});
			toast.success(
				$i18n.t('Provisional tax payment recorded') +
					(r?.entry_number
						? ` (${r.entry_number})`
						: r?.entry_status === 'draft'
							? ` (${$i18n.t('draft')})`
							: '')
			);
			provAmount = '';
			provRef = '';
			provFcAmount = '';
			provRate = '';
			provYearPicked = false;
			showProvisional = false;
			if (result) await calc();
		} catch (err: any) {
			toast.error(`${err?.detail ?? err}`);
		}
		recording = false;
	};

	// The provisional-payment dialog previews its legs: DR the prepaid-tax account
	// (from Tax → Accounts, read when the dialog opens) / CR the bank.
	let prepaidRole: any = undefined; // undefined = not read yet, null = could not read
	const openProvisional = async () => {
		showProvisional = true;
		try {
			const map = await getTaxAccounts(companyId);
			prepaidRole = (map.roles ?? []).find((r: any) => r.role === 'cit_prepaid') ?? null;
		} catch {
			prepaidRole = null;
		}
	};
	$: prepaidAccount = prepaidRole?.accounts?.[0] ?? null;
	$: prepaidMissing = !!prepaidRole && !prepaidAccount;
	$: provBankAccount =
		provBank === '' ? null : bankAccounts.find((b: any) => b.id === Number(provBank));

	$: hasEntry =
		!!result &&
		(result.entry_blockers ?? []).length === 0 &&
		result.suggested_entry?.lines?.length > 0;
	const sum = (lines: any[], key: 'debit' | 'credit') =>
		(lines ?? []).reduce((t, l) => t + (Number(l?.[key]) || 0), 0);
</script>

<div class="flex flex-col gap-4">
	<div class="flex flex-col gap-1">
		<h2 class="text-lg font-semibold">{citLabel}</h2>
		<p class="text-sm text-muted-foreground">
			{$i18n.t(
				'Accounting profit comes from the ledger. Type the adjustments of the tax computation below (add-backs and deductions); rates and reductions come from Settings → Countries.'
			)}
		</p>
	</div>

	<!-- Period + inputs -->
	<div class="grid grid-cols-[repeat(auto-fill,minmax(min(11rem,100%),1fr))] items-end gap-4">
		<div class="grid gap-2">
			<Label for="cit-fy">{$i18n.t('Fiscal year')}</Label>
			<NativeSelect.Root id="cit-fy" class="w-full" bind:value={choice} onchange={onChoice}>
				{#each choices as c}<NativeSelect.Option value={c.key}>{c.label}</NativeSelect.Option
					>{/each}
				<NativeSelect.Option value="">{$i18n.t('Custom period')}</NativeSelect.Option>
			</NativeSelect.Root>
		</div>
		<div class="grid gap-2">
			<Label for="cit-start">{$i18n.t('Period start')}</Label>
			<Input id="cit-start" type="date" bind:value={periodStart} onchange={() => (choice = '')} />
		</div>
		<div class="grid gap-2">
			<Label for="cit-end">{$i18n.t('Period end')}</Label>
			<Input id="cit-end" type="date" bind:value={periodEnd} onchange={() => (choice = '')} />
		</div>
		<div class="grid gap-2">
			<Label for="cit-losses">{$i18n.t('Losses brought forward')}</Label>
			<Input
				id="cit-losses"
				type="number"
				step="0.01"
				class="text-right tabular-nums"
				bind:value={priorYearLosses}
			/>
		</div>
		{#if provisional}
			<div class="grid gap-2">
				<Label for="cit-prov">{$i18n.t('Provisional tax paid for this year')}</Label>
				<Input
					id="cit-prov"
					type="number"
					step="0.01"
					class="text-right tabular-nums"
					bind:value={provisionalPaid}
					placeholder={$i18n.t('from the ledger')}
				/>
			</div>
		{/if}
		<div class="grid gap-2">
			<Label for="cit-paid">{$i18n.t('{{tax}} already paid', { tax: citLabel })}</Label>
			<Input
				id="cit-paid"
				type="number"
				step="0.01"
				class="text-right tabular-nums"
				bind:value={citAlreadyPaid}
				placeholder={$i18n.t('from paid filings')}
			/>
		</div>
		{#if hasTiers}
			<div class="flex h-9 items-center gap-2">
				<Checkbox id="cit-two-tier" bind:checked={twoTier} />
				<Label for="cit-two-tier" class="font-normal">{$i18n.t('Two-tiered rates elected')}</Label>
				<Tip
					content={$i18n.t(
						'Only one entity of a group of connected entities may elect the two-tiered rates; the others pay the top rate on the whole profit.'
					)}
				>
					<Info class="size-4 text-muted-foreground" aria-hidden="true" />
				</Tip>
			</div>
		{/if}
	</div>

	<!-- Adjustments -->
	<Card.Root class="gap-4">
		<Card.Header>
			<Card.Title>{$i18n.t('Tax computation adjustments')}</Card.Title>
			<Card.Description>
				{$i18n.t(
					'Add back what the tax office refuses (book depreciation, fines…); deduct what it does not tax (bank interest, dividends) and the depreciation allowances.'
				)}
			</Card.Description>
		</Card.Header>
		<Card.Content class="flex flex-col gap-3">
			<div class="flex flex-wrap items-center gap-2">
				<NativeSelect.Root
					size="sm"
					class="max-w-full sm:max-w-80"
					bind:value={preset}
					onchange={addPreset}
					aria-label={$i18n.t('— add a usual line —')}
				>
					<NativeSelect.Option value="">{$i18n.t('— add a usual line —')}</NativeSelect.Option>
					{#each PRESETS as p}<NativeSelect.Option value={p.label}
							>{p.kind === 'add' ? '+' : '−'} {$i18n.t(p.label)}</NativeSelect.Option
						>{/each}
				</NativeSelect.Root>
				<Button variant="outline" size="sm" onclick={() => addAdjustment('add')}>
					<Plus />{$i18n.t('Add-back')}
				</Button>
				<Button variant="outline" size="sm" onclick={() => addAdjustment('deduct')}>
					<Minus />{$i18n.t('Deduction')}
				</Button>
			</div>
			{#if adjustments.length === 0}
				<p class="text-sm text-muted-foreground">
					{$i18n.t('No adjustments — the accounting profit is used as is.')}
				</p>
			{:else}
				<div class="overflow-hidden rounded-md border">
					<Table.Root>
						<Table.Header class="bg-muted/50">
							<Table.Row class="hover:bg-transparent">
								<Table.Head class="w-36">{$i18n.t('Type')}</Table.Head>
								<Table.Head>{$i18n.t('Description')}</Table.Head>
								<Table.Head class="w-44 text-right">{$i18n.t('Amount')}</Table.Head>
								<Table.Head class="w-10"
									><span class="sr-only">{$i18n.t('Remove')}</span></Table.Head
								>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each adjustments as a, i}
								<Table.Row class="hover:bg-transparent">
									<Table.Cell class="py-1.5">
										<NativeSelect.Root
											size="sm"
											class="w-full min-w-28"
											bind:value={a.kind}
											aria-label={$i18n.t('Type')}
										>
											<NativeSelect.Option value="add">{$i18n.t('Add back')}</NativeSelect.Option>
											<NativeSelect.Option value="deduct">{$i18n.t('Deduct')}</NativeSelect.Option>
										</NativeSelect.Root>
									</Table.Cell>
									<Table.Cell class="min-w-48 py-1.5">
										<Input
											type="text"
											class="h-8"
											bind:value={a.label}
											placeholder={$i18n.t('Description')}
											aria-label={$i18n.t('Description')}
										/>
									</Table.Cell>
									<Table.Cell class="py-1.5">
										<Input
											type="number"
											step="0.01"
											class="h-8 min-w-32 text-right tabular-nums"
											bind:value={a.amount}
											aria-label={$i18n.t('Amount')}
										/>
									</Table.Cell>
									<Table.Cell class="py-1.5 text-right">
										<Tip content={$i18n.t('Remove')}>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label={$i18n.t('Remove')}
												onclick={() => removeAdjustment(i)}
											>
												<X />
											</Button>
										</Tip>
									</Table.Cell>
								</Table.Row>
							{/each}
						</Table.Body>
					</Table.Root>
				</div>
			{/if}
		</Card.Content>
	</Card.Root>

	<div class="flex flex-wrap items-center gap-2">
		<Button variant={hasEntry ? 'outline' : 'default'} disabled={calculating} onclick={calc}>
			{#if calculating}<Spinner />{:else}<Calculator />{/if}
			{$i18n.t('Calculate')}
		</Button>
		{#if provisional}
			<Button variant="outline" onclick={openProvisional}>
				<Landmark />{$i18n.t('Record a provisional tax payment')}
			</Button>
		{/if}
	</div>

	{#if calculating}
		<div class="flex flex-col gap-2 rounded-xl border p-4" aria-busy="true">
			<span class="sr-only">{$i18n.t('Calculating...')}</span>
			{#each Array(8) as _}<Skeleton class="h-6 w-full" />{/each}
		</div>
	{/if}

	{#if result && !calculating}
		<Card.Root class="gap-4">
			<Card.Header>
				<Card.Title>{citLabel}</Card.Title>
				<Card.Description class="tabular-nums"
					>{result.period_start} → {result.period_end}</Card.Description
				>
			</Card.Header>
			<Card.Content>
				<Table.Root class="text-[13px]">
					<Table.Body>
						<Table.Row class="hover:bg-transparent">
							<Table.Cell class="whitespace-normal">{$i18n.t('Total Revenue')}</Table.Cell>
							<Table.Cell class="text-right tabular-nums">{fmt(result.revenue)}</Table.Cell>
						</Table.Row>
						<Table.Row class="hover:bg-transparent">
							<Table.Cell class="whitespace-normal">{$i18n.t('Total Cost')}</Table.Cell>
							<Table.Cell class="text-right tabular-nums">{fmt(result.cost)}</Table.Cell>
						</Table.Row>
						<Table.Row class="font-semibold hover:bg-transparent">
							<Table.Cell class="whitespace-normal"
								>{$i18n.t('Profit before tax per accounts')}</Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								>{fmt(result.income_before_tax)}</Table.Cell
							>
						</Table.Row>
						{#if result.booked_tax_added_back}
							<Table.Row class="hover:bg-transparent">
								<Table.Cell class="pl-6 whitespace-normal"
									>{$i18n.t('Add: income tax charged in the accounts')}</Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									>{fmt(result.booked_tax_added_back)}</Table.Cell
								>
							</Table.Row>
						{/if}
						{#each result.adjustments ?? [] as a}
							<Table.Row class="hover:bg-transparent">
								<Table.Cell class="pl-6 whitespace-normal"
									>{a.kind === 'add' ? $i18n.t('Add') : $i18n.t('Less')}: {a.label}</Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									>{a.kind === 'add' ? '' : '−'}{fmt(a.amount)}</Table.Cell
								>
							</Table.Row>
						{/each}
						<Table.Row class="font-semibold hover:bg-transparent">
							<Table.Cell class="whitespace-normal">{$i18n.t('Adjusted profit')}</Table.Cell>
							<Table.Cell class="text-right tabular-nums">{fmt(result.adjusted_profit)}</Table.Cell>
						</Table.Row>
						<Table.Row class="hover:bg-transparent">
							<Table.Cell class="whitespace-normal"
								>{$i18n.t('Less: losses brought forward')}</Table.Cell
							>
							<Table.Cell class="text-right tabular-nums"
								>{fmt(result.prior_year_losses)}</Table.Cell
							>
						</Table.Row>
						<Table.Row class="bg-muted/50 font-semibold hover:bg-muted/50">
							<Table.Cell class="whitespace-normal">{$i18n.t('Assessable profit')}</Table.Cell>
							<Table.Cell class="text-right tabular-nums"
								>{fmt(result.profit_to_declare)}</Table.Cell
							>
						</Table.Row>

						{#if tiered(result.cit_tiers)}
							{#each result.cit_tiers as t}
								<Table.Row class="hover:bg-transparent">
									<Table.Cell class="pl-6 whitespace-normal">
										{citLabel} @ <span class="tabular-nums">{pct(t.rate)}</span>
										{$i18n.t('on')} <span class="tabular-nums">{fmt(t.base)}</span>
										<span class="text-muted-foreground">
											({t.up_to !== null && t.up_to !== undefined
												? $i18n.t('up to {{cap}}', { cap: fmt(t.up_to) })
												: $i18n.t('remainder')})
										</span>
									</Table.Cell>
									<Table.Cell class="text-right tabular-nums">{fmt(t.tax)}</Table.Cell>
								</Table.Row>
							{/each}
							<Table.Row class="font-semibold hover:bg-transparent">
								<Table.Cell class="whitespace-normal"
									>{citLabel} {$i18n.t('before reductions')}</Table.Cell
								>
								<Table.Cell class="text-right tabular-nums">{fmt(result.cit)}</Table.Cell>
							</Table.Row>
						{:else}
							<Table.Row class="hover:bg-transparent">
								<Table.Cell class="whitespace-normal">
									{citLabel} (<span class="tabular-nums"
										>{pct(result.cit_tiers?.[0]?.rate ?? result.cit_rate)}</span
									>)
								</Table.Cell>
								<Table.Cell class="text-right tabular-nums">{fmt(result.cit)}</Table.Cell>
							</Table.Row>
						{/if}
						{#if result.preferential}
							<Table.Row class="hover:bg-transparent">
								<Table.Cell class="whitespace-normal">
									{$i18n.t('Less: preferential exemption')} (<span class="tabular-nums"
										>{pct(result.cit_preferential_rate)}</span
									>)
								</Table.Cell>
								<Table.Cell class="text-right tabular-nums">{fmt(result.preferential)}</Table.Cell>
							</Table.Row>
						{/if}
						{#if result.reduction_rate}
							<Table.Row class="hover:bg-transparent">
								<Table.Cell class="whitespace-normal">
									{$i18n.t('Less: tax reduction')} (<span class="tabular-nums"
										>{pct(result.reduction_rate)}{result.reduction_cap !== null &&
										result.reduction_cap !== undefined
											? `, ${$i18n.t('capped at')} ${fmt(result.reduction_cap)}`
											: ''}</span
									>)
								</Table.Cell>
								<Table.Cell class="text-right tabular-nums">{fmt(result.reduction)}</Table.Cell>
							</Table.Row>
						{/if}
						<Table.Row class="bg-muted/50 font-semibold hover:bg-muted/50">
							<Table.Cell class="whitespace-normal"
								>{citLabel} {$i18n.t('for the period')}</Table.Cell
							>
							<Table.Cell class="text-right tabular-nums">{fmt(result.tax_for_period)}</Table.Cell>
						</Table.Row>
						{#if result.cit_provisional}
							<Table.Row class="hover:bg-transparent">
								<Table.Cell class="whitespace-normal">
									{$i18n.t('Less: provisional tax paid by the year-end')}
									<span class="text-muted-foreground">
										({result.provisional_paid_source === 'payments'
											? $i18n.t('from the payments recorded')
											: result.provisional_paid_source === 'manual'
												? $i18n.t('typed')
												: $i18n.t('no prepaid-tax account mapped')})
									</span>
								</Table.Cell>
								<Table.Cell class="text-right tabular-nums"
									>{fmt(result.provisional_paid)}</Table.Cell
								>
							</Table.Row>
						{/if}
						{#if result.cit_already_paid || !blank(citAlreadyPaid)}
							<Table.Row class="hover:bg-transparent">
								<Table.Cell class="whitespace-normal">
									{$i18n.t('Less: {{tax}} already paid', { tax: citLabel })}
									{#if blank(citAlreadyPaid)}
										<span class="text-muted-foreground"
											>({$i18n.t('paid filings in the period')}:
											<span class="tabular-nums">{fmt(result.cit_paid_from_filings)}</span>)</span
										>
									{/if}
								</Table.Cell>
								<Table.Cell class="text-right tabular-nums"
									>{fmt(result.cit_already_paid)}</Table.Cell
								>
							</Table.Row>
						{/if}
						<Table.Row
							class="bg-muted/50 font-semibold hover:bg-muted/50 {result.provisional_paid_after_year_end
								? ''
								: 'border-b-0'}"
						>
							<Table.Cell class="whitespace-normal">
								{result.cit_due < 0
									? $i18n.t('Refund / carried forward')
									: $i18n.t('Balance at the year-end (the filing amount)')}
							</Table.Cell>
							<Table.Cell class="text-right tabular-nums">
								{result.currency ?? ''}
								{fmt(Math.abs(result.cit_due))}
							</Table.Cell>
						</Table.Row>
						{#if result.provisional_paid_after_year_end}
							<Table.Row class="hover:bg-transparent">
								<Table.Cell class="whitespace-normal text-muted-foreground">
									{$i18n.t(
										'Provisional tax for this year paid after the year-end — set off when the return is settled'
									)}
								</Table.Cell>
								<Table.Cell class="text-right text-muted-foreground tabular-nums"
									>{fmt(result.provisional_paid_after_year_end)}</Table.Cell
								>
							</Table.Row>
							<Table.Row class="border-b-0 font-medium hover:bg-transparent">
								<Table.Cell class="whitespace-normal"
									>{$i18n.t('Left to pay from the bank at settlement')}</Table.Cell
								>
								<Table.Cell class="text-right tabular-nums">
									{result.currency ?? ''}
									{fmt(Math.max(result.cit_due_after_set_off, 0))}
								</Table.Cell>
							</Table.Row>
						{/if}
					</Table.Body>
				</Table.Root>
			</Card.Content>
		</Card.Root>

		{#if (result.warnings ?? []).length > 0}
			<Alert.Root variant="warning">
				<TriangleAlert />
				<Alert.Description>
					{#each result.warnings as w}<p>{$i18n.t(w)}</p>{/each}
				</Alert.Description>
			</Alert.Root>
		{/if}

		{#if (result.entry_blockers ?? []).length > 0}
			<Alert.Root variant="warning">
				<TriangleAlert />
				<Alert.Title>{$i18n.t('Accrual entry not available')}</Alert.Title>
				<Alert.Description>
					<ul class="list-disc pl-4">
						{#each result.entry_blockers as b}<li>{$i18n.t(b)}</li>{/each}
					</ul>
					<Button variant="outline" size="sm" class="mt-2" onclick={() => dispatch('gotoAccounts')}>
						{$i18n.t('Open Tax accounts')}
					</Button>
				</Alert.Description>
			</Alert.Root>
		{:else if result.suggested_entry?.lines?.length > 0}
			<div class="flex flex-col gap-2">
				<h3 class="text-sm font-medium">
					{$i18n.t('Suggested accrual entry')}
					<span class="font-normal text-muted-foreground tabular-nums"
						>({result.suggested_entry.date})</span
					>
				</h3>
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
							{#each result.suggested_entry.lines as line}
								<Table.Row>
									<Table.Cell>
										<span class="font-mono">{line.account_code}</span>
										<span class="text-muted-foreground">{line.account_name ?? ''}</span>
									</Table.Cell>
									<Table.Cell class="whitespace-normal">{line.description ?? ''}</Table.Cell>
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
									>{fmt(sum(result.suggested_entry.lines, 'debit'))}</Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									>{fmt(sum(result.suggested_entry.lines, 'credit'))}</Table.Cell
								>
							</Table.Row>
						</Table.Footer>
					</Table.Root>
				</div>
			</div>
		{/if}

		<div class="flex flex-wrap gap-2">
			{#if result.suggested_entry?.lines?.length > 0}
				<Button disabled={creating} onclick={createEntry}>
					{#if creating}<Spinner />{/if}
					{creating ? $i18n.t('Creating...') : $i18n.t('Create Accrual Entry (Draft)')}
				</Button>
			{/if}
			<Button variant="outline" disabled={saving} onclick={save}>
				{#if saving}<Spinner />{:else}<Save />{/if}
				{saving ? $i18n.t('Saving...') : $i18n.t('Save as Filing')}
			</Button>
			<Button variant="outline" onclick={doExport}>
				<Download />{$i18n.t('Export Excel')}
			</Button>
		</div>
	{/if}

	<TaxFilingsList {companyId} taxType="cit" bind:this={filingsList} on:gotoAccounts />
</div>

{#if provisional}
	<Dialog.Root bind:open={showProvisional}>
		<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
			<Dialog.Header>
				<Dialog.Title>{$i18n.t('Provisional tax payment')}</Dialog.Title>
				<Dialog.Description>
					{$i18n.t(
						"The tax office's demand note asks for a year's tax in advance, usually 75% then 25%. Record each instalment from the note with the year it is for: paid before that year's end it is netted in the year-end accrual; paid after (the second instalment) it is set off when the year's return is settled from the filings list below — never paid twice."
					)}
				</Dialog.Description>
			</Dialog.Header>

			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2">
					<Label for="prov-amount">{$i18n.t('Amount')}</Label>
					<Input
						id="prov-amount"
						type="number"
						step="0.01"
						class="text-right tabular-nums"
						bind:value={provAmount}
					/>
				</div>
				<div class="grid gap-2">
					<Label for="prov-date">{$i18n.t('Paid on')}</Label>
					<Input id="prov-date" type="date" bind:value={provDate} />
				</div>
				<div class="grid gap-2">
					<Label for="prov-fy">{$i18n.t('Provisional tax for')}</Label>
					<NativeSelect.Root
						id="prov-fy"
						class="w-full"
						bind:value={provPeriodEnd}
						onchange={() => (provYearPicked = true)}
					>
						{#each provYears as y}<NativeSelect.Option value={y.end}
								>{$i18n.t('FY')} {y.label} ({$i18n.t('ends')} {y.end})</NativeSelect.Option
							>{/each}
					</NativeSelect.Root>
				</div>
				<div class="grid gap-2">
					<Label for="prov-bank">{$i18n.t('Bank account')}</Label>
					<NativeSelect.Root id="prov-bank" class="w-full" bind:value={provBank}>
						<NativeSelect.Option value="">{$i18n.t('— select —')}</NativeSelect.Option>
						{#each bankAccounts as b}<NativeSelect.Option value={b.id}
								>{b.code} - {b.name}</NativeSelect.Option
							>{/each}
					</NativeSelect.Root>
				</div>
				{#if provForeign}
					<div class="grid gap-2">
						<Label for="prov-fc">{$i18n.t('Amount debited')} ({provFx.bank_currency})</Label>
						<Input
							id="prov-fc"
							type="number"
							step="0.01"
							class="text-right tabular-nums"
							bind:value={provFcAmount}
							placeholder={provFx.bank_fc_suggested != null
								? `${$i18n.t('at the rate')}: ${fmt(provFx.bank_fc_suggested)}`
								: ''}
						/>
					</div>
					<div class="grid gap-2">
						<Label for="prov-rate"
							>{$i18n.t('Rate')} {provFx.bank_currency} → {provFx.base_currency}</Label
						>
						<Input
							id="prov-rate"
							type="number"
							step="0.00000001"
							class="text-right tabular-nums"
							bind:value={provRate}
							placeholder={provFx.rate != null
								? `${provFx.rate} (${provFx.rate_source})`
								: $i18n.t('no rate on file — type it')}
						/>
					</div>
				{/if}
				<div class="grid gap-2 sm:col-span-2">
					<Label for="prov-ref">{$i18n.t('Reference')}</Label>
					<Input
						id="prov-ref"
						type="text"
						class="sm:max-w-64"
						bind:value={provRef}
						placeholder={$i18n.t('demand note no.')}
					/>
				</div>
			</div>

			<!-- What the payment books -->
			<div class="flex flex-col gap-2">
				<span class="text-[13px] font-medium">{$i18n.t('This will book:')}</span>
				{#if prepaidRole === undefined}
					<div class="flex flex-col gap-2 rounded-md border p-3">
						{#each Array(2) as _}<Skeleton class="h-6 w-full" />{/each}
					</div>
				{:else}
					<div class="overflow-hidden rounded-md border">
						<Table.Root class="text-[13px]">
							<Table.Body>
								<Table.Row class="hover:bg-transparent">
									<Table.Cell class="w-10 py-1.5 text-muted-foreground">DR</Table.Cell>
									<Table.Cell class="py-1.5 whitespace-normal">
										{#if prepaidAccount}
											<span class="font-mono">{prepaidAccount.code}</span>
											{prepaidAccount.name}
										{:else}
											<span class="inline-flex items-center gap-1 text-destructive">
												<CircleAlert class="size-3.5" />{$i18n.t('— not mapped —')}
											</span>
										{/if}
										{#if prepaidRole?.label}
											<span class="block text-xs text-muted-foreground"
												>{$i18n.t(prepaidRole.label)}</span
											>
										{/if}
									</Table.Cell>
									<Table.Cell class="py-1.5 text-right tabular-nums"
										>{fmt(num(provAmount) ?? 0)}</Table.Cell
									>
								</Table.Row>
								{#if !provForeign}
									<Table.Row class="border-b-0 hover:bg-transparent">
										<Table.Cell class="py-1.5 text-muted-foreground">CR</Table.Cell>
										<Table.Cell class="py-1.5 whitespace-normal">
											{#if provBankAccount}
												<span class="font-mono">{provBankAccount.code}</span>
												{provBankAccount.name}
											{:else}
												<span class="text-muted-foreground">{$i18n.t('Bank account')}</span>
											{/if}
										</Table.Cell>
										<Table.Cell class="py-1.5 text-right tabular-nums"
											>{fmt(num(provAmount) ?? 0)}</Table.Cell
										>
									</Table.Row>
								{/if}
							</Table.Body>
						</Table.Root>
					</div>
				{/if}
				{#if provForeign}
					{#if provFx.missing?.length}
						<Alert.Root variant="warning">
							<TriangleAlert />
							<Alert.Title>{$i18n.t('Missing')}: {provFx.missing.join(' · ')}</Alert.Title>
						</Alert.Root>
					{:else}
						<p class="text-[13px] text-muted-foreground">
							{$i18n.t(
								'Booked in {{base}} through the exchange clearing account, then moved to the bank in {{ccy}}.',
								{ base: provFx.base_currency, ccy: provFx.bank_currency }
							)}
							{#if provFx.fx_kind}
								{$i18n.t(provFx.fx_kind === 'loss' ? 'Exchange loss' : 'Exchange gain')}:
								<span class="tabular-nums"
									>{fmt(Math.abs(provFx.fx_base))} {provFx.base_currency}</span
								>
								→ {provFx.fx_account ? `${provFx.fx_account.code} ${provFx.fx_account.name}` : ''}
							{/if}
						</p>
					{/if}
				{/if}
				{#if prepaidMissing}
					<Alert.Root variant="warning">
						<TriangleAlert />
						<Alert.Title
							>{$i18n.t('Missing')}: {$i18n.t(prepaidRole?.label ?? 'cit_prepaid')}</Alert.Title
						>
						<Alert.Description>
							<Button
								variant="link"
								size="sm"
								onclick={() => {
									showProvisional = false;
									dispatch('gotoAccounts');
								}}>{$i18n.t('Open Tax accounts')}</Button
							>
						</Alert.Description>
					</Alert.Root>
				{/if}
			</div>

			<Dialog.Footer>
				<Button variant="outline" onclick={() => (showProvisional = false)}
					>{$i18n.t('Cancel')}</Button
				>
				<Button disabled={recording || prepaidMissing} onclick={recordProvisional}>
					{#if recording}<Spinner />{/if}
					{recording ? $i18n.t('Recording...') : $i18n.t('Record payment')}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}
