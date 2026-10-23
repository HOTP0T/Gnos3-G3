<script lang="ts">
	import { onMount, getContext, untrack } from 'svelte';
	import { page as pageStore } from '$app/stores';
	import { toast } from 'svelte-sonner';

	import Search from '@lucide/svelte/icons/search';
	import Rows3 from '@lucide/svelte/icons/rows-3';
	import Rows2 from '@lucide/svelte/icons/rows-2';
	import Columns3 from '@lucide/svelte/icons/columns-3';
	import Ellipsis from '@lucide/svelte/icons/ellipsis';
	import ExternalLink from '@lucide/svelte/icons/external-link';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import IdCard from '@lucide/svelte/icons/id-card';
	import ArrowUp from '@lucide/svelte/icons/arrow-up';
	import ArrowDown from '@lucide/svelte/icons/arrow-down';

	import {
		getBusinessCards,
		getBusinessCardCompanies,
		deleteBusinessCard,
		reprocessBusinessCard,
		syncBusinessCardFromK4mi,
		type BusinessCard
	} from '$lib/apis/business-cards';
	import { k4miDocHref } from '$lib/apis/k4mi';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import * as ToggleGroup from '$lib/components/ui/toggle-group/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';
	import TablePagination from '$lib/components/gnos3-ui/TablePagination.svelte';
	import BusinessCardDetailDrawer from './BusinessCardDetailDrawer.svelte';

	const i18n: any = getContext('i18n');

	let cards = $state<BusinessCard[]>([]);
	let companies = $state<string[]>([]);
	let total = $state(0);
	let loading = $state(true);
	let mounted = false;

	let page = $state(1);
	const perPage = 50;

	let searchQuery = $state('');
	let searchDebounce: ReturnType<typeof setTimeout>;
	let companyFilter = $state('');
	let needsReviewOnly = $state(false);
	let statusFilter = $state('');

	let sortBy = $state('');
	let sortDir = $state<'asc' | 'desc'>('asc');

	let showDeleteConfirm = $state(false);
	let deleteTarget = $state<BusinessCard | null>(null);
	let reprocessingIds = $state<Set<number>>(new Set());
	let syncingIds = $state<Set<number>>(new Set());

	let selectedCard = $state<BusinessCard | null>(null);

	let density = $state<'compact' | 'comfortable'>('comfortable');
	let visibleColumns = $state<Set<string>>(new Set());

	const COLUMNS: Array<{
		key: keyof BusinessCard;
		label: string;
		sortable: boolean;
		readonly?: boolean;
		minW: string;
		alwaysVisible?: boolean;
	}> = [
		{ key: 'full_name', label: 'Name', sortable: true, minW: '12rem', alwaysVisible: true },
		{ key: 'job_title', label: 'Job title', sortable: false, minW: '10rem' },
		{ key: 'company_name', label: 'Company', sortable: true, minW: '10rem' },
		{ key: 'email', label: 'Email', sortable: true, minW: '14rem' },
		{ key: 'phone', label: 'Phone', sortable: false, minW: '8rem' },
		{ key: 'mobile', label: 'Mobile', sortable: false, minW: '8rem' },
		{ key: 'website', label: 'Website', sortable: false, minW: '10rem' },
		{ key: 'k4mi_notes', label: 'Notes', sortable: false, readonly: true, minW: '16rem' }
	];

	const shownColumns = $derived(
		COLUMNS.filter((c) => c.alwaysVisible || visibleColumns.has(String(c.key)))
	);
	const cellPad = $derived(density === 'compact' ? 'py-1' : 'py-2');

	const initials = (name: string | null | undefined) =>
		(name || '?')
			.split(/\s+/)
			.filter(Boolean)
			.slice(0, 2)
			.map((p) => p[0]?.toUpperCase())
			.join('') || '?';

	const statusOf = (card: BusinessCard): string =>
		card.processing_status === 'processing' || card.processing_status === 'pending'
			? card.processing_status
			: card.processing_status === 'failed'
				? 'failed'
				: card.needs_review
					? 'needs_review'
					: 'ok';

	const formatK4miNotes = (notes: unknown): string => {
		if (!Array.isArray(notes) || notes.length === 0) return '';
		return notes
			.map((n) => {
				if (typeof n === 'string') return n;
				if (n && typeof n === 'object' && 'text' in n)
					return String((n as { text?: unknown }).text ?? '');
				return '';
			})
			.filter(Boolean)
			.join(' · ');
	};

	const loadCards = async () => {
		loading = true;
		try {
			const res = await getBusinessCards(localStorage.token, {
				q: searchQuery || undefined,
				company: companyFilter || undefined,
				status: statusFilter || undefined,
				needs_review: needsReviewOnly ? true : undefined,
				sort_by: sortBy || undefined,
				sort_dir: sortBy ? sortDir : undefined,
				limit: perPage,
				offset: (page - 1) * perPage
			});
			cards = res.business_cards ?? [];
			total = res.total ?? 0;

			if (selectedCard) {
				const refreshed = cards.find((c) => c.id === selectedCard!.id);
				if (refreshed) selectedCard = refreshed;
			}
		} catch (err) {
			toast.error(`${err}`);
		}
		loading = false;
	};

	const loadCompanies = async () => {
		try {
			companies = await getBusinessCardCompanies(localStorage.token);
		} catch {
			companies = [];
		}
	};

	// A filter changed: back to page 1 (the page effect reloads) or reload in place.
	const filtersChanged = () => {
		if (page === 1) loadCards();
		else page = 1;
	};

	let lastPage = 0;
	$effect(() => {
		const p = page;
		if (!mounted || p === lastPage) return;
		lastPage = p;
		untrack(loadCards);
	});

	const handleSort = (key: string) => {
		if (sortBy === key) {
			if (sortDir === 'asc') {
				sortDir = 'desc';
			} else {
				sortBy = '';
				sortDir = 'asc';
			}
		} else {
			sortBy = key;
			sortDir = 'asc';
		}
		filtersChanged();
	};

	const debouncedSearch = () => {
		clearTimeout(searchDebounce);
		searchDebounce = setTimeout(filtersChanged, 300);
	};

	const handleDelete = (card: BusinessCard) => {
		deleteTarget = card;
		showDeleteConfirm = true;
	};

	const confirmDelete = async () => {
		if (!deleteTarget) return;
		try {
			await deleteBusinessCard(localStorage.token, deleteTarget.id);
			cards = cards.filter((c) => c.id !== deleteTarget!.id);
			total = Math.max(0, total - 1);
			if (selectedCard?.id === deleteTarget.id) selectedCard = null;
			toast.success($i18n.t('Deleted'));
		} catch (err) {
			toast.error(`${err}`);
		}
		deleteTarget = null;
	};

	const handleReprocess = async (card: BusinessCard) => {
		if (!card.k4mi_document_id) return;
		reprocessingIds = new Set([...reprocessingIds, card.id]);
		try {
			await reprocessBusinessCard(localStorage.token, card.id);
			toast.success($i18n.t('Re-extraction queued'));
			setTimeout(loadCards, 1500);
		} catch (err) {
			toast.error(`${err}`);
		} finally {
			reprocessingIds.delete(card.id);
			reprocessingIds = new Set(reprocessingIds);
		}
	};

	const handleSync = async (card: BusinessCard) => {
		if (!card.k4mi_document_id) return;
		syncingIds = new Set([...syncingIds, card.id]);
		try {
			await syncBusinessCardFromK4mi(localStorage.token, card.id);
			toast.success($i18n.t('Syncing from K4mi…'));
			setTimeout(loadCards, 1500);
		} catch (err) {
			toast.error(`${err}`);
		} finally {
			syncingIds.delete(card.id);
			syncingIds = new Set(syncingIds);
		}
	};

	const onCardUpdated = (updated: BusinessCard) => {
		const idx = cards.findIndex((c) => c.id === updated.id);
		if (idx !== -1) cards[idx] = updated;
		cards = [...cards];
		selectedCard = updated;
	};

	const setDensity = (d: string) => {
		if (d !== 'compact' && d !== 'comfortable') return;
		density = d;
		try {
			localStorage.setItem('bc-table-density', density);
		} catch {}
	};

	const saveColumns = () => {
		try {
			localStorage.setItem('bc-table-columns', JSON.stringify(Array.from(visibleColumns)));
		} catch {}
	};

	const toggleColumn = (key: string) => {
		const next = new Set(visibleColumns);
		if (next.has(key)) next.delete(key);
		else next.add(key);
		visibleColumns = next;
		saveColumns();
	};

	const resetColumns = () => {
		visibleColumns = new Set(COLUMNS.map((c) => String(c.key)));
		saveColumns();
	};

	onMount(() => {
		try {
			const d = localStorage.getItem('bc-table-density');
			if (d === 'compact' || d === 'comfortable') density = d;
		} catch {}

		try {
			const stored = localStorage.getItem('bc-table-columns');
			visibleColumns = new Set(stored ? JSON.parse(stored) : COLUMNS.map((c) => String(c.key)));
		} catch {
			visibleColumns = new Set(COLUMNS.map((c) => String(c.key)));
		}

		const url = $pageStore.url;
		if (url.searchParams.get('needs_review') === 'true') needsReviewOnly = true;
		const company = url.searchParams.get('company');
		if (company) companyFilter = company;

		mounted = true;
		lastPage = page;
		loadCards();
		loadCompanies();
	});
