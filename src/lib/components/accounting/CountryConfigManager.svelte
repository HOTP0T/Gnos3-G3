<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	import Plus from '@lucide/svelte/icons/plus';
	import Globe from '@lucide/svelte/icons/globe';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';

	import { getCountryConfigs, updateCountryConfig } from '$lib/apis/accounting';
	import { CIT_KIND_TERMS, TAX_KIND_TERMS } from '$lib/utils/taxTerms';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as InputGroup from '$lib/components/ui/input-group/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';

	const i18n: any = getContext('i18n');

	let loading = true;
	let loadError = '';
	let saving = false;
	let configs: any[] = [];
	let selected = '';
	let form: any = null;
	let newCountryName = '';

	const FREQ = ['monthly', 'quarterly', 'yearly'];
	const FREQ_LABELS: Record<string, string> = { monthly: 'Monthly', quarterly: 'Quarterly', yearly: 'Yearly' };
	// What the taxes are: screens and the books name them from these, in their
	// own language. The official names below are the country's, kept for reference.
	const TAX_KINDS = Object.keys(TAX_KIND_TERMS);
	const CIT_KINDS = Object.keys(CIT_KIND_TERMS);

	// Rates are stored as decimals (0.20) but shown/edited as percentages (20).
	const pct = (v: any) =>
		v === null || v === undefined || v === '' ? '' : +(Number(v) * 100).toFixed(6);
	const dec = (v: any) => (v === '' || v === null || v === undefined ? null : Number(v) / 100);

	function toForm(c: any) {
		return {
			country: c.country,
			tax_kind: c.tax_kind ?? 'vat',
			cit_kind: c.cit_kind ?? 'cit',
			tax_name: c.tax_name ?? '',
			tax_name_full: c.tax_name_full ?? '',
			currency: c.currency ?? '',
			filing_frequency: c.filing_frequency ?? 'monthly',
			vat_standard_rate: pct(c.vat_standard_rate),
			vat_reduced_rates: (c.vat_reduced_rates ?? [])
				.map((r: number) => +(Number(r) * 100).toFixed(6))
				.join(', '),
			collected_pattern: c.collected_pattern ?? '',
			deductible_pattern: c.deductible_pattern ?? '',
			settlement_payable_code: c.settlement_payable_code ?? '',
			settlement_receivable_code: c.settlement_receivable_code ?? '',
			collected_label: c.collected_label ?? '',
			deductible_label: c.deductible_label ?? '',
			payable_label: c.payable_label ?? '',
			receivable_label: c.receivable_label ?? '',
			declaration_label: c.declaration_label ?? '',
			surcharge_urban_rate: pct(c.surcharge_urban_rate),
			surcharge_education_rate: pct(c.surcharge_education_rate),
			surcharge_local_education_rate: pct(c.surcharge_local_education_rate),
			cit_rate: pct(c.cit_rate),
			cit_preferential_rate: pct(c.cit_preferential_rate),
			ir_rate: pct(c.ir_rate),
			// Jurisdiction shape (Hong Kong: no VAT, tiered profits tax with provisional prepayments, MPF)
			has_vat: c.has_vat !== false,
			cit_label: c.cit_label ?? '',
			cit_frequency: c.cit_frequency ?? 'yearly',
			cit_tiers: (c.cit_tiers ?? [])
				.map((t: any) => `${t.up_to ?? ''}:${+(Number(t.rate) * 100).toFixed(6)}`)
				.join(', '),
			cit_reduction_rate: pct(c.cit_reduction_rate),
			cit_reduction_cap: c.cit_reduction_cap ?? '',
			cit_provisional: !!c.cit_provisional,
			tax_year_start_month: Number(c.tax_year_start_month ?? 1) || 1,
			withholds_iit: c.withholds_iit !== false,
			payroll_scheme: c.payroll_scheme ?? ''
		};
	}

	// "2000000:8.25, :16.5" → [{up_to: 2000000, rate: 0.0825}, {up_to: null, rate: 0.165}]
	function parseTiers(raw: string): any[] | null {
		const tiers = String(raw ?? '')
			.split(',')
			.map((s) => s.trim())
			.filter(Boolean)
			.map((s) => {
				const [cap, rate] = s.split(':').map((x) => x.trim());
				const r = Number(rate) / 100;
				if (isNaN(r)) return null;
				return { up_to: cap === '' ? null : Number(cap), rate: r };
			})
			.filter(Boolean);
		return tiers.length ? tiers : null;
	}

	function selectCountry() {
		const c = configs.find((x) => x.country === selected);
		form = c ? toForm(c) : null;
	}

	const load = async () => {
		loading = true;
		loadError = '';
		try {
			const res = await getCountryConfigs();
			configs = Array.isArray(res) ? res : [];
			if (configs.length && !configs.some((c) => c.country === selected)) {
				selected = configs[0].country;
			}
			selectCountry();
		} catch (err: any) {
			loadError = `${err?.detail ?? err}`;
			toast.error(`${$i18n.t('Failed to load country settings')}: ${err?.detail ?? err}`);
		}
		loading = false;
	};

	const addCountry = () => {
		const name = newCountryName.trim();
		if (!name) return;
		const existing = configs.find((c) => c.country.toLowerCase() === name.toLowerCase());
		if (existing) {
			selected = existing.country;
		} else {
			const blank = {
				country: name,
				tax_name: 'VAT',
				currency: 'USD',
				filing_frequency: 'monthly',
				vat_reduced_rates: []
			};
			configs = [...configs, blank].sort((a, b) => a.country.localeCompare(b.country));
			selected = name;
		}
		newCountryName = '';
		selectCountry();
	};

	const save = async () => {
		if (!form) return;
		saving = true;
		try {
			const reduced = String(form.vat_reduced_rates || '')
				.split(',')
				.map((s) => s.trim())
				.filter(Boolean)
				.map((s) => Number(s) / 100)
				.filter((n) => !isNaN(n));
			const payload = {
				tax_kind: form.tax_kind || 'vat',
				cit_kind: form.cit_kind || 'cit',
				tax_name: form.tax_name || form.country,
				tax_name_full: form.tax_name_full || null,
				currency: form.currency || 'USD',
				filing_frequency: form.filing_frequency || 'monthly',
				vat_standard_rate: dec(form.vat_standard_rate) ?? 0,
				vat_reduced_rates: reduced,
				collected_pattern: form.collected_pattern || null,
				deductible_pattern: form.deductible_pattern || null,
				settlement_payable_code: form.settlement_payable_code || null,
				settlement_receivable_code: form.settlement_receivable_code || null,
				collected_label: form.collected_label || null,
				deductible_label: form.deductible_label || null,
				payable_label: form.payable_label || null,
				receivable_label: form.receivable_label || null,
				declaration_label: form.declaration_label || null,
				surcharge_urban_rate: dec(form.surcharge_urban_rate) ?? 0,
				surcharge_education_rate: dec(form.surcharge_education_rate) ?? 0,
				surcharge_local_education_rate: dec(form.surcharge_local_education_rate) ?? 0,
				cit_rate: dec(form.cit_rate),
				cit_preferential_rate: dec(form.cit_preferential_rate),
				ir_rate: dec(form.ir_rate),
				has_vat: !!form.has_vat,
				cit_label: form.cit_label || null,
				cit_frequency: form.cit_frequency || 'yearly',
				cit_tiers: parseTiers(form.cit_tiers),
				cit_reduction_rate: dec(form.cit_reduction_rate),
				cit_reduction_cap:
					form.cit_reduction_cap === '' || form.cit_reduction_cap === null
						? null
						: Number(form.cit_reduction_cap),
				cit_provisional: !!form.cit_provisional,
				tax_year_start_month: Number(form.tax_year_start_month) || 1,
				withholds_iit: !!form.withholds_iit,
				payroll_scheme: form.payroll_scheme || null
			};
			const updated = await updateCountryConfig(form.country, payload);
			const idx = configs.findIndex((c) => c.country === form.country);
			if (idx >= 0) configs[idx] = updated;
			else configs = [...configs, updated];
			configs = configs;
			toast.success($i18n.t('Country settings saved'));
		} catch (err: any) {
			toast.error(`${$i18n.t('Failed to save country settings')}: ${err?.detail ?? err}`);
		}
		saving = false;
	};

	onMount(load);

	// Settings rows (design system → Settings): label and description on the left, control on the right
	const rowCls = 'flex flex-col gap-2 py-3 sm:flex-row sm:items-center sm:justify-between sm:gap-6';
	const switchRowCls = 'flex items-center gap-3 py-3';
	const labelColCls = 'grid min-w-0 gap-1';
	const descCls = 'text-sm text-muted-foreground';
	const textCls = 'w-full sm:w-72 sm:shrink-0';
	const shortCls = 'w-full sm:w-40 sm:shrink-0';
	const pctCls = 'h-9 w-full sm:w-40 sm:shrink-0';
	const numCls = 'text-right tabular-nums';
	const cardHeaderCls = 'border-b py-4 [.border-b]:pb-4';
