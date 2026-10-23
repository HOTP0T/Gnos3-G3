<!--
	The invoice table's filters (design system → Invoices → Table): the two most used filters
	(Status, Needs Review) as faceted buttons with dashed borders, the rest in a Filters popover
	whose button counts what is active, then Clear Filters. Rendered inline in the table toolbar.
	Every change dispatches `filter` with the full filter object.
-->
<script lang="ts">
	import { getContext, createEventDispatcher } from 'svelte';

	import CirclePlus from '@lucide/svelte/icons/circle-plus';
	import ListFilter from '@lucide/svelte/icons/list-filter';
	import X from '@lucide/svelte/icons/x';
	import Check from '@lucide/svelte/icons/check';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as Popover from '$lib/components/ui/popover/index.js';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let vendor = '';
	export let dateFrom = '';
	export let dateTo = '';
	export let minAmount: string = '';
	export let maxAmount: string = '';
	export let status = '';
	export let needsReview: boolean | undefined = undefined;
	export let tag = '';
	export let availableTags: string[] = [];

	const STATUS_OPTIONS = [
		{ value: 'completed', label: 'Completed' },
		{ value: 'processing', label: 'Processing' },
		{ value: 'pending', label: 'Pending' },
		{ value: 'failed', label: 'Failed' }
	];

	$: statusLabel = STATUS_OPTIONS.find((o) => o.value === status)?.label ?? status;
	$: reviewValue = needsReview === true ? 'yes' : needsReview === false ? 'no' : '';
	// What the Filters popover holds; its button shows the count.
	$: moreCount = [vendor, dateFrom, dateTo, minAmount, maxAmount, tag].filter(Boolean).length;
	$: anyActive = moreCount > 0 || !!status || needsReview !== undefined;

	const applyFilters = () => {
		dispatch('filter', {
			vendor,
			date_from: dateFrom || undefined,
			date_to: dateTo || undefined,
			min_amount: minAmount ? parseFloat(minAmount) : undefined,
			max_amount: maxAmount ? parseFloat(maxAmount) : undefined,
			status: status || undefined,
			needs_review: needsReview,
			tag: tag || undefined
		});
	};

	const clearMore = () => {
		vendor = '';
		dateFrom = '';
		dateTo = '';
		minAmount = '';
		maxAmount = '';
		tag = '';
		applyFilters();
	};

	const clearFilters = () => {
		vendor = '';
		dateFrom = '';
		dateTo = '';
		minAmount = '';
		maxAmount = '';
		status = '';
		needsReview = undefined;
		tag = '';
		applyFilters();
	};

	const valueOf = (e: Event) => (e.currentTarget as HTMLInputElement).value;
</script>

