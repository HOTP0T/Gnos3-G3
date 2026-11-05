<!--
	The vault's folders and notes. Drag a note or a folder onto a folder (or the vault's name) to
	move it; double-click a name to rename it; the ⋯ menu has the rest.
-->
<script lang="ts">
	import { getContext, tick } from 'svelte';
	import { toast } from 'svelte-sonner';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Folder from '@lucide/svelte/icons/folder';
	import FolderOpen from '@lucide/svelte/icons/folder-open';
	import FileText from '@lucide/svelte/icons/file-text';
	import Ellipsis from '@lucide/svelte/icons/ellipsis';
	import Pin from '@lucide/svelte/icons/pin';
	import FilePlus from '@lucide/svelte/icons/file-plus';
	import FolderPlus from '@lucide/svelte/icons/folder-plus';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { deleteNoteById } from '$lib/apis/notes';
	import {
		createFolder,
		deleteFolder,
		moveNote,
		renameFolder,
		updateNoteMeta,
		type TreeNote
	} from '$lib/apis/note-vaults';
	import TypeIcon from '../TypeIcon.svelte';
	import {
		canWrite,
		chartColor,
		cleanTitle,
		currentVault,
		folderName,
		joinFolder,
		parentFolder,
		patchTreeNote,
		prefs,
		refreshTree,
		tree,
		typeOf
	} from '../vault';

	const i18n: any = getContext('i18n');

	let {
		activeNoteId = null,
		sort = 'name',
		onOpenNote,
		onNewNote,
		onDeleted
	}: {
		activeNoteId?: string | null;
		sort?: 'name' | 'updated' | 'created';
		onOpenNote: (id: string) => void;
		onNewNote: (folder: string) => void;
		onDeleted: (id: string) => void;
	} = $props();

	const vaultId = $derived($currentVault?.id ?? '');
	const writable = $derived(canWrite($currentVault));

	let expanded: Set<string> = $state(new Set());
	let loadedFor = '';
	$effect(() => {
		if (vaultId && vaultId !== loadedFor) {
			loadedFor = vaultId;
			expanded = new Set(prefs.get<string[]>(`expanded.${vaultId}`, []));
		}
	});
	const saveExpanded = () => prefs.set(`expanded.${vaultId}`, [...expanded]);

	// Opening a note reveals its folder.
	$effect(() => {
		const id = activeNoteId;
		const note = id ? $tree?.notes.find((n) => n.id === id) : null;
		if (note?.folder) {
			const parts = note.folder.split('/');
			let changed = false;
			const next = new Set(expanded);
			for (let i = 1; i <= parts.length; i++) {
				const p = parts.slice(0, i).join('/');
				if (!next.has(p)) {
					next.add(p);
					changed = true;
				}
			}
			if (changed) {
				expanded = next;
				saveExpanded();
			}
		}
	});

	type Row =
		| { kind: 'folder'; path: string; depth: number; count: number }
		| { kind: 'note'; note: TreeNote; depth: number };

	const rows: Row[] = $derived.by(() => {
		const t = $tree;
		if (!t) return [];
		const byFolder = new Map<string, TreeNote[]>();
		for (const n of t.notes) {
			const list = byFolder.get(n.folder) ?? [];
			list.push(n);
			byFolder.set(n.folder, list);
		}
		const childFolders = new Map<string, string[]>();
		for (const f of t.folders) {
			const parent = parentFolder(f);
			const list = childFolders.get(parent) ?? [];
			list.push(f);
			childFolders.set(parent, list);
		}
		const countIn = (path: string): number =>
			(byFolder.get(path)?.length ?? 0) +
			(childFolders.get(path) ?? []).reduce((s, c) => s + countIn(c), 0);
		const sortNotes = (list: TreeNote[]) =>
			[...list].sort((a, b) =>
				sort === 'updated'
					? b.updated_at - a.updated_at
					: sort === 'created'
						? b.created_at - a.created_at
						: (a.title || '').localeCompare(b.title || '', undefined, {
								numeric: true,
								sensitivity: 'base'
							})
			);
		const out: Row[] = [];
		const walk = (path: string, depth: number) => {
			for (const f of (childFolders.get(path) ?? []).sort((a, b) =>
				folderName(a).localeCompare(folderName(b), undefined, {
					numeric: true,
					sensitivity: 'base'
				})
			)) {
				out.push({ kind: 'folder', path: f, depth, count: countIn(f) });
				if (expanded.has(f)) walk(f, depth + 1);
			}
			for (const n of sortNotes(byFolder.get(path) ?? []))
				out.push({ kind: 'note', note: n, depth });
		};
		walk('', 0);
		return out;
	});

	const toggle = (path: string) => {
		const next = new Set(expanded);
		if (next.has(path)) next.delete(path);
		else next.add(path);
		expanded = next;
		saveExpanded();
	};

	export const collapseAll = () => {
		expanded = new Set();
		saveExpanded();
	};

	// --- rename -----------------------------------------------------------------

	let renaming: string | null = $state(null); // 'note:<id>' | 'folder:<path>'
	let renameValue = $state('');

	const startRename = async (key: string, value: string) => {
		if (!writable) return;
		renaming = key;
		renameValue = value;
		await tick();
		const input = document.getElementById('tree-rename-input') as HTMLInputElement | null;
		input?.focus();
		input?.select();
	};

	const commitRename = async () => {
		const key = renaming;
		renaming = null;
		if (!key) return;
		const value = renameValue.trim();
		if (key.startsWith('note:')) {
			const id = key.slice(5);
			const title = cleanTitle(value);
			const note = $tree?.notes.find((n) => n.id === id);
			if (!title || title === note?.title) return;
			try {
				const res = await updateNoteMeta(localStorage.token, id, { title });
				patchTreeNote(id, { title: res.title });
			} catch (e) {
				toast.error(`${e}`);
			}
		} else {
			const path = key.slice(7);
			const name = value.replace(/\//g, ' ').trim();
			if (!name || name === folderName(path)) return;
			try {
				await renameFolder(localStorage.token, vaultId, path, joinFolder(parentFolder(path), name));
				await refreshTree(localStorage.token);
			} catch (e) {
				toast.error(`${e}`);
			}
		}
	};

	// --- folders ----------------------------------------------------------------

	let newFolderParent: string | null = $state(null);
	let newFolderName = $state('');

	export const startNewFolder = async (parent = '') => {
		if (!writable) return;
		newFolderParent = parent;
		newFolderName = '';
		if (parent) {
			expanded = new Set([...expanded, parent]);
		}
		await tick();
		(document.getElementById('tree-new-folder-input') as HTMLInputElement | null)?.focus();
	};

	const commitNewFolder = async () => {
		const parent = newFolderParent;
		newFolderParent = null;
		const name = newFolderName.replace(/\//g, ' ').trim();
		if (parent === null || !name) return;
		try {
			const res = await createFolder(localStorage.token, vaultId, joinFolder(parent, name));
			expanded = new Set([...expanded, res.path]);
			saveExpanded();
			await refreshTree(localStorage.token);
		} catch (e) {
			toast.error(`${e}`);
		}
	};

	let folderToDelete: string | null = $state(null);
	let noteToDelete: TreeNote | null = $state(null);

	const removeFolder = async (mode: 'move_up' | 'delete') => {
		const path = folderToDelete;
		folderToDelete = null;
		if (!path) return;
		try {
			await deleteFolder(localStorage.token, vaultId, path, mode);
			await refreshTree(localStorage.token);
		} catch (e) {
			toast.error(`${e}`);
		}
	};

	const removeNote = async () => {
		const note = noteToDelete;
		noteToDelete = null;
		if (!note) return;
		const ok = await deleteNoteById(localStorage.token, note.id).catch((e) => {
			toast.error(`${e}`);
			return null;
		});
		if (ok) {
			await refreshTree(localStorage.token);
			onDeleted(note.id);
		}
	};

	// --- drag and drop ------------------------------------------------------------

	let dragItem: { kind: 'note' | 'folder'; id: string } | null = null;
	let dropTarget: string | null = $state(null); // folder path, '' = root

	const onDragStart = (e: DragEvent, kind: 'note' | 'folder', id: string) => {
		if (!writable) return;
		dragItem = { kind, id };
		e.dataTransfer?.setData('text/plain', id);
		if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move';
	};

	const canDrop = (path: string) => {
		if (!dragItem) return false;
		if (dragItem.kind === 'folder')
			return (
				path !== dragItem.id &&
				!path.startsWith(dragItem.id + '/') &&
				parentFolder(dragItem.id) !== path
			);
		const note = $tree?.notes.find((n) => n.id === dragItem!.id);
		return !!note && note.folder !== path;
	};

	const onDrop = async (path: string) => {
		const item = dragItem;
		const ok = canDrop(path);
		dragItem = null;
		dropTarget = null;
		if (!item || !ok) return;
		try {
			if (item.kind === 'note') {
				patchTreeNote(item.id, { folder: path });
				await moveNote(localStorage.token, item.id, vaultId, path);
			} else {
				await renameFolder(
					localStorage.token,
					vaultId,
					item.id,
					joinFolder(path, folderName(item.id))
				);
				if (path) expanded = new Set([...expanded, path]);
			}
		} catch (e) {
			toast.error(`${e}`);
		}
		await refreshTree(localStorage.token);
	};

	export const dropOnRoot = {
		over: (e: DragEvent) => {
			if (canDrop('')) {
				e.preventDefault();
				dropTarget = '';
			}
		},
		drop: (e: DragEvent) => {
			e.preventDefault();
			onDrop('');
		}
	};
</script>

<Dialog.Root open={folderToDelete !== null} onOpenChange={(o) => !o && (folderToDelete = null)}>
	<Dialog.Content class="sm:max-w-md">
		<Dialog.Header>
			<Dialog.Title
				>{$i18n.t('Delete the folder “{{name}}”?', {
					name: folderName(folderToDelete ?? '')
				})}</Dialog.Title
			>
			<Dialog.Description>
				{$i18n.t('Its notes can move up one level, or be deleted with it.')}
			</Dialog.Description>
		</Dialog.Header>
		<Dialog.Footer class="gap-2">
			<Button variant="outline" onclick={() => (folderToDelete = null)}>{$i18n.t('Cancel')}</Button>
			<Button variant="outline" onclick={() => removeFolder('move_up')}
				>{$i18n.t('Keep the notes')}</Button
			>
			<Button variant="destructive" onclick={() => removeFolder('delete')}
				>{$i18n.t('Delete the notes too')}</Button
			>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<Dialog.Root open={noteToDelete !== null} onOpenChange={(o) => !o && (noteToDelete = null)}>
	<Dialog.Content class="sm:max-w-md">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Delete this note?')}</Dialog.Title>
			<Dialog.Description>
				{$i18n.t('“{{title}}” will be deleted. Links to it will show it as not created.', {
					title: noteToDelete?.title ?? ''
				})}
			</Dialog.Description>
		</Dialog.Header>
		<Dialog.Footer>
			<Button variant="outline" onclick={() => (noteToDelete = null)}>{$i18n.t('Cancel')}</Button>
			<Button variant="destructive" onclick={removeNote}>{$i18n.t('Delete note')}</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

{#snippet newFolderRow(depth: number)}
	<div class="flex h-7 items-center gap-1.5 pr-2" style="padding-left: {0.5 + depth * 0.85}rem">
		<span class="w-3.5"></span>
		<Folder class="size-4 shrink-0 text-muted-foreground" />
		<input
			id="tree-new-folder-input"
			class="h-6 min-w-0 flex-1 rounded border border-ring bg-background px-1 text-sm outline-none"
			placeholder={$i18n.t('Folder name')}
			bind:value={newFolderName}
			onkeydown={(e) => {
				if (e.key === 'Enter') commitNewFolder();
				if (e.key === 'Escape') newFolderParent = null;
			}}
			onblur={commitNewFolder}
		/>
	</div>
{/snippet}

<div class="pb-6 text-sm" role="tree" aria-label={$i18n.t('Files')}>
	{#if newFolderParent === ''}
		{@render newFolderRow(0)}
	{/if}
	{#each rows as row (row.kind === 'folder' ? `f:${row.path}` : `n:${row.note.id}`)}
		{#if row.kind === 'folder'}
			{@const open = expanded.has(row.path)}
			<div
				role="treeitem"
				aria-expanded={open}
				aria-selected="false"
				tabindex="-1"
				class="group flex h-7 cursor-pointer items-center gap-1.5 rounded-md pr-1 select-none hover:bg-sidebar-accent {dropTarget ===
				row.path
					? 'bg-primary/10 ring-1 ring-primary/40'
					: ''}"
				style="padding-left: {0.5 + row.depth * 0.85}rem"
				draggable={writable}
				ondragstart={(e) => onDragStart(e, 'folder', row.path)}
				ondragover={(e) => {
					if (canDrop(row.path)) {
						e.preventDefault();
						dropTarget = row.path;
					}
				}}
				ondragleave={() => dropTarget === row.path && (dropTarget = null)}
				ondrop={(e) => {
					e.preventDefault();
					onDrop(row.path);
				}}
				onclick={() => toggle(row.path)}
				ondblclick={() => startRename(`folder:${row.path}`, folderName(row.path))}
				onkeydown={(e) => e.key === 'Enter' && toggle(row.path)}
			>
				<ChevronRight
					class="size-3.5 shrink-0 text-muted-foreground transition-transform {open
						? 'rotate-90'
						: ''}"
				/>
				{#if open}<FolderOpen class="size-4 shrink-0 text-muted-foreground" />{:else}<Folder
						class="size-4 shrink-0 text-muted-foreground"
					/>{/if}
				{#if renaming === `folder:${row.path}`}
					<input
						id="tree-rename-input"
						class="h-6 min-w-0 flex-1 rounded border border-ring bg-background px-1 text-sm outline-none"
						bind:value={renameValue}
						onclick={(e) => e.stopPropagation()}
						onkeydown={(e) => {
							e.stopPropagation();
							if (e.key === 'Enter') commitRename();
							if (e.key === 'Escape') renaming = null;
						}}
						onblur={commitRename}
					/>
				{:else}
					<span class="min-w-0 flex-1 truncate">{folderName(row.path)}</span>
					<span class="text-xs text-muted-foreground tabular-nums group-hover:hidden"
						>{row.count || ''}</span
					>
				{/if}
				{#if writable && renaming !== `folder:${row.path}`}
					<DropdownMenu.Root>
						<DropdownMenu.Trigger>
							{#snippet child({ props })}
								<button
									{...props}
									type="button"
									class="hidden size-6 items-center justify-center rounded text-muted-foreground group-hover:inline-flex hover:bg-background data-[state=open]:inline-flex"
									aria-label={$i18n.t('Folder actions')}
									onclick={(e) => e.stopPropagation()}
								>
									<Ellipsis class="size-4" />
								</button>
							{/snippet}
						</DropdownMenu.Trigger>
						<DropdownMenu.Content align="start" class="w-48">
							<DropdownMenu.Item onSelect={() => onNewNote(row.path)}
								><FilePlus />{$i18n.t('New note here')}</DropdownMenu.Item
							>
							<DropdownMenu.Item onSelect={() => startNewFolder(row.path)}
								><FolderPlus />{$i18n.t('New folder inside')}</DropdownMenu.Item
							>
							<DropdownMenu.Item
								onSelect={() => startRename(`folder:${row.path}`, folderName(row.path))}
								><Pencil />{$i18n.t('Rename')}</DropdownMenu.Item
							>
							<DropdownMenu.Separator />
							<DropdownMenu.Item variant="destructive" onSelect={() => (folderToDelete = row.path)}
								><Trash2 />{$i18n.t('Delete')}</DropdownMenu.Item
							>
						</DropdownMenu.Content>
					</DropdownMenu.Root>
				{/if}
			</div>
			{#if newFolderParent === row.path && open}
				{@render newFolderRow(row.depth + 1)}
			{/if}
		{:else}
			{@const t = typeOf($currentVault, row.note.type)}
			{@const active = row.note.id === activeNoteId}
			<div
				role="treeitem"
				aria-selected={active}
				tabindex="-1"
				class="group flex h-7 cursor-pointer items-center gap-1.5 rounded-md pr-1 select-none {active
					? 'bg-sidebar-accent font-medium text-sidebar-accent-foreground'
					: 'hover:bg-sidebar-accent/70'}"
				style="padding-left: {0.5 + row.depth * 0.85}rem"
				draggable={writable}
				ondragstart={(e) => onDragStart(e, 'note', row.note.id)}
				onclick={(e) =>
					e.metaKey || e.ctrlKey
						? window.open(`/notes/${row.note.id}`, '_blank')
						: onOpenNote(row.note.id)}
				ondblclick={() => startRename(`note:${row.note.id}`, row.note.title)}
				onkeydown={(e) => e.key === 'Enter' && onOpenNote(row.note.id)}
				title={row.note.excerpt || row.note.title}
			>
				<span class="w-3.5 shrink-0"></span>
				{#if t}
					<TypeIcon icon={t.icon} class="size-4 shrink-0" style="color: {chartColor(t.color)}" />
				{:else}
					<FileText class="size-4 shrink-0 text-muted-foreground" />
				{/if}
				{#if renaming === `note:${row.note.id}`}
					<input
						id="tree-rename-input"
						class="h-6 min-w-0 flex-1 rounded border border-ring bg-background px-1 text-sm outline-none"
						bind:value={renameValue}
						onclick={(e) => e.stopPropagation()}
						onkeydown={(e) => {
							e.stopPropagation();
							if (e.key === 'Enter') commitRename();
							if (e.key === 'Escape') renaming = null;
						}}
						onblur={commitRename}
					/>
				{:else}
					<span class="min-w-0 flex-1 truncate">{row.note.title || $i18n.t('Untitled')}</span>
					{#if row.note.is_pinned}<Pin class="size-3 shrink-0 text-muted-foreground" />{/if}
				{/if}
				{#if writable && renaming !== `note:${row.note.id}`}
					<DropdownMenu.Root>
						<DropdownMenu.Trigger>
							{#snippet child({ props })}
								<button
									{...props}
									type="button"
									class="hidden size-6 items-center justify-center rounded text-muted-foreground group-hover:inline-flex hover:bg-background data-[state=open]:inline-flex"
									aria-label={$i18n.t('Note actions')}
									onclick={(e) => e.stopPropagation()}
								>
									<Ellipsis class="size-4" />
								</button>
							{/snippet}
						</DropdownMenu.Trigger>
						<DropdownMenu.Content align="start" class="w-44">
							<DropdownMenu.Item onSelect={() => window.open(`/notes/${row.note.id}`, '_blank')}
								>{$i18n.t('Open in new tab')}</DropdownMenu.Item
							>
							<DropdownMenu.Item onSelect={() => startRename(`note:${row.note.id}`, row.note.title)}
								><Pencil />{$i18n.t('Rename')}</DropdownMenu.Item
							>
							<DropdownMenu.Separator />
							<DropdownMenu.Item variant="destructive" onSelect={() => (noteToDelete = row.note)}
								><Trash2 />{$i18n.t('Delete')}</DropdownMenu.Item
							>
						</DropdownMenu.Content>
					</DropdownMenu.Root>
				{/if}
			</div>
		{/if}
	{/each}
	{#if $tree && !rows.length && newFolderParent === null}
		<p class="px-3 py-4 text-sm text-muted-foreground">
			{$i18n.t('No notes yet. Create one with +.')}
		</p>
	{/if}
</div>
