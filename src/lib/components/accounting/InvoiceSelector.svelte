<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';

	import Search from '@lucide/svelte/icons/search';
	import Info from '@lucide/svelte/icons/info';
	import ExternalLink from '@lucide/svelte/icons/external-link';
	import FileSearch from '@lucide/svelte/icons/file-search';
	import ChevronLeft from '@lucide/svelte/icons/chevron-left';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';

	import { getInvoiceList } from '$lib/apis/accounting';
	import K4miDocLink from '$lib/components/common/K4miDocLink.svelte';

	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Popover from '$lib/components/ui/popover/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;

	let loading = false;
	let invoices: any[] = [];
	let total = 0;
	let search = '';
	let searchDebounce: ReturnType<typeof setTimeout>;
	let offset = 0;
	const limit = 20;

	// Filter state
	let statusFilter: string = 'all'; // 'all' | 'review' | 'ready'
	let sortBy: string = 'date_desc'; // 'date_desc' | 'amount_desc' | 'vendor_asc'

	// Details popover: the invoice whose details are open
	let previewInvoice: any = null;

	const sortOptions: Record<string, { sort_by: string; sort_dir: string }> = {
		date_desc: { sort_by: 'invoice_date', sort_dir: 'desc' },
		amount_desc: { sort_by: 'total_amount', sort_dir: 'desc' },
		vendor_asc: { sort_by: 'vendor_name', sort_dir: 'asc' }
	};

	const loadInvoices = async (resetOffset = true) => {
		if (resetOffset) offset = 0;
		loading = true;
		try {
			const params: Record<string, any> = { limit, offset };
			if (search) params.q = search;

			// Status filter
			if (statusFilter === 'review') {
				params.needs_review = true;
			} else if (statusFilter === 'ready') {
				params.needs_review = false;
			}

			// Sort
			const sort = sortOptions[sortBy] ?? sortOptions.date_desc;
			params.sort_by = sort.sort_by;
			params.sort_dir = sort.sort_dir;

			const res = await getInvoiceList(params);
			if (res && res.invoices) {
				invoices = res.invoices;
				total = res.total ?? invoices.length;
			} else if (Array.isArray(res)) {
				invoices = res;
				total = res.length;
			} else {
				invoices = [];
				total = 0;
			}
		} catch (err) {
			toast.error(`${$i18n.t('Failed to load invoices')}: ${err}`);
		}
		loading = false;
	};

	const handleSearch = () => {
		clearTimeout(searchDebounce);
		searchDebounce = setTimeout(() => loadInvoices(), 300);
	};

	const selectInvoice = (invoice: any) => {
		dispatch('select', invoice);
		show = false;
	};

	const formatCurrency = (val: any) => {
		if (val === null || val === undefined) return '—';
		return parseFloat(val).toLocaleString(undefined, {
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		});
	};

	const formatDate = (val: any) => (val ? dayjs(val).format('YYYY-MM-DD') : '—');

	const getLineItemsCount = (invoice: any): number => {
		if (!invoice.line_items) return 0;
		if (Array.isArray(invoice.line_items)) return invoice.line_items.length;
		if (typeof invoice.line_items === 'object' && invoice.line_items.items) {
			return Array.isArray(invoice.line_items.items) ? invoice.line_items.items.length : 0;
		}
		return 0;
	};

	// Row keyboard access: Enter / Space on the row itself selects it.
	const rowKeydown = (e: KeyboardEvent, invoice: any) => {
		if (e.target !== e.currentTarget) return;
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			selectInvoice(invoice);
		}
	};

	$: if (show) {
		previewInvoice = null;
		loadInvoices();
	}
</script>