</script>

<div class="flex max-w-4xl flex-col gap-4">
	<div class="grid max-w-3xl gap-1">
		<h2 class="text-lg font-semibold">{$i18n.t('Countries')}</h2>
		<p class="text-sm text-muted-foreground">
			{$i18n.t(
				'Per-country tax parameters. These drive the tax module (VAT, corporate and individual income tax) and override the built-in defaults. Rates are entered as percentages.'
			)}
		</p>
	</div>

	{#if loading}
		<div class="flex flex-wrap items-end gap-3">
			<Skeleton class="h-9 w-64" />
			<Skeleton class="h-9 w-56" />
		</div>
		{#each Array(2) as _}
			<Card.Root>
				<Card.Header><Skeleton class="h-5 w-40" /></Card.Header>
				<Card.Content class="flex flex-col gap-4">
					{#each Array(3) as __}
						<div class="flex items-center justify-between gap-6">
							<Skeleton class="h-4 w-48" />
							<Skeleton class="h-9 w-56" />
						</div>
					{/each}
				</Card.Content>
			</Card.Root>
		{/each}
	{:else if loadError}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Failed to load country settings')}</Alert.Title>
			<Alert.Description>
				<p>{loadError}</p>
				<Button variant="outline" size="sm" class="mt-2" onclick={load}>
					<RotateCcw />{$i18n.t('Retry')}
				</Button>
			</Alert.Description>
		</Alert.Root>
	{:else}
		<!-- Country picker + add -->
		<div class="flex flex-wrap items-end gap-3">
			<div class="grid w-full gap-2 sm:w-auto">
				<Label for="cc-country">{$i18n.t('Country')}</Label>
				<NativeSelect.Root
					id="cc-country"
					class="w-full sm:w-64"
					value={selected}
					onchange={(e: Event) => {
						selected = (e.currentTarget as HTMLSelectElement).value;
						selectCountry();
					}}
				>
					{#each configs as c}
						<NativeSelect.Option value={c.country}>{c.country}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
			</div>
			<div class="flex w-full items-center gap-2 sm:w-auto">
				<Input
					class="sm:w-52"
					bind:value={newCountryName}
					placeholder={$i18n.t('Add country…')}
					aria-label={$i18n.t('Add country…')}
					onkeydown={(e: KeyboardEvent) => e.key === 'Enter' && addCountry()}
				/>
				<Button variant="outline" onclick={addCountry}>
					<Plus />{$i18n.t('Add')}
				</Button>
			</div>
		</div>

		{#if form}
			<!-- General -->
			<Card.Root class="gap-0 py-0">
				<Card.Header class={cardHeaderCls}>
					<Card.Title>{$i18n.t('General')}</Card.Title>
				</Card.Header>
				<Card.Content class="divide-y">
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-taxkind">{$i18n.t('Tax type')}</Label>
							<p class={descCls}>
								{$i18n.t('How screens and entries name this tax, in their own language.')}
							</p>
						</div>
						<NativeSelect.Root id="cc-taxkind" class={shortCls} bind:value={form.tax_kind}>
							{#each TAX_KINDS as k}<NativeSelect.Option value={k}
									>{$i18n.t(TAX_KIND_TERMS[k])}</NativeSelect.Option
								>{/each}
						</NativeSelect.Root>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-taxname">{$i18n.t('Official tax name')}</Label>
							<p class={descCls}>{$i18n.t("In the country's language, for reference")}</p>
						</div>
						<Input
							id="cc-taxname"
							class={textCls}
							bind:value={form.tax_name}
							placeholder="TVA / VAT / 增值税"
						/>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-taxnamefull">{$i18n.t('Official full name')}</Label>
						</div>
						<Input id="cc-taxnamefull" class={textCls} bind:value={form.tax_name_full} />
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-currency">{$i18n.t('Currency')}</Label>
						</div>
						<Input
							id="cc-currency"
							class={shortCls}
							bind:value={form.currency}
							maxlength={3}
							placeholder="EUR"
						/>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-freq">{$i18n.t('Filing frequency')}</Label>
						</div>
						<NativeSelect.Root id="cc-freq" class={shortCls} bind:value={form.filing_frequency}>
							{#each FREQ as f}<NativeSelect.Option value={f}>{$i18n.t(FREQ_LABELS[f])}</NativeSelect.Option
								>{/each}
						</NativeSelect.Root>
					</div>
				</Card.Content>
			</Card.Root>

			<!-- VAT -->
			<Card.Root class="gap-0 py-0">
				<Card.Header class={cardHeaderCls}>
					<Card.Title>{$i18n.t('VAT / Sales tax')}</Card.Title>
				</Card.Header>
				<Card.Content class="divide-y">
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-vat">{$i18n.t('Standard rate')}</Label>
						</div>
						<InputGroup.Root class={pctCls}>
							<InputGroup.Input
								id="cc-vat"
								type="number"
								step="0.01"
								class={numCls}
								bind:value={form.vat_standard_rate}
							/>
							<InputGroup.Addon align="inline-end">%</InputGroup.Addon>
						</InputGroup.Root>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-reduced">{$i18n.t('Reduced rates')}</Label>
							<p class={descCls}>{$i18n.t('comma-separated')}</p>
						</div>
						<InputGroup.Root class="h-9 w-full sm:w-72 sm:shrink-0">
							<InputGroup.Input
								id="cc-reduced"
								class={numCls}
								bind:value={form.vat_reduced_rates}
								placeholder="10, 5.5, 2.1"
							/>
							<InputGroup.Addon align="inline-end">%</InputGroup.Addon>
						</InputGroup.Root>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-colpat">{$i18n.t('Collected acct pattern')}</Label>
						</div>
						<Input
							id="cc-colpat"
							class="{shortCls} font-mono text-[13px] md:text-[13px]"
							bind:value={form.collected_pattern}
							placeholder="4457%"
						/>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-dedpat">{$i18n.t('Deductible acct pattern')}</Label>
						</div>
						<Input
							id="cc-dedpat"
							class="{shortCls} font-mono text-[13px] md:text-[13px]"
							bind:value={form.deductible_pattern}
							placeholder="4456%"
						/>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-payc">{$i18n.t('Settlement payable code')}</Label>
						</div>
						<Input
							id="cc-payc"
							class="{shortCls} font-mono text-[13px] md:text-[13px]"
							bind:value={form.settlement_payable_code}
							placeholder="4455"
						/>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-recc">{$i18n.t('Settlement receivable code')}</Label>
						</div>
						<Input
							id="cc-recc"
							class="{shortCls} font-mono text-[13px] md:text-[13px]"
							bind:value={form.settlement_receivable_code}
						/>
					</div>
					<p class="{descCls} py-3">
						{$i18n.t(
							"Official terms in the country's language, kept for reference. Screens use the Gnos3 language; entries use each company's books language."
						)}
					</p>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-lcol">{$i18n.t('Collected label')}</Label>
						</div>
						<Input id="cc-lcol" class={textCls} bind:value={form.collected_label} />
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-lded">{$i18n.t('Deductible label')}</Label>
						</div>
						<Input id="cc-lded" class={textCls} bind:value={form.deductible_label} />
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-lpay">{$i18n.t('Payable label')}</Label>
						</div>
						<Input id="cc-lpay" class={textCls} bind:value={form.payable_label} />
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-lrec">{$i18n.t('Receivable label')}</Label>
						</div>
						<Input id="cc-lrec" class={textCls} bind:value={form.receivable_label} />
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-ldec">{$i18n.t('Declaration label')}</Label>
						</div>
						<Input id="cc-ldec" class={textCls} bind:value={form.declaration_label} />
					</div>
				</Card.Content>
			</Card.Root>

			<!-- Surcharges -->
			<Card.Root class="gap-0 py-0">
				<Card.Header class={cardHeaderCls}>
					<Card.Title>{$i18n.t('VAT surcharges')}</Card.Title>
					<Card.Description>
						{$i18n.t(
							'Levied on VAT payable (e.g. China urban-construction / education / local-education).'
						)}
					</Card.Description>
				</Card.Header>
				<Card.Content class="divide-y">
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-su">{$i18n.t('Urban construction')}</Label>
						</div>
						<InputGroup.Root class={pctCls}>
							<InputGroup.Input
								id="cc-su"
								type="number"
								step="0.01"
								class={numCls}
								bind:value={form.surcharge_urban_rate}
							/>
							<InputGroup.Addon align="inline-end">%</InputGroup.Addon>
						</InputGroup.Root>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-se">{$i18n.t('Education surcharge')}</Label>
						</div>
						<InputGroup.Root class={pctCls}>
							<InputGroup.Input
								id="cc-se"
								type="number"
								step="0.01"
								class={numCls}
								bind:value={form.surcharge_education_rate}
							/>
							<InputGroup.Addon align="inline-end">%</InputGroup.Addon>
						</InputGroup.Root>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-sl">{$i18n.t('Local education surcharge')}</Label>
						</div>
						<InputGroup.Root class={pctCls}>
							<InputGroup.Input
								id="cc-sl"
								type="number"
								step="0.01"
								class={numCls}
								bind:value={form.surcharge_local_education_rate}
							/>
							<InputGroup.Addon align="inline-end">%</InputGroup.Addon>
						</InputGroup.Root>
					</div>
				</Card.Content>
			</Card.Root>

			<!-- Jurisdiction shape -->
			<Card.Root class="gap-0 py-0">
				<Card.Header class={cardHeaderCls}>
					<Card.Title>{$i18n.t('What this country levies')}</Card.Title>
					<Card.Description>
						{$i18n.t(
							'Hong Kong: no VAT, a yearly two-tier Profits Tax with provisional prepayments, no salary withholding, MPF. Everything below is read by the Tax tab, the booking engine and the closing checklist.'
						)}
					</Card.Description>
				</Card.Header>
				<Card.Content class="divide-y">
					<div class={switchRowCls}>
						<Checkbox id="cc-hasvat" bind:checked={form.has_vat} />
						<Label for="cc-hasvat" class="leading-snug">{$i18n.t('Levies VAT / GST')}</Label>
					</div>
					<div class={switchRowCls}>
						<Checkbox id="cc-iit" bind:checked={form.withholds_iit} />
						<Label for="cc-iit" class="leading-snug"
							>{$i18n.t('Employer withholds personal income tax')}</Label
						>
					</div>
					<div class={switchRowCls}>
						<Checkbox id="cc-prov" bind:checked={form.cit_provisional} />
						<Label for="cc-prov" class="leading-snug"
							>{$i18n.t('Tax office bills provisional (prepaid) income tax')}</Label
						>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-tysm">{$i18n.t('Year of assessment starts in month')}</Label>
							<p class={descCls}>1–12</p>
						</div>
						<Input
							id="cc-tysm"
							type="number"
							min="1"
							max="12"
							class="w-full sm:w-24 sm:shrink-0 {numCls}"
							bind:value={form.tax_year_start_month}
						/>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-payroll">{$i18n.t('Mandatory pension scheme')}</Label>
						</div>
						<NativeSelect.Root id="cc-payroll" class={shortCls} bind:value={form.payroll_scheme}>
							<NativeSelect.Option value="">{$i18n.t('— none —')}</NativeSelect.Option>
							<NativeSelect.Option value="mpf">{$i18n.t('MPF (Hong Kong)')}</NativeSelect.Option>
						</NativeSelect.Root>
					</div>
				</Card.Content>
			</Card.Root>

			<!-- Income taxes -->
			<Card.Root class="gap-0 py-0">
				<Card.Header class={cardHeaderCls}>
					<Card.Title>{$i18n.t('Income taxes')}</Card.Title>
				</Card.Header>
				<Card.Content class="divide-y">
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-citkind">{$i18n.t('Corporate tax type')}</Label>
						</div>
						<NativeSelect.Root id="cc-citkind" class={textCls} bind:value={form.cit_kind}>
							{#each CIT_KINDS as k}<NativeSelect.Option value={k}
									>{$i18n.t(CIT_KIND_TERMS[k])}</NativeSelect.Option
								>{/each}
						</NativeSelect.Root>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-citlabel">{$i18n.t('Official corporate tax name')}</Label>
							<p class={descCls}>{$i18n.t("In the country's language, for reference")}</p>
						</div>
						<Input
							id="cc-citlabel"
							type="text"
							class={textCls}
							placeholder="IS / 企业所得税 / Profits Tax"
							bind:value={form.cit_label}
						/>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-citfreq">{$i18n.t('Computed')}</Label>
						</div>
						<NativeSelect.Root id="cc-citfreq" class={textCls} bind:value={form.cit_frequency}>
							<NativeSelect.Option value="yearly">{$i18n.t('Yearly')}</NativeSelect.Option>
							<NativeSelect.Option value="quarterly"
								>{$i18n.t('Quarterly (cumulative prepayments)')}</NativeSelect.Option
							>
						</NativeSelect.Root>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-cit">{$i18n.t('Corporate income tax rate')}</Label>
						</div>
						<InputGroup.Root class={pctCls}>
							<InputGroup.Input
								id="cc-cit"
								type="number"
								step="0.01"
								class={numCls}
								bind:value={form.cit_rate}
							/>
							<InputGroup.Addon align="inline-end">%</InputGroup.Addon>
						</InputGroup.Root>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-tiers">{$i18n.t('Tiered rates')}</Label>
							<p class={descCls}>up_to:rate%, …</p>
						</div>
						<Input
							id="cc-tiers"
							type="text"
							class="{textCls} tabular-nums"
							placeholder="2000000:8.25, :16.5"
							bind:value={form.cit_tiers}
						/>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-citp">{$i18n.t('CIT preferential rate')}</Label>
						</div>
						<InputGroup.Root class={pctCls}>
							<InputGroup.Input
								id="cc-citp"
								type="number"
								step="0.01"
								class={numCls}
								bind:value={form.cit_preferential_rate}
							/>
							<InputGroup.Addon align="inline-end">%</InputGroup.Addon>
						</InputGroup.Root>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-red">{$i18n.t('One-off tax reduction')}</Label>
						</div>
						<InputGroup.Root class={pctCls}>
							<InputGroup.Input
								id="cc-red"
								type="number"
								step="0.01"
								class={numCls}
								bind:value={form.cit_reduction_rate}
							/>
							<InputGroup.Addon align="inline-end">%</InputGroup.Addon>
						</InputGroup.Root>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-redcap">{$i18n.t('Reduction cap (amount)')}</Label>
						</div>
						<Input
							id="cc-redcap"
							type="number"
							step="0.01"
							class="{shortCls} {numCls}"
							bind:value={form.cit_reduction_cap}
						/>
					</div>
					<div class={rowCls}>
						<div class={labelColCls}>
							<Label for="cc-ir">{$i18n.t('Individual income tax rate')}</Label>
						</div>
						<InputGroup.Root class={pctCls}>
							<InputGroup.Input
								id="cc-ir"
								type="number"
								step="0.01"
								class={numCls}
								bind:value={form.ir_rate}
							/>
							<InputGroup.Addon align="inline-end">%</InputGroup.Addon>
						</InputGroup.Root>
					</div>
				</Card.Content>
			</Card.Root>

			<!-- Save once, at the end; kept in view while scrolling -->
			<div
				class="sticky bottom-0 z-10 flex items-center justify-between gap-3 border-t bg-background py-3"
			>
				<span class="min-w-0 truncate text-sm text-muted-foreground">{form.country}</span>
				<Button onclick={save} disabled={saving}>
					{#if saving}<Spinner />{/if}
					{saving ? $i18n.t('Saving...') : $i18n.t('Save')}
				</Button>
			</div>
		{:else}
			<Empty.Root class="border">
				<Empty.Header>
					<Empty.Media variant="icon"><Globe /></Empty.Media>
					<Empty.Title>{$i18n.t('No country selected.')}</Empty.Title>
					<Empty.Description>
						{$i18n.t('Add a country above to set its tax parameters.')}
					</Empty.Description>
				</Empty.Header>
			</Empty.Root>
		{/if}
	{/if}
</div>