<!-- Status -->
<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		{#snippet child({ props })}
			<Button {...props} variant="outline" size="sm" class="border-dashed">
				<CirclePlus />{$i18n.t('Status')}
				{#if status}
					<Separator orientation="vertical" class="mx-0.5 h-4!" />
					<Badge variant="secondary" class="rounded-sm px-1.5 font-normal"
						>{$i18n.t(statusLabel)}</Badge
					>
				{/if}
			</Button>
		{/snippet}
	</DropdownMenu.Trigger>
	<DropdownMenu.Content align="start" class="w-48">
		<DropdownMenu.RadioGroup
			value={status}
			onValueChange={(v) => {
				status = v;
				applyFilters();
			}}
		>
			{#each STATUS_OPTIONS as o}
				<DropdownMenu.RadioItem value={o.value} closeOnSelect
					>{$i18n.t(o.label, { context: 'gnos3' })}</DropdownMenu.RadioItem
				>
			{/each}
		</DropdownMenu.RadioGroup>
		{#if status}
			<DropdownMenu.Separator />
			<DropdownMenu.Item
				onSelect={() => {
					status = '';
					applyFilters();
				}}>{$i18n.t('All')}</DropdownMenu.Item
			>
		{/if}
	</DropdownMenu.Content>
</DropdownMenu.Root>

<!-- Needs Review -->
<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		{#snippet child({ props })}
			<Button {...props} variant="outline" size="sm" class="border-dashed">
				<CirclePlus />{$i18n.t('Needs Review')}
				{#if needsReview !== undefined}
					<Separator orientation="vertical" class="mx-0.5 h-4!" />
					<Badge variant="secondary" class="rounded-sm px-1.5 font-normal"
						>{needsReview ? $i18n.t('Yes') : $i18n.t('No')}</Badge
					>
				{/if}
			</Button>
		{/snippet}
	</DropdownMenu.Trigger>
	<DropdownMenu.Content align="start" class="w-40">
		<DropdownMenu.RadioGroup
			value={reviewValue}
			onValueChange={(v) => {
				needsReview = v === 'yes' ? true : v === 'no' ? false : undefined;
				applyFilters();
			}}
		>
			<DropdownMenu.RadioItem value="yes" closeOnSelect>{$i18n.t('Yes')}</DropdownMenu.RadioItem>
			<DropdownMenu.RadioItem value="no" closeOnSelect>{$i18n.t('No')}</DropdownMenu.RadioItem>
		</DropdownMenu.RadioGroup>
		{#if needsReview !== undefined}
			<DropdownMenu.Separator />
			<DropdownMenu.Item
				onSelect={() => {
					needsReview = undefined;
					applyFilters();
				}}>{$i18n.t('All')}</DropdownMenu.Item
			>
		{/if}
	</DropdownMenu.Content>
</DropdownMenu.Root>

<!-- Vendor, dates, amounts, tags -->
<Popover.Root>
	<Popover.Trigger>
		{#snippet child({ props })}
			<Button {...props} variant="outline" size="sm">
				<ListFilter />{$i18n.t('Filters')}
				{#if moreCount > 0}
					<Badge variant="count" class="h-[18px] min-w-[18px]">{moreCount}</Badge>
				{/if}
			</Button>
		{/snippet}
	</Popover.Trigger>
	<Popover.Content align="start" class="w-80 gap-4">
		<div class="grid gap-1.5">
			<Label for="inv-filter-vendor">{$i18n.t('Vendor')}</Label>
			<Input
				id="inv-filter-vendor"
				class="h-8"
				value={vendor}
				placeholder={$i18n.t('Search vendor...')}
				oninput={(e) => {
					vendor = valueOf(e);
					applyFilters();
				}}
			/>
		</div>
		<div class="grid grid-cols-2 gap-3">
			<div class="grid gap-1.5">
				<Label for="inv-filter-from">{$i18n.t('Date From')}</Label>
				<Input
					id="inv-filter-from"
					type="date"
					class="h-8"
					value={dateFrom}
					onchange={(e) => {
						dateFrom = valueOf(e);
						applyFilters();
					}}
				/>
			</div>
			<div class="grid gap-1.5">
				<Label for="inv-filter-to">{$i18n.t('Date To')}</Label>
				<Input
					id="inv-filter-to"
					type="date"
					class="h-8"
					value={dateTo}
					onchange={(e) => {
						dateTo = valueOf(e);
						applyFilters();
					}}
				/>
			</div>
		</div>
		<div class="grid grid-cols-2 gap-3">
			<div class="grid gap-1.5">
				<Label for="inv-filter-min">{$i18n.t('Min Amount')}</Label>
				<Input
					id="inv-filter-min"
					type="number"
					step="0.01"
					class="h-8 text-right tabular-nums"
					placeholder="0.00"
					value={minAmount}
					oninput={(e) => {
						minAmount = valueOf(e);
						applyFilters();
					}}
				/>
			</div>
			<div class="grid gap-1.5">
				<Label for="inv-filter-max">{$i18n.t('Max Amount')}</Label>
				<Input
					id="inv-filter-max"
					type="number"
					step="0.01"
					class="h-8 text-right tabular-nums"
					placeholder="0.00"
					value={maxAmount}
					oninput={(e) => {
						maxAmount = valueOf(e);
						applyFilters();
					}}
				/>
			</div>
		</div>
		{#if availableTags.length > 0}
			<div class="grid gap-1.5">
				<span class="text-sm font-medium">{$i18n.t('Tags')}</span>
				<div class="flex max-h-32 flex-wrap gap-1.5 overflow-y-auto">
					{#each availableTags as t}
						<Button
							variant={tag === t ? 'secondary' : 'outline'}
							size="xs"
							aria-pressed={tag === t}
							onclick={() => {
								tag = tag === t ? '' : t;
								applyFilters();
							}}
						>
							{#if tag === t}<Check />{/if}{t}
						</Button>
					{/each}
				</div>
			</div>
		{/if}
		{#if moreCount > 0}
			<div class="flex justify-end">
				<Button variant="ghost" size="sm" onclick={clearMore}>{$i18n.t('Clear Filters')}</Button>
			</div>
		{/if}
	</Popover.Content>
</Popover.Root>

{#if anyActive}
	<Button variant="ghost" size="sm" onclick={clearFilters}>
		{$i18n.t('Clear Filters')}<X />
	</Button>
{/if}
