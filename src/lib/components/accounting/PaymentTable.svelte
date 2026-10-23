<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';

	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import ArrowDownLeft from '@lucide/svelte/icons/arrow-down-left';
	import ArrowUpRight from '@lucide/svelte/icons/arrow-up-right';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import Wallet from '@lucide/svelte/icons/wallet';
	import RotateCw from '@lucide/svelte/icons/rotate-cw';

	import { getPayments, deletePayment, getAccounts } from '$lib/apis/accounting';
	import { convertRowAmount } from '$lib/utils/currency';
	import { user, isAdmin } from '$lib/stores';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';
	import TablePagination from '$lib/components/gnos3-ui/TablePagination.svelte';
	import PaymentFormModal from '$lib/components/accounting/PaymentFormModal.svelte';

	const i18n: any = getContext('i18n');
	const displayCurrency = getContext<Writable<string>>('displayCurrency');
	const exchangeRates = getContext<Writable<any[]>>('exchangeRates');
	const companyCurrencyCtx = getContext<Writable<string>>('companyCurrency');

	export let companyId: number;

	// Permissions (UX gating; backend enforces the real check)
	$: canWrite = $isAdmin || Boolean($user?.permissions?.modules?.accounting?.write);
	$: canDelete = $isAdmin || Boolean($user?.permissions?.modules?.accounting?.admin);

	// Data
	let payments: any[] = [];
	let total = 0;
	let loading = true;
	let loadError = '';
	let accounts: any[] = [];

	// Pagination
	let page = 1;
	let perPage = 20;

	// Filters
	let filterDirection = '';
	let filterMethod = '';
	let filterDateFrom = '';
	let filterDateTo = '';

	$: hasFilters = !!(filterDirection || filterMethod || filterDateFrom || filterDateTo);

	// Delete confirmation
	let showDeleteConfirm = false;
	let deleteTarget: any = null;

	// Form modal
	let showFormModal = false;

	// Methods are plain outline badges: colour is kept for status.
	const METHOD_LABELS: Record<string, string> = {
		cash: 'Cash',
		bank_transfer: 'Bank Transfer',
		check: 'Check',
		credit_card: 'Credit Card',
		other: 'Other'
	};

	// ─── Helpers ────────────────────────────────────────────────────────────────

	const formatDate = (val: any) => {
		if (!val) return '-';
		return dayjs(val).format('YYYY-MM-DD');
	};

	// ─── Currency conversion ────────────────────────────────────────────────────
	$: nativeCurrency = $companyCurrencyCtx || 'EUR';

	// A payment is shown in the display currency converted FROM ITS OWN currency
	// (a USD wire stays USD 1,200 when USD is selected; HKD 9,300 when HKD is).
	const cvt = (amount: any, date?: string, rowCurrency?: string | null) =>
		convertRowAmount(
			amount,
			rowCurrency,
			$displayCurrency,
			nativeCurrency,
			$exchangeRates ?? [],
			date
		);

	// ─── Data loading ───────────────────────────────────────────────────────────

	const loadPayments = async () => {
		loading = true;
		loadError = '';
		try {
			const params: Record<string, any> = {
				limit: perPage,
				offset: (page - 1) * perPage,
				company_id: companyId
			};
			if (filterDirection) params.direction = filterDirection;
			if (filterMethod) params.method = filterMethod;
			if (filterDateFrom) params.date_from = filterDateFrom;
			if (filterDateTo) params.date_to = filterDateTo;

			const res = await getPayments(params);
			if (res) {
				if (Array.isArray(res)) {
					payments = res;
					total = res.length;
				} else {
					payments = res.payments ?? [];
					total = res.total ?? payments.length;
				}
			}
		} catch (err) {
			loadError = `${err}`;
			toast.error(`${err}`);
		}
		loading = false;
	};

	const loadAccounts = async () => {
		try {
			const res = await getAccounts({ company_id: companyId });
			if (Array.isArray(res)) {
				accounts = res;
			} else {
				accounts = res?.items ?? res?.accounts ?? [];
			}
		} catch {
			accounts = [];
		}
	};

	// ─── Filter handlers ────────────────────────────────────────────────────────

	const applyFilters = () => {
		page = 1;
		loadPayments();
	};

	const resetFilters = () => {
		filterDirection = '';
		filterMethod = '';
		filterDateFrom = '';
		filterDateTo = '';
		page = 1;
		loadPayments();
	};

	// ─── Delete ─────────────────────────────────────────────────────────────────

	const confirmDelete = (payment: any) => {
		deleteTarget = payment;
		showDeleteConfirm = true;
	};

	const handleDelete = async () => {
		if (!deleteTarget) return;
		try {
			await deletePayment(deleteTarget.id);
			toast.success($i18n.t('Payment deleted'));
			if (payments.length === 1 && page > 1) {
				page -= 1;
			}
			loadPayments();
		} catch (err) {
			toast.error(`${err}`);
		}
		deleteTarget = null;
	};

	// ─── Form modal ─────────────────────────────────────────────────────────────

	const handleFormSave = () => {
		loadPayments();
	};

	// ─── Lifecycle ──────────────────────────────────────────────────────────────

	let mounted = false;

	$: if (mounted && page) {
		loadPayments();
	}

	onMount(() => {
		loadPayments().then(() => {
			mounted = true;
		});
		loadAccounts();
	});
