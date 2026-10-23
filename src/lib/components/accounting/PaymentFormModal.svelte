<script lang="ts">
	import { getContext, createEventDispatcher, onMount, tick } from 'svelte';
	import { get } from 'svelte/store';
	import { toast } from 'svelte-sonner';

	import Check from '@lucide/svelte/icons/check';
	import ChevronsUpDown from '@lucide/svelte/icons/chevrons-up-down';
	import ExternalLink from '@lucide/svelte/icons/external-link';
	import Link2 from '@lucide/svelte/icons/link-2';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import ArrowRightLeft from '@lucide/svelte/icons/arrow-right-left';

	import { createPayment, getPaymentPreview } from '$lib/apis/accounting';
	import K4miDocLink from '$lib/components/common/K4miDocLink.svelte';
	import InvoiceSelector from '$lib/components/accounting/InvoiceSelector.svelte';

	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Popover from '$lib/components/ui/popover/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';

	const i18n: any = getContext('i18n');
	// The company's own currency (set by the company layout) — the form's default.
	const companyCurrencyCtx = getContext<any>('companyCurrency');
	const companyCurrency = (): string => {
		try {
			const v =
				companyCurrencyCtx && typeof companyCurrencyCtx.subscribe === 'function'
					? get(companyCurrencyCtx)
					: companyCurrencyCtx;
			return (v as string) || 'USD';
		} catch {
			return 'USD';
		}
	};
	const dispatch = createEventDispatcher();

	export let show = false;
	export let accounts: any[] = [];
	export let companyId: number;
	export let prefill: any = null;

	// Form state
	let payment_date = '';
	let amount: number | null = null;
	let currency = 'USD';
	let direction = 'outbound';
	let method = 'bank_transfer';
	let payer = '';
	let payee = '';
	let reference = '';
	let notes = '';
	let invoice_id: number | null = null;
	let debit_account_id: number | null = null;
	let credit_account_id: number | null = null;

	let showAdvanced = false;
	let saving = false;

	// What the payment will book — resolved by the backend from the linked
	// invoice, the bank account's defaults, bank-line rules or the company
	// default; never guessed. The human fills whatever is still open.
	let plan: any = null;
	let planLoading = false;
	let planTimer: any = null;
	let editingSide: string | null = null;
	let sideSearch = '';

	$: parentIds = new Set(accounts.map((a: any) => a.parent_id).filter(Boolean));
	$: leafAccounts = accounts.filter((a: any) => !parentIds.has(a.id));
	$: counterpartId = direction === 'outbound' ? debit_account_id : credit_account_id;
	$: bankId = direction === 'outbound' ? credit_account_id : debit_account_id;

	const refreshPlan = async () => {
		if (!show || !companyId) return;
		planLoading = true;
		try {
			plan = await getPaymentPreview({
				company_id: companyId,
				direction,
				amount: amount ?? 0,
				invoice_id: invoice_id ?? undefined,
				bank_statement_line_id: prefill?._bank_statement_line_id ?? undefined,
				payee: payee || undefined,
				payer: payer || undefined,
				reference: reference || undefined,
				debit_account_id: debit_account_id ?? undefined,
				credit_account_id: credit_account_id ?? undefined,
				currency: currency || undefined,
				payment_date: payment_date || undefined
			});
		} catch {
			plan = null;
		}
		planLoading = false;
	};
	const schedulePlan = () => {
		clearTimeout(planTimer);
		planTimer = setTimeout(refreshPlan, 250);
	};
	$: if (show && mounted) {
		// re-resolve whenever an input that can change the accounts changes
		void [
			direction,
			invoice_id,
			payee,
			payer,
			reference,
			debit_account_id,
			credit_account_id,
			amount,
			currency,
			payment_date
		];
		schedulePlan();
	}
	const chooseSide = (role: string, id: number) => {
		const isCounterpart = role === 'counterpart';
		if ((direction === 'outbound') === isCounterpart) debit_account_id = id;
		else credit_account_id = id;
		editingSide = null;
		sideSearch = '';
	};
	// `q` and the account list are passed in so the {#each} in the template
	// re-renders when the search text changes (Svelte only tracks what the
	// template expression reads, not what the function reads).
	const sideCandidates = (line: any, q: string, leafAccounts: any[]) => {
		q = (q || '').toLowerCase();
		const cands = (line.candidates ?? []).map((c: any) => c.id);
		const typeOk = (a: any) =>
			line.role === 'bank'
				? a.account_type === 'asset'
				: ['liability', 'asset'].includes(a.account_type);
		return leafAccounts
			.filter(
				(a: any) => typeOk(a) && (!q || a.code.includes(q) || a.name.toLowerCase().includes(q))
			)
			.sort(
				(a: any, b: any) =>
					(cands.includes(b.id) ? 1 : 0) - (cands.includes(a.id) ? 1 : 0) ||
					a.code.localeCompare(b.code)
			)
			.slice(0, 60);
	};
	const SOURCE_LABEL: Record<string, string> = {
		human: 'chosen',
		invoice: "from the invoice's entry",
		matched: 'from the matched entry',
		bank_default: 'bank account default',
		rule: 'from rule',
		company: 'company default',
		missing: 'account required'
	};
	$: fxRate = plan?.exchange_rate ?? null;
	$: fxForeign = !!fxRate && fxRate.currency !== fxRate.base;
	$: planReady = !!plan && plan.complete;
	let showInvoiceSelector = false;
	let invoiceLabel = '';
	let invoiceK4miDocId: number | null = null;

	const fmt = (n: any) =>
		n === null || n === undefined || n === ''
			? '—'
			: Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

	// Custom payment methods (persisted in localStorage)
	const CUSTOM_METHODS_KEY = 'accounting-custom-payment-methods';
	let customMethods: string[] = [];
	let customMethodInput = '';

	const builtinMethods = ['cash', 'bank_transfer', 'check', 'credit_card'];

	function loadCustomMethods() {
		try {
			const saved = localStorage.getItem(CUSTOM_METHODS_KEY);
			if (saved) customMethods = JSON.parse(saved);
		} catch {}
	}

	function saveCustomMethod(name: string) {
		if (!name || builtinMethods.includes(name) || customMethods.includes(name)) return;
		customMethods = [...customMethods, name];
		try {
			localStorage.setItem(CUSTOM_METHODS_KEY, JSON.stringify(customMethods));
		} catch {}
	}

	loadCustomMethods();

	let mounted = false;

	const resetForm = () => {
		const today = new Date();
		payment_date = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
		amount = null;
		currency = companyCurrency();
		direction = 'outbound';
		method = 'bank_transfer';
		payer = '';
		payee = '';
		reference = '';
		notes = '';
		invoice_id = null;
		debit_account_id = null;
		credit_account_id = null;
		showAdvanced = false;
		invoiceLabel = '';
		editingSide = null;
		sideSearch = '';
	};

	// Reset the form ONCE when the modal opens (or a new prefill arrives). Kept
	// out of a reactive block: a `$:` that read `payment_date` re-ran on every
	// keystroke and reset the date, amount and currency the user had just typed.
	const openForm = (pre: any) => {
		resetForm();
		if (pre) {
			if (pre.payment_date) payment_date = pre.payment_date;
			amount = pre.amount || null;
			currency = pre.currency || companyCurrency();
			direction = pre.direction || 'outbound';
			method = pre.method || 'bank_transfer';
			payer = pre.payer || '';
			payee = pre.payee || '';
			reference = pre.reference || '';
			if (pre.invoice_id) {
				invoice_id = pre.invoice_id;
				invoiceLabel = pre.reference || `#${pre.invoice_id}`;
			}
		}
	};
	let wasShown = false;
	$: {
		if (show && !wasShown) openForm(prefill);
		wasShown = show;
	}

	const handleSave = async () => {
		if (!payment_date || !amount || amount <= 0) {
			toast.error($i18n.t('Please fill in required fields (date and amount)'));
			return;
		}

		saving = true;
		try {
			// Resolve custom method
			let finalMethod = method;
			if (method === '__other__') {
				if (!customMethodInput.trim()) {
					toast.error($i18n.t('Please enter a custom payment method'));
					saving = false;
					return;
				}
				finalMethod = customMethodInput.trim().toLowerCase().replace(/\s+/g, '_');
				saveCustomMethod(finalMethod);
				customMethodInput = '';
			}

			const data: Record<string, any> = {
				payment_date,
				amount,
				currency,
				direction,
				method: finalMethod,
				payer: payer || null,
				payee: payee || null,
				reference: reference || null,
				notes: notes || null
			};

			if (invoice_id) {
				data.invoice_id = invoice_id;
			}
			if (debit_account_id) {
				data.debit_account_id = debit_account_id;
			}
			if (credit_account_id) {
				data.credit_account_id = credit_account_id;
			}

			await createPayment(data, companyId, prefill?._bank_statement_line_id);
			toast.success($i18n.t('Payment recorded'));
			show = false;
			await tick();
			dispatch('save');
		} catch (err: any) {
			toast.error(`${$i18n.t('Failed to record payment')}: ${err?.detail ?? err}`);
		}
		saving = false;
	};

	onMount(() => {
		mounted = true;
	});
