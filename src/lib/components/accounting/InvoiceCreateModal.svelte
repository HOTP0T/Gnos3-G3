<script lang="ts">
	import { getContext, createEventDispatcher, tick } from 'svelte';
	import { toast } from 'svelte-sonner';
	import type { Writable } from 'svelte/store';

	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';

	import { createManualInvoice, getNextInvoiceNumber } from '$lib/apis/accounting';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Collapsible from '$lib/components/ui/collapsible/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';

	const i18n: any = getContext('i18n');
	const companyCurrencyCtx = getContext<Writable<string>>('companyCurrency');
	const dispatch = createEventDispatcher();

	export let show = false;
	export let companyId: number;
	export let companyName: string = '';

	// Form state
	let invoice_number = '';
	let nextNumberHint = '';
	let client_name = '';
	let vendor_name = '';
	let invoice_date = '';
	let due_date = '';
	let currency = 'EUR';
	let subtotal: number | null = null;
	let tax_amount: number | null = null;
	let tax_inclusive = false;
	let total_amount: number | null = null;
	let payment_terms = '';
	let po_number = '';
	let description = '';
	let business_unit = '';

	// Line items
	let lineItems: { description: string; quantity: number; unit_price: number; amount: number }[] =
		[];
	let showLineItems = false;
	let showAdvanced = false;
	let saving = false;

	const resetForm = () => {
		const today = new Date();
		invoice_date = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
		invoice_number = '';
		nextNumberHint = '';
		client_name = '';
		vendor_name = companyName;
		due_date = '';
		currency = $companyCurrencyCtx || 'EUR';
		subtotal = null;
		tax_amount = null;
		tax_inclusive = false;
		total_amount = null;
		payment_terms = '';
		po_number = '';
		description = '';
		business_unit = '';
		lineItems = [];
		showLineItems = false;
		showAdvanced = false;
	};

	async function fetchNextNumber() {
		try {
			const res = await getNextInvoiceNumber(companyId);
			nextNumberHint = res.next_number;
		} catch {
			nextNumberHint = '';
		}
	}

	$: if (show) {
		resetForm();
		fetchNextNumber();
	}

	// Auto-compute amounts from line items
	function recalcFromLines() {
		if (lineItems.length > 0) {
			for (const li of lineItems) {
				li.amount = Math.round((li.quantity || 0) * (li.unit_price || 0) * 100) / 100;
			}
			lineItems = [...lineItems]; // trigger reactivity
			subtotal = Math.round(lineItems.reduce((sum, li) => sum + (li.amount || 0), 0) * 100) / 100;
			total_amount = Math.round(((subtotal || 0) + (tax_amount || 0)) * 100) / 100;
		}
	}

	// Auto-compute total from subtotal + tax
	$: if (subtotal !== null && tax_amount !== null) {
		total_amount = Math.round((subtotal + tax_amount) * 100) / 100;
	}

	function addLineItem() {
		lineItems = [...lineItems, { description: '', quantity: 1, unit_price: 0, amount: 0 }];
		showLineItems = true;
	}

	function removeLineItem(index: number) {
		lineItems = lineItems.filter((_, i) => i !== index);
		recalcFromLines();
	}

	const handleSave = async () => {
		if (!client_name.trim()) {
			toast.error($i18n.t('Client name is required'));
			return;
		}
		if (!total_amount || total_amount <= 0) {
			toast.error($i18n.t('Total amount must be greater than 0'));
			return;
		}
		if (!invoice_date) {
			toast.error($i18n.t('Invoice date is required'));
			return;
		}

		saving = true;
		try {
			const data: Record<string, any> = {
				client_name: client_name.trim(),
				invoice_date,
				total_amount,
				currency
			};

			if (invoice_number.trim()) data.invoice_number = invoice_number.trim();
			if (vendor_name.trim()) data.vendor_name = vendor_name.trim();
			if (due_date) data.due_date = due_date;
			if (subtotal !== null) data.subtotal = subtotal;
			if (tax_amount !== null) data.tax_amount = tax_amount;
			if (tax_inclusive) data.tax_inclusive = true;
			if (payment_terms.trim()) data.payment_terms = payment_terms.trim();
			if (po_number.trim()) data.po_number = po_number.trim();
			if (description.trim()) data.description = description.trim();
			if (business_unit.trim()) data.business_unit = business_unit.trim();
			if (lineItems.length > 0) {
				data.line_items = lineItems.map((li) => ({
					description: li.description,
					quantity: li.quantity,
					unit_price: li.unit_price,
					amount: li.amount
				}));
			}

			await createManualInvoice(companyId, data);
			toast.success($i18n.t('Invoice created'));
			show = false;
			await tick();
			dispatch('save');
		} catch (err: any) {
			toast.error(`${$i18n.t('Failed to create invoice')}: ${err?.detail ?? err}`);
		}
		saving = false;
	};
