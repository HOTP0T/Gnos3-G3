<!--
	The vault's note types (Person, Project, Meeting…): name, icon, colour and fields. A field of kind
	"note" / "notes" is a relation to other notes: it appears in the graph and in backlinks.
-->
<script lang="ts">
	import { getContext } from 'svelte';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Plus from '@lucide/svelte/icons/plus';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import type { FieldKind, NoteType, TypeField } from '$lib/apis/note-vaults';
	import TypeIcon, { TYPE_COLORS, TYPE_ICONS } from '../TypeIcon.svelte';
	import { chartColor, typeName } from '../vault';
	import { ENTITY_META, ENTITY_TYPES } from '../entities';

	const i18n: any = getContext('i18n');

	let { types = $bindable([]), editable = true }: { types: NoteType[]; editable?: boolean } =
		$props();

	let openKey: string | null = $state(null);

	const KINDS: { kind: FieldKind; label: string }[] = [
		{ kind: 'text', label: 'Text' },
		{ kind: 'number', label: 'Number' },
		{ kind: 'date', label: 'Date' },
		{ kind: 'checkbox', label: 'Checkbox' },
		{ kind: 'select', label: 'Choice' },
		{ kind: 'multiselect', label: 'Several choices' },
		{ kind: 'url', label: 'Web address' },
		{ kind: 'note', label: 'Link to a note' },
		{ kind: 'notes', label: 'Links to notes' },
		{ kind: 'entity', label: 'Link to Gnos3 data' }
	];

	const uniqueKey = (base: string, taken: string[]) => {
		let key = base;
		let n = 2;
		while (taken.includes(key)) key = `${base}_${n++}`;
		return key;
	};

	const addType = () => {
		const key = uniqueKey(
			'type',
			types.map((t) => t.key)
		);
		types = [
			...types,
			{
				key,
				name: $i18n.t('New type'),
				icon: 'bookmark',
				color: TYPE_COLORS[types.length % TYPE_COLORS.length],
				builtin: false,
				fields: []
			}
		];
		openKey = key;
	};

	/** A built-in type shows its words in the UI language; once its words are edited it keeps
	 * them as written, so freeze all of them in the current language first. */
	const materialize = (t: NoteType): NoteType =>
		t.builtin
			? {
					...t,
					builtin: false,
					name: $i18n.t(t.name),
					fields: t.fields.map((f) => ({
						...f,
						label: $i18n.t(f.label),
						...(f.options ? { options: f.options.map((o) => $i18n.t(o)) } : {})
					}))
				}
			: t;

	/** Text edits (name, field labels, choices) turn a built-in type into the vault's own. */
	const editText = (index: number, change: (t: NoteType) => NoteType) => {
		types = types.map((t, i) => (i === index ? change(materialize(t)) : t));
	};

	const update = (index: number, patch: Partial<NoteType>) => {
		types = types.map((t, i) => (i === index ? { ...t, ...patch } : t));
	};

	const updateField = (ti: number, fi: number, patch: Partial<TypeField>) => {
		const change = (t: NoteType) => ({
			...t,
			fields: t.fields.map((f, i) => (i === fi ? { ...f, ...patch } : f))
		});
		if ('label' in patch || 'options' in patch) editText(ti, change);
		else types = types.map((t, i) => (i === ti ? change(t) : t));
	};

	const addField = (ti: number) => {
		const key = uniqueKey(
			'field',
			types[ti].fields.map((f) => f.key)
		);
		editText(ti, (t) => ({
			...t,
			fields: [...t.fields, { key, label: $i18n.t('New field'), kind: 'text' }]
		}));
	};
</script>

