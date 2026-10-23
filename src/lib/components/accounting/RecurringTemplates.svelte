<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';
	import Eye from '@lucide/svelte/icons/eye';
	import Ellipsis from '@lucide/svelte/icons/ellipsis';
	import Play from '@lucide/svelte/icons/play';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Repeat from '@lucide/svelte/icons/repeat';
	import Check from '@lucide/svelte/icons/check';

	import {
		getRecurringTemplates,
		createRecurringTemplate,
		updateRecurringTemplate,
		deleteRecurringTemplate,
		generateRecurringNow,
		previewRecurring,
		getAccounts
	} from '$lib/apis/accounting';

	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';

	const i18n: any = getContext('i18n');
	export let companyId: number;

	let templates: any[] = [];
	let accounts: any[] = [];
	let loading = true;
	let showForm = false;
	let editingId: number | null = null;

	let showDeleteConfirm = false;
	let deleteTarget: any = null;

	// Form state
	let form = {
		name: '',
		frequency: 'monthly',
		day_of_month: 1,
		start_date: new Date().toISOString().slice(0, 10),
		end_date: '',
		currency: 'USD',
		reference_prefix: '',
		description: '',
		auto_post: false,
		lines: [
			{ account_code: '', debit: 0, credit: 0, description: '' },
			{ account_code: '', debit: 0, credit: 0, description: '' }
		]
	};

	const load = async () => {
		loading = true;
		try {
			const [tmplData, acctData] = await Promise.all([
				getRecurringTemplates(companyId),
				getAccounts({ company_id: companyId })
			]);
			templates = tmplData ?? [];
			const accts = acctData?.accounts ?? acctData ?? [];
			accounts = Array.isArray(accts) ? accts : [];
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
		loading = false;
	};

	onMount(load);

	const addLine = () => {
		form.lines = [...form.lines, { account_code: '', debit: 0, credit: 0, description: '' }];
	};
	const removeLine = (i: number) => {
		form.lines = form.lines.filter((_, idx) => idx !== i);
	};

	const resetForm = () => {
		editingId = null;
		form = {
			name: '',
			frequency: 'monthly',
			day_of_month: 1,
			start_date: new Date().toISOString().slice(0, 10),
			end_date: '',
			currency: 'USD',
			reference_prefix: '',
			description: '',
			auto_post: false,
			lines: [
				{ account_code: '', debit: 0, credit: 0, description: '' },
				{ account_code: '', debit: 0, credit: 0, description: '' }
			]
		};
	};

	const openNew = () => {
		resetForm();
		showForm = true;
	};

	const handleEdit = (tmpl: any) => {
		editingId = tmpl.id;
		const lines = (tmpl.lines_template ?? []).map((l: any) => ({
			account_code: l.account_code ?? '',
			debit: l.debit ?? 0,
			credit: l.credit ?? 0,
			description: l.description ?? ''
		}));
		while (lines.length < 2) lines.push({ account_code: '', debit: 0, credit: 0, description: '' });
		form = {
			name: tmpl.name ?? '',
			frequency: tmpl.frequency ?? 'monthly',
			day_of_month: tmpl.day_of_month ?? 1,
			start_date: tmpl.start_date ?? new Date().toISOString().slice(0, 10),
			end_date: tmpl.end_date ?? '',
			currency: tmpl.currency ?? 'USD',
			reference_prefix: tmpl.reference_prefix ?? '',
			description: tmpl.description ?? '',
			auto_post: !!tmpl.auto_post,
			lines
		};
		showForm = true;
	};

	const handleSubmit = async () => {
		if (!form.name) {
			toast.error($i18n.t('Name is required'));
			return;
		}
		if (form.lines.length < 2) {
			toast.error($i18n.t('At least 2 lines required'));
			return;
		}
		const payload = {
			name: form.name,
			frequency: form.frequency,
			day_of_month: form.day_of_month,
			start_date: form.start_date,
			end_date: form.end_date || undefined,
			currency: form.currency,
			reference_prefix: form.reference_prefix || undefined,
			description: form.description || undefined,
			auto_post: form.auto_post,
			transaction_type: 'others',
			lines_template: form.lines.filter((l) => l.account_code)
		};
		try {
			if (editingId) {
				await updateRecurringTemplate(editingId, payload);
				toast.success($i18n.t('Template updated'));
			} else {
				await createRecurringTemplate(companyId, payload);
				toast.success($i18n.t('Template created'));
			}
			showForm = false;
			resetForm();
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const handlePreview = async (id: number) => {
		try {
			const p = await previewRecurring(id);
			const lines = p?.lines ?? [];
			const summary = lines
				.map((l: any) => `${l.account_code} ${l.debit ? 'DR ' + l.debit : 'CR ' + l.credit}`)
				.join(' · ');
			toast.info(
				`${$i18n.t('Next', { context: 'run' })}: ${p?.transaction_date ?? ''} — ${summary || $i18n.t('no lines')}`
			);
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const handleDelete = async (id: number) => {
		try {
			await deleteRecurringTemplate(id);
			toast.success($i18n.t('Template deleted'));
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const handleGenerate = async (id: number) => {
		try {
			const res = await generateRecurringNow(id);
			toast.success($i18n.t(`Generated ${res.generated} entries`));
			await load();
		} catch (err: any) {
			toast.error(err?.detail ?? `${err}`);
		}
	};

	const freqLabel = (f: string) => {
		const map: Record<string, string> = {
			weekly: 'Weekly',
			monthly: 'Monthly',
			quarterly: 'Quarterly',
			yearly: 'Yearly'
		};
		return map[f] || f;
	};
</script>

<ConfirmDialog
	bind:open={showDeleteConfirm}
	title={$i18n.t('Delete recurring template?')}
	description={deleteTarget
		? `"${deleteTarget.name}" — ${$i18n.t('no further entries will be generated from it. Entries already generated stay.')}`
		: ''}
	confirmLabel={$i18n.t('Delete')}
	destructive
	onconfirm={() => (deleteTarget ? handleDelete(deleteTarget.id) : undefined)}
	oncancel={() => (deleteTarget = null)}
/>

<div class="flex flex-col gap-4">
	<div class="flex flex-wrap items-center justify-between gap-2">
		<h3 class="text-lg font-semibold">{$i18n.t('Recurring Transactions')}</h3>
		<Button variant="outline" size="sm" onclick={openNew}>
			<Plus />{$i18n.t('New Template')}
		</Button>
	</div>

	{#if loading}
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(3) as _}
				<Skeleton class="h-8 w-full" />
			{/each}
		</div>
	{:else if templates.length === 0}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><Repeat /></Empty.Media>
				<Empty.Title>{$i18n.t('No recurring templates')}</Empty.Title>
				<Empty.Description>
					{$i18n.t('Create one for repeating entries like rent, salaries, or subscriptions.')}
				</Empty.Description>
			</Empty.Header>
			<Empty.Content>
				<Button variant="outline" size="sm" onclick={openNew}>
					<Plus />{$i18n.t('New Template')}
				</Button>
			</Empty.Content>
		</Empty.Root>
	{:else}
		<div class="overflow-hidden rounded-md border">
			<Table.Root>
				<Table.Header class="bg-muted/50">
					<Table.Row class="hover:bg-transparent">
						<Table.Head>{$i18n.t('Name', { context: 'gnos3' })}</Table.Head>
						<Table.Head>{$i18n.t('Frequency')}</Table.Head>
						<Table.Head>{$i18n.t('Next', { context: 'run' })}</Table.Head>
						<Table.Head>{$i18n.t('Last')}</Table.Head>
						<Table.Head>{$i18n.t('Currency')}</Table.Head>
						<Table.Head>{$i18n.t('Status')}</Table.Head>
						<Table.Head class="w-20"><span class="sr-only">{$i18n.t('Actions')}</span></Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each templates as tmpl (tmpl.id)}
						<Table.Row>
							<Table.Cell class="max-w-[18rem]">
								<div class="truncate font-medium">{tmpl.name}</div>
								{#if tmpl.description}
									<div class="truncate text-xs text-muted-foreground" title={tmpl.description}>
										{tmpl.description}
									</div>
								{/if}
							</Table.Cell>
							<Table.Cell>
								<Badge variant="outline">{$i18n.t(freqLabel(tmpl.frequency))}</Badge>
							</Table.Cell>
							<Table.Cell class="tabular-nums">{tmpl.next_run_date ?? '—'}</Table.Cell>
							<Table.Cell class="text-muted-foreground tabular-nums">
								{tmpl.last_generated_date ?? '—'}
							</Table.Cell>
							<Table.Cell class="font-mono text-[13px]">{tmpl.currency}</Table.Cell>
							<Table.Cell>
								<div class="flex items-center gap-1">
									{#if !tmpl.is_active}
										<Badge variant="secondary">{$i18n.t('Inactive')}</Badge>
									{/if}
									{#if tmpl.auto_post}
										<Badge variant="status"
											><Check class="text-success" />{$i18n.t('Auto-post')}</Badge
										>
									{/if}
									{#if tmpl.is_active && !tmpl.auto_post}
										<span class="text-muted-foreground">—</span>
									{/if}
								</div>
							</Table.Cell>
							<Table.Cell class="text-right">
								<div class="inline-flex items-center gap-0.5">
									<Tip content={$i18n.t('Preview')}>
										<Button
											variant="ghost"
											size="icon-xs"
											aria-label={$i18n.t('Preview')}
											onclick={() => handlePreview(tmpl.id)}
										>
											<Eye />
										</Button>
									</Tip>
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
										<DropdownMenu.Content align="end" class="w-48">
											<DropdownMenu.Item onSelect={() => handleGenerate(tmpl.id)}>
												<Play />{$i18n.t('Generate Now')}
											</DropdownMenu.Item>
											<DropdownMenu.Item onSelect={() => handleEdit(tmpl)}>
												<Pencil />{$i18n.t('Edit')}
											</DropdownMenu.Item>
											<DropdownMenu.Separator />
											<DropdownMenu.Item
												variant="destructive"
												onSelect={() => {
													deleteTarget = tmpl;
													showDeleteConfirm = true;
												}}
											>
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
	{/if}
</div>

<!-- New / edit template -->
<Dialog.Root bind:open={showForm}>
	<Dialog.Content class="max-h-[90vh] gap-5 overflow-y-auto sm:max-w-3xl">
		<Dialog.Header>
			<Dialog.Title>
				{editingId ? $i18n.t('Edit Template') : $i18n.t('New Template')}
			</Dialog.Title>
			<Dialog.Description
				>{$i18n.t('An entry with these lines is generated on each run date.')}</Dialog.Description
			>
		</Dialog.Header>

		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(10rem,100%),1fr))] gap-4">
			<div class="grid content-start gap-2">
				<Label for="rt-name">{$i18n.t('Name', { context: 'gnos3' })}</Label>
				<Input id="rt-name" type="text" bind:value={form.name} placeholder={$i18n.t('Monthly rent')} />
			</div>
			<div class="grid content-start gap-2">
				<Label for="rt-frequency">{$i18n.t('Frequency')}</Label>
				<NativeSelect.Root id="rt-frequency" class="w-full" bind:value={form.frequency}>
					<NativeSelect.Option value="weekly">{$i18n.t('Weekly')}</NativeSelect.Option>
					<NativeSelect.Option value="monthly">{$i18n.t('Monthly')}</NativeSelect.Option>
					<NativeSelect.Option value="quarterly">{$i18n.t('Quarterly')}</NativeSelect.Option>
					<NativeSelect.Option value="yearly">{$i18n.t('Yearly')}</NativeSelect.Option>
				</NativeSelect.Root>
			</div>
			<div class="grid content-start gap-2">
				<Label for="rt-start">{$i18n.t('Start Date')}</Label>
				<Input id="rt-start" type="date" class="tabular-nums" bind:value={form.start_date} />
			</div>
			<div class="grid content-start gap-2">
				<Label for="rt-currency">{$i18n.t('Currency')}</Label>
				<Input
					id="rt-currency"
					type="text"
					class="font-mono uppercase"
					bind:value={form.currency}
				/>
			</div>
			<div class="col-span-full grid gap-2">
				<Label for="rt-description">{$i18n.t('Description')}</Label>
				<Input id="rt-description" type="text" bind:value={form.description} />
			</div>
		</div>

		<div class="grid gap-2">
			<div class="flex items-center justify-between">
				<h4 class="text-sm font-medium">{$i18n.t('Journal Lines')}</h4>
				<Button variant="ghost" size="sm" onclick={addLine}>
					<Plus />{$i18n.t('Add Line')}
				</Button>
			</div>
			<div class="overflow-hidden rounded-md border">
				<Table.Root>
					<Table.Header class="bg-muted/50">
						<Table.Row class="hover:bg-transparent">
							<Table.Head class="min-w-[14rem]">{$i18n.t('Account', { context: 'gnos3' })}</Table.Head>
							<Table.Head class="w-28 text-right">{$i18n.t('Debit')}</Table.Head>
							<Table.Head class="w-28 text-right">{$i18n.t('Credit')}</Table.Head>
							<Table.Head class="min-w-[8rem]">{$i18n.t('Description')}</Table.Head>
							<Table.Head class="w-10"><span class="sr-only">{$i18n.t('Remove')}</span></Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each form.lines as line, i}
							<Table.Row class="hover:bg-transparent">
								<Table.Cell>
									<NativeSelect.Root
										size="sm"
										class="w-full"
										aria-label={$i18n.t('Account', { context: 'gnos3' })}
										bind:value={line.account_code}
									>
										<NativeSelect.Option value="">{$i18n.t('Account...')}</NativeSelect.Option>
										{#each accounts as acct}
											<NativeSelect.Option value={acct.code}
												>{acct.code} — {acct.name}</NativeSelect.Option
											>
										{/each}
									</NativeSelect.Root>
								</Table.Cell>
								<Table.Cell>
									<Input
										type="number"
										class="h-8 min-w-24 text-right tabular-nums"
										aria-label={$i18n.t('Debit')}
										bind:value={line.debit}
										placeholder={$i18n.t('Debit')}
									/>
								</Table.Cell>
								<Table.Cell>
									<Input
										type="number"
										class="h-8 min-w-24 text-right tabular-nums"
										aria-label={$i18n.t('Credit')}
										bind:value={line.credit}
										placeholder={$i18n.t('Credit')}
									/>
								</Table.Cell>
								<Table.Cell>
									<Input
										type="text"
										class="h-8 min-w-[8rem]"
										aria-label={$i18n.t('Description')}
										bind:value={line.description}
										placeholder={$i18n.t('Description')}
									/>
								</Table.Cell>
								<Table.Cell>
									{#if form.lines.length > 2}
										<Tip content={$i18n.t('Remove line')}>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label={$i18n.t('Remove line')}
												onclick={() => removeLine(i)}
											>
												<X />
											</Button>
										</Tip>
									{/if}
								</Table.Cell>
							</Table.Row>
						{/each}
					</Table.Body>
				</Table.Root>
			</div>
		</div>

		<Dialog.Footer class="gap-3 sm:items-center sm:justify-between">
			<div class="flex items-center gap-2">
				<Checkbox id="rt-auto-post" bind:checked={form.auto_post} />
				<Label for="rt-auto-post" class="font-normal"
					>{$i18n.t('Auto-post generated entries')}</Label
				>
			</div>
			<div class="flex flex-wrap justify-end gap-2">
				<Button
					variant="outline"
					onclick={() => {
						showForm = false;
						resetForm();
					}}
				>
					{$i18n.t('Cancel')}
				</Button>
				<Button onclick={handleSubmit}>
					{editingId ? $i18n.t('Save Changes') : $i18n.t('Create Template')}
				</Button>
			</div>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
