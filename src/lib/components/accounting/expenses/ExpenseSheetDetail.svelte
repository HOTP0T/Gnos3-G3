<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import {
		getExpenseSheet,
		updateExpenseSheet,
		deleteExpenseSheet,
		transitionExpenseSheet,
		getExpenseSheetCandidates,
		downloadExpenseSheetPdf,
		downloadExpenseSheetExcel
	} from '$lib/apis/accounting';
	import dayjs from 'dayjs';
	import { user, isAdmin } from '$lib/stores';

	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import FileDown from '@lucide/svelte/icons/file-down';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Plus from '@lucide/svelte/icons/plus';
	import Send from '@lucide/svelte/icons/send';
	import Check from '@lucide/svelte/icons/check';
	import X from '@lucide/svelte/icons/x';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Banknote from '@lucide/svelte/icons/banknote';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Paperclip from '@lucide/svelte/icons/paperclip';
	import CircleX from '@lucide/svelte/icons/circle-x';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import ReceiptText from '@lucide/svelte/icons/receipt-text';

	import K4miDocLink from '$lib/components/common/K4miDocLink.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';
	import ExpenseSheetStatusBadge from './ExpenseSheetStatusBadge.svelte';

	const i18n: any = getContext('i18n');

	export let companyId: number;
	export let sheetId: number;

	// Deleting a sheet is for accounting admins (the server answers 403 otherwise).
	$: canDelete = $isAdmin || Boolean($user?.permissions?.modules?.accounting?.admin);
	$: sheetsHref = `/accounting/company/${companyId}/expenses?tab=sheets`;

	let sheet: any = null;
	let loading = true;
	let showPicker = false;
	let candidates: any[] = [];
	let selectedIds = new Set<number>();
	let note = '';
	let rejectionReason = '';
	let transitionTarget = '';
	let transitioning = false;

	// ── Sheet details editing ───────────────────────────────────────────
	// Reference / title / period are fixable after generation. The backend
	// keeps these editable until the sheet is paid (its JE is posted by then),
	// so the button follows the same rule.
	let showEdit = false;
	let savingEdit = false;
	let editForm = {
		reference: '',
		title: '',
		period_start: '',
		period_end: '',
		notes: ''
	};

	const openEdit = () => {
		if (!sheet) return;
		editForm = {
			reference: sheet.reference ?? '',
			title: sheet.title ?? '',
			period_start: sheet.period_start ?? '',
			period_end: sheet.period_end ?? '',
			notes: sheet.notes ?? ''
		};
		showEdit = true;
	};

	const saveEdit = async () => {
		if (!sheet) return;
		savingEdit = true;
		try {
			// Only send changed fields — a no-op PATCH shouldn't touch the period.
			const payload: Record<string, any> = {};
			if (editForm.reference.trim() && editForm.reference.trim() !== sheet.reference)
				payload.reference = editForm.reference.trim();
			if (editForm.title !== (sheet.title ?? '')) payload.title = editForm.title;
			if (editForm.period_start && editForm.period_start !== sheet.period_start)
				payload.period_start = editForm.period_start;
			if (editForm.period_end && editForm.period_end !== sheet.period_end)
				payload.period_end = editForm.period_end;
			if (editForm.notes !== (sheet.notes ?? '')) payload.notes = editForm.notes;

			if (!Object.keys(payload).length) {
				showEdit = false;
				return;
			}
			sheet = await updateExpenseSheet(sheetId, payload);
			toast.success($i18n.t('Sheet updated'));
			showEdit = false;
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		savingEdit = false;
	};

	const exportSheet = async (kind: 'pdf' | 'excel') => {
		try {
			if (kind === 'pdf') await downloadExpenseSheetPdf(sheetId);
			else await downloadExpenseSheetExcel(sheetId);
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const load = async () => {
		loading = true;
		try {
			sheet = await getExpenseSheet(sheetId);
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		loading = false;
	};

	onMount(load);

	const openPicker = async () => {
		if (!sheet) return;
		try {
			const res = await getExpenseSheetCandidates(companyId, {
				employee_id: sheet.employee_id,
				period_start: sheet.period_start,
				period_end: sheet.period_end
			});
			const existing = new Set((sheet.lines ?? []).map((l: any) => l.invoice_id));
			candidates = (res?.invoices ?? []).filter((inv: any) => !existing.has(inv.id));
			selectedIds = new Set();
			showPicker = true;
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const addSelected = async () => {
		if (!selectedIds.size) {
			toast.error($i18n.t('Pick at least one invoice'));
			return;
		}
		try {
			sheet = await updateExpenseSheet(sheetId, {
				add_invoice_ids: Array.from(selectedIds)
			});
			toast.success($i18n.t('Receipts added'));
			showPicker = false;
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	// A line is an invoice (accountant flow) or an employee's expense (portal
	// flow). A removed expense stays approved and goes back to "To reimburse".
	let removingKey = '';
	const removeLine = async (l: any) => {
		const isItem = l.source === 'expense_item';
		const id = isItem ? l.expense_item_id : l.invoice_id;
		if (!id || removingKey) return;
		removingKey = `${l.source}:${id}`;
		try {
			sheet = await updateExpenseSheet(
				sheetId,
				isItem ? { remove_expense_item_ids: [id] } : { remove_invoice_ids: [id] }
			);
			toast.success($i18n.t('Receipt removed'));
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		} finally {
			removingKey = '';
		}
	};

	let showDeleteConfirm = false;
	const handleDelete = () => {
		showDeleteConfirm = true;
	};

	const doDelete = async () => {
		try {
			await deleteExpenseSheet(sheetId);
			toast.success($i18n.t('Sheet deleted'));
			goto(sheetsHref);
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const openTransition = (target: string) => {
		transitionTarget = target;
		note = '';
		rejectionReason = '';
	};

	// The server records who did it from the sign-in; only a rejection needs a reason.
	$: reasonMissing = transitionTarget === 'reject' && !rejectionReason.trim();

	const confirmTransition = async () => {
		if (transitioning) return; // guard against double-submit (double-click)
		if (reasonMissing) return;
		transitioning = true;
		try {
			const done = transitionCopy.message;
			sheet = await transitionExpenseSheet(sheetId, {
				target: transitionTarget as any,
				note: note || undefined,
				rejection_reason: transitionTarget === 'reject' ? rejectionReason.trim() : undefined
			});
			toast.success($i18n.t(done));
			transitionTarget = '';
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		} finally {
			transitioning = false;
		}
	};

	// What each transition dialog says (the title asks, the button repeats the
	// verb, the message is the toast once it is done).
	const TRANSITION_COPY: Record<
		string,
		{ title: string; description: string; confirm: string; message: string }
	> = {
		submit: {
			title: 'Submit this sheet?',
			description: 'It goes to an approver.',
			confirm: 'Submit',
			message: 'Sheet submitted'
		},
		approve: {
			title: 'Approve this sheet?',
			description: 'Approving builds the reimbursement journal entry as a draft.',
			confirm: 'Approve',
			message: 'Sheet approved'
		},
		reject: {
			title: 'Reject this sheet?',
			description: '',
			confirm: 'Reject',
			message: 'Sheet rejected'
		},
		mark_paid: {
			title: 'Mark this sheet paid?',
			description: 'Marking it paid posts the reimbursement journal entry.',
			confirm: 'Mark Paid',
			message: 'Sheet marked paid'
		}
	};
	$: transitionCopy = TRANSITION_COPY[transitionTarget] ?? {
		title: transitionTarget,
		description: '',
		confirm: 'Confirm',
		message: 'Sheet updated'
	};

	const fmtTime = (v: string | null | undefined) => (v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '');

	const toggleCandidate = (id: number) => {
		if (selectedIds.has(id)) selectedIds.delete(id);
		else selectedIds.add(id);
		selectedIds = new Set(selectedIds);
	};

	const money = (amount: any, currency?: string) => {
		if (amount == null) return '';
		const n = typeof amount === 'number' ? amount : parseFloat(amount);
		if (!isFinite(n)) return '';
		try {
			return new Intl.NumberFormat(undefined, {
				style: 'currency',
				currency: currency || sheet?.currency || 'USD'
			}).format(n);
		} catch {
			return `${currency} ${n.toFixed(2)}`;
		}
	};

	// SSO bridge handles the URL; we just need to know whether a doc id exists.
	const hasK4miDoc = (id: number | null | undefined) => !!id;

	// Collapsible journal-entry drill-down: each category = one debit line;
	// expand it to see the individual receipts/items that rolled into it.
	let expandedCats = new Set<number | null>();
	const toggleCat = (id: number | null) => {
		const next = new Set(expandedCats);
		next.has(id) ? next.delete(id) : next.add(id);
		expandedCats = next;
	};
	$: linesByCat = (() => {
		const m = new Map<number | null, any[]>();
		for (const l of sheet?.lines ?? []) {
			const k = (l.category_id ?? null) as number | null;
			if (!m.has(k)) m.set(k, []);
			(m.get(k) as any[]).push(l);
		}
		return m;
	})();
</script>

{#if loading}
	<div class="flex flex-col gap-4">
		<Skeleton class="h-8 w-28" />
		<Skeleton class="h-8 w-64" />
		<div class="grid gap-4 md:grid-cols-3">
			{#each Array(3) as _}<Skeleton class="h-20 rounded-xl" />{/each}
		</div>
		<Skeleton class="h-64 rounded-xl" />
	</div>
{:else if !sheet}
	<Alert.Root variant="destructive">
		<CircleAlert />
		<Alert.Title>{$i18n.t('Sheet not found')}</Alert.Title>
		<Alert.Description>
			<Button variant="outline" size="sm" class="mt-2" href={sheetsHref}>
				<ArrowLeft />{$i18n.t('All sheets')}
			</Button>
		</Alert.Description>
	</Alert.Root>
{:else}
	<div class="flex flex-col gap-4">
		<div>
			<Button variant="ghost" size="sm" class="-ml-2 pl-1.5" href={sheetsHref}>
				<ArrowLeft />{$i18n.t('All sheets')}
			</Button>
		</div>

		<!-- Title, status and actions -->
		<div class="flex flex-wrap items-start justify-between gap-3">
			<div class="min-w-0">
				<div class="flex flex-wrap items-center gap-2">
					<h2 class="font-mono text-xl font-semibold">{sheet.reference}</h2>
					<ExpenseSheetStatusBadge status={sheet.status} />
				</div>
				{#if sheet.title}
					<p class="mt-0.5 text-sm text-muted-foreground">{sheet.title}</p>
				{/if}
			</div>
			<div class="flex flex-wrap items-center gap-2">
				<Button variant="outline" size="sm" onclick={() => exportSheet('pdf')}>
					<FileDown />{$i18n.t('PDF')}
				</Button>
				<Button variant="outline" size="sm" onclick={() => exportSheet('excel')}>
					<FileDown />{$i18n.t('Excel')}
				</Button>

				{#if sheet.status !== 'paid'}
					<Button variant="outline" size="sm" onclick={openEdit}>
						<Pencil />{$i18n.t('Edit details')}
					</Button>
				{/if}

				{#if sheet.status === 'draft'}
					{#if canDelete}
						<Button
							variant="outline"
							size="sm"
							class="text-destructive hover:text-destructive"
							onclick={handleDelete}
						>
							<Trash2 />{$i18n.t('Delete')}
						</Button>
					{/if}
					<Button variant="outline" size="sm" onclick={openPicker}>
						<Plus />{$i18n.t('Add Receipts')}
					</Button>
					<Button size="sm" onclick={() => openTransition('submit')}>
						<Send />{$i18n.t('Submit')}
					</Button>
				{:else if sheet.status === 'submitted'}
					<Button variant="outline" size="sm" onclick={() => openTransition('reject')}>
						<X />{$i18n.t('Reject')}
					</Button>
					<Button size="sm" onclick={() => openTransition('approve')}>
						<Check />{$i18n.t('Approve')}
					</Button>
				{:else if sheet.status === 'approved'}
					<Button variant="outline" size="sm" onclick={() => openTransition('reject')}>
						<X />{$i18n.t('Reject')}
					</Button>
					<Button size="sm" onclick={() => openTransition('mark_paid')}>
						<Banknote />{$i18n.t('Mark Paid')}
					</Button>
				{/if}
			</div>
		</div>

		<!-- Who, when, how much -->
		<div class="grid gap-4 md:grid-cols-3">
			<Card.Root size="sm" class="gap-1">
				<Card.Content>
					<div class="text-sm text-muted-foreground">{$i18n.t('Employee')}</div>
					<div class="mt-1 font-medium">
						{sheet.employee_name ?? `#${sheet.employee_id}`}
						{#if sheet.employee_code}
							<span class="font-normal text-muted-foreground">({sheet.employee_code})</span>
						{/if}
					</div>
				</Card.Content>
			</Card.Root>
			<Card.Root size="sm" class="gap-1">
				<Card.Content>
					<div class="text-sm text-muted-foreground">{$i18n.t('Period')}</div>
					<div class="mt-1 font-medium tabular-nums">
						{sheet.period_start} → {sheet.period_end}
					</div>
				</Card.Content>
			</Card.Root>
			<Card.Root size="sm" class="gap-1">
				<Card.Content>
					<div class="text-sm text-muted-foreground">{$i18n.t('Totals')}</div>
					<div class="mt-1 font-medium tabular-nums">
						{money(sheet.total_amount, sheet.currency)}
						<span class="ml-1 text-sm font-normal text-muted-foreground">
							({money(sheet.subtotal, sheet.currency)} + {money(sheet.tax_amount, sheet.currency)})
						</span>
					</div>
				</Card.Content>
			</Card.Root>
		</div>

		<!-- Status trail -->
		{#if sheet.submitted_at || sheet.approved_at || sheet.paid_at || sheet.rejected_at || sheet.transaction_entry_number || sheet.transaction_id}
			<div class="flex flex-wrap items-center gap-x-5 gap-y-1 text-sm text-muted-foreground">
				{#if sheet.submitted_at}
					<span
						>{$i18n.t('Submitted')}:
						<span class="tabular-nums">{fmtTime(sheet.submitted_at)}</span>
						{#if sheet.submitted_by}({sheet.submitted_by}){/if}</span
					>
				{/if}
				{#if sheet.approved_at}
					<span
						>{$i18n.t('Approved')}:
						<span class="tabular-nums">{fmtTime(sheet.approved_at)}</span>
						{#if sheet.approved_by}({sheet.approved_by}){/if}</span
					>
				{/if}
				{#if sheet.paid_at}
					<span
						>{$i18n.t('Paid')}: <span class="tabular-nums">{fmtTime(sheet.paid_at)}</span>
						{#if sheet.paid_by}({sheet.paid_by}){/if}</span
					>
				{/if}
				{#if sheet.rejected_at}
					<span class="inline-flex items-center gap-1.5 text-destructive">
						<CircleX class="size-4 shrink-0" />
						<span
							>{$i18n.t('Rejected')}:
							<span class="tabular-nums">{fmtTime(sheet.rejected_at)}</span>
							{#if sheet.rejection_reason}<span class="text-muted-foreground">
									— {sheet.rejection_reason}</span
								>{/if}</span
						>
					</span>
				{/if}
				{#if sheet.transaction_entry_number}
					<span
						>{$i18n.t('Journal Entry')}:
						<span class="font-mono text-[13px] text-foreground"
							>{sheet.transaction_entry_number}</span
						></span
					>
				{:else if sheet.transaction_id}
					<span>{$i18n.t('Journal Entry: draft')}</span>
				{/if}
			</div>
		{/if}

		<!-- Reimbursement journal entry (expand a debit line to its receipts) -->
		{#if sheet.category_totals?.length}
			<Card.Root>
				<Card.Header>
					<Card.Title>{$i18n.t('Reimbursement journal entry')}</Card.Title>
					<Card.Description>
						{#if sheet.transaction_entry_number}
							<span class="font-mono text-[13px]">{sheet.transaction_entry_number}</span> · {$i18n.t(
								'posted'
							)}
						{:else if sheet.transaction_id}
							{$i18n.t('draft — posts when the sheet is paid')}
						{:else}
							{$i18n.t('builds when the sheet is approved')}
						{/if}
					</Card.Description>
				</Card.Header>
				<Card.Content>
					<div class="overflow-hidden rounded-md border">
						<Table.Root>
							<Table.Header class="bg-muted/50">
								<Table.Row class="hover:bg-transparent">
									<Table.Head>{$i18n.t('Account / Category')}</Table.Head>
									<Table.Head class="text-right">{$i18n.t('Items')}</Table.Head>
									<Table.Head class="text-right">{$i18n.t('Debit')}</Table.Head>
									<Table.Head class="text-right">{$i18n.t('Credit')}</Table.Head>
								</Table.Row>
							</Table.Header>
							<Table.Body>
								{#each sheet.category_totals as g}
									{@const catId = g.category_id ?? null}
									{@const open = expandedCats.has(catId)}
									<Table.Row
										class="cursor-pointer"
										tabindex={0}
										aria-expanded={open}
										onclick={() => toggleCat(catId)}
										onkeydown={(e: KeyboardEvent) => {
											if (e.key === 'Enter' || e.key === ' ') {
												e.preventDefault();
												toggleCat(catId);
											}
										}}
									>
										<Table.Cell class="whitespace-normal">
											<span class="inline-flex items-center gap-1.5">
												<ChevronRight
													class="size-4 shrink-0 text-muted-foreground transition-transform motion-reduce:transition-none {open
														? 'rotate-90'
														: ''}"
												/>
												{g.category_label}
											</span>
											{#if g.tax_amount && Number(g.tax_amount) > 0}
												<span class="text-[13px] text-muted-foreground tabular-nums"
													>({money(g.subtotal, sheet.currency)} + {money(
														g.tax_amount,
														sheet.currency
													)}
													{$i18n.t('tax')})</span
												>
											{/if}
										</Table.Cell>
										<Table.Cell class="text-right tabular-nums">{g.count}</Table.Cell>
										<Table.Cell class="text-right font-medium tabular-nums"
											>{money(g.total_amount, sheet.currency)}</Table.Cell
										>
										<Table.Cell class="text-right text-muted-foreground">—</Table.Cell>
									</Table.Row>
									{#if open}
										{#each linesByCat.get(catId) ?? [] as l}
											<Table.Row class="bg-muted/30 text-[13px] hover:bg-muted/30">
												<Table.Cell class="pl-9 whitespace-normal text-muted-foreground">
													<span class="tabular-nums">{l.invoice_date ?? '—'}</span>
													· <span class="text-foreground">{l.vendor_name ?? ''}</span>
													{#if l.description}<span> — {l.description}</span>{/if}
													{#if l.has_receipt}
														<Paperclip
															class="ml-1 inline size-3.5 align-[-2px]"
															aria-label={$i18n.t('Has receipt')}
														/>
													{/if}
													{#if hasK4miDoc(l.k4mi_document_id)}
														<K4miDocLink
															docId={l.k4mi_document_id}
															extraClass="ml-1 font-mono text-link underline-offset-4 hover:underline"
															>#{l.k4mi_document_id}</K4miDocLink
														>
													{/if}
												</Table.Cell>
												<Table.Cell></Table.Cell>
												<Table.Cell class="text-right text-muted-foreground tabular-nums">
													{#if l.converted_total != null}
														{money(l.converted_total, sheet.currency)}
														<span>({money(l.total_amount, l.currency)})</span>
													{:else}
														{money(l.total_amount, l.currency)}
													{/if}
												</Table.Cell>
												<Table.Cell></Table.Cell>
											</Table.Row>
										{/each}
									{/if}
								{/each}
								<!-- Credit line: owed to the employee -->
								<Table.Row class="hover:bg-transparent">
									<Table.Cell
										>{$i18n.t('Due to')}
										{sheet.employee_name ?? `#${sheet.employee_id}`}</Table.Cell
									>
									<Table.Cell></Table.Cell>
									<Table.Cell class="text-right text-muted-foreground">—</Table.Cell>
									<Table.Cell class="text-right font-medium tabular-nums"
										>{money(sheet.total_amount, sheet.currency)}</Table.Cell
									>
								</Table.Row>
							</Table.Body>
							<Table.Footer>
								<Table.Row class="hover:bg-transparent">
									<Table.Cell class="font-semibold">{$i18n.t('Total')}</Table.Cell>
									<Table.Cell></Table.Cell>
									<Table.Cell class="text-right font-semibold tabular-nums"
										>{money(sheet.total_amount, sheet.currency)}</Table.Cell
									>
									<Table.Cell class="text-right font-semibold tabular-nums"
										>{money(sheet.total_amount, sheet.currency)}</Table.Cell
									>
								</Table.Row>
							</Table.Footer>
						</Table.Root>
					</div>
				</Card.Content>
			</Card.Root>
		{/if}

		<!-- Receipts -->
		<Card.Root>
			<Card.Header>
				<Card.Title>{$i18n.t('Receipts')} ({sheet.lines?.length ?? 0})</Card.Title>
			</Card.Header>
			<Card.Content>
				{#if !sheet.lines?.length}
					<Empty.Root class="border border-dashed p-6">
						<Empty.Header>
							<Empty.Media variant="icon"><ReceiptText /></Empty.Media>
							<Empty.Title>{$i18n.t('No receipts on this sheet yet.')}</Empty.Title>
						</Empty.Header>
						{#if sheet.status === 'draft'}
							<Empty.Content>
								<Button variant="outline" size="sm" onclick={openPicker}>
									<Plus />{$i18n.t('Add Receipts')}
								</Button>
							</Empty.Content>
						{/if}
					</Empty.Root>
				{:else}
					<div class="overflow-hidden rounded-md border">
						<Table.Root>
							<Table.Header class="bg-muted/50">
								<Table.Row class="hover:bg-transparent">
									<Table.Head>{$i18n.t('Date')}</Table.Head>
									<Table.Head>{$i18n.t('Vendor')}</Table.Head>
									<Table.Head>{$i18n.t('Category')}</Table.Head>
									<Table.Head>{$i18n.t('Description')}</Table.Head>
									<Table.Head class="text-right">{$i18n.t('Subtotal')}</Table.Head>
									<Table.Head class="text-right">{$i18n.t('Tax')}</Table.Head>
									<Table.Head class="text-right">{$i18n.t('Total')}</Table.Head>
									<Table.Head class="text-right">K4mi</Table.Head>
									{#if sheet.status === 'draft'}
										<Table.Head class="w-10"
											><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head
										>
									{/if}
								</Table.Row>
							</Table.Header>
							<Table.Body>
								{#each sheet.lines as l}
									<Table.Row>
										<Table.Cell class="tabular-nums">{l.invoice_date ?? '—'}</Table.Cell>
										<Table.Cell class="font-medium">{l.vendor_name ?? ''}</Table.Cell>
										<Table.Cell class="text-muted-foreground">{l.category_label}</Table.Cell>
										<Table.Cell
											class="max-w-xs truncate text-muted-foreground"
											title={l.description ?? ''}>{l.description ?? ''}</Table.Cell
										>
										<Table.Cell class="text-right tabular-nums"
											>{money(l.subtotal, l.currency)}</Table.Cell
										>
										<Table.Cell class="text-right tabular-nums"
											>{money(l.tax_amount, l.currency)}</Table.Cell
										>
										<Table.Cell class="text-right font-medium tabular-nums"
											>{money(l.total_amount, l.currency)}</Table.Cell
										>
										<Table.Cell class="text-right">
											{#if hasK4miDoc(l.k4mi_document_id)}
												<K4miDocLink
													docId={l.k4mi_document_id}
													extraClass="font-mono text-[13px] text-link underline-offset-4 hover:underline"
													>#{l.k4mi_document_id}</K4miDocLink
												>
											{/if}
										</Table.Cell>
										{#if sheet.status === 'draft'}
											<Table.Cell class="text-right">
												{#if l.invoice_id || l.expense_item_id}
													<Tip content={$i18n.t('Remove from sheet')}>
														<Button
															variant="ghost"
															size="icon-xs"
															aria-label={$i18n.t('Remove from sheet')}
															disabled={!!removingKey}
															onclick={() => removeLine(l)}
														>
															<X />
														</Button>
													</Tip>
												{/if}
											</Table.Cell>
										{/if}
									</Table.Row>
								{/each}
							</Table.Body>
						</Table.Root>
					</div>
				{/if}
			</Card.Content>
		</Card.Root>
	</div>

	<!-- Receipt picker -->
	<Dialog.Root bind:open={showPicker}>
		<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-3xl">
			<Dialog.Header>
				<Dialog.Title>{$i18n.t('Add Receipts')} ({candidates.length})</Dialog.Title>
				<Dialog.Description>
					{$i18n.t('Invoices for this employee in the sheet period that are not on it yet.')}
				</Dialog.Description>
			</Dialog.Header>
			{#if candidates.length === 0}
				<Empty.Root class="border border-dashed p-6">
					<Empty.Header>
						<Empty.Media variant="icon"><ReceiptText /></Empty.Media>
						<Empty.Description>
							{$i18n.t(
								'No eligible invoices for this employee in this period. Assign the employee in K4mi first.'
							)}
						</Empty.Description>
					</Empty.Header>
				</Empty.Root>
			{:else}
				<div class="max-h-[50vh] overflow-y-auto rounded-md border">
					<Table.Root>
						<Table.Header class="bg-muted/50">
							<Table.Row class="hover:bg-transparent">
								<Table.Head class="w-10"
									><span class="sr-only">{$i18n.t('Select')}</span></Table.Head
								>
								<Table.Head>{$i18n.t('Date')}</Table.Head>
								<Table.Head>{$i18n.t('Vendor')}</Table.Head>
								<Table.Head class="text-right">{$i18n.t('Total')}</Table.Head>
								<Table.Head class="text-right">K4mi</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each candidates as inv}
								<Table.Row data-state={selectedIds.has(inv.id) ? 'selected' : undefined}>
									<Table.Cell>
										<Checkbox
											checked={selectedIds.has(inv.id)}
											onCheckedChange={() => toggleCandidate(inv.id)}
											aria-label={inv.vendor_name ?? `#${inv.id}`}
										/>
									</Table.Cell>
									<Table.Cell class="tabular-nums">{inv.invoice_date ?? '—'}</Table.Cell>
									<Table.Cell>{inv.vendor_name ?? ''}</Table.Cell>
									<Table.Cell class="text-right tabular-nums"
										>{money(inv.total_amount, inv.currency)}</Table.Cell
									>
									<Table.Cell class="text-right">
										{#if hasK4miDoc(inv.k4mi_document_id)}
											<K4miDocLink
												docId={inv.k4mi_document_id}
												extraClass="font-mono text-[13px] text-link underline-offset-4 hover:underline"
												>#{inv.k4mi_document_id}</K4miDocLink
											>
										{/if}
									</Table.Cell>
								</Table.Row>
							{/each}
						</Table.Body>
					</Table.Root>
				</div>
			{/if}
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (showPicker = false)}>{$i18n.t('Cancel')}</Button>
				<Button disabled={!selectedIds.size} onclick={addSelected}>
					<Plus />{$i18n.t('Add')} ({selectedIds.size})
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>

	<!-- Edit sheet details -->
	<Dialog.Root bind:open={showEdit}>
		<Dialog.Content class="sm:max-w-lg">
			<Dialog.Header>
				<Dialog.Title>{$i18n.t('Edit sheet details')}</Dialog.Title>
				<Dialog.Description class="font-mono text-[13px]">{sheet.reference}</Dialog.Description>
			</Dialog.Header>
			<div class="grid gap-4">
				<div class="grid gap-1.5">
					<Label for="es-edit-ref">{$i18n.t('Reference')}</Label>
					<Input id="es-edit-ref" class="font-mono" bind:value={editForm.reference} />
					<p class="text-[13px] text-muted-foreground">
						{$i18n.t('Must be unique within this company.')}
					</p>
				</div>
				<div class="grid gap-1.5">
					<Label for="es-edit-title">{$i18n.t('Sheet name')}</Label>
					<Input id="es-edit-title" bind:value={editForm.title} />
				</div>
				<div class="grid grid-cols-2 gap-3">
					<div class="grid gap-1.5">
						<Label for="es-edit-start">{$i18n.t('Period start')}</Label>
						<Input id="es-edit-start" type="date" bind:value={editForm.period_start} />
					</div>
					<div class="grid gap-1.5">
						<Label for="es-edit-end">{$i18n.t('Period end')}</Label>
						<Input id="es-edit-end" type="date" bind:value={editForm.period_end} />
					</div>
				</div>
				<div class="grid gap-1.5">
					<Label for="es-edit-notes">{$i18n.t('Notes', { context: 'gnos3' })}</Label>
					<Input id="es-edit-notes" bind:value={editForm.notes} />
				</div>
				{#if sheet.status !== 'draft'}
					<Alert.Root variant="warning">
						<TriangleAlert />
						<Alert.Description>
							{$i18n.t(
								'This sheet is already past draft — changing its details does not alter the amounts or the journal entry.'
							)}
						</Alert.Description>
					</Alert.Root>
				{/if}
			</div>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (showEdit = false)}>{$i18n.t('Cancel')}</Button>
				<Button disabled={savingEdit} onclick={saveEdit}>
					{#if savingEdit}<Spinner />{/if}
					{savingEdit ? $i18n.t('Saving...') : $i18n.t('Save')}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>

	<!-- Submit / approve / reject / mark paid -->
	<Dialog.Root
		open={!!transitionTarget}
		onOpenChange={(v) => {
			if (!v) transitionTarget = '';
		}}
	>
		<Dialog.Content class="sm:max-w-lg">
			<Dialog.Header>
				<Dialog.Title>{$i18n.t(transitionCopy.title)}</Dialog.Title>
				<Dialog.Description>
					<span class="font-mono text-[13px]">{sheet.reference}</span>
					{#if transitionCopy.description}· {$i18n.t(transitionCopy.description)}{/if}
				</Dialog.Description>
			</Dialog.Header>
			<div class="grid gap-4">
				{#if transitionTarget === 'reject'}
					<div class="grid gap-1.5">
						<Label for="es-tr-reason">{$i18n.t('Rejection reason')} *</Label>
						<Textarea
							id="es-tr-reason"
							rows={3}
							required
							aria-required="true"
							bind:value={rejectionReason}
						/>
					</div>
				{/if}
				<div class="grid gap-1.5">
					<Label for="es-tr-note">{$i18n.t('Note (optional)')}</Label>
					<Input id="es-tr-note" bind:value={note} />
				</div>
			</div>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (transitionTarget = '')}
					>{$i18n.t('Cancel')}</Button
				>
				<Button disabled={transitioning || reasonMissing} onclick={confirmTransition}>
					{#if transitioning}<Spinner />{/if}
					{transitioning ? $i18n.t('Working...') : $i18n.t(transitionCopy.confirm)}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>

	<ConfirmDialog
		bind:open={showDeleteConfirm}
		title={$i18n.t('Delete this draft sheet?')}
		description={`${sheet.reference} ${$i18n.t('will be deleted. This cannot be undone.')}`}
		confirmLabel={$i18n.t('Delete')}
		destructive
		onconfirm={doDelete}
	/>
{/if}