<Dialog.Root bind:open={show}>
	<Dialog.Content class="flex max-h-[90vh] flex-col gap-4 sm:max-w-5xl">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Select Invoice')}</Dialog.Title>
			<Dialog.Description>{$i18n.t('Click an invoice to link it.')}</Dialog.Description>
		</Dialog.Header>

		<!-- Search + filters -->
		<div class="flex flex-wrap items-center gap-2">
			<div class="relative w-full">
				<Search
					class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
				/>
				<Input
					type="search"
					class="pl-8"
					placeholder={$i18n.t(
						'Search by vendor, invoice number, client, description, or amount...'
					)}
					aria-label={$i18n.t('Search')}
					bind:value={search}
					oninput={handleSearch}
				/>
			</div>
			<div class="flex items-center gap-1.5">
				<label for="inv-sel-status" class="text-sm text-muted-foreground">{$i18n.t('Status')}</label
				>
				<NativeSelect.Root
					id="inv-sel-status"
					size="sm"
					bind:value={statusFilter}
					onchange={() => loadInvoices()}
				>
					<NativeSelect.Option value="all">{$i18n.t('All')}</NativeSelect.Option>
					<NativeSelect.Option value="review">{$i18n.t('Needs Review')}</NativeSelect.Option>
					<NativeSelect.Option value="ready">{$i18n.t('Ready')}</NativeSelect.Option>
				</NativeSelect.Root>
			</div>
			<div class="flex items-center gap-1.5">
				<label for="inv-sel-sort" class="text-sm text-muted-foreground">{$i18n.t('Sort')}</label>
				<NativeSelect.Root
					id="inv-sel-sort"
					size="sm"
					bind:value={sortBy}
					onchange={() => loadInvoices()}
				>
					<NativeSelect.Option value="date_desc">{$i18n.t('Date (newest)')}</NativeSelect.Option>
					<NativeSelect.Option value="amount_desc"
						>{$i18n.t('Amount (highest)')}</NativeSelect.Option
					>
					<NativeSelect.Option value="vendor_asc">{$i18n.t('Vendor (A-Z)')}</NativeSelect.Option>
				</NativeSelect.Root>
			</div>
			{#if !loading && total > 0}
				<span class="ml-auto text-sm text-muted-foreground tabular-nums">
					{total}
					{$i18n.t('invoices')}
				</span>
			{/if}
		</div>

		<!-- Invoice list -->
		<div class="min-h-0 flex-1 overflow-y-auto">
			{#if loading}
				<div class="flex flex-col gap-2 rounded-md border p-3">
					{#each Array(6) as _}
						<Skeleton class="h-8 w-full" />
					{/each}
				</div>
			{:else if invoices.length === 0}
				<Empty.Root class="border border-dashed">
					<Empty.Header>
						<Empty.Media variant="icon"><FileSearch /></Empty.Media>
						<Empty.Title>{$i18n.t('No invoices found')}</Empty.Title>
						<Empty.Description>
							{$i18n.t('Try another search, or set the status filter to All.')}
						</Empty.Description>
					</Empty.Header>
				</Empty.Root>
			{:else}
				<div class="overflow-hidden rounded-md border">
					<Table.Root class="text-[13px]">
						<Table.Header class="bg-muted/50">
							<Table.Row class="hover:bg-transparent">
								<Table.Head>{$i18n.t('Invoice #')}</Table.Head>
								<Table.Head>{$i18n.t('Vendor')}</Table.Head>
								<Table.Head>{$i18n.t('Client')}</Table.Head>
								<Table.Head>{$i18n.t('Description')}</Table.Head>
								<Table.Head>{$i18n.t('Date')}</Table.Head>
								<Table.Head>{$i18n.t('Due')}</Table.Head>
								<Table.Head class="text-right">{$i18n.t('Amount')}</Table.Head>
								<Table.Head>{$i18n.t('Cur.')}</Table.Head>
								<Table.Head>{$i18n.t('Status')}</Table.Head>
								<Table.Head><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each invoices as invoice (invoice.id)}
								<Table.Row
									class="cursor-pointer"
									tabindex={0}
									onclick={() => selectInvoice(invoice)}
									onkeydown={(e: KeyboardEvent) => rowKeydown(e, invoice)}
								>
									<Table.Cell class="font-mono text-[13px]">
										<span class="inline-flex max-w-[9rem] items-center gap-1">
											<span class="truncate" title={invoice.invoice_number ?? ''}
												>{invoice.invoice_number ?? `#${invoice.id}`}</span
											>
											{#if invoice.k4mi_document_id}
												<K4miDocLink
													docId={invoice.k4mi_document_id}
													title={$i18n.t('Open in K4mi')}
													extraClass="inline-flex shrink-0 text-link"
													stopPropagation
												>
													<ExternalLink class="size-3.5" />
													<span class="sr-only">{$i18n.t('Open in K4mi')}</span>
												</K4miDocLink>
											{/if}
										</span>
									</Table.Cell>
									<Table.Cell class="max-w-[9rem]">
										<span class="block truncate" title={invoice.vendor_name ?? ''}
											>{invoice.vendor_name ?? '—'}</span
										>
									</Table.Cell>
									<Table.Cell class="max-w-[7rem]">
										<span class="block truncate" title={invoice.client_name ?? ''}
											>{invoice.client_name ?? '—'}</span
										>
									</Table.Cell>
									<Table.Cell class="max-w-[8rem] text-muted-foreground">
										<span class="block truncate" title={invoice.description ?? ''}
											>{invoice.description || '—'}</span
										>
									</Table.Cell>
									<Table.Cell class="tabular-nums">{formatDate(invoice.invoice_date)}</Table.Cell>
									<Table.Cell class="text-muted-foreground tabular-nums"
										>{formatDate(invoice.due_date)}</Table.Cell
									>
									<Table.Cell class="text-right font-medium tabular-nums">
										{formatCurrency(invoice.total_amount)}
									</Table.Cell>
									<Table.Cell class="font-mono text-[13px] text-muted-foreground">
										{invoice.currency ?? 'USD'}
									</Table.Cell>
									<Table.Cell>
										<StatusBadge
											kind="booking"
											status={invoice.needs_review ? 'review' : 'ready'}
										/>
									</Table.Cell>
									<Table.Cell class="text-right" onclick={(e: MouseEvent) => e.stopPropagation()}>
										<div class="inline-flex items-center gap-1">
											<!-- Details popover -->
											<Popover.Root
												open={previewInvoice?.id === invoice.id}
												onOpenChange={(o) => {
													if (o) previewInvoice = invoice;
													else if (previewInvoice?.id === invoice.id) previewInvoice = null;
												}}
											>
												<Popover.Trigger>
													{#snippet child({ props })}
														<Button
															{...props}
															variant="ghost"
															size="icon-xs"
															aria-label={$i18n.t('Invoice details')}
															title={$i18n.t('Invoice details')}
														>
															<Info />
														</Button>
													{/snippet}
												</Popover.Trigger>
												<Popover.Content side="left" align="center" class="w-80 gap-3">
													<h3 class="font-medium">{$i18n.t('Invoice Details')}</h3>
													<dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 text-[13px]">
														<dt class="text-muted-foreground">{$i18n.t('Invoice #')}</dt>
														<dd class="text-right font-mono">
															{invoice.invoice_number ?? `#${invoice.id}`}
														</dd>
														<dt class="text-muted-foreground">{$i18n.t('Vendor')}</dt>
														<dd class="truncate text-right">{invoice.vendor_name ?? '—'}</dd>
														<dt class="text-muted-foreground">{$i18n.t('Client')}</dt>
														<dd class="truncate text-right">{invoice.client_name ?? '—'}</dd>
														{#if invoice.description}
															<dt class="text-muted-foreground">{$i18n.t('Description')}</dt>
															<dd class="truncate text-right" title={invoice.description}>
																{invoice.description}
															</dd>
														{/if}
													</dl>
													<Separator />
													<dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 text-[13px]">
														<dt class="text-muted-foreground">{$i18n.t('Date')}</dt>
														<dd class="text-right tabular-nums">
															{formatDate(invoice.invoice_date)}
														</dd>
														<dt class="text-muted-foreground">{$i18n.t('Due Date')}</dt>
														<dd class="text-right tabular-nums">{formatDate(invoice.due_date)}</dd>
														<dt class="text-muted-foreground">{$i18n.t('Amount')}</dt>
														<dd class="text-right font-medium tabular-nums">
															{formatCurrency(invoice.total_amount)}
															<span class="font-mono text-xs text-muted-foreground"
																>{invoice.currency ?? 'USD'}</span
															>
														</dd>
														{#if invoice.subtotal !== null && invoice.subtotal !== undefined}
															<dt class="text-muted-foreground">{$i18n.t('Subtotal')}</dt>
															<dd class="text-right tabular-nums">
																{formatCurrency(invoice.subtotal)}
															</dd>
														{/if}
														{#if invoice.tax_amount !== null && invoice.tax_amount !== undefined}
															<dt class="text-muted-foreground">
																{$i18n.t('Tax')}
																{#if invoice.tax_inclusive}
																	<span class="text-xs">({$i18n.t('incl.')})</span>
																{/if}
															</dt>
															<dd class="text-right tabular-nums">
																{formatCurrency(invoice.tax_amount)}
															</dd>
														{/if}
													</dl>
													<Separator />
													<dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 text-[13px]">
														{#if invoice.po_number}
															<dt class="text-muted-foreground">{$i18n.t('PO #')}</dt>
															<dd class="text-right font-mono">{invoice.po_number}</dd>
														{/if}
														{#if invoice.business_unit}
															<dt class="text-muted-foreground">{$i18n.t('Business Unit')}</dt>
															<dd class="text-right">{invoice.business_unit}</dd>
														{/if}
														{#if invoice.payment_terms}
															<dt class="text-muted-foreground">{$i18n.t('Payment Terms')}</dt>
															<dd class="text-right">{invoice.payment_terms}</dd>
														{/if}
														<dt class="text-muted-foreground">{$i18n.t('Line Items')}</dt>
														<dd class="text-right tabular-nums">{getLineItemsCount(invoice)}</dd>
														<dt class="text-muted-foreground">{$i18n.t('Status')}</dt>
														<dd class="text-right">
															<StatusBadge
																kind="booking"
																status={invoice.needs_review ? 'review' : 'ready'}
																label={invoice.needs_review
																	? $i18n.t('Needs Review')
																	: $i18n.t('Ready')}
															/>
														</dd>
														{#if invoice.confidence_score !== null && invoice.confidence_score !== undefined}
															<dt class="text-muted-foreground">{$i18n.t('Confidence')}</dt>
															<dd class="text-right">
																<StatusBadge kind="confidence" status={invoice.confidence_score} />
															</dd>
														{/if}
													</dl>
													{#if invoice.k4mi_document_id}
														<Separator />
														<K4miDocLink
															docId={invoice.k4mi_document_id}
															title={$i18n.t('View full document in K4mi')}
															extraClass="inline-flex items-center gap-1.5 text-link underline-offset-4 hover:underline"
															stopPropagation
														>
															<ExternalLink class="size-3.5" />
															{$i18n.t('View full document in K4mi')}
														</K4miDocLink>
													{/if}
												</Popover.Content>
											</Popover.Root>
											<Button variant="outline" size="xs" onclick={() => selectInvoice(invoice)}>
												{$i18n.t('Select')}
											</Button>
										</div>
									</Table.Cell>
								</Table.Row>
							{/each}
						</Table.Body>
					</Table.Root>
				</div>
			{/if}
		</div>

		<!-- Pagination -->
		{#if !loading && total > limit}
			<div class="flex flex-wrap items-center justify-between gap-2 text-sm">
				<span class="text-muted-foreground tabular-nums">
					{$i18n.t('Showing')}
					{offset + 1}–{offset + invoices.length}
					{$i18n.t('of')}
					{total}
				</span>
				<div class="flex items-center gap-2">
					<Button
						variant="outline"
						size="sm"
						disabled={offset === 0}
						onclick={() => {
							offset = Math.max(0, offset - limit);
							loadInvoices(false);
						}}
					>
						<ChevronLeft />{$i18n.t('Previous')}
					</Button>
					<Button
						variant="outline"
						size="sm"
						disabled={offset + invoices.length >= total}
						onclick={() => {
							offset += limit;
							loadInvoices(false);
						}}
					>
						{$i18n.t('Next')}<ChevronRight />
					</Button>
				</div>
			</div>
		{/if}
	</Dialog.Content>
</Dialog.Root>