<div class="space-y-2">
	{#each types as type, ti (type.key)}
		{@const open = openKey === type.key}
		<div class="rounded-lg border">
			<button
				type="button"
				class="flex w-full items-center gap-2 px-3 py-2 text-left"
				onclick={() => (openKey = open ? null : type.key)}
			>
				<ChevronRight
					class="size-4 text-muted-foreground transition-transform {open ? 'rotate-90' : ''}"
				/>
				<TypeIcon icon={type.icon} class="size-4" style="color: {chartColor(type.color)}" />
				<span class="flex-1 text-sm font-medium">{typeName(type, $i18n)}</span>
				<span class="text-xs text-muted-foreground"
					>{$i18n.t('{{n}} fields', { n: type.fields.length })}</span
				>
			</button>
			{#if open}
				<div class="space-y-3 border-t px-3 py-3">
					<div class="grid gap-3 sm:grid-cols-[1fr_auto]">
						<label class="space-y-1">
							<span class="text-xs text-muted-foreground">{$i18n.t('Name')}</span>
							<Input
								value={typeName(type, $i18n)}
								disabled={!editable}
								onchange={(e) => {
									const name = (e.currentTarget as HTMLInputElement).value.trim();
									if (name) editText(ti, (t) => ({ ...t, name }));
								}}
							/>
						</label>
						<div class="space-y-1">
							<span class="text-xs text-muted-foreground">{$i18n.t('Colour')}</span>
							<div class="flex h-9 items-center gap-1">
								{#each TYPE_COLORS as color}
									<button
										type="button"
										disabled={!editable}
										class="size-6 rounded-full border-2 {type.color === color
											? 'border-foreground'
											: 'border-transparent'}"
										style="background: {chartColor(color)}"
										aria-label={color}
										onclick={() => (types = types.map((t, i) => (i === ti ? { ...t, color } : t)))}
									></button>
								{/each}
							</div>
						</div>
					</div>
					<div class="space-y-1">
						<span class="text-xs text-muted-foreground">{$i18n.t('Icon')}</span>
						<div class="flex flex-wrap gap-1">
							{#each Object.keys(TYPE_ICONS) as icon}
								<button
									type="button"
									disabled={!editable}
									class="inline-flex size-8 items-center justify-center rounded-md border {type.icon ===
									icon
										? 'border-primary bg-primary/10'
										: 'border-transparent hover:bg-accent'}"
									onclick={() => (types = types.map((t, i) => (i === ti ? { ...t, icon } : t)))}
									aria-label={icon}
								>
									<TypeIcon {icon} class="size-4" />
								</button>
							{/each}
						</div>
					</div>

					<div class="space-y-2">
						<div class="text-xs text-muted-foreground">{$i18n.t('Fields')}</div>
						{#each type.fields as field, fi (field.key)}
							<div class="space-y-2 rounded-md bg-muted/40 p-2">
								<div class="flex flex-wrap items-center gap-2">
									<Input
										class="h-8 min-w-36 flex-1"
										value={type.builtin ? $i18n.t(field.label) : field.label}
										disabled={!editable}
										onchange={(e) => {
											const label = (e.currentTarget as HTMLInputElement).value.trim();
											// The key stays: notes already hold values under it.
											if (label) updateField(ti, fi, { label });
										}}
										aria-label={$i18n.t('Field name')}
									/>
									<NativeSelect.Root
										size="sm"
										class="w-44"
										value={field.kind}
										disabled={!editable}
										onchange={(e) =>
											updateField(ti, fi, {
												kind: (e.currentTarget as HTMLSelectElement).value as FieldKind
											})}
									>
										{#each KINDS as k}<NativeSelect.Option value={k.kind}
												>{$i18n.t(k.label)}</NativeSelect.Option
											>{/each}
									</NativeSelect.Root>
									{#if editable}
										<Button
											variant="ghost"
											size="icon-sm"
											onclick={() => update(ti, { fields: type.fields.filter((_, i) => i !== fi) })}
											aria-label={$i18n.t('Remove field')}><Trash2 /></Button
										>
									{/if}
								</div>
								{#if field.kind === 'select' || field.kind === 'multiselect'}
									<Input
										class="h-8"
										disabled={!editable}
										value={(field.options ?? [])
											.map((o) => (type.builtin ? $i18n.t(o) : o))
											.join(', ')}
										placeholder={$i18n.t('Choices, separated by commas')}
										onchange={(e) =>
											updateField(ti, fi, {
												options: (e.currentTarget as HTMLInputElement).value
													.split(',')
													.map((o) => o.trim())
													.filter(Boolean)
											})}
									/>
								{:else if field.kind === 'note' || field.kind === 'notes'}
									<NativeSelect.Root
										size="sm"
										class="w-full"
										value={field.note_type ?? ''}
										disabled={!editable}
										onchange={(e) =>
											updateField(ti, fi, {
												note_type: (e.currentTarget as HTMLSelectElement).value || undefined
											})}
									>
										<NativeSelect.Option value="">{$i18n.t('Any note')}</NativeSelect.Option>
										{#each types as t}<NativeSelect.Option value={t.key}
												>{$i18n.t('Suggest notes of type {{type}}', {
													type: typeName(t, $i18n)
												})}</NativeSelect.Option
											>{/each}
									</NativeSelect.Root>
								{:else if field.kind === 'entity'}
									<NativeSelect.Root
										size="sm"
										class="w-full"
										value={field.entity_type ?? ''}
										disabled={!editable}
										onchange={(e) =>
											updateField(ti, fi, {
												entity_type: (e.currentTarget as HTMLSelectElement).value || undefined
											})}
									>
										<NativeSelect.Option value="">{$i18n.t('Any Gnos3 data')}</NativeSelect.Option>
										{#each ENTITY_TYPES as et}<NativeSelect.Option value={et}
												>{$i18n.t(ENTITY_META[et].label)}</NativeSelect.Option
											>{/each}
									</NativeSelect.Root>
								{/if}
							</div>
						{/each}
						{#if editable}
							<Button variant="outline" size="sm" onclick={() => addField(ti)}
								><Plus />{$i18n.t('Add field')}</Button
							>
						{/if}
					</div>
					{#if editable}
						<div class="flex justify-end border-t pt-3">
							<Button
								variant="ghost"
								size="sm"
								class="text-destructive"
								onclick={() => {
									types = types.filter((_, i) => i !== ti);
									openKey = null;
								}}
							>
								<Trash2 />{$i18n.t('Remove this type')}
							</Button>
						</div>
					{/if}
				</div>
			{/if}
		</div>
	{/each}
	{#if editable}
		<Button variant="outline" size="sm" onclick={addType}><Plus />{$i18n.t('Add a type')}</Button>
	{/if}
	<p class="text-xs text-muted-foreground">
		{$i18n.t(
			'Removing a type or a field keeps what notes already hold; it is shown under other properties.'
		)}
	</p>
</div>