</script>

<Dialog.Root bind:open={show}>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-3xl [&>*]:min-w-0">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Create Invoice')}</Dialog.Title>
		</Dialog.Header>

		<div class="grid gap-4">
			<!-- Row: Invoice # + Date + Due Date -->
			<div class="grid gap-3 sm:grid-cols-3">
				<div class="grid gap-1.5">
					<Label for="inv-number">{$i18n.t('Invoice #')}</Label>
					<Input
						id="inv-number"
						type="text"
						class="font-mono text-[13px]"
						bind:value={invoice_number}
						placeholder={nextNumberHint || $i18n.t('Auto-generated')}
					/>
				</div>
				<div class="grid gap-1.5">
					<Label for="inv-date">{$i18n.t('Date')} *</Label>
					<Input id="inv-date" type="date" required bind:value={invoice_date} />
				</div>
				<div class="grid gap-1.5">
					<Label for="inv-due-date">{$i18n.t('Due Date')}</Label>
					<Input id="inv-due-date" type="date" bind:value={due_date} />
				</div>
			</div>

			<!-- Row: Vendor (From) + Client (To) -->
			<div class="grid gap-3 sm:grid-cols-2">
				<div class="grid gap-1.5">
					<Label for="inv-vendor">{$i18n.t('From (Vendor)')}</Label>
					<Input
						id="inv-vendor"
						type="text"
						bind:value={vendor_name}
						placeholder={companyName || $i18n.t('Your company')}
					/>
				</div>
				<div class="grid gap-1.5">
					<Label for="inv-client">{$i18n.t('To (Client)')} *</Label>
					<Input
						id="inv-client"
						type="text"
						required
						bind:value={client_name}
						placeholder={$i18n.t('Client name')}
					/>
				</div>
			</div>

			<!-- Line Items Section -->
			<div class="grid gap-2">
				<div class="flex items-center justify-between">
					<button
						type="button"
						class="group inline-flex items-center gap-1.5 rounded-sm text-sm font-medium text-muted-foreground hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
						aria-expanded={showLineItems}
						onclick={() => {
							if (lineItems.length === 0) addLineItem();
							showLineItems = !showLineItems;
						}}
					>
						<ChevronRight class="size-4 transition-transform {showLineItems ? 'rotate-90' : ''}" />
						{$i18n.t('Line Items')} ({lineItems.length})
					</button>
					{#if showLineItems}
						<Button variant="ghost" size="xs" onclick={addLineItem}>
							<Plus />{$i18n.t('Add Line')}
						</Button>
					{/if}
				</div>

				{#if showLineItems && lineItems.length > 0}
					<div class="overflow-hidden rounded-md border">
						<Table.Root>
							<Table.Header class="bg-muted/50">
								<Table.Row class="hover:bg-transparent">
									<Table.Head>{$i18n.t('Description')}</Table.Head>
									<Table.Head class="w-20 text-right">{$i18n.t('Qty')}</Table.Head>
									<Table.Head class="w-28 text-right">{$i18n.t('Unit Price')}</Table.Head>
									<Table.Head class="w-28 text-right">{$i18n.t('Amount')}</Table.Head>
									<Table.Head class="w-10"
										><span class="sr-only">{$i18n.t('Remove')}</span></Table.Head
									>
								</Table.Row>
							</Table.Header>
							<Table.Body>
								{#each lineItems as item, idx}
									<Table.Row class="hover:bg-transparent">
										<Table.Cell class="py-1.5">
											<Input
												type="text"
												class="h-8 min-w-[10rem]"
												aria-label={$i18n.t('Description')}
												bind:value={item.description}
												placeholder={$i18n.t('Description')}
											/>
										</Table.Cell>
										<Table.Cell class="py-1.5">
											<Input
												type="number"
												step="0.01"
												min="0"
												class="h-8 min-w-[4.5rem] text-right tabular-nums"
												aria-label={$i18n.t('Qty')}
												bind:value={item.quantity}
												onchange={recalcFromLines}
											/>
										</Table.Cell>
										<Table.Cell class="py-1.5">
											<Input
												type="number"
												step="0.01"
												min="0"
												class="h-8 min-w-[6.5rem] text-right tabular-nums"
												aria-label={$i18n.t('Unit Price')}
												bind:value={item.unit_price}
												onchange={recalcFromLines}
											/>
										</Table.Cell>
										<Table.Cell class="py-1.5 text-right tabular-nums">
											{(item.amount || 0).toLocaleString(undefined, {
												minimumFractionDigits: 2,
												maximumFractionDigits: 2
											})}
										</Table.Cell>
										<Table.Cell class="py-1.5 text-center">
											<Tip content={$i18n.t('Remove')}>
												<Button
													variant="ghost"
													size="icon-xs"
													aria-label={$i18n.t('Remove')}
													onclick={() => removeLineItem(idx)}
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
			</div>

			<!-- Row: Subtotal + Tax + Currency + Total -->
			<div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
				<div class="grid gap-1.5">
					<Label for="inv-subtotal">{$i18n.t('Subtotal')}</Label>
					<Input
						id="inv-subtotal"
						type="number"
						step="0.01"
						min="0"
						class="text-right tabular-nums"
						bind:value={subtotal}
						placeholder="0.00"
					/>
				</div>
				<div class="grid gap-1.5">
					<Label for="inv-tax">{$i18n.t('Tax')}</Label>
					<Input
						id="inv-tax"
						type="number"
						step="0.01"
						min="0"
						class="text-right tabular-nums"
						bind:value={tax_amount}
						placeholder="0.00"
					/>
				</div>
				<div class="grid gap-1.5">
					<Label for="inv-currency">{$i18n.t('Currency')}</Label>
					<Input
						id="inv-currency"
						type="text"
						maxlength={3}
						class="font-mono uppercase"
						bind:value={currency}
						placeholder="EUR"
					/>
				</div>
				<div class="grid gap-1.5">
					<Label for="inv-total">{$i18n.t('Total')} *</Label>
					<Input
						id="inv-total"
						type="number"
						step="0.01"
						min="0"
						required
						class="text-right font-medium tabular-nums"
						bind:value={total_amount}
						placeholder="0.00"
					/>
				</div>
			</div>

			<!-- Advanced section -->
			<Collapsible.Root bind:open={showAdvanced} class="grid gap-3">
				<Collapsible.Trigger
					class="group inline-flex w-fit items-center gap-1.5 rounded-sm text-sm font-medium text-muted-foreground hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
				>
					<ChevronRight class="size-4 transition-transform {showAdvanced ? 'rotate-90' : ''}" />
					{$i18n.t('Advanced')}
				</Collapsible.Trigger>
				<Collapsible.Content class="grid gap-3">
					<div class="grid gap-3 sm:grid-cols-2">
						<div class="grid gap-1.5">
							<Label for="inv-terms">{$i18n.t('Payment Terms')}</Label>
							<Input
								id="inv-terms"
								type="text"
								bind:value={payment_terms}
								placeholder={$i18n.t('e.g. Net 30')}
							/>
						</div>
						<div class="grid gap-1.5">
							<Label for="inv-po">{$i18n.t('PO Number')}</Label>
							<Input
								id="inv-po"
								type="text"
								bind:value={po_number}
								placeholder={$i18n.t('Purchase order ref')}
							/>
						</div>
					</div>
					<div class="grid gap-3 sm:grid-cols-2">
						<div class="grid gap-1.5">
							<Label for="inv-bu">{$i18n.t('Business Unit')}</Label>
							<Input id="inv-bu" type="text" bind:value={business_unit} />
						</div>
						<div class="flex items-end pb-2">
							<div class="flex items-center gap-2">
								<Checkbox id="inv-tax-inclusive" bind:checked={tax_inclusive} />
								<Label for="inv-tax-inclusive" class="font-normal">{$i18n.t('Tax Inclusive')}</Label
								>
							</div>
						</div>
					</div>
					<div class="grid gap-1.5">
						<Label for="inv-desc">{$i18n.t('Description')}</Label>
						<Textarea
							id="inv-desc"
							bind:value={description}
							rows={2}
							class="resize-none"
							placeholder={$i18n.t('Invoice notes or description')}
						/>
					</div>
				</Collapsible.Content>
			</Collapsible.Root>
		</div>

		<Dialog.Footer>
			<Button
				variant="outline"
				disabled={saving}
				onclick={() => {
					show = false;
				}}
			>
				{$i18n.t('Cancel')}
			</Button>
			<Button disabled={saving} onclick={handleSave}>
				{#if saving}
					<Spinner />{$i18n.t('Creating...')}
				{:else}
					{$i18n.t('Create Invoice')}
				{/if}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
