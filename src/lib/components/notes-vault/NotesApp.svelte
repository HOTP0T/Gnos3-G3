<!--
	Notes: vaults of linked notes (folders, [[links]], backlinks, graph, properties, daily notes,
	templates, links to Gnos3 data). Mounted by routes/(app)/notes/+layout.svelte so the sidebar stays
	while notes change; the route says what the main area shows (home, a note, the graph).

	Shortcuts: Ctrl/⌘ O go to a note · Ctrl/⌘ Shift F search · Ctrl/⌘ Shift G graph · Alt N new note.
-->
<script lang="ts">
	import { getContext, onDestroy, onMount, untrack } from 'svelte';
	import { get } from 'svelte/store';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import ChevronsUpDown from '@lucide/svelte/icons/chevrons-up-down';
	import Check from '@lucide/svelte/icons/check';
	import Lock from '@lucide/svelte/icons/lock';
	import Users from '@lucide/svelte/icons/users';
	import Plus from '@lucide/svelte/icons/plus';
	import Settings2 from '@lucide/svelte/icons/settings-2';
	import FilePlus from '@lucide/svelte/icons/file-plus';
	import FolderPlus from '@lucide/svelte/icons/folder-plus';
	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import Orbit from '@lucide/svelte/icons/orbit';
	import Search from '@lucide/svelte/icons/search';
	import Files from '@lucide/svelte/icons/files';
	import Hash from '@lucide/svelte/icons/hash';
	import ArrowDownUp from '@lucide/svelte/icons/arrow-down-up';
	import ChevronsDownUp from '@lucide/svelte/icons/chevrons-down-up';
	import PanelLeft from '@lucide/svelte/icons/panel-left';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Share2 from '@lucide/svelte/icons/share-2';
	import FileText from '@lucide/svelte/icons/file-text';
	import NotebookPen from '@lucide/svelte/icons/notebook-pen';

	import { Button } from '$lib/components/ui/button/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as Popover from '$lib/components/ui/popover/index.js';
	import * as Tooltip from '$lib/components/ui/tooltip/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';

	import { isAdmin, mobile, showSidebar } from '$lib/stores';
	import { ensureModulesLoaded } from '$lib/stores/modules';
	import { getNoteById } from '$lib/apis/notes';
	import { createVaultNote, getNotePlace, getSharedWithMe } from '$lib/apis/note-vaults';
	import dayjs from '$lib/dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';

	import {
		canWrite,
		cleanTitle,
		currentVault,
		currentVaultId,
		loadTree,
		loadVaults,
		normalizeTitle,
		prefs,
		refreshTree,
		tree,
		treeError,
		treeVaultId,
		vaultName,
		vaults
	} from './vault';
	import { applyTemplate, stripFrontmatter } from './markdown';
	import FileTree from './sidebar/FileTree.svelte';
	import SearchPane from './sidebar/SearchPane.svelte';
	import TagsPane from './sidebar/TagsPane.svelte';
	import DailyCalendar from './sidebar/DailyCalendar.svelte';
	import VaultNoteEditor from './VaultNoteEditor.svelte';
	import GraphView from './graph/GraphView.svelte';
	import QuickSwitcher from './QuickSwitcher.svelte';
	import Home from './Home.svelte';
	import VaultSettingsDialog from './dialogs/VaultSettingsDialog.svelte';
	import NewVaultDialog from './dialogs/NewVaultDialog.svelte';

	dayjs.extend(relativeTime);

	const i18n: any = getContext('i18n');

	let {
		noteId = null,
		view = 'home'
	}: { noteId?: string | null; view?: 'home' | 'note' | 'graph' } = $props();

	let ready = $state(false);
	let sidebarTab: 'files' | 'search' | 'tags' = $state(prefs.get('sidebar.tab', 'files'));
	// On a phone the sidebar covers the note: closed while a note is open, opened by its button.
	let sidebarOpen = $state(get(mobile) ? !noteId : prefs.get('sidebar.open', true));
	let sidebarWidth = $state(prefs.get('sidebar.width', 272));
	let sort: 'name' | 'updated' | 'created' = $state(prefs.get('sidebar.sort', 'name'));
	let searchQuery = $state('');
	let selectedTag: string | null = $state(null);
	let showSwitcher = $state(false);
	let showSettings = $state(false);
	let settingsTab = $state('general');
	let showNewVault = $state(false);
	let showCalendar = $state(false);
	let sharedNotes: { id: string; title: string; updated_at: number }[] = $state([]);
	let sharedOpen = $state(prefs.get('sidebar.sharedOpen', true));
	let fileTree: any = $state(null);

	// --- dates in the UI language --------------------------------------------------
	$effect(() => {
		const langs: string[] = $i18n.languages ?? [];
		for (const lang of langs) {
			try {
				dayjs.locale(lang.toLowerCase());
				break;
			} catch {
				// try the next one
			}
		}
	});

	// --- loading --------------------------------------------------------------------

	onMount(async () => {
		ensureModulesLoaded().catch(() => {});
		try {
			await loadVaults(localStorage.token);
		} catch (e) {
			toast.error(`${e}`);
		}
		getSharedWithMe(localStorage.token)
			.then((list) => (sharedNotes = list))
			.catch(() => {});
		ready = true;
		window.addEventListener('keydown', onKeydown);
	});

	onDestroy(() => {
		window.removeEventListener('keydown', onKeydown);
	});

	// The open vault's tree.
	$effect(() => {
		const id = $currentVaultId;
		if (!id) return;
		untrack(() => {
			prefs.set('vault', id);
			if (get(treeVaultId) !== id) {
				tree.set(null);
				loadTree(localStorage.token, id);
			}
		});
	});

	// Opening a note from another vault switches to that vault.
	$effect(() => {
		const id = noteId;
		if (!id || !ready) return;
		untrack(async () => {
			const place = await getNotePlace(localStorage.token, id).catch(() => null);
			if (place?.vault_permission && place.vault_id !== get(currentVaultId)) {
				if (!(get(vaults) ?? []).some((v) => v.id === place.vault_id))
					await loadVaults(localStorage.token);
				currentVaultId.set(place.vault_id);
			}
		});
	});

	// --- navigation ---------------------------------------------------------------------

	const openNote = (id: string) => {
		goto(`/notes/${id}`);
		if ($mobile) sidebarOpen = false;
	};

	const createNote = async (
		title: string,
		opts: {
			folder?: string;
			type?: string | null;
			open?: boolean;
			md?: string;
			properties?: Record<string, unknown>;
			unique?: boolean;
		} = {}
	) => {
		const vault = get(currentVault);
		if (!vault || !canWrite(vault)) {
			toast.error($i18n.t('You can only read this vault.'));
			return null;
		}
		try {
			const res = await createVaultNote(localStorage.token, vault.id, {
				title: cleanTitle(title) || $i18n.t('Untitled'),
				folder: opts.folder ?? '',
				md: opts.md ?? '',
				properties: { ...(opts.properties ?? {}), ...(opts.type ? { type: opts.type } : {}) },
				unique: opts.unique ?? true
			});
			await refreshTree(localStorage.token);
			if (opts.open) openNote(res.id);
			return { id: res.id, title: res.title };
		} catch (e) {
			toast.error(`${e}`);
			return null;
		}
	};

	const currentFolder = () => {
		const id = noteId;
		return (id && get(tree)?.notes.find((n) => n.id === id)?.folder) || '';
	};

	const newNote = async (folder?: string) => {
		const created = await createNote($i18n.t('Untitled'), {
			folder: folder ?? currentFolder(),
			open: true
		});
		if (created) {
			setTimeout(() => {
				const input = document.getElementById('note-title-input') as HTMLTextAreaElement | null;
				input?.focus();
				input?.select();
			}, 400);
		}
	};

	const openDaily = async (date: Date = new Date()) => {
		const vault = get(currentVault);
		if (!vault) return;
		showCalendar = false;
		const daily = vault.settings.daily ?? {
			folder: 'Daily notes',
			format: 'YYYY-MM-DD',
			template_id: null
		};
		const title = dayjs(date).format(daily.format || 'YYYY-MM-DD');
		const existing = get(tree)?.notes.find(
			(n) =>
				normalizeTitle(n.title) === normalizeTitle(title) &&
				(n.folder === daily.folder || !daily.folder)
		);
		if (existing) {
			openNote(existing.id);
			return;
		}
		let md = '';
		let properties: Record<string, unknown> = {};
		if (daily.template_id) {
			const tpl = await getNoteById(localStorage.token, daily.template_id).catch(() => null);
			if (tpl) {
				md = applyTemplate(stripFrontmatter(tpl.data?.content?.md ?? ''), {
					title,
					now: date,
					dayjs
				});
				properties = tpl.data?.properties ?? {};
			}
		}
		await createNote(title, { folder: daily.folder, md, properties, open: true, unique: false });
	};

	const showTag = (tag: string) => {
		selectedTag = tag;
		setTab('tags');
		sidebarOpen = true;
	};

	const setTab = (tab: typeof sidebarTab) => {
		sidebarTab = tab;
		prefs.set('sidebar.tab', tab);
	};

	const toggleSidebar = () => {
		sidebarOpen = !sidebarOpen;
		if (!$mobile) prefs.set('sidebar.open', sidebarOpen);
	};

	const onKeydown = (e: KeyboardEvent) => {
		const mod = e.metaKey || e.ctrlKey;
		const key = e.key.toLowerCase();
		if (mod && !e.shiftKey && !e.altKey && key === 'o') {
			e.preventDefault();
			showSwitcher = true;
		} else if (mod && e.shiftKey && key === 'f') {
			e.preventDefault();
			sidebarOpen = true;
			setTab('search');
		} else if (mod && e.shiftKey && key === 'g') {
			e.preventDefault();
			goto('/notes/graph');
		} else if (e.altKey && !mod && (key === 'n' || e.code === 'KeyN')) {
			e.preventDefault();
			if (canWrite(get(currentVault))) newNote();
		}
	};

	const startResize = (event: PointerEvent) => {
		const startX = event.clientX;
		const start = sidebarWidth;
		const move = (e: PointerEvent) =>
			(sidebarWidth = Math.min(480, Math.max(220, start + e.clientX - startX)));
		const up = () => {
			window.removeEventListener('pointermove', move);
			window.removeEventListener('pointerup', up);
			prefs.set('sidebar.width', sidebarWidth);
		};
		window.addEventListener('pointermove', move);
		window.addEventListener('pointerup', up);
	};

	const SORTS = [
		{ key: 'name', label: 'Name' },
		{ key: 'updated', label: 'Last edited' },
		{ key: 'created', label: 'Created' }
	] as const;
