<!--
	A note's properties, under its title: its type (Person, Project, Meeting…), the type's fields,
	tags, aliases and any other property (as imported from another vault). Relations to other notes
	are fields of kind "note" / "notes": they show in the graph and in the other note's backlinks.
	Changes are saved after a short pause (POST /note-vaults/notes/{id}/meta).
-->
<script lang="ts">
	import { getContext, untrack } from 'svelte';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';
	import Tag from '@lucide/svelte/icons/tag';
	import Shapes from '@lucide/svelte/icons/shapes';
	import ExternalLink from '@lucide/svelte/icons/external-link';
	import FileText from '@lucide/svelte/icons/file-text';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import type { NoteType, TypeField, Vault } from '$lib/apis/note-vaults';
	import { chartColor, notesById, noteTypes, prefs, typeName, typeOf } from '../vault';
	import { ENTITY_META, entityHref, opensOutside } from '../entities';
	import RefPicker from './RefPicker.svelte';
	import TypeIcon from '../TypeIcon.svelte';

	const i18n: any = getContext('i18n');

	let {
		vault,
		noteId,
		properties = {},
		editable = false,
		onChange,
		onOpenNote,
		onCreateNote
	}: {
		vault: Vault | null;
		noteId: string;
		properties: Record<string, any>;
		editable?: boolean;
		onChange: (values: Record<string, any>) => void;
		onOpenNote: (id: string) => void;
		onCreateNote: (
			title: string,
			type: string | null
		) => Promise<{ id: string; title: string } | null>;
	} = $props();

	let open = $state(prefs.get('properties.open', true));
	let values: Record<string, any> = $state({});
	let tagInput = $state('');
	let aliasInput = $state('');
	let newKey = $state('');
	let addingKey = $state(false);

	// Take the stored properties whenever another note is shown (or they change elsewhere).
	$effect(() => {
		const incoming = properties;
		untrack(() => {
			values = JSON.parse(JSON.stringify(incoming ?? {}));
		});
	});

	const type: NoteType | null = $derived(typeOf(vault, values.type));
	const fields: TypeField[] = $derived(type?.fields ?? []);
	const fieldKeys = $derived(new Set(fields.map((f) => f.key)));
	const otherKeys = $derived(
		Object.keys(values).filter((k) => !['type', 'tags', 'aliases'].includes(k) && !fieldKeys.has(k))
	);
	const tags: string[] = $derived(
		Array.isArray(values.tags) ? values.tags : values.tags ? [values.tags] : []
	);
	const aliases: string[] = $derived(
		Array.isArray(values.aliases) ? values.aliases : values.aliases ? [values.aliases] : []
	);
	const filled = $derived(Object.keys(values).filter((k) => !isEmpty(values[k])).length);

	function isEmpty(v: any) {
		return v === null || v === undefined || v === '' || (Array.isArray(v) && v.length === 0);
	}

	const commit = () => {
		const clean: Record<string, any> = {};
		for (const [k, v] of Object.entries(values)) if (!isEmpty(v)) clean[k] = v;
		onChange(clean);
	};

	const set = (key: string, value: any) => {
		values = { ...values, [key]: value };
		commit();
	};

	const remove = (key: string) => {
		const { [key]: _, ...rest } = values;
		values = rest;
		commit();
	};

	const addTag = () => {
		const tag = tagInput.trim().replace(/^#/, '').replace(/\s+/g, '-');
		tagInput = '';
		if (!tag || tags.some((t) => t.toLowerCase() === tag.toLowerCase())) return;
		set('tags', [...tags, tag]);
	};

	const addAlias = () => {
		const alias = aliasInput.trim();
		aliasInput = '';
		if (!alias || aliases.includes(alias)) return;
		set('aliases', [...aliases, alias]);
	};

	const refs = (value: any): { id: string; title: string }[] =>
		(Array.isArray(value) ? value : value ? [value] : []).filter(
			(v: any) => v && (v.id || v.title)
		);

	const label = (field: TypeField) => (type?.builtin ? $i18n.t(field.label) : field.label);

	const optionLabel = (option: string) => (type?.builtin ? $i18n.t(option) : option);
</script>

{#snippet noteChip(ref: { id: string; title: string }, onRemove: () => void)}
	{@const live = ref.id ? $notesById.get(ref.id) : undefined}
	{@const t = typeOf(vault, live?.type)}
	<span
		class="inline-flex max-w-full items-center gap-1 rounded-md border bg-background px-1.5 py-0.5 text-xs"
	>
		<FileText class="size-3 shrink-0" style={t ? `color: ${chartColor(t.color)}` : ''} />
		<button
			type="button"
			class="truncate {live ? 'text-link hover:underline' : 'text-muted-foreground'}"
			onclick={() => live && onOpenNote(live.id)}
		>
			{live?.title ?? ref.title}
		</button>
		{#if editable}
			<button
				type="button"
				class="text-muted-foreground hover:text-foreground"
				onclick={onRemove}
				aria-label={$i18n.t('Remove')}
			>
				<X class="size-3" />
			</button>
		{/if}
	</span>
{/snippet}

{#snippet pickerTrigger(props: Record<string, unknown>)}
	<button
		{...props}
		type="button"
		class="inline-flex h-6 items-center gap-1 rounded-md px-1.5 text-xs text-muted-foreground hover:bg-accent hover:text-accent-foreground"
	>
		<Plus class="size-3" />{$i18n.t('Add')}
	</button>
{/snippet}

<section class="mt-3 mb-1 text-sm" aria-label={$i18n.t('Properties')}>
	<button
		type="button"
		class="mb-1 inline-flex items-center gap-1 rounded-md px-1 py-0.5 text-xs font-medium text-muted-foreground hover:text-foreground"
		onclick={() => {
			open = !open;
			prefs.set('properties.open', open);
		}}
	>
		<ChevronRight class="size-3.5 transition-transform {open ? 'rotate-90' : ''}" />
		{$i18n.t('Properties')}
		{#if !open && filled}<span class="tabular-nums">· {filled}</span>{/if}
	</button>

	{#if open}
		<div class="grid grid-cols-[minmax(7rem,9rem)_1fr] items-start gap-x-3 gap-y-1">
			<!-- Type -->
			<div class="flex h-8 items-center gap-1.5 text-muted-foreground">
				<Shapes class="size-3.5" />{$i18n.t('Type')}
			</div>
			<div class="flex min-h-8 items-center">
				{#if editable}
					<NativeSelect.Root
						size="sm"
						class="w-48"
						value={values.type ?? ''}
						onchange={(e) => set('type', (e.currentTarget as HTMLSelectElement).value || null)}
					>
						<NativeSelect.Option value="">{$i18n.t('Note')}</NativeSelect.Option>
						{#each noteTypes(vault) as t (t.key)}
							<NativeSelect.Option value={t.key}>{typeName(t, $i18n)}</NativeSelect.Option>
						{/each}
						{#if values.type && !type}
							<NativeSelect.Option value={values.type}>{values.type}</NativeSelect.Option>
						{/if}
					</NativeSelect.Root>
				{:else if type}
					<span class="inline-flex items-center gap-1.5">
						<TypeIcon icon={type.icon} class="size-4" style="color: {chartColor(type.color)}" />
						{typeName(type, $i18n)}
					</span>
				{:else}
					<span class="text-muted-foreground">{values.type ?? $i18n.t('Note')}</span>
				{/if}
			</div>

			<!-- The type's fields -->
			{#each fields as field (field.key)}
				{@const value = values[field.key]}
				<div class="flex h-8 items-center truncate text-muted-foreground" title={label(field)}>
					{label(field)}
				</div>
				<div class="flex min-h-8 min-w-0 flex-wrap items-center gap-1">
					{#if field.kind === 'note' || field.kind === 'notes'}
						{#each refs(value) as ref, i (ref.id ?? ref.title)}
							{@render noteChip(ref, () => {
								const list = refs(value).filter((_, j) => j !== i);
								set(field.key, field.kind === 'note' ? null : list);
							})}
						{/each}
						{#if editable && (field.kind === 'notes' || !refs(value).length)}
							<RefPicker
								mode="note"
								noteType={field.note_type ?? null}
								exclude={[noteId, ...refs(value).map((r) => r.id)]}
								onPick={(picked) =>
									set(field.key, field.kind === 'note' ? picked : [...refs(value), picked])}
								onCreate={(title) => onCreateNote(title, field.note_type ?? null)}
							>
								{#snippet trigger({ props })}{@render pickerTrigger(props)}{/snippet}
							</RefPicker>
						{:else if !refs(value).length}
							<span class="text-muted-foreground">—</span>
						{/if}
					{:else if field.kind === 'entity'}
						{#if value?.entity_type}
							{@const Icon = ENTITY_META[value.entity_type as keyof typeof ENTITY_META]?.icon}
							<span
								class="inline-flex max-w-full items-center gap-1 rounded-md border bg-background px-1.5 py-0.5 text-xs"
							>
								{#if Icon}<Icon class="size-3 text-muted-foreground" />{/if}
								<a
									class="truncate text-link hover:underline"
									href={entityHref(value.entity_type, value.entity_id)}
									target={opensOutside(value.entity_type) ? '_blank' : undefined}
								>
									{value.label ?? value.entity_id}
								</a>
								{#if editable}
									<button
										type="button"
										class="text-muted-foreground hover:text-foreground"
										onclick={() => set(field.key, null)}
										aria-label={$i18n.t('Remove')}
									>
										<X class="size-3" />
									</button>
								{/if}
							</span>
						{:else if editable}
							<RefPicker
								mode="entity"
								entityType={field.entity_type ?? null}
								onPick={(picked) => set(field.key, picked)}
							>
								{#snippet trigger({ props })}{@render pickerTrigger(props)}{/snippet}
							</RefPicker>
						{:else}
							<span class="text-muted-foreground">—</span>
						{/if}
					{:else if field.kind === 'checkbox'}
						<Checkbox
							checked={!!value}
							disabled={!editable}
							onCheckedChange={(checked) => set(field.key, checked ? true : null)}
						/>
					{:else if field.kind === 'select'}
						{#if editable}
							<NativeSelect.Root
								size="sm"
								class="w-48"
								value={value ?? ''}
								onchange={(e) =>
									set(field.key, (e.currentTarget as HTMLSelectElement).value || null)}
							>
								<NativeSelect.Option value="">—</NativeSelect.Option>
								{#each field.options ?? [] as option}
									<NativeSelect.Option value={option}>{optionLabel(option)}</NativeSelect.Option>
								{/each}
							</NativeSelect.Root>
						{:else}
							<span>{value ? optionLabel(value) : '—'}</span>
						{/if}
					{:else if field.kind === 'multiselect'}
						{#each field.options ?? [] as option}
							{@const on = Array.isArray(value) && value.includes(option)}
							<button
								type="button"
								disabled={!editable}
								class="h-6 rounded-md border px-2 text-xs {on
									? 'border-primary bg-primary/10 text-foreground'
									: 'text-muted-foreground hover:bg-accent'}"
								onclick={() => {
									const list = Array.isArray(value) ? value : [];
									set(field.key, on ? list.filter((o) => o !== option) : [...list, option]);
								}}
							>
								{optionLabel(option)}
							</button>
						{/each}
					{:else if editable}
						<Input
							type={field.kind === 'number'
								? 'number'
								: field.kind === 'date'
									? 'date'
									: field.kind === 'url'
										? 'url'
										: 'text'}
							class="h-8 w-full max-w-sm border-transparent bg-transparent shadow-none hover:border-input focus-visible:border-input dark:bg-transparent"
							value={value ?? ''}
							placeholder={field.kind === 'url' ? 'https://' : '—'}
							onchange={(e) => {
								const raw = (e.currentTarget as HTMLInputElement).value;
								set(
									field.key,
									field.kind === 'number' ? (raw === '' ? null : Number(raw)) : raw.trim() || null
								);
							}}
						/>
						{#if field.kind === 'url' && value}
							<a
								href={value}
								target="_blank"
								rel="noopener noreferrer"
								class="text-muted-foreground hover:text-foreground"
								aria-label={$i18n.t('Open')}
							>
								<ExternalLink class="size-3.5" />
							</a>
						{/if}
					{:else}
						<span class="truncate">{value ?? '—'}</span>
					{/if}
				</div>
			{/each}

			<!-- Tags -->
			<div class="flex h-8 items-center gap-1.5 text-muted-foreground">
				<Tag class="size-3.5" />{$i18n.t('Tags')}
			</div>
			<div class="flex min-h-8 flex-wrap items-center gap-1">
				{#each tags as tag (tag)}
					<span
						class="note-tag-chip inline-flex items-center gap-1 rounded-md bg-primary/10 px-1.5 py-0.5 text-xs text-link"
					>
						#{tag}
						{#if editable}
							<button
								type="button"
								class="opacity-60 hover:opacity-100"
								onclick={() =>
									set(
										'tags',
										tags.filter((t) => t !== tag)
									)}
								aria-label={$i18n.t('Remove')}
							>
								<X class="size-3" />
							</button>
						{/if}
					</span>
				{/each}
				{#if editable}
					<input
						class="h-6 w-28 rounded-md bg-transparent px-1.5 text-xs outline-none placeholder:text-muted-foreground focus:bg-accent"
						placeholder={$i18n.t('Add tag')}
						bind:value={tagInput}
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ',') {
								e.preventDefault();
								addTag();
							}
						}}
						onblur={addTag}
					/>
				{:else if !tags.length}
					<span class="text-muted-foreground">—</span>
				{/if}
			</div>

			<!-- Aliases -->
			{#if editable || aliases.length}
				<div
					class="flex h-8 items-center text-muted-foreground"
					title={$i18n.t('Other names [[links]] can use for this note')}
				>
					{$i18n.t('Aliases')}
				</div>
				<div class="flex min-h-8 flex-wrap items-center gap-1">
					{#each aliases as alias (alias)}
						<span class="inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-xs">
							{alias}
							{#if editable}
								<button
									type="button"
									class="opacity-60 hover:opacity-100"
									onclick={() =>
										set(
											'aliases',
											aliases.filter((a) => a !== alias)
										)}
									aria-label={$i18n.t('Remove')}
								>
									<X class="size-3" />
								</button>
							{/if}
						</span>
					{/each}
					{#if editable}
						<input
							class="h-6 w-28 rounded-md bg-transparent px-1.5 text-xs outline-none placeholder:text-muted-foreground focus:bg-accent"
							placeholder={$i18n.t('Add alias')}
							bind:value={aliasInput}
							onkeydown={(e) => {
								if (e.key === 'Enter') {
									e.preventDefault();
									addAlias();
								}
							}}
							onblur={addAlias}
						/>
					{/if}
				</div>
			{/if}

			<!-- Other properties (imported, or added by hand) -->
			{#each otherKeys as key (key)}
				{@const value = values[key]}
				{@const noteRefs = refs(value)}
				<div class="flex h-8 items-center truncate text-muted-foreground" title={key}>{key}</div>
				<div class="flex min-h-8 min-w-0 items-center gap-1">
					{#if noteRefs.length && typeof value !== 'string'}
						<div class="flex flex-wrap gap-1">
							{#each noteRefs as ref (ref.id ?? ref.title)}
								{@render noteChip(ref, () =>
									set(key, Array.isArray(value) ? noteRefs.filter((r) => r !== ref) : null)
								)}
							{/each}
						</div>
					{:else if editable}
						<Input
							class="h-8 w-full max-w-sm border-transparent bg-transparent shadow-none hover:border-input focus-visible:border-input dark:bg-transparent"
							value={typeof value === 'object' ? JSON.stringify(value) : String(value ?? '')}
							onchange={(e) => set(key, (e.currentTarget as HTMLInputElement).value.trim() || null)}
						/>
					{:else}
						<span class="truncate"
							>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</span
						>
					{/if}
					{#if editable}
						<button
							type="button"
							class="text-muted-foreground hover:text-foreground"
							onclick={() => remove(key)}
							aria-label={$i18n.t('Remove')}
						>
							<X class="size-3.5" />
						</button>
					{/if}
				</div>
			{/each}
		</div>

		{#if editable}
			<div class="mt-1">
				{#if addingKey}
					<input
						class="h-7 w-48 rounded-md border bg-transparent px-2 text-xs outline-none focus:border-ring"
						placeholder={$i18n.t('Property name')}
						bind:value={newKey}
						autofocus
						onkeydown={(e) => {
							if (e.key === 'Enter') {
								const key = newKey.trim().replace(/[^\p{L}\p{N}_-]+/gu, '_');
								if (
									key &&
									!(key in values) &&
									!['type', 'tags', 'aliases', 'title'].includes(key)
								) {
									values = { ...values, [key]: '' };
								}
								newKey = '';
								addingKey = false;
							} else if (e.key === 'Escape') {
								addingKey = false;
							}
						}}
						onblur={() => (addingKey = false)}
					/>
				{:else}
					<button
						type="button"
						class="inline-flex h-7 items-center gap-1 rounded-md px-1.5 text-xs text-muted-foreground hover:bg-accent hover:text-accent-foreground"
						onclick={() => (addingKey = true)}
					>
						<Plus class="size-3.5" />{$i18n.t('Add property')}
					</button>
				{/if}
			</div>
		{/if}
	{/if}
</section>