</script>

<div class="flex flex-col gap-4">
	<div class="flex flex-wrap items-center gap-2">
		<div class="relative w-full sm:w-72">
			<Search
				class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
			/>
			<Input
				type="search"
				class="h-8 pl-8"
				placeholder={$i18n.t('Search name, company, email, notes…')}
				bind:value={searchQuery}
				oninput={debouncedSearch}
			/>
		</div>

		<NativeSelect.Root
			size="sm"
			class="max-w-56"
			value={companyFilter}
			aria-label={$i18n.t('Company')}
			onchange={(e: Event) => {
				companyFilter = (e.currentTarget as HTMLSelectElement).value;
				filtersChanged();
			}}
		>
			<NativeSelect.Option value="">{$i18n.t('All companies')}</NativeSelect.Option>
			{#each companies as c}
				<NativeSelect.Option value={c}>{c}</NativeSelect.Option>
			{/each}
		</NativeSelect.Root>

		<NativeSelect.Root
			size="sm"
			value={statusFilter}
			aria-label={$i18n.t('Status')}
			onchange={(e: Event) => {
				statusFilter = (e.currentTarget as HTMLSelectElement).value;
				filtersChanged();
			}}
		>
			<NativeSelect.Option value="">{$i18n.t('Any status')}</NativeSelect.Option>
			<NativeSelect.Option value="completed">{$i18n.t('Completed')}</NativeSelect.Option>
			<NativeSelect.Option value="processing">{$i18n.t('Processing')}</NativeSelect.Option>
			<NativeSelect.Option value="pending">{$i18n.t('Pending', { context: 'gnos3' })}</NativeSelect.Option>
			<NativeSelect.Option value="failed">{$i18n.t('Failed')}</NativeSelect.Option>
		</NativeSelect.Root>

		<div class="flex items-center gap-2">
			<Checkbox
				id="bc-needs-review"
				checked={needsReviewOnly}
				onCheckedChange={(v) => {
					needsReviewOnly = v === true;
					filtersChanged();
				}}
			/>
			<Label for="bc-needs-review" class="font-normal">{$i18n.t('Needs review only')}</Label>
		</div>

		<div class="ml-auto flex items-center gap-2">
			<span class="text-sm text-muted-foreground tabular-nums">
				{total}
				{$i18n.t('cards')}
			</span>

			<ToggleGroup.Root
				type="single"
				variant="outline"
				size="sm"
				value={density}
				onValueChange={(v) => setDensity(v)}
				aria-label={$i18n.t('Density')}
			>
				<ToggleGroup.Item value="compact" aria-label={$i18n.t('Compact density')}>
					<Rows3 />
				</ToggleGroup.Item>
				<ToggleGroup.Item value="comfortable" aria-label={$i18n.t('Comfortable density')}>
					<Rows2 />
				</ToggleGroup.Item>
			</ToggleGroup.Root>

			<DropdownMenu.Root>
				<DropdownMenu.Trigger>
					{#snippet child({ props })}
						<Button
							{...props}
							variant="outline"
							size="icon-sm"
							aria-label={$i18n.t('Show/hide columns')}
						>
							<Columns3 />
						</Button>
					{/snippet}
				</DropdownMenu.Trigger>
				<DropdownMenu.Content align="end" class="w-56">
					<DropdownMenu.Label>{$i18n.t('Visible columns')}</DropdownMenu.Label>
					{#each COLUMNS as col}
						<DropdownMenu.CheckboxItem
							checked={col.alwaysVisible || visibleColumns.has(String(col.key))}
							disabled={col.alwaysVisible}
							closeOnSelect={false}
							onCheckedChange={() => !col.alwaysVisible && toggleColumn(String(col.key))}
						>
							{$i18n.t(col.label, { context: 'gnos3' })}
						</DropdownMenu.CheckboxItem>
					{/each}
					<DropdownMenu.Separator />
					<DropdownMenu.Item onSelect={resetColumns}>{$i18n.t('Show all')}</DropdownMenu.Item>
				</DropdownMenu.Content>
			</DropdownMenu.Root>
		</div>
	</div>

	{#if loading && cards.length === 0}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(6) as _}
				<Skeleton class="h-8 w-full" />
			{/each}
		</div>
	{:else if cards.length === 0}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><IdCard /></Empty.Media>
				<Empty.Title>{$i18n.t('No business cards found.')}</Empty.Title>
				<Empty.Description>
					{$i18n.t('Tag a K4mi document with')} <code>business_card</code>
					{$i18n.t('to extract one.')}
				</Empty.Description>
			</Empty.Header>
		</Empty.Root>
	{:else}
		<div class="overflow-hidden rounded-md border">
			<Table.Root class={density === 'compact' ? 'text-xs' : ''}>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						{#each shownColumns as col}
							<Table.Head style="min-width: {col.minW}">
								{#if col.sortable}
									<button
										type="button"
										class="-mx-1 inline-flex items-center gap-1 rounded-sm px-1 hover:text-foreground focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
										onclick={() => handleSort(String(col.key))}
										aria-sort={sortBy === col.key
											? sortDir === 'asc'
												? 'ascending'
												: 'descending'
											: undefined}
									>
										{$i18n.t(col.label, { context: 'gnos3' })}
										{#if sortBy === col.key}
											{#if sortDir === 'asc'}<ArrowUp class="size-3.5 text-muted-foreground" />{:else}<ArrowDown
													class="size-3.5 text-muted-foreground"
												/>{/if}
										{/if}
									</button>
								{:else}
									{$i18n.t(col.label, { context: 'gnos3' })}
								{/if}
							</Table.Head>
						{/each}
						<Table.Head style="width: 8rem">{$i18n.t('Status')}</Table.Head>
						<Table.Head class="w-12"><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each cards as card (card.id)}
						<Table.Row
							class="cursor-pointer"
							data-state={selectedCard?.id === card.id ? 'selected' : undefined}
							onclick={() => (selectedCard = card)}
							onkeydown={(e: KeyboardEvent) => {
								if (e.key === 'Enter' || e.key === ' ') {
									e.preventDefault();
									selectedCard = card;
								}
							}}
							tabindex={0}
						>
							{#each shownColumns as col}
								<Table.Cell class="{cellPad} max-w-[22rem]" style="min-width: {col.minW}">
									{#if col.key === 'full_name'}
										<div class="flex items-center gap-2">
											<span
												class="inline-flex size-6 shrink-0 items-center justify-center rounded-full bg-muted text-[10px] font-medium"
												>{initials(card.full_name)}</span
											>
											{#if card.full_name}
												<span class="truncate font-medium">{card.full_name}</span>
											{:else}
												<span class="text-muted-foreground">{$i18n.t('Untitled card')}</span>
											{/if}
										</div>
									{:else if col.readonly && col.key === 'k4mi_notes'}
										{@const noteText = formatK4miNotes(card.k4mi_notes)}
										{#if noteText}
											<span
												class="line-clamp-2 text-xs leading-snug whitespace-normal text-muted-foreground"
												title={noteText}>{noteText}</span
											>
										{:else}
											<span class="text-muted-foreground">—</span>
										{/if}
									{:else if col.key === 'email' && card.email}
										<a
											class="block truncate text-link underline-offset-4 hover:underline"
											href="mailto:{card.email}"
											onclick={(e) => e.stopPropagation()}>{card.email}</a
										>
									{:else if (card as any)[col.key]}
										<span class="block truncate">{(card as any)[col.key]}</span>
									{:else}
										<span class="text-muted-foreground">—</span>
									{/if}
								</Table.Cell>
							{/each}
							<Table.Cell class={cellPad}>
								<StatusBadge kind="extraction" status={statusOf(card)} />
							</Table.Cell>
							<Table.Cell class="{cellPad} text-right">
								<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
								<div class="inline-flex" onclick={(e) => e.stopPropagation()}>
									<DropdownMenu.Root>
										<DropdownMenu.Trigger>
											{#snippet child({ props })}
												<Button
													{...props}
													variant="ghost"
													size="icon-xs"
													aria-label={$i18n.t('More actions')}
												>
													{#if syncingIds.has(card.id) || reprocessingIds.has(card.id)}
														<Spinner />
													{:else}
														<Ellipsis />
													{/if}
												</Button>
											{/snippet}
										</DropdownMenu.Trigger>
										<DropdownMenu.Content align="end" class="w-60">
											{#if card.k4mi_document_id}
												<DropdownMenu.Item>
													{#snippet child({ props })}
														<a
															{...props}
															href={k4miDocHref(card.k4mi_document_id!)}
															target="_blank"
															rel="noopener noreferrer"
														>
															<ExternalLink />{$i18n.t('Open in K4mi')}
														</a>
													{/snippet}
												</DropdownMenu.Item>
												<DropdownMenu.Item
													disabled={syncingIds.has(card.id)}
													onSelect={() => handleSync(card)}
												>
													<RefreshCw />{$i18n.t('Sync notes & metadata from K4mi')}
												</DropdownMenu.Item>
												<DropdownMenu.Item
													disabled={reprocessingIds.has(card.id)}
													onSelect={() => handleReprocess(card)}
												>
													<RotateCcw />{$i18n.t('Re-extract from the document')}
												</DropdownMenu.Item>
												<DropdownMenu.Separator />
											{/if}
											<DropdownMenu.Item variant="destructive" onSelect={() => handleDelete(card)}>
												<Trash2 />{$i18n.t('Delete')}
											</DropdownMenu.Item>
										</DropdownMenu.Content>
									</DropdownMenu.Root>
								</div>
							</Table.Cell>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</div>

		<TablePagination bind:page count={total} {perPage} />
	{/if}
</div>

{#if selectedCard}
	<BusinessCardDetailDrawer
		card={selectedCard}
		onclose={() => (selectedCard = null)}
		onupdated={onCardUpdated}
		ondeleterequest={(c) => {
			selectedCard = null;
			handleDelete(c);
		}}
	/>
{/if}

<ConfirmDialog
	bind:open={showDeleteConfirm}
	title={$i18n.t('Delete business card?')}
	description={deleteTarget
		? `${$i18n.t('Permanently delete the card for')} "${deleteTarget.full_name ?? ''}"? ${$i18n.t('The K4mi document stays.')}`
		: ''}
	confirmLabel={$i18n.t('Delete')}
	destructive
	onconfirm={confirmDelete}
	oncancel={() => (deleteTarget = null)}
/>
