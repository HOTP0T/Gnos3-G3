<script lang="ts">
	import { getContext, createEventDispatcher, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { MONTH_NAMES } from '$lib/utils/fiscalYear';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import ImageUp from '@lucide/svelte/icons/image-up';
	import Trash2 from '@lucide/svelte/icons/trash-2';

	import {
		createCompany,
		updateCompany,
		getChartTemplates,
		getPeriodTemplates,
		uploadCompanyLogo,
		deleteCompanyLogo
	} from '$lib/apis/accounting';
	import CompanyLogo from '$lib/components/accounting/CompanyLogo.svelte';
	import {
		LOGO_ACCEPT,
		MAX_LOGO_FILE_BYTES,
		prepareLogoFile
	} from '$lib/components/accounting/companyLogo';

	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;
	export let company: any = null;
	export let onSave: (() => void) | null = null;

	// Form state
	let name = '';
	let country = '';
	let currency = 'USD';
	let description = '';
	// Month the fiscal year starts: 1 = calendar year, 4 = April – March (usual in Hong Kong).
	let fiscalYearStartMonth = 1;
	// Language of the text the system writes into this company's books (entry
	// descriptions, line labels, the tax worksheet). Each language in its own name.
	const BOOKS_LANGUAGES = [
		{ value: 'en', label: 'English' },
		{ value: 'fr-FR', label: 'Français' },
		{ value: 'es-ES', label: 'Español' },
		{ value: 'pt-PT', label: 'Português (Portugal)' },
		{ value: 'pt-BR', label: 'Português (Brasil)' },
		{ value: 'zh-CN', label: '简体中文' },
		{ value: 'zh-TW', label: '繁體中文' }
	];
	let booksLanguage = 'en';
	let chart_template_id: number | null = null;
	let period_template_id: number | null = null;

	let submitting = false;
	let loadingTemplates = false;
	let createdCompany: any = null;

	// Logo: a picked file is shrunk to a PNG in the browser, previewed, and uploaded with Save.
	let logoInput: HTMLInputElement;
	let logoFile: Blob | null = null;
	let logoPreview: string | null = null;
	let logoRemoved = false;
	let preparingLogo = false;

	// undefined = show the saved logo; null = none
	$: logoSrc = logoPreview ?? (logoRemoved ? null : undefined);
	$: hasLogo = Boolean(logoPreview) || (!logoRemoved && Boolean(company?.logo_updated_at));
	$: logoCompany = {
		id: company?.id ?? 0,
		name: name || company?.name || '',
		logo_updated_at: company?.logo_updated_at ?? null
	};

	// Template options
	let chartTemplates: any[] = [];
	let periodTemplates: any[] = [];

	const COUNTRY_OPTIONS = [
		{ value: 'France', currency: 'EUR', label: 'France' },
		{ value: 'United States', currency: 'USD', label: 'United States' },
		{ value: 'United Kingdom', currency: 'GBP', label: 'United Kingdom' },
		{ value: 'Germany', currency: 'EUR', label: 'Germany' },
		{ value: 'China', currency: 'CNY', label: 'China' },
		{ value: 'Japan', currency: 'JPY', label: 'Japan' },
		{ value: 'Canada', currency: 'CAD', label: 'Canada' },
		{ value: 'Australia', currency: 'AUD', label: 'Australia' },
		{ value: 'Switzerland', currency: 'CHF', label: 'Switzerland' },
		{ value: 'Spain', currency: 'EUR', label: 'Spain' },
		{ value: 'Italy', currency: 'EUR', label: 'Italy' },
		{ value: 'Belgium', currency: 'EUR', label: 'Belgium' },
		{ value: 'Netherlands', currency: 'EUR', label: 'Netherlands' },
		{ value: 'Brazil', currency: 'BRL', label: 'Brazil' },
		{ value: 'India', currency: 'INR', label: 'India' },
		{ value: 'South Korea', currency: 'KRW', label: 'South Korea' },
		{ value: 'Mexico', currency: 'MXN', label: 'Mexico' },
		{ value: 'Singapore', currency: 'SGD', label: 'Singapore' },
		{ value: 'Hong Kong', currency: 'HKD', label: 'Hong Kong' },
		{ value: 'Morocco', currency: 'MAD', label: 'Morocco' }
	];

	const CURRENCY_OPTIONS = [
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

	// Custom input state for "Other" selections
	let countrySelectValue = '';
	let customCountry = '';
	let currencySelectValue = '';
	let customCurrency = '';

	$: isCustomCountry = countrySelectValue === '__other__';
	$: isCustomCurrency = currencySelectValue === '__other__';

	// Sync country from select/custom input
	$: country = isCustomCountry ? customCountry : countrySelectValue;
	// Sync currency from select/custom input
	$: currency = isCustomCurrency ? customCurrency : currencySelectValue;

	$: isEditMode = company !== null && company !== undefined;

	// When country changes from dropdown, auto-set currency and suggest chart template
	const handleCountryChange = () => {
		if (countrySelectValue && countrySelectValue !== '__other__') {
			const matched = COUNTRY_OPTIONS.find((c) => c.value === countrySelectValue);
			if (matched) {
				currencySelectValue = matched.currency;
				customCurrency = '';
			}
			// Auto-select matching chart template (user can override to "None")
			const matchingTemplate = chartTemplates.find(
				(t) => t.country && t.country.toLowerCase() === countrySelectValue.toLowerCase()
			);
			chart_template_id = matchingTemplate ? matchingTemplate.id : null;
		}
	};

	$: if (show) {
		initForm();
		loadTemplates();
	}

	const resetLogo = () => {
		if (logoPreview) URL.revokeObjectURL(logoPreview);
		logoPreview = null;
		logoFile = null;
		logoRemoved = false;
	};

	const handleLogoPicked = async (e: Event) => {
		const input = e.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		input.value = ''; // picking the same file again still fires change
		if (!file) return;
		if (file.size > MAX_LOGO_FILE_BYTES) {
			toast.error($i18n.t('The logo must be 10 MB or smaller'));
			return;
		}
		preparingLogo = true;
		try {
			const png = await prepareLogoFile(file);
			resetLogo();
			logoFile = png;
			logoPreview = URL.createObjectURL(png);
		} catch {
			toast.error($i18n.t("Couldn't read this image. Use a PNG, JPEG, WebP, GIF or SVG file."));
		}
		preparingLogo = false;
	};

	const removeLogo = () => {
		resetLogo();
		logoRemoved = true;
	};

	// After the company itself is saved; a failure here keeps the company and says so.
	const saveLogo = async (companyId: number) => {
		try {
			if (logoFile) return await uploadCompanyLogo(companyId, logoFile);
			if (logoRemoved && company?.logo_updated_at) return await deleteCompanyLogo(companyId);
		} catch (err: any) {
			toast.error(
				`${$i18n.t("The company was saved but its logo wasn't")}: ${err?.detail || `${err}`}`
			);
		}
		return null;
	};

	onDestroy(resetLogo);

	const initForm = () => {
		createdCompany = null;
		resetLogo();
		if (company) {
			name = company.name || '';
			description = company.description || '';
			fiscalYearStartMonth = Number(company.fiscal_year_start_month ?? 1) || 1;
			booksLanguage = company.books_language || 'en';
			chart_template_id = company.chart_template_id || null;
			period_template_id = company.period_template_id || null;

			// Country: check if it's in the known list
			const companyCountry = company.country || '';
			if (COUNTRY_OPTIONS.some((c) => c.value === companyCountry)) {
				countrySelectValue = companyCountry;
				customCountry = '';
			} else if (companyCountry) {
				countrySelectValue = '__other__';
				customCountry = companyCountry;
			} else {
				countrySelectValue = '';
				customCountry = '';
			}

			// Currency: check if it's in the known list
			const companyCurrency = company.currency || 'USD';
			if (CURRENCY_OPTIONS.includes(companyCurrency)) {
				currencySelectValue = companyCurrency;
				customCurrency = '';
			} else if (companyCurrency) {
				currencySelectValue = '__other__';
				customCurrency = companyCurrency;
			} else {
				currencySelectValue = 'USD';
				customCurrency = '';
			}
		} else {
			name = '';
			booksLanguage = 'en';
			countrySelectValue = '';
			customCountry = '';
			currencySelectValue = 'USD';
			customCurrency = '';
			description = '';
			chart_template_id = null;
			period_template_id = null;
		}
	};

	const loadTemplates = async () => {
		loadingTemplates = true;
		try {
			const [chartRes, periodRes] = await Promise.all([getChartTemplates(), getPeriodTemplates()]);

			const chartList = Array.isArray(chartRes) ? chartRes : (chartRes?.templates ?? []);
			chartTemplates = chartList;

			const periodList = Array.isArray(periodRes) ? periodRes : (periodRes?.templates ?? []);
			periodTemplates = periodList;
		} catch (err: any) {
			console.error('Failed to load templates:', err);
		}
		loadingTemplates = false;
	};

	// Escape, the close button and a click outside all close the dialog; after a create they
	// finish the create (reload the list) like Done does.
	const handleOpenChange = (open: boolean) => {
		if (!open && createdCompany) finishCreate();
	};

	const handleSubmit = async () => {
		if (!name.trim()) {
			toast.error($i18n.t('Name is required'));
			return;
		}

		submitting = true;
		try {
			const payload: Record<string, any> = {
				name: name.trim(),
				country: country.trim() || null,
				currency: currency.trim() || 'USD',
				description: description.trim() || null,
				fiscal_year_start_month: Number(fiscalYearStartMonth) || 1,
				books_language: booksLanguage || 'en'
			};

			// Always include template IDs (even null for clearing)
			payload.chart_template_id = chart_template_id || null;
			payload.period_template_id = period_template_id || null;

			let result;
			if (isEditMode) {
				result = await updateCompany(company.id, payload);
				result = (await saveLogo(company.id)) ?? result;
				toast.success($i18n.t('Company updated'));
				dispatch('save', result);
				if (onSave) {
					onSave();
				}
				show = false;
			} else {
				result = await createCompany(payload);
				result = (await saveLogo(result.id)) ?? result;
				toast.success($i18n.t('Company created'));
				// Keep the modal open on a post-create step so the user can import the
				// new company's fixed-asset register right away (finalized on Done).
				createdCompany = result;
			}
		} catch (err: any) {
			toast.error(err?.detail || `${err}`);
		} finally {
			submitting = false;
		}
	};

	const finishCreate = () => {
		const c = createdCompany;
		createdCompany = null;
		show = false;
		dispatch('save', c);
		if (onSave) {
			onSave();
		}
	};

	const goToAssets = () => {
		const id = createdCompany?.id;
		finishCreate();
		if (id) goto(`/accounting/company/${id}/assets`);
	};
</script>

<Dialog.Root bind:open={show} onOpenChange={handleOpenChange}>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-lg">
		<Dialog.Header>
			<Dialog.Title>
				{createdCompany
					? $i18n.t('Company Created')
					: isEditMode
						? $i18n.t('Edit Company')
						: $i18n.t('Create Company')}
			</Dialog.Title>
		</Dialog.Header>

		{#if createdCompany}
			<Alert.Root>
				<CircleCheck class="text-success!" />
				<Alert.Description class="text-foreground">
					{$i18n.t(
						'Company created. Import its fixed-asset register now, or later from the Fixed Assets tab.'
					)}
				</Alert.Description>
			</Alert.Root>
			<Dialog.Footer>
				<Button variant="outline" onclick={finishCreate}>{$i18n.t('Done')}</Button>
				<Button onclick={goToAssets}>{$i18n.t('Import Fixed Assets')}</Button>
			</Dialog.Footer>
		{:else}
			<form class="flex flex-col gap-4" on:submit|preventDefault={handleSubmit}>
				<!-- Logo -->
				<div class="flex items-center gap-4" role="group" aria-labelledby="company-logo-label">
					<CompanyLogo company={logoCompany} src={logoSrc} size="lg" />
					<div class="flex min-w-0 flex-col gap-2">
						<div id="company-logo-label" class="text-sm leading-none font-medium">
							{$i18n.t('Logo')}
						</div>
						<div class="flex flex-wrap gap-2">
							<input
								bind:this={logoInput}
								type="file"
								accept={LOGO_ACCEPT}
								class="sr-only"
								tabindex="-1"
								aria-hidden="true"
								on:change={handleLogoPicked}
							/>
							<Button
								type="button"
								variant="outline"
								size="sm"
								disabled={preparingLogo}
								aria-describedby="company-logo-help"
								onclick={() => logoInput?.click()}
							>
								{#if preparingLogo}<Spinner />{:else}<ImageUp />{/if}
								{hasLogo ? $i18n.t('Change logo') : $i18n.t('Upload logo')}
							</Button>
							{#if hasLogo}
								<Button type="button" variant="ghost" size="sm" onclick={removeLogo}>
									<Trash2 />{$i18n.t('Remove')}
								</Button>
							{/if}
						</div>
						<p id="company-logo-help" class="text-sm text-muted-foreground">
							{$i18n.t('PNG, JPEG, WebP or SVG. Shown on the company list.')}
						</p>
					</div>
				</div>

				<!-- Name -->
				<div class="flex flex-col gap-2">
					<Label for="company-name">
						{$i18n.t('Legal Entity Name')}
						<span class="text-destructive" aria-hidden="true">*</span>
					</Label>
					<Input
						id="company-name"
						type="text"
						bind:value={name}
						placeholder={$i18n.t('name as appears on legal documents')}
						required
					/>
				</div>

				<!-- Country & Currency -->
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
					<div class="flex flex-col gap-2">
						<Label for="company-country">{$i18n.t('Country')}</Label>
						<NativeSelect.Root
							id="company-country"
							class="w-full"
							bind:value={countrySelectValue}
							onchange={(e: Event) => {
								// read the choice from the event: the binding may not have run yet
								countrySelectValue = (e.currentTarget as HTMLSelectElement).value;
								handleCountryChange();
							}}
						>
							<option value="">{$i18n.t('Select country...')}</option>
							{#each COUNTRY_OPTIONS as opt}
								<option value={opt.value}>{opt.label}</option>
							{/each}
							<option value="__other__">{$i18n.t('Other')}</option>
						</NativeSelect.Root>
						{#if isCustomCountry}
							<Input
								type="text"
								bind:value={customCountry}
								aria-label={$i18n.t('Country')}
								placeholder={$i18n.t('Enter country name')}
							/>
						{/if}
					</div>

					<div class="flex flex-col gap-2">
						<Label for="company-currency">{$i18n.t('Currency')}</Label>
						<NativeSelect.Root
							id="company-currency"
							class="w-full"
							bind:value={currencySelectValue}
						>
							{#each CURRENCY_OPTIONS as cur}
								<option value={cur}>{cur}</option>
							{/each}
							<option value="__other__">{$i18n.t('Other')}</option>
						</NativeSelect.Root>
						{#if isCustomCurrency}
							<Input
								type="text"
								bind:value={customCurrency}
								aria-label={$i18n.t('Currency')}
								placeholder={$i18n.t('e.g. XOF, TND')}
							/>
						{/if}
					</div>
				</div>

				<!-- Description -->
				<div class="flex flex-col gap-2">
					<Label for="company-description">{$i18n.t('Description')}</Label>
					<Textarea
						id="company-description"
						bind:value={description}
						placeholder={$i18n.t('Optional description')}
						rows={2}
						class="min-h-0 resize-none"
					/>
				</div>

				<!-- Fiscal year -->
				<div class="flex flex-col gap-2">
					<Label for="company-fy">{$i18n.t('Fiscal year starts in')}</Label>
					<!-- plain <option>s keep the month a number (bind:value reads option.__value) -->
					<NativeSelect.Root
						id="company-fy"
						class="w-full"
						bind:value={fiscalYearStartMonth}
						aria-describedby="company-fy-help"
					>
						{#each MONTH_NAMES as m, i}
							<option value={i + 1}
								>{$i18n.t(m)}{i === 0
									? ` (${$i18n.t('calendar year')})`
									: i === 3
										? ` (${$i18n.t('April – March')})`
										: ''}</option
							>
						{/each}
					</NativeSelect.Root>
					<p id="company-fy-help" class="text-sm text-muted-foreground">
						{$i18n.t(
							'Drives the year-to-date columns, the year-end close and the income-tax period. Most Hong Kong companies close on 31 March or 31 December.'
						)}
					</p>
				</div>

				<!-- Books language -->
				<div class="flex flex-col gap-2">
					<Label for="company-books-lang">{$i18n.t('Books language')}</Label>
					<NativeSelect.Root
						id="company-books-lang"
						class="w-full"
						bind:value={booksLanguage}
						aria-describedby="company-books-lang-help"
					>
						{#each BOOKS_LANGUAGES as l}
							<NativeSelect.Option value={l.value}>{l.label}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
					<p id="company-books-lang-help" class="text-sm text-muted-foreground">
						{$i18n.t(
							'Language of the text Gnos3 writes into the books: entry descriptions, line labels and the tax worksheet. Entries already booked keep their text.'
						)}
					</p>
				</div>

				<!-- Templates -->
				<Separator />
				<div class="text-sm font-medium">{$i18n.t('Templates')}</div>

				{#if loadingTemplates}
					<div
						class="flex flex-col gap-4"
						aria-busy="true"
						aria-label={$i18n.t('Loading templates...')}
					>
						{#each Array(2) as _}
							<div class="flex flex-col gap-2">
								<Skeleton class="h-4 w-40" />
								<Skeleton class="h-9 w-full" />
							</div>
						{/each}
					</div>
				{:else}
					<!-- Chart Template (plain <option>s: the ids stay numbers and "none" stays null) -->
					<div class="flex flex-col gap-2">
						<Label for="chart-template">{$i18n.t('Chart of Accounts Template')}</Label>
						<NativeSelect.Root id="chart-template" class="w-full" bind:value={chart_template_id}>
							<option value={null}>{$i18n.t('None (start from scratch)')}</option>
							{#each chartTemplates as template}
								<option value={template.id}>
									{template.name}
									{#if template.country}({template.country}){/if}
									{#if template.is_builtin}
										- {$i18n.t('Built-in')}{/if}
								</option>
							{/each}
						</NativeSelect.Root>
						{#if chartTemplates.length === 0}
							<p class="text-sm text-muted-foreground">{$i18n.t('No chart templates available')}</p>
						{/if}
					</div>

					<!-- Period Template -->
					<div class="flex flex-col gap-2">
						<Label for="period-template">{$i18n.t('Accounting Period Template')}</Label>
						<NativeSelect.Root id="period-template" class="w-full" bind:value={period_template_id}>
							<option value={null}>{$i18n.t('None (configure later)')}</option>
							{#each periodTemplates as template}
								<option value={template.id}>
									{template.name}
									{#if template.description}
										- {template.description}{/if}
								</option>
							{/each}
						</NativeSelect.Root>
						{#if periodTemplates.length === 0}
							<p class="text-sm text-muted-foreground">
								{$i18n.t('No period templates available')}
							</p>
						{/if}
					</div>
				{/if}

				<!-- Actions -->
				<Dialog.Footer class="pt-2">
					<Button type="button" variant="outline" onclick={() => (show = false)}>
						{$i18n.t('Cancel')}
					</Button>
					<Button type="submit" disabled={submitting}>
						{#if submitting}
							<Spinner />{$i18n.t('Saving...')}
						{:else}
							{isEditMode ? $i18n.t('Update') : $i18n.t('Create')}
						{/if}
					</Button>
				</Dialog.Footer>
			</form>
		{/if}
	</Dialog.Content>
</Dialog.Root>