</script>

<ConfirmDialog
	bind:open={showDeleteConfirm}
	title={$i18n.t('Delete Payment')}
	description={$i18n.t(
		'Are you sure you want to delete this payment? This action cannot be undone.'
	)}
	confirmLabel={$i18n.t('Delete')}
	destructive
	onconfirm={handleDelete}
	oncancel={() => (deleteTarget = null)}
/>

<PaymentFormModal bind:show={showFormModal} {accounts} {companyId} on:save={handleFormSave} />

<div class="flex flex-col gap-4">
	<!-- Header: title + count + the primary action -->
	<div class="flex flex-wrap items-center justify-between gap-2">
		<div class="flex items-baseline gap-2">
			<h2 class="text-lg font-semibold">{$i18n.t('Payments')}</h2>
			<span class="text-sm text-muted-foreground tabular-nums">{total}</span>
		</div>
		{#if canWrite}
			<Button size="sm" onclick={() => (showFormModal = true)}>
				<Plus />{$i18n.t('Record Payment')}
			</Button>
		{/if}
	</div>

	<!-- Toolbar: filters -->
	<div class="flex flex-wrap items-center gap-x-3 gap-y-2">
		<div class="flex items-center gap-1.5">
			<label for="filter-direction" class="text-sm text-muted-foreground"
				>{$i18n.t('Direction')}</label
			>
			<NativeSelect.Root
				id="filter-direction"
				size="sm"
				bind:value={filterDirection}
				onchange={applyFilters}
			>
				<NativeSelect.Option value="">{$i18n.t('All')}</NativeSelect.Option>
				<NativeSelect.Option value="inbound">{$i18n.t('Inbound')}</NativeSelect.Option>
				<NativeSelect.Option value="outbound">{$i18n.t('Outbound')}</NativeSelect.Option>
			</NativeSelect.Root>
		</div>

		<div class="flex items-center gap-1.5">
			<label for="filter-method" class="text-sm text-muted-foreground">{$i18n.t('Method')}</label>
			<NativeSelect.Root
				id="filter-method"
				size="sm"
				bind:value={filterMethod}
				onchange={applyFilters}
			>
				<NativeSelect.Option value="">{$i18n.t('All')}</NativeSelect.Option>
				<NativeSelect.Option value="cash">{$i18n.t('Cash')}</NativeSelect.Option>
				<NativeSelect.Option value="bank_transfer">{$i18n.t('Bank Transfer')}</NativeSelect.Option>
				<NativeSelect.Option value="check">{$i18n.t('Check')}</NativeSelect.Option>
				<NativeSelect.Option value="credit_card">{$i18n.t('Credit Card')}</NativeSelect.Option>
				<NativeSelect.Option value="other">{$i18n.t('Other')}</NativeSelect.Option>
			</NativeSelect.Root>
		</div>

		<div class="flex items-center gap-1.5">
			<label for="filter-date-from" class="text-sm text-muted-foreground">{$i18n.t('From')}</label>
			<Input
				id="filter-date-from"
				type="date"
				class="h-8 w-auto tabular-nums"
				bind:value={filterDateFrom}
				onchange={applyFilters}
			/>
		</div>

		<div class="flex items-center gap-1.5">
			<label for="filter-date-to" class="text-sm text-muted-foreground">{$i18n.t('To')}</label>
			<Input
				id="filter-date-to"
				type="date"
				class="h-8 w-auto tabular-nums"
				bind:value={filterDateTo}
				onchange={applyFilters}
			/>
		</div>

		{#if hasFilters}
			<Button variant="ghost" size="sm" onclick={resetFilters}>
				<X />{$i18n.t('Clear')}
			</Button>
		{/if}
	</div>

	<!-- Table -->
	{#if loading && payments.length === 0}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(8) as _}
				<Skeleton class="h-8 w-full" />
			{/each}
		</div>
	{:else if loadError && payments.length === 0}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Failed to load payments')}</Alert.Title>
			<Alert.Description>
				<p>{loadError}</p>
				<Button variant="outline" size="sm" class="mt-2" onclick={loadPayments}>
					<RotateCw />{$i18n.t('Retry')}
				</Button>
			</Alert.Description>
		</Alert.Root>
	{:else if payments.length === 0}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><Wallet /></Empty.Media>
				<Empty.Title>{$i18n.t('No payments found')}</Empty.Title>
				<Empty.Description>
					{#if hasFilters}
						{$i18n.t('Try other filters, or clear them to see every payment.')}
					{:else}
						{$i18n.t('Record a payment, or match a bank line in the Bank tab.')}
					{/if}
				</Empty.Description>
			</Empty.Header>
			<Empty.Content>
				{#if hasFilters}
					<Button variant="outline" size="sm" onclick={resetFilters}>
						<X />{$i18n.t('Clear')}
					</Button>
				{:else if canWrite}
					<Button size="sm" onclick={() => (showFormModal = true)}>
						<Plus />{$i18n.t('Record Payment')}
					</Button>
				{/if}
			</Empty.Content>
		</Empty.Root>
	{:else}
		<div class="overflow-hidden rounded-md border">
			<Table.Root>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						<Table.Head>{$i18n.t('#')}</Table.Head>
						<Table.Head>{$i18n.t('Date')}</Table.Head>
						<Table.Head>{$i18n.t('Direction')}</Table.Head>
						<Table.Head>{$i18n.t('Currency')}</Table.Head>
						<Table.Head class="text-right">{$i18n.t('Amount')}</Table.Head>
						<Table.Head>{$i18n.t('Method')}</Table.Head>
						<Table.Head>{$i18n.t('Payer / Payee')}</Table.Head>
						<Table.Head>{$i18n.t('Invoice')}</Table.Head>
						<Table.Head>{$i18n.t('Reference')}</Table.Head>
						<Table.Head class="w-12"><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each payments as payment (payment.id)}
						<Table.Row>
							<Table.Cell class="font-mono text-[13px] text-muted-foreground"
								>{payment.id}</Table.Cell
							>

							<Table.Cell class="tabular-nums">{formatDate(payment.payment_date)}</Table.Cell>

							<Table.Cell>
								{#if payment.direction === 'inbound'}
									<Badge variant="status"><ArrowDownLeft />{$i18n.t('In')}</Badge>
								{:else}
									<Badge variant="status"><ArrowUpRight />{$i18n.t('Out')}</Badge>
								{/if}
							</Table.Cell>

							<Table.Cell class="font-mono text-[13px] text-muted-foreground">
								{payment.currency ?? '—'}
							</Table.Cell>

							<Table.Cell class="text-right font-medium tabular-nums">
								{#key $displayCurrency}
									{@const c = cvt(payment.amount, payment.payment_date, payment.currency)}
									{#if c.converting}
										{#if c.hasRate}
											<span
												>{c.display}
												<span class="text-xs font-normal text-muted-foreground">{c.to}</span></span
											>
											<div class="text-xs font-normal text-muted-foreground">
												{c.original}
												{c.from}
											</div>
										{:else}
											<span class="inline-flex items-center gap-1">
												{c.original}
												{c.from}
												<Tip content={$i18n.t('No exchange rate available')}>
													<TriangleAlert
														class="size-3.5 text-warning"
														aria-label={$i18n.t('No exchange rate available')}
													/>
												</Tip>
											</span>
										{/if}
									{:else}
										{c.original}
									{/if}
								{/key}
							</Table.Cell>

							<Table.Cell>
								<Badge variant="outline">
									{$i18n.t(METHOD_LABELS[payment.method] ?? payment.method ?? '-')}
								</Badge>
							</Table.Cell>

							<Table.Cell class="max-w-[12rem]">
								{@const party = payment.direction === 'inbound' ? payment.payer : payment.payee}
								{#if party}
									<span class="block truncate" title={party}>{party}</span>
								{:else}
									<span class="text-muted-foreground">—</span>
								{/if}
							</Table.Cell>

							<Table.Cell>
								{#if payment.invoice_id}
									<a
										href="/accounting/company/{companyId}/entries?invoice_id={payment.invoice_id}"
										class="font-mono text-[13px] text-link underline-offset-4 hover:underline"
										title={$i18n.t('Entries for this invoice')}
									>
										#{payment.invoice_id}
									</a>
								{:else}
									<span class="text-muted-foreground">—</span>
								{/if}
							</Table.Cell>

							<Table.Cell class="max-w-[10rem]">
								{#if payment.reference}
									<span class="block truncate font-mono text-[13px]" title={payment.reference}>
										{payment.reference}
									</span>
								{:else}
									<span class="text-muted-foreground">—</span>
								{/if}
							</Table.Cell>

							<Table.Cell class="text-right">
								{#if canDelete}
									<Tip content={$i18n.t('Delete')}>
										<Button
											variant="ghost"
											size="icon-xs"
											class="text-muted-foreground hover:text-destructive"
											aria-label={$i18n.t('Delete')}
											onclick={() => confirmDelete(payment)}
										>
											<Trash2 />
										</Button>
									</Tip>
								{/if}
							</Table.Cell>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</div>

		<!-- Per page + count + pager -->
		<div class="flex flex-wrap items-center gap-x-4 gap-y-2">
			<div class="flex items-center gap-1.5">
				<label for="payments-per-page" class="text-sm text-muted-foreground"
					>{$i18n.t('Per page')}</label
				>
				<NativeSelect.Root
					id="payments-per-page"
					size="sm"
					bind:value={perPage}
					onchange={() => {
						page = 1;
						loadPayments();
					}}
				>
					<NativeSelect.Option value={20}>20</NativeSelect.Option>
					<NativeSelect.Option value={50}>50</NativeSelect.Option>
					<NativeSelect.Option value={100}>100</NativeSelect.Option>
				</NativeSelect.Root>
			</div>
			<TablePagination class="flex-1" bind:page count={total} {perPage} />
		</div>
	{/if}
</div>