</script>

<Dialog.Root bind:open={show}>
	<Dialog.Content class="max-h-[90vh] gap-5 overflow-y-auto sm:max-w-2xl">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Record Payment')}</Dialog.Title>
			<Dialog.Description>
				{$i18n.t(
					'The accounts are resolved for you where a rule or default exists; nothing is guessed.'
				)}
			</Dialog.Description>
		</Dialog.Header>

		<div class="grid gap-4">
			<!-- Date + Amount + Currency -->
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
				<div class="grid content-start gap-2">
					<Label for="payment-date">{$i18n.t('Date')} *</Label>
					<Input id="payment-date" type="date" class="tabular-nums" bind:value={payment_date} />
				</div>
				<div class="grid content-start gap-2">
					<Label for="payment-amount">{$i18n.t('Amount')} *</Label>
					<Input
						id="payment-amount"
						type="number"
						step="0.01"
						min="0"
						class="text-right tabular-nums"
						bind:value={amount}
						placeholder="0.00"
					/>
				</div>
				<div class="grid content-start gap-2">
					<Label for="payment-currency">{$i18n.t('Currency')}</Label>
					<Input
						id="payment-currency"
						type="text"
						maxlength={3}
						class="font-mono uppercase"
						bind:value={currency}
						placeholder="USD"
					/>
				</div>
			</div>

			<!-- Direction + Method -->
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
				<div class="grid content-start gap-2">
					<Label for="payment-direction">{$i18n.t('Direction')}</Label>
					<NativeSelect.Root id="payment-direction" class="w-full" bind:value={direction}>
						<NativeSelect.Option value="inbound">{$i18n.t('Inbound')}</NativeSelect.Option>
						<NativeSelect.Option value="outbound">{$i18n.t('Outbound')}</NativeSelect.Option>
					</NativeSelect.Root>
				</div>
				<div class="grid content-start gap-2">
					<Label for="payment-method">{$i18n.t('Method')}</Label>
					<NativeSelect.Root id="payment-method" class="w-full" bind:value={method}>
						<NativeSelect.Option value="cash">{$i18n.t('Cash')}</NativeSelect.Option>
						<NativeSelect.Option value="bank_transfer"
							>{$i18n.t('Bank Transfer')}</NativeSelect.Option
						>
						<NativeSelect.Option value="check">{$i18n.t('Check')}</NativeSelect.Option>
						<NativeSelect.Option value="credit_card">{$i18n.t('Credit Card')}</NativeSelect.Option>
						{#each customMethods as cm}
							<NativeSelect.Option value={cm}>{cm.replace(/_/g, ' ')}</NativeSelect.Option>
						{/each}
						<NativeSelect.Option value="__other__"
							>{$i18n.t('Other (custom)...')}</NativeSelect.Option
						>
					</NativeSelect.Root>
					{#if method === '__other__'}
						<Input
							type="text"
							aria-label={$i18n.t('Other (custom)...')}
							bind:value={customMethodInput}
							placeholder={$i18n.t('e.g. Mobile Payment, Wire Transfer...')}
						/>
					{/if}
				</div>
			</div>

			<!-- Payer + Payee -->
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
				<div class="grid content-start gap-2">
					<Label for="payment-payer">{$i18n.t('Payer')}</Label>
					<Input
						id="payment-payer"
						type="text"
						bind:value={payer}
						placeholder={$i18n.t('Payer name')}
					/>
				</div>
				<div class="grid content-start gap-2">
					<Label for="payment-payee">{$i18n.t('Payee')}</Label>
					<Input
						id="payment-payee"
						type="text"
						bind:value={payee}
						placeholder={$i18n.t('Payee name')}
					/>
				</div>
			</div>

			<!-- Reference -->
			<div class="grid gap-2">
				<Label for="payment-reference">{$i18n.t('Reference')}</Label>
				<Input
					id="payment-reference"
					type="text"
					class="font-mono placeholder:font-sans"
					bind:value={reference}
					placeholder={$i18n.t('Check #, transaction ID, etc.')}
				/>
			</div>

			<!-- Invoice link -->
			<div class="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm">
				<Link2 class="size-4 text-muted-foreground" />
				<span class="text-muted-foreground">
					{$i18n.t('Invoice')}
					<span class="sr-only">({$i18n.t('optional')})</span>
				</span>
				{#if invoiceLabel}
					<span class="min-w-0 truncate font-medium">{invoiceLabel}</span>
					{#if invoiceK4miDocId}
						<K4miDocLink
							docId={invoiceK4miDocId}
							extraClass="inline-flex shrink-0 text-link"
							title={$i18n.t('Open in K4mi')}
						>
							<ExternalLink class="size-3.5" />
							<span class="sr-only">{$i18n.t('Open in K4mi')}</span>
						</K4miDocLink>
					{/if}
					<Button
						variant="ghost"
						size="xs"
						class="text-muted-foreground hover:text-destructive"
						onclick={() => {
							invoice_id = null;
							invoiceLabel = '';
							invoiceK4miDocId = null;
						}}
					>
						{$i18n.t('Remove')}
					</Button>
				{:else}
					<span class="text-muted-foreground">{$i18n.t('No invoice linked')}</span>
				{/if}
				<Separator orientation="vertical" class="mx-1 h-4!" />
				<Button variant="link" size="sm" onclick={() => (showInvoiceSelector = true)}>
					{$i18n.t('Browse')}
				</Button>
			</div>

			<!-- Notes -->
			<div class="grid gap-2">
				<Label for="payment-notes">{$i18n.t('Notes', { context: 'gnos3' })}</Label>
				<Textarea
					id="payment-notes"
					class="min-h-16 resize-none"
					bind:value={notes}
					placeholder={$i18n.t('Additional notes...')}
					rows={2}
				/>
			</div>
		</div>

		<!-- What this payment will book: the legs, where each account comes from, and the gaps -->
		<div class="grid gap-1.5" aria-busy={planLoading}>
			<span class="text-[13px] font-medium">{$i18n.t('This will book:')}</span>
			{#if plan}
				<div class="overflow-hidden rounded-md border {planLoading ? 'opacity-60' : ''}">
					<Table.Root class="text-[13px]">
						<Table.Body>
							{#each plan.lines as line}
								{@const missing = line.source === 'missing'}
								<Table.Row
									class="align-top hover:bg-transparent {missing
										? 'bg-warning/5 hover:bg-warning/5'
										: ''}"
								>
									<Table.Cell class="w-36 py-2 align-top whitespace-normal">
										<div class="font-medium">{$i18n.t(line.label)}</div>
										<div class="text-xs text-muted-foreground">
											{line.side === 'debit' ? $i18n.t('Debit') : $i18n.t('Credit')}
										</div>
									</Table.Cell>
									<Table.Cell class="py-2 align-top whitespace-normal">
										<Popover.Root
											open={editingSide === line.role}
											onOpenChange={(o) => {
												if (o) {
													editingSide = line.role;
													sideSearch = '';
												} else if (editingSide === line.role) editingSide = null;
											}}
										>
											<Popover.Trigger>
												{#snippet child({ props })}
													<button
														{...props}
														type="button"
														class="flex h-8 w-full min-w-0 items-center justify-between gap-2 rounded-md border border-input bg-transparent px-2.5 text-left text-sm shadow-xs transition-colors outline-none hover:bg-accent/50 focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 aria-invalid:border-destructive aria-invalid:ring-[3px] aria-invalid:ring-destructive/20 dark:bg-input/30"
														aria-invalid={missing ? 'true' : undefined}
													>
														{#if line.account_id}
															<span class="min-w-0 truncate">
																<span class="font-mono text-[13px]">{line.account_code}</span>
																{line.account_name}
															</span>
														{:else}
															<span class="truncate text-muted-foreground"
																>-- {$i18n.t('Select account')} --</span
															>
														{/if}
														<ChevronsUpDown class="size-4 shrink-0 opacity-50" />
													</button>
												{/snippet}
											</Popover.Trigger>
											<Popover.Content
												align="start"
												class="w-[min(24rem,calc(100vw-2rem))] gap-0 p-0"
											>
												<div class="border-b p-2">
													<Input
														class="h-8"
														placeholder={$i18n.t('Search accounts...')}
														aria-label={$i18n.t('Search accounts...')}
														value={sideSearch}
														oninput={(e: Event) => {
															sideSearch = (e.currentTarget as HTMLInputElement).value;
														}}
													/>
												</div>
												<div class="max-h-64 overflow-y-auto p-1">
													{#each sideCandidates(line, sideSearch, leafAccounts) as a (a.id)}
														<button
															type="button"
															class="flex w-full items-baseline gap-2 rounded-sm px-2 py-1.5 text-left text-sm outline-none hover:bg-accent focus-visible:bg-accent"
															onclick={() => chooseSide(line.role, a.id)}
														>
															<span class="font-mono text-[13px]">{a.code}</span>
															<span class="min-w-0 flex-1 truncate text-muted-foreground"
																>{a.name}</span
															>
															{#if (line.candidates ?? []).some((c: any) => c.id === a.id)}
																<Badge variant="info" class="self-center"
																	>{$i18n.t('suggested')}</Badge
																>
															{/if}
															{#if a.id === line.account_id}<Check
																	class="size-4 self-center"
																/>{/if}
														</button>
													{:else}
														<p class="px-2 py-3 text-center text-sm text-muted-foreground">
															{$i18n.t('No accounts found')}
														</p>
													{/each}
												</div>
											</Popover.Content>
										</Popover.Root>
										<p
											class="mt-1 text-xs {missing ? 'text-destructive' : 'text-muted-foreground'}"
										>
											{$i18n.t(SOURCE_LABEL[line.source] ?? line.source)}
										</p>
										{#if line.note}
											<p class="mt-0.5 flex gap-1 text-xs text-muted-foreground">
												<TriangleAlert class="mt-px size-3.5 shrink-0 text-warning" />
												<span>{$i18n.t(line.note)}</span>
											</p>
										{/if}
									</Table.Cell>
									<Table.Cell
										class="w-28 py-2 pt-3.5 text-right align-top font-medium tabular-nums"
									>
										{fmt(plan.amount)}
									</Table.Cell>
								</Table.Row>
							{/each}

							<!-- The realized exchange difference is a leg of its own -->
							{#if plan.fx}
								<Table.Row
									class="align-top hover:bg-transparent {plan.fx.account_id
										? ''
										: 'bg-warning/5 hover:bg-warning/5'}"
								>
									<Table.Cell class="w-36 py-2 align-top whitespace-normal">
										<div class="font-medium">{$i18n.t(plan.fx.label)}</div>
										<div class="text-xs text-muted-foreground">
											{$i18n.t('booked at')}
											<span class="tabular-nums">{plan.fx.settled_rate}</span>,
											{$i18n.t('paid at')} <span class="tabular-nums">{fxRate?.rate}</span>
										</div>
									</Table.Cell>
									<Table.Cell class="py-2 align-top whitespace-normal">
										{#if plan.fx.account_id}
											<span class="font-mono text-[13px]">{plan.fx.account_code}</span>
											{plan.fx.account_name}
										{:else}
											<p class="text-xs text-destructive">
												{$i18n.t(
													'exchange gain / loss account not set — booked as a draft with a gap'
												)}
											</p>
										{/if}
									</Table.Cell>
									<Table.Cell
										class="w-28 py-2 pt-3.5 text-right align-top font-medium tabular-nums"
									>
										{fmt(plan.fx.amount_base)}
										<span class="font-mono text-xs font-normal text-muted-foreground"
											>{fxRate?.base ?? ''}</span
										>
									</Table.Cell>
								</Table.Row>
							{/if}
						</Table.Body>
					</Table.Root>
				</div>

				<!-- Exchange rate: a notice, never a line -->
				{#if fxForeign}
					{#if fxRate.rate}
						<p class="flex items-center gap-1.5 text-xs text-muted-foreground">
							<ArrowRightLeft class="size-3.5 shrink-0" />
							<span class="tabular-nums">
								{fxRate.currency} → {fxRate.base}: {fxRate.rate} ({$i18n.t('rate on file')}, {fxRate.date})
							</span>
						</p>
					{:else}
						<Alert.Root variant="warning">
							<TriangleAlert />
							<Alert.Title>{fxRate.currency} → {fxRate.base}</Alert.Title>
							<Alert.Description>
								{$i18n.t(
									'no rate on file for {{date}} — the entry stays a draft until one is added in Exchange Rates',
									{ date: fxRate.date }
								)}
							</Alert.Description>
						</Alert.Root>
					{/if}
				{/if}

				{#if plan.warnings?.length}
					<ul class="grid gap-0.5 text-xs text-muted-foreground">
						{#each plan.warnings as w}
							<li class="flex gap-1">
								<TriangleAlert class="mt-px size-3.5 shrink-0 text-warning" /><span>{$i18n.t(w)}</span>
							</li>
						{/each}
					</ul>
				{/if}
			{:else if planLoading}
				<div class="grid gap-2 rounded-md border p-3">
					<Skeleton class="h-8 w-full" />
					<Skeleton class="h-8 w-full" />
				</div>
			{:else}
				<p class="rounded-md border border-dashed px-3 py-2.5 text-sm text-muted-foreground">
					{$i18n.t('Fill in the payment to see the entry.')}
				</p>
			{/if}
		</div>

		<Dialog.Footer>
			<Button variant="outline" disabled={saving} onclick={() => (show = false)}>
				{$i18n.t('Cancel')}
			</Button>
			<Button disabled={saving || !planReady} onclick={handleSave}>
				{#if saving}
					<Spinner />{$i18n.t('Saving...')}
				{:else}
					{$i18n.t('Record Payment')}
				{/if}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Opened from inside the dialog: created after it, so its portal stacks above it -->
<InvoiceSelector
	bind:show={showInvoiceSelector}
	on:select={(e) => {
		const inv = e.detail;
		invoice_id = inv.id;
		invoiceLabel = inv.invoice_number
			? `${inv.invoice_number} — ${inv.vendor_name ?? ''}`
			: `#${inv.id} — ${inv.vendor_name ?? ''}`;
		invoiceK4miDocId = inv.k4mi_document_id ?? null;
		if (inv.vendor_name && direction === 'outbound' && !payee) payee = inv.vendor_name;
		if (inv.vendor_name && direction === 'inbound' && !payer) payer = inv.vendor_name;
		if (inv.total_amount && !amount) amount = parseFloat(String(inv.total_amount));
		if (inv.currency) currency = inv.currency;
	}}
/>
