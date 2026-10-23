<script lang="ts">
	import { onMount, getContext, createEventDispatcher } from 'svelte';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import Ellipsis from '@lucide/svelte/icons/ellipsis';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import FileText from '@lucide/svelte/icons/file-text';
	import Info from '@lucide/svelte/icons/info';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';

	import {
		getTaxFilings,
		markTaxFilingPaid,
		deleteTaxFiling,
		getAccounts,
		getTaxPaymentPreview
	} from '$lib/apis/accounting';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let companyId: number;
	export let taxType: string;

	let loading = true;
	let loadError = '';
	let filings: any[] = [];
	let accounts: any[] = [];

	let payingId: number | null = null;
	let payFiling: any = null;
	let payOpen = false;
	let bankAccountId: number | '' = '';
	let payableAccountId: number | '' = '';
	let paidDate = '';
	// CIT: the year's final tax as printed on the assessment notice (blank = as accrued).
	let assessedAmount: string | number | null = '';
	let processing = false;
	// What the settlement will book (debit and credit legs) + roles still unmapped.
	let preview: {
		legs: any[];
		missing: string[];
		total: number;
		bank?: number;
		warnings?: string[];
		over_under?: number;
		tax_accrued?: number;
		bank_fx?: any;
	} | null = null;
	let previewLoading = false;
	const blank = (v: any) => v === '' || v === null || v === undefined;
	const assessed = () =>
		blank(assessedAmount) ? undefined : parseFloat(String(assessedAmount)) || 0;
	$: isCit = taxType === 'cit';
	// Foreign-currency bank account: what left the bank in its currency, and the
	// rate (prefilled from the rate table; typed when the bank's rate differs).
	let bankFcAmount: string | number | null = '';
	let bankRate: string | number | null = '';
	const numOr = (v: any) => (blank(v) ? undefined : parseFloat(String(v)) || undefined);
	$: bankFx = preview?.bank_fx ?? null;
	$: foreignBank = !!bankFx?.foreign;

	// Delete confirmation
	let deleteTarget: any = null;
	let showDeleteConfirm = false;

	const fmt = (v: any): string => {
		const n = typeof v === 'string' ? parseFloat(v) : (v ?? 0);
		return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	};
	const today = () => new Date().toISOString().slice(0, 10);
	const fmtDate = (d: any) => (d ? dayjs(d).format('YYYY-MM-DD') : '—');

	$: parentIds = new Set(accounts.map((a: any) => a.parent_id).filter(Boolean));
	$: leafAccounts = accounts.filter((a: any) => !parentIds.has(a.id));
	$: bankAccounts = leafAccounts.filter((a: any) => !a.account_type || a.account_type === 'asset');
	$: payableAccounts = leafAccounts.filter((a: any) => a.account_type === 'liability');
	$: selectedBank =
		bankAccountId === '' ? null : bankAccounts.find((a: any) => a.id === Number(bankAccountId));

	export async function reload() {
		loading = true;
		loadError = '';
		try {
			const res = await getTaxFilings({ company_id: companyId, tax_type: taxType });
			filings = Array.isArray(res) ? res : [];
		} catch (err: any) {
			loadError = `${err?.detail ?? err}`;
			toast.error(`${$i18n.t('Failed to load filings')}: ${err?.detail ?? err}`);
		}
		loading = false;
	}

	onMount(async () => {
		try {
			const a = await getAccounts({ company_id: companyId, active: true });
			accounts = Array.isArray(a) ? a : (a?.items ?? a?.accounts ?? []);
		} catch {
			accounts = [];
		}
		await reload();
	});

	const loadPreview = async (f: any) => {
		previewLoading = true;
		try {
			preview = await getTaxPaymentPreview(
				f.id,
				payableAccountId === '' ? undefined : Number(payableAccountId),
				isCit ? assessed() : undefined,
				{
					bank_account_id: bankAccountId === '' ? undefined : Number(bankAccountId),
					bank_fc_amount: numOr(bankFcAmount),
					rate: numOr(bankRate),
					paid_date: paidDate || undefined
				}
			);
		} catch (err: any) {
			preview = null;
			toast.error(`${$i18n.t('Failed to preview payment')}: ${err?.detail ?? err}`);
		}
		previewLoading = false;
	};

	const startPay = async (f: any) => {
		payingId = f.id;
		payFiling = f;
		bankAccountId = '';
		payableAccountId = '';
		assessedAmount = '';
		bankFcAmount = '';
		bankRate = '';
		paidDate = today();
		preview = null;
		payOpen = true;
		await loadPreview(f);
	};

	const closePay = () => {
		payOpen = false;
		payingId = null;
	};

	const confirmPay = async (f: any) => {
		if (!bankAccountId) {
			toast.error($i18n.t('Select a bank account'));
			return;
		}
		processing = true;
		try {
			await markTaxFilingPaid(f.id, {
				bank_account_id: Number(bankAccountId),
				paid_date: paidDate || today(),
				payable_account_id: payableAccountId === '' ? undefined : Number(payableAccountId),
				assessed_amount: isCit ? assessed() : undefined,
				bank_fc_amount: foreignBank ? numOr(bankFcAmount) : undefined,
				rate: foreignBank ? numOr(bankRate) : undefined
			});
			toast.success(
				(preview?.bank ?? preview?.total ?? 0) > 0
					? $i18n.t('Filing marked paid')
					: $i18n.t('Filing settled against provisional tax — no bank movement')
			);
			closePay();
			await reload();
		} catch (err: any) {
			toast.error(`${$i18n.t('Failed to mark paid')}: ${err?.detail ?? err}`);
		}
		processing = false;
	};

	const askRemove = (f: any) => {
		deleteTarget = f;
		showDeleteConfirm = true;
	};

	const remove = async (f: any) => {
		try {
			await deleteTaxFiling(f.id);
			await reload();
		} catch (err: any) {
			toast.error(`${err?.detail ?? err}`);
		}
	};

	// The API stores draft / entry_posted / paid plus an `overdue` flag; the list
	// shows what matters for payment: open, overdue or paid.
	const statusKey = (f: any) => (f.status === 'paid' ? 'paid' : f.overdue ? 'overdue' : 'open');
	const entryStatusText = (f: any) => {
		const st = f.settlement_entry_status;
		return st === 'posted'
			? $i18n.t('Posted')
			: st === 'voided'
				? $i18n.t('Voided')
				: $i18n.t('Draft');
	};
	const entryNumber = (f: any) =>
		f.settlement_entry_number ? f.settlement_entry_number : `#${f.settlement_transaction_id}`;
	const periodText = (f: any) => `${fmtDate(f.period_start)} → ${fmtDate(f.period_end)}`;
	const money = (v: any, ccy?: string | null) => `${ccy ? `${ccy} ` : ''}${fmt(v)}`;