</script>

<Tooltip.Provider delayDuration={300}>
	<div
		class="flex h-screen max-h-[100dvh] w-full max-w-full bg-background text-foreground transition-width duration-200 ease-in-out {$showSidebar
			? 'md:max-w-[calc(100%-var(--sidebar-width))]'
			: 'md:max-w-[calc(100%-49px)]'}"
	>
		<!-- Sidebar -->
		{#if sidebarOpen}
			{#if $mobile}
				<button
					type="button"
					class="fixed inset-0 z-30 bg-black/30"
					aria-label={$i18n.t('Close')}
					onclick={() => (sidebarOpen = false)}
				></button>
			{/if}
			<aside
				class="flex min-h-0 flex-col border-r bg-sidebar text-sidebar-foreground {$mobile
					? 'fixed inset-y-0 left-0 z-40 w-[min(85vw,20rem)] shadow-xl'
					: 'relative shrink-0'}"
				style={$mobile ? '' : `width: ${sidebarWidth}px`}
				aria-label={$i18n.t('Notes')}
			>
				<!-- Vault switcher -->
				<div class="flex h-12 shrink-0 items-center gap-1 px-2">
					{#if $mobile}
						<Button
							variant="ghost"
							size="icon-sm"
							onclick={() => showSidebar.set(!$showSidebar)}
							aria-label={$i18n.t('Open Sidebar')}><PanelLeft /></Button
						>
					{/if}
					<DropdownMenu.Root>
						<DropdownMenu.Trigger>
							{#snippet child({ props })}
								<button
									{...props}
									type="button"
									class="flex h-9 min-w-0 flex-1 items-center gap-2 rounded-md px-2 text-left hover:bg-sidebar-accent"
								>
									<span
										class="flex size-6 shrink-0 items-center justify-center rounded-md bg-primary/10 text-link"
									>
										{#if $currentVault?.kind === 'shared'}<Users
												class="size-3.5"
											/>{:else}<NotebookPen class="size-3.5" />{/if}
									</span>
									<span class="min-w-0 flex-1 truncate text-sm font-semibold"
										>{vaultName($currentVault, $i18n) || $i18n.t('Notes')}</span
									>
									<ChevronsUpDown class="size-4 shrink-0 text-muted-foreground" />
								</button>
							{/snippet}
						</DropdownMenu.Trigger>
						<DropdownMenu.Content align="start" class="w-64">
							<DropdownMenu.Label class="text-xs text-muted-foreground"
								>{$i18n.t('Vaults')}</DropdownMenu.Label
							>
							{#each $vaults ?? [] as v (v.id)}
								<DropdownMenu.Item
									onSelect={() => {
										currentVaultId.set(v.id);
										if (noteId || view === 'graph') goto('/notes');
									}}
								>
									{#if v.kind === 'shared'}<Users />{:else}<Lock />{/if}
									<span class="min-w-0 flex-1 truncate">{vaultName(v, $i18n)}</span>
									<span class="text-xs text-muted-foreground tabular-nums"
										>{v.note_count ?? ''}</span
									>
									{#if v.id === $currentVaultId}<Check class="text-link" />{/if}
								</DropdownMenu.Item>
							{/each}
							<DropdownMenu.Separator />
							{#if $currentVault}
								<DropdownMenu.Item
									onSelect={() => {
										settingsTab = 'general';
										showSettings = true;
									}}><Settings2 />{$i18n.t('Vault settings')}</DropdownMenu.Item
								>
							{/if}
							{#if $isAdmin}
								<DropdownMenu.Item onSelect={() => (showNewVault = true)}
									><Plus />{$i18n.t('New shared vault')}</DropdownMenu.Item
								>
							{/if}
						</DropdownMenu.Content>
					</DropdownMenu.Root>
					{#if !$mobile}
						<Tip content={$i18n.t('Hide')}>
							<Button
								variant="ghost"
								size="icon-sm"
								onclick={toggleSidebar}
								aria-label={$i18n.t('Hide')}><PanelLeft /></Button
							>
						</Tip>
					{/if}
				</div>

				<!-- Actions -->
				<div class="flex shrink-0 items-center gap-0.5 px-2 pb-2">
					{#if canWrite($currentVault)}
						<Tip content={`${$i18n.t('New note')} (Alt N)`}>
							<Button
								variant="ghost"
								size="icon-sm"
								onclick={() => newNote()}
								aria-label={$i18n.t('New note')}><FilePlus /></Button
							>
						</Tip>
						<Tip content={$i18n.t('New folder')}>
							<Button
								variant="ghost"
								size="icon-sm"
								onclick={() => {
									setTab('files');
									setTimeout(() => fileTree?.startNewFolder(''), 0);
								}}
								aria-label={$i18n.t('New folder')}><FolderPlus /></Button
							>
						</Tip>
						<Popover.Root bind:open={showCalendar}>
							<Popover.Trigger>
								{#snippet child({ props })}
									<Button
										{...props}
										variant="ghost"
										size="icon-sm"
										aria-label={$i18n.t('Daily notes')}><CalendarDays /></Button
									>
								{/snippet}
							</Popover.Trigger>
							<Popover.Content align="start" class="w-auto p-3">
								<DailyCalendar onPick={(d) => openDaily(d)} />
								<Button variant="outline" size="sm" class="mt-2 w-full" onclick={() => openDaily()}
									>{$i18n.t("Today's note")}</Button
								>
							</Popover.Content>
						</Popover.Root>
					{/if}
					<Tip content={`${$i18n.t('Graph view')} (Ctrl/⌘ Shift G)`}>
						<Button
							variant={view === 'graph' ? 'secondary' : 'ghost'}
							size="icon-sm"
							onclick={() => goto('/notes/graph')}
							aria-label={$i18n.t('Graph view')}><Orbit /></Button
						>
					</Tip>
					<div class="flex-1"></div>
					<Tip content={`${$i18n.t('Go to a note')} (Ctrl/⌘ O)`}>
						<button
							type="button"
							class="inline-flex h-8 items-center gap-1.5 rounded-md border bg-background px-2 text-xs whitespace-nowrap text-muted-foreground hover:text-foreground"
							onclick={() => (showSwitcher = true)}
						>
							<Search class="size-3.5" />{$i18n.t('Go to…')}
						</button>
					</Tip>
				</div>

				<!-- Tabs -->
				<div class="flex shrink-0 items-center gap-0.5 border-y px-2 py-1" role="tablist">
					{#each [{ key: 'files', label: 'Files', icon: Files }, { key: 'search', label: 'Search', icon: Search }, { key: 'tags', label: 'Tags', icon: Hash }] as tab (tab.key)}
						<button
							type="button"
							role="tab"
							aria-selected={sidebarTab === tab.key}
							class="inline-flex h-7 flex-1 items-center justify-center gap-1.5 rounded-md text-xs {sidebarTab ===
							tab.key
								? 'bg-background font-medium text-foreground shadow-xs'
								: 'text-muted-foreground hover:text-foreground'}"
							onclick={() => setTab(tab.key as typeof sidebarTab)}
						>
							<tab.icon class="size-3.5" />{$i18n.t(tab.label)}
						</button>
					{/each}
					{#if sidebarTab === 'files'}
						<DropdownMenu.Root>
							<DropdownMenu.Trigger>
								{#snippet child({ props })}
									<Button {...props} variant="ghost" size="icon-xs" aria-label={$i18n.t('Sort')}
										><ArrowDownUp /></Button
									>
								{/snippet}
							</DropdownMenu.Trigger>
							<DropdownMenu.Content align="end" class="w-44">
								<DropdownMenu.Label class="text-xs text-muted-foreground"
									>{$i18n.t('Sort notes by')}</DropdownMenu.Label
								>
								{#each SORTS as s (s.key)}
									<DropdownMenu.Item
										onSelect={() => {
											sort = s.key;
											prefs.set('sidebar.sort', sort);
										}}
									>
										<span class="flex-1">{$i18n.t(s.label)}</span>{#if sort === s.key}<Check
												class="text-link"
											/>{/if}
									</DropdownMenu.Item>
								{/each}
								<DropdownMenu.Separator />
								<DropdownMenu.Item onSelect={() => fileTree?.collapseAll()}
									><ChevronsDownUp />{$i18n.t('Collapse all')}</DropdownMenu.Item
								>
							</DropdownMenu.Content>
						</DropdownMenu.Root>
					{/if}
				</div>

				<!-- Pane -->
				<div class="min-h-0 flex-1 overflow-y-auto pt-2">
					{#if $treeError && !$tree}
						<p class="px-3 py-2 text-sm text-muted-foreground">
							{$i18n.t('The vault could not be loaded.')}
						</p>
					{:else if !$tree}
						<div class="space-y-1.5 px-3 py-1">
							{#each [70, 55, 80, 45, 65] as w}<div
									class="h-5 animate-pulse rounded bg-sidebar-accent"
									style="width: {w}%"
								></div>{/each}
						</div>
					{:else if sidebarTab === 'files'}
						<div
							class="min-h-full px-1"
							role="presentation"
							ondragover={(e) => fileTree?.dropOnRoot.over(e)}
							ondrop={(e) => fileTree?.dropOnRoot.drop(e)}
						>
							<FileTree
								bind:this={fileTree}
								activeNoteId={noteId}
								{sort}
								onOpenNote={openNote}
								onNewNote={(folder) => newNote(folder)}
								onDeleted={(id) => id === noteId && goto('/notes')}
							/>
							{#if sharedNotes.length}
								<div class="mt-2 border-t pt-2">
									<button
										type="button"
										class="flex w-full items-center gap-1 px-2 py-1 text-xs font-medium text-muted-foreground hover:text-foreground"
										onclick={() => {
											sharedOpen = !sharedOpen;
											prefs.set('sidebar.sharedOpen', sharedOpen);
										}}
									>
										<ChevronRight
											class="size-3.5 transition-transform {sharedOpen ? 'rotate-90' : ''}"
										/>
										<Share2 class="size-3.5" />{$i18n.t('Shared with me')}
										<span class="ml-auto tabular-nums">{sharedNotes.length}</span>
									</button>
									{#if sharedOpen}
										{#each sharedNotes as n (n.id)}
											<button
												type="button"
												class="flex h-7 w-full items-center gap-1.5 rounded-md px-2 text-left text-sm {n.id ===
												noteId
													? 'bg-sidebar-accent font-medium'
													: 'hover:bg-sidebar-accent/70'}"
												onclick={() => openNote(n.id)}
											>
												<FileText class="size-4 shrink-0 text-muted-foreground" />
												<span class="truncate">{n.title || $i18n.t('Untitled')}</span>
											</button>
										{/each}
									{/if}
								</div>
							{/if}
						</div>
					{:else if sidebarTab === 'search'}
						<SearchPane bind:query={searchQuery} onOpenNote={openNote} />
					{:else}
						<TagsPane bind:selected={selectedTag} onOpenNote={openNote} />
					{/if}
				</div>
				{#if !$mobile}
					<div
						role="separator"
						aria-orientation="vertical"
						class="absolute inset-y-0 -right-1 z-10 w-2 cursor-col-resize hover:bg-primary/10"
						onpointerdown={startResize}
					></div>
				{/if}
			</aside>
		{/if}

		<!-- Main -->
		<main class="relative flex min-w-0 flex-1 flex-col">
			{#if !sidebarOpen}
				<div class="absolute top-1.5 left-2 z-20">
					<Tip content={$i18n.t('Show notes')}>
						<Button
							variant="ghost"
							size="icon-sm"
							onclick={toggleSidebar}
							aria-label={$i18n.t('Show notes')}><PanelLeft /></Button
						>
					</Tip>
				</div>
			{/if}
			<div class="min-h-0 flex-1 {sidebarOpen ? '' : 'pl-10'}">
				{#if !ready}
					<div class="flex h-full items-center justify-center text-sm text-muted-foreground">
						{$i18n.t('Loading…')}
					</div>
				{:else if !$currentVault}
					<div class="flex h-full items-center justify-center text-sm text-muted-foreground">
						{$i18n.t('Notes are not available.')}
					</div>
				{:else if view === 'graph'}
					<div class="flex h-full flex-col">
						<div class="flex h-11 shrink-0 items-center gap-2 border-b px-3 text-sm">
							<Orbit class="size-4 text-muted-foreground" />
							<span class="font-medium">{$i18n.t('Graph view')}</span>
							<span class="text-muted-foreground">· {vaultName($currentVault, $i18n)}</span>
						</div>
						<div class="min-h-0 flex-1">
							<GraphView
								vaultId={$currentVault.id}
								mode="global"
								focusId={null}
								onOpenNote={openNote}
								onCreateNote={(t) => createNote(t, { open: true })}
								onTag={showTag}
							/>
						</div>
					</div>
				{:else if noteId}
					<VaultNoteEditor
						{noteId}
						onOpenNote={openNote}
						onCreateNote={createNote}
						onTag={showTag}
						onDeleted={() => {
							refreshTree(localStorage.token);
							goto('/notes');
						}}
					/>
				{:else}
					<Home
						onOpenNote={openNote}
						onNewNote={() => newNote()}
						onDaily={() => openDaily()}
						onGraph={() => goto('/notes/graph')}
						onSwitcher={() => (showSwitcher = true)}
					/>
				{/if}
			</div>
		</main>
	</div>

	<QuickSwitcher
		bind:open={showSwitcher}
		onOpenNote={openNote}
		onCreate={(title) => createNote(title, { folder: currentFolder(), open: true })}
		onSearch={(q) => {
			searchQuery = q;
			sidebarOpen = true;
			setTab('search');
		}}
		onDaily={() => openDaily()}
		onGraph={() => goto('/notes/graph')}
	/>

	{#if $currentVault}
		<VaultSettingsDialog
			bind:open={showSettings}
			bind:tab={settingsTab}
			vault={$currentVault}
			onDeleted={async () => {
				currentVaultId.set(null);
				await loadVaults(localStorage.token);
				goto('/notes');
			}}
		/>
	{/if}
	<NewVaultDialog
		bind:open={showNewVault}
		onCreated={async (vault) => {
			await loadVaults(localStorage.token);
			currentVaultId.set(vault.id);
			goto('/notes');
			toast.success($i18n.t('Vault created'));
		}}
	/>
</Tooltip.Provider>

<style>
	/* Nodes inside the note editor (editor/WikiLink.ts, EntityRef.ts, Tags.ts). */
	:global(.note-vault-editor .wiki-link) {
		color: var(--link);
		text-decoration: none;
		border-radius: 0.25rem;
		padding: 0 0.125rem;
		background: color-mix(in srgb, var(--primary) 8%, transparent);
		cursor: pointer;
	}
	:global(.note-vault-editor .wiki-link:hover) {
		text-decoration: underline;
		text-underline-offset: 3px;
	}
	:global(.note-vault-editor .wiki-link.wiki-link-ghost) {
		color: var(--muted-foreground);
		background: transparent;
		text-decoration: underline dashed;
		text-underline-offset: 3px;
	}
	:global(.note-vault-editor .entity-ref) {
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		border: 1px solid var(--border);
		border-radius: 0.375rem;
		padding: 0 0.375rem;
		font-size: 0.925em;
		color: var(--foreground);
		text-decoration: none;
		vertical-align: baseline;
		cursor: pointer;
		white-space: nowrap;
	}
	:global(.note-vault-editor .entity-ref:hover) {
		background: var(--accent);
	}
	:global(.note-vault-editor .entity-ref-icon) {
		display: inline-flex;
		color: var(--muted-foreground);
	}
	:global(.note-vault-editor .note-tag) {
		color: var(--link);
		background: color-mix(in srgb, var(--primary) 10%, transparent);
		border-radius: 0.25rem;
		padding: 0 0.15rem;
	}
	/* A drawn ```mermaid block (editor/MermaidBlocks.svelte.ts): collapsed, not display:none, so the
	   arrow keys can still walk into the source. */
	:global(.note-vault-editor pre:has(+ .note-mermaid:not([data-source]))) {
		height: 0;
		min-height: 0;
		margin: 0;
		padding: 0;
		border: 0;
		overflow: hidden;
	}
	/* highlight.js has no Mermaid grammar: it guesses a language and paints it in pale colours. */
	:global(.note-vault-editor code.language-mermaid),
	:global(.note-vault-editor code.language-mermaid span) {
		color: var(--foreground);
	}
	:global(.note-vault-editor .note-mermaid) {
		margin-block: 0.5rem 1rem;
		white-space: normal;
		user-select: none;
	}
	:global(.note-vault-editor .ProseMirror-selectednode.wiki-link),
	:global(.note-vault-editor .ProseMirror-selectednode.entity-ref) {
		outline: 2px solid var(--ring);
		outline-offset: 1px;
	}
</style>
