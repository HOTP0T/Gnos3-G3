<script lang="ts">
	import { getContext, createEventDispatcher } from 'svelte';
	import { toast } from 'svelte-sonner';

	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';

	import {
		importChartTemplateFromExcel,
		importPeriodTemplateFromExcel,
		importCompanyAccountsFromExcel,
		importCompanyPeriodsFromExcel,
		importCompanyAssetsFromExcel
	} from '$lib/apis/accounting';

	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;
	export let type: 'chart' | 'period' | 'asset' = 'chart';
	export let companyId: number | undefined = undefined;
	export let onImported: (() => void) | undefined = undefined;

	// Form state
	let name = '';
	let country = '';
	let file: File | null = null;
	let fileInput: HTMLInputElement | null = null;
	let submitting = false;

	// Result state
	let result: { imported_count?: number; skipped_count?: number; errors?: string[] } | null = null;

	$: if (show) {
		resetForm();
	}

	$: title = companyId
		? type === 'chart'
			? $i18n.t('Import Accounts from Excel')
			: type === 'asset'
				? $i18n.t('Import Fixed Assets from Excel')
				: $i18n.t('Import Periods from Excel')
		: type === 'chart'
			? $i18n.t('Import Chart Template from Excel')
			: $i18n.t('Import Period Template from Excel');

	const resetForm = () => {
		name = '';
		country = '';
		file = null;
		result = null;
		submitting = false;
		if (fileInput) {
			fileInput.value = '';
		}
	};

	const handleFileChange = (event: Event) => {
		const target = event.target as HTMLInputElement;
		if (target.files && target.files.length > 0) {
			file = target.files[0];
		}
	};

	const handleSubmit = async (e?: Event) => {
		e?.preventDefault();
		if (!file) {
			toast.error($i18n.t('Please select a file'));
			return;
		}

		if (!companyId && !name.trim()) {
			toast.error($i18n.t('Please enter a template name'));
			return;
		}

		submitting = true;
		try {
			let res: any;

			if (companyId) {
				// Import directly to company
				if (type === 'chart') {
					res = await importCompanyAccountsFromExcel(companyId, file);
				} else if (type === 'asset') {
					res = await importCompanyAssetsFromExcel(companyId, file);
				} else {
					res = await importCompanyPeriodsFromExcel(companyId, file);
				}
			} else {
				// Import as template (chart/period only — assets have no template)
				if (type === 'chart') {
					res = await importChartTemplateFromExcel(name.trim(), file, country.trim() || undefined);
				} else {
					res = await importPeriodTemplateFromExcel(name.trim(), file);
				}
			}

			result = {
				imported_count: res?.imported ?? res?.imported_count ?? res?.count ?? 0,
				skipped_count: res?.skipped ?? res?.skipped_count ?? 0,
				errors: res?.errors ?? []
			};

			toast.success($i18n.t('Import completed'));
			dispatch('imported');
			if (onImported) {
				onImported();
			}
		} catch (err: any) {
			const msg = err?.detail ?? err?.message ?? String(err);
			toast.error($i18n.t('Import failed') + ': ' + msg);
		}
		submitting = false;
	};
</script>

<Dialog.Root bind:open={show}>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-lg">
		<Dialog.Header>
			<Dialog.Title>{title}</Dialog.Title>
			{#if !result}
				<Dialog.Description>{$i18n.t('An .xlsx or .xls file.')}</Dialog.Description>
			{/if}
		</Dialog.Header>

		{#if result}
			<!-- Result View -->
			<div class="grid gap-3">
				<Alert.Root>
					<CircleCheck class="text-success" />
					<Alert.Title>{$i18n.t('Import Complete')}</Alert.Title>
					<Alert.Description class="tabular-nums">
						<div>{$i18n.t('Imported')}: {result.imported_count ?? 0}</div>
						{#if result.skipped_count}
							<div>{$i18n.t('Skipped')}: {result.skipped_count}</div>
						{/if}
					</Alert.Description>
				</Alert.Root>

				{#if result.errors && result.errors.length > 0}
					<Alert.Root variant="destructive">
						<CircleAlert />
						<Alert.Title>{$i18n.t('Errors')}</Alert.Title>
						<Alert.Description>
							<ul class="max-h-32 list-inside list-disc space-y-0.5 overflow-y-auto">
								{#each result.errors as error}
									<li>{error}</li>
								{/each}
							</ul>
						</Alert.Description>
					</Alert.Root>
				{/if}
			</div>

			<Dialog.Footer>
				<Button onclick={() => (show = false)}>{$i18n.t('Done')}</Button>
			</Dialog.Footer>
		{:else}
			<!-- Upload Form -->
			<form id="excel-import-form" class="grid gap-4" onsubmit={handleSubmit}>
				<div class="grid gap-2">
					<Label for="import-file">{$i18n.t('Excel File')} *</Label>
					<Input
						id="import-file"
						type="file"
						accept=".xlsx,.xls"
						bind:ref={fileInput}
						onchange={handleFileChange}
					/>
				</div>

				<!-- Name (only for template import, not company import) -->
				{#if !companyId}
					<div class="grid gap-2">
						<Label for="import-name">{$i18n.t('Template Name')} *</Label>
						<Input
							id="import-name"
							type="text"
							bind:value={name}
							placeholder={type === 'chart'
								? $i18n.t('e.g. French PCG')
								: $i18n.t('e.g. Calendar Year 2026')}
							required
						/>
					</div>
				{/if}

				<!-- Country (only for chart template import) -->
				{#if type === 'chart' && !companyId}
					<div class="grid gap-2">
						<Label for="import-country">{$i18n.t('Country')}</Label>
						<Input
							id="import-country"
							type="text"
							bind:value={country}
							placeholder={$i18n.t('e.g. FR (optional)')}
						/>
					</div>
				{/if}
			</form>

			<Dialog.Footer>
				<Button variant="outline" onclick={() => (show = false)}>{$i18n.t('Cancel')}</Button>
				<Button
					type="submit"
					form="excel-import-form"
					disabled={submitting || !file || (!companyId && !name.trim())}
				>
					{#if submitting}
						<Spinner />
						{$i18n.t('Importing...')}
					{:else}
						{$i18n.t('Import')}
					{/if}
				</Button>
			</Dialog.Footer>
		{/if}
	</Dialog.Content>
</Dialog.Root>