</script>

<div class="flex flex-col gap-2">
	<h3 class="text-sm font-medium">{$i18n.t('Filings')}</h3>

	{#if loading && filings.length === 0}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(3) as _}
				<Skeleton class="h-8 w-full" />
			{/each}
		</div>
	{:else if loadError && filings.length === 0}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Failed to load filings')}</Alert.Title>
			<Alert.Description>
				<p>{loadError}</p>
				<Button variant="outline" size="sm" class="mt-2" onclick={reload}>
					<RotateCcw />{$i18n.t('Retry')}
				</Button>
			</Alert.Description>
		</Alert.Root>
	{:else if filings.length === 0}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><FileText /></Empty.Media>
				<Empty.Title>{$i18n.t('No filings yet')}</Empty.Title>
				<Empty.Description>
					{$i18n.t('No saved filings yet. Calculate a period and Save it as a filing.')}
				</Empty.Description>
			</Empty.Header>
		</Empty.Root>
	{:else}
		<div class="overflow-hidden rounded-md border">
			<Table.Root>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						<Table.Head>{$i18n.t('Period')}</Table.Head>
						<Table.Head>{$i18n.t('Due date')}</Table.Head>
						<Table.Head class="text-right">{$i18n.t('Amount')}</Table.Head>
						<Table.Head>{$i18n.t('Entry')}</Table.Head>
						<Table.Head>{$i18n.t('Status')}</Table.Head>
						<Table.Head class="text-right"
							><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head
						>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each filings as f (f.id)}
						<Table.Row>
							<Table.Cell class="tabular-nums">{periodText(f)}</Table.Cell>
							<Table.Cell class="tabular-nums">{fmtDate(f.due_date)}</Table.Cell>
							<Table.Cell class="text-right tabular-nums"
								>{money(f.tax_amount, f.currency)}</Table.Cell
							>
							<Table.Cell>
								{#if f.settlement_transaction_id}
									<span class="text-muted-foreground">{entryStatusText(f)}</span>
									<span class="font-mono text-[13px]">{entryNumber(f)}</span>
								{:else}
									<span class="text-muted-foreground">—</span>
								{/if}
							</Table.Cell>
							<Table.Cell><StatusBadge kind="tax" status={statusKey(f)} /></Table.Cell>
							<Table.Cell class="text-right">
								<div class="inline-flex items-center justify-end gap-1">
									{#if f.status !== 'paid' && Number(f.tax_amount) <= 0}
										<Tip
											content={$i18n.t(
												'Nothing to pay: the tax office refunds or credits the excess — record the refund as a receipt against the prepaid-tax account.'
											)}
										>
											<span
												class="inline-flex items-center gap-1 text-[13px] text-muted-foreground"
											>
												{$i18n.t('Refund / nothing to pay')}<Info class="size-3.5" />
											</span>
										</Tip>
									{:else if f.status !== 'paid'}
										<Button variant="outline" size="xs" onclick={() => startPay(f)}>
											{isCit ? $i18n.t('Settle') : $i18n.t('Mark Paid')}
										</Button>
									{:else}
										<span class="text-[13px] text-muted-foreground tabular-nums">
											{$i18n.t('Paid')}
											{fmtDate(f.paid_date)}
										</span>
									{/if}
									{#if f.status !== 'paid'}
										<DropdownMenu.Root>
											<DropdownMenu.Trigger>
												{#snippet child({ props })}
													<Button
														{...props}
														variant="ghost"
														size="icon-xs"
														aria-label={$i18n.t('More actions')}
													>
														<Ellipsis />
													</Button>
												{/snippet}
											</DropdownMenu.Trigger>
											<DropdownMenu.Content align="end" class="w-44">
												<DropdownMenu.Item variant="destructive" onSelect={() => askRemove(f)}>
													<Trash2 />{$i18n.t('Delete')}
												</DropdownMenu.Item>
											</DropdownMenu.Content>
										</DropdownMenu.Root>
									{/if}
								</div>
							</Table.Cell>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</div>
	{/if}
</div>

<Dialog.Root
	bind:open={payOpen}
	onOpenChange={(v) => {
		if (!v) payingId = null;
	}}
>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
		{#if payFiling}
			{@const f = payFiling}
			<Dialog.Header>
				<Dialog.Title>{isCit ? $i18n.t('Settle') : $i18n.t('Mark Paid')}</Dialog.Title>
				<Dialog.Description class="tabular-nums">
					{periodText(f)} · {money(f.tax_amount, f.currency)}
				</Dialog.Description>
			</Dialog.Header>

			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2">
					<Label for="pay-bank-{f.id}">{$i18n.t('Bank / cash account (credit)')}</Label>
					<NativeSelect.Root
						id="pay-bank-{f.id}"
						class="w-full"
						bind:value={bankAccountId}
						onchange={() => {
							bankFcAmount = '';
							bankRate = '';
							loadPreview(f);
						}}
					>
						<NativeSelect.Option value="">{$i18n.t('Select account...')}</NativeSelect.Option>
						{#each bankAccounts as acct}
							<NativeSelect.Option value={acct.id}>{acct.code} - {acct.name}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
				<div class="grid gap-2">
					<Label for="pay-date-{f.id}">{$i18n.t('Paid date')}</Label>
					<Input
						id="pay-date-{f.id}"
						type="date"
						bind:value={paidDate}
						onchange={() => loadPreview(f)}
					/>
				</div>
				{#if foreignBank}
					<div class="grid gap-2">
						<Label for="pay-fc-{f.id}">{$i18n.t('Amount debited')} ({bankFx.bank_currency})</Label>
						<Input
							id="pay-fc-{f.id}"
							type="number"
							step="0.01"
							class="text-right tabular-nums"
							bind:value={bankFcAmount}
							onchange={() => loadPreview(f)}
							placeholder={bankFx.bank_fc_suggested != null
								? `${$i18n.t('at the rate')}: ${fmt(bankFx.bank_fc_suggested)}`
								: ''}
						/>
					</div>
					<div class="grid gap-2">
						<Label for="pay-rate-{f.id}"
							>{$i18n.t('Rate')} {bankFx.bank_currency} → {bankFx.base_currency}</Label
						>
						<Input
							id="pay-rate-{f.id}"
							type="number"
							step="0.00000001"
							class="text-right tabular-nums"
							bind:value={bankRate}
							onchange={() => loadPreview(f)}
							placeholder={bankFx.rate != null
								? `${bankFx.rate} (${bankFx.rate_source})`
								: $i18n.t('no rate on file — type it')}
						/>
					</div>
				{/if}
				<div class="grid gap-2">
					<Label for="pay-payable-{f.id}">{$i18n.t('Tax payable account (debit)')}</Label>
					<NativeSelect.Root
						id="pay-payable-{f.id}"
						class="w-full"
						bind:value={payableAccountId}
						onchange={() => loadPreview(f)}
					>
						<NativeSelect.Option value=""
							>{$i18n.t('From Tax accounts mapping')}</NativeSelect.Option
						>
						{#each payableAccounts as acct}
							<NativeSelect.Option value={acct.id}>{acct.code} - {acct.name}</NativeSelect.Option>
						{/each}
					</NativeSelect.Root>
				</div>
				{#if isCit}
					<div class="grid gap-2 sm:col-span-2">
						<Label for="pay-assessed-{f.id}">
							{$i18n.t(
								"Final tax per the assessment notice (the year's tax, before provisional tax)"
							)}
						</Label>
						<Input
							id="pay-assessed-{f.id}"
							type="number"
							step="0.01"
							class="text-right tabular-nums sm:max-w-64"
							bind:value={assessedAmount}
							onchange={() => loadPreview(f)}
							placeholder={preview?.tax_accrued !== undefined
								? `${$i18n.t('as accrued')}: ${fmt(preview.tax_accrued)}`
								: $i18n.t('as accrued')}
						/>
					</div>
				{/if}
			</div>

			<div class="flex flex-col gap-2">
				<span class="text-[13px] font-medium">{$i18n.t('This will book:')}</span>
				{#if previewLoading && !preview}
					<div class="flex flex-col gap-2 rounded-md border p-3">
						{#each Array(3) as _}<Skeleton class="h-6 w-full" />{/each}
					</div>
				{:else if preview}
					<div class="overflow-hidden rounded-md border" class:opacity-60={previewLoading}>
						<Table.Root class="text-[13px]">
							<Table.Body>
								{#each preview.legs as leg}
									<Table.Row class="hover:bg-transparent">
										<Table.Cell class="w-10 py-1.5 text-muted-foreground"
											>{(leg.side ?? 'debit') === 'debit' ? 'DR' : 'CR'}</Table.Cell
										>
										<Table.Cell class="py-1.5 whitespace-normal">
											{#if leg.account}
												<span class="font-mono">{leg.account.code}</span>
												{leg.account.name}
											{:else}
												<span class="inline-flex items-center gap-1 text-destructive">
													<CircleAlert class="size-3.5" />{$i18n.t('— not mapped —')}
												</span>
											{/if}
											<!-- The line text the payment entry will carry, in the books language -->
											<span class="block text-xs text-muted-foreground">{leg.label}</span>
										</Table.Cell>
										<Table.Cell class="py-1.5 text-right tabular-nums">{fmt(leg.amount)}</Table.Cell
										>
									</Table.Row>
								{/each}
								<Table.Row class="font-medium hover:bg-transparent">
									<Table.Cell class="py-1.5 text-muted-foreground">
										{(preview.bank ?? preview.total) > 0 ? 'CR' : ''}
									</Table.Cell>
									<Table.Cell class="py-1.5 whitespace-normal">
										{#if (preview.bank ?? preview.total) > 0}
											{#if selectedBank}
												<span class="font-mono">{selectedBank.code}</span>
												{selectedBank.name}
											{:else}
												{$i18n.t('Bank')}
											{/if}
										{:else}
											{$i18n.t('Nothing to pay from the bank')}
										{/if}
									</Table.Cell>
									<Table.Cell class="py-1.5 text-right tabular-nums">
										{fmt(preview.bank ?? preview.total)}
									</Table.Cell>
								</Table.Row>
							</Table.Body>
						</Table.Root>
					</div>
					{#if foreignBank}
						<p class="text-[13px] text-muted-foreground">
							{$i18n.t(
								'Paid from a {{ccy}} account: the obligations are cleared in {{base}} through the exchange clearing account, then the clearing is moved to the bank in {{ccy}}.',
								{ ccy: bankFx.bank_currency, base: bankFx.base_currency }
							)}
							{#if bankFx.fx_kind}
								— {$i18n.t(bankFx.fx_kind === 'loss' ? 'exchange loss' : 'exchange gain')}
								<span class="tabular-nums"
									>{fmt(Math.abs(bankFx.fx_base))} {bankFx.base_currency}</span
								>
								→ {bankFx.fx_account
									? `${bankFx.fx_account.code} ${bankFx.fx_account.name}`
									: $i18n.t('account not set')}
							{/if}
						</p>
					{/if}
					{#if (preview.warnings ?? []).length > 0}
						<Alert.Root variant="warning">
							<TriangleAlert />
							<Alert.Description>
								{#each preview.warnings ?? [] as w}<p>{$i18n.t(w)}</p>{/each}
							</Alert.Description>
						</Alert.Root>
					{/if}
					{#if preview.missing.length > 0}
						<Alert.Root variant="warning">
							<TriangleAlert />
							<Alert.Title>{$i18n.t('Missing')}: {preview.missing.map((m) => $i18n.t(m)).join(' · ')}</Alert.Title>
							<Alert.Description>
								<p>
									{$i18n.t(
										'Map the missing role(s) in the Accounts tab (or pick a tax payable account above) before recording.'
									)}
								</p>
								<Button
									variant="link"
									size="sm"
									onclick={() => {
										closePay();
										dispatch('gotoAccounts');
									}}>{$i18n.t('Open Tax accounts')}</Button
								>
							</Alert.Description>
						</Alert.Root>
					{/if}
				{/if}
			</div>

			<Dialog.Footer>
				<Button variant="outline" onclick={closePay}>{$i18n.t('Cancel')}</Button>
				<Button
					disabled={processing ||
						!bankAccountId ||
						(preview?.missing?.length ?? 0) > 0 ||
						(foreignBank && numOr(bankFcAmount) === undefined)}
					onclick={() => confirmPay(f)}
				>
					{#if processing}<Spinner />{/if}
					{processing ? $i18n.t('Recording...') : $i18n.t('Record payment')}
				</Button>
			</Dialog.Footer>
		{/if}
	</Dialog.Content>
</Dialog.Root>

<ConfirmDialog
	bind:open={showDeleteConfirm}
	title={$i18n.t('Delete filing?')}
	description={deleteTarget
		? `${periodText(deleteTarget)} · ${money(deleteTarget.tax_amount, deleteTarget.currency)}. ${$i18n.t('The saved computation is removed; entries already created stay in the ledger.')}`
		: ''}
	confirmLabel={$i18n.t('Delete')}
	destructive
	onconfirm={async () => {
		if (deleteTarget) await remove(deleteTarget);
		deleteTarget = null;
	}}
	oncancel={() => (deleteTarget = null)}
/>
