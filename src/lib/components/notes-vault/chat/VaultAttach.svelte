<!--
	In the chat's + menu → Notes: attach a whole vault, a folder or a tag.
	- A vault: its knowledge base (the chat searches it; prepared on first use).
	- A folder / tag small enough to read whole: its notes, one by one (as upstream's note items).
	- A larger folder / tag: its notes' embeddings, through the vault's base (`knowledge_id`).
	Shown inside upstream's InputMenu/Notes.svelte, so it uses that menu's look.
-->
<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Folder from '@lucide/svelte/icons/folder';
	import Hash from '@lucide/svelte/icons/hash';
	import Lock from '@lucide/svelte/icons/lock';
	import Users from '@lucide/svelte/icons/users';
	import Loader from '@lucide/svelte/icons/loader-circle';
	import {
		getVaults,
		getVaultTree,
		prepareVaultKnowledge,
		prepareVaultScope,
		type Vault,
		type VaultTree
	} from '$lib/apis/note-vaults';
	import { vaultName } from '../vault';

	const i18n: any = getContext('i18n');

	let { onSelect }: { onSelect: (item: any) => void } = $props();

	let list: Vault[] = $state([]);
	let open: string | null = $state(null);
	let trees: Record<string, VaultTree> = $state({});
	let busy: string | null = $state(null);

	onMount(async () => {
		list = (await getVaults(localStorage.token).catch(() => [])).filter(
			(v) => (v.note_count ?? 0) > 0
		);
	});

	const expand = async (vault: Vault) => {
		open = open === vault.id ? null : vault.id;
		if (open && !trees[vault.id]) {
			trees = {
				...trees,
				[vault.id]: await getVaultTree(localStorage.token, vault.id).catch(() => ({
					folders: [],
					notes: []
				}))
			};
		}
	};

	const tagsOf = (tree: VaultTree | undefined) => {
		const counts = new Map<string, number>();
		for (const n of tree?.notes ?? [])
			for (const t of n.tags ?? []) counts.set(t, (counts.get(t) ?? 0) + 1);
		return [...counts.entries()].sort((a, b) => a[0].localeCompare(b[0]));
	};

	const attachVault = async (vault: Vault) => {
		busy = vault.id;
		try {
			const res = await prepareVaultKnowledge(localStorage.token, vault.id);
			onSelect({
				type: 'collection',
				id: res.knowledge_id,
				name: vaultName(vault, $i18n),
				description: $i18n.t('Notes vault'),
				gnos3_notes_vault: vault.id
			});
			if (res.pending) {
				toast.info(
					$i18n.t('The chat can already search this vault; {{count}} more notes are being read.', {
						count: res.pending
					})
				);
			}
		} catch (e) {
			toast.error(`${e}`);
		}
		busy = null;
	};

	const attachScope = async (
		vault: Vault,
		scope: { folder?: string; tag?: string },
		label: string
	) => {
		const key = `${vault.id}:${scope.folder ?? ''}:${scope.tag ?? ''}`;
		busy = key;
		try {
			const res = await prepareVaultScope(localStorage.token, vault.id, scope);
			if (res.mode === 'empty') {
				toast.info($i18n.t('No note there.'));
			} else if (res.mode === 'notes') {
				for (const note of res.notes ?? []) {
					onSelect({ type: 'note', id: note.id, name: note.title, description: label });
				}
			} else {
				onSelect({
					type: 'collection',
					id: `notes-scope:${key}`,
					knowledge_id: res.knowledge_id,
					legacy: true,
					collection_names: res.collection_names,
					name: label,
					description: $i18n.t('{{count}} notes', { count: res.count })
				});
				if ((res.total ?? 0) > (res.count ?? 0)) {
					toast.info(
						$i18n.t('The chat searches the {{count}} most recently edited notes of {{total}}.', {
							count: res.count,
							total: res.total
						})
					);
				}
			}
		} catch (e) {
			toast.error(`${e}`);
		}
		busy = null;
	};
</script>

{#if list.length}
	<div class="mb-1 border-b border-gray-100 pb-1 dark:border-gray-800">
		<div class="px-2.5 pt-1 pb-0.5 text-xs text-gray-500">{$i18n.t('Vaults')}</div>
		{#each list as vault (vault.id)}
			<div class="flex items-center gap-0.5">
				<button
					type="button"
					class="flex size-7 shrink-0 items-center justify-center rounded-lg text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800"
					aria-label={$i18n.t('Folders and tags')}
					onclick={() => expand(vault)}
				>
					<ChevronRight
						class="size-3.5 transition-transform {open === vault.id ? 'rotate-90' : ''}"
					/>
				</button>
				<button
					type="button"
					class="flex min-w-0 flex-1 items-center gap-1.5 rounded-xl px-2 py-1 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800"
					onclick={() => attachVault(vault)}
					title={$i18n.t('The chat searches every note of this vault')}
				>
					{#if busy === vault.id}<Loader
							class="size-4 animate-spin"
						/>{:else if vault.kind === 'shared'}<Users class="size-4" />{:else}<Lock
							class="size-4"
						/>{/if}
					<span class="line-clamp-1 flex-1">{vaultName(vault, $i18n)}</span>
					<span class="text-xs text-gray-500 tabular-nums">{vault.note_count}</span>
				</button>
			</div>
			{#if open === vault.id}
				<div class="ml-7 max-h-48 overflow-y-auto">
					{#each trees[vault.id]?.folders ?? [] as folder (folder)}
						{@const key = `${vault.id}:${folder}:`}
						<button
							type="button"
							class="flex w-full items-center gap-1.5 rounded-xl py-1 pr-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800"
							style="padding-left: {0.5 + (folder.split('/').length - 1) * 0.75}rem"
							onclick={() => attachScope(vault, { folder }, folder)}
						>
							{#if busy === key}<Loader class="size-3.5 animate-spin" />{:else}<Folder
									class="size-3.5 text-gray-500"
								/>{/if}
							<span class="line-clamp-1">{folder.split('/').pop()}</span>
						</button>
					{/each}
					{#each tagsOf(trees[vault.id]) as [tag, count] (tag)}
						{@const key = `${vault.id}::${tag}`}
						<button
							type="button"
							class="flex w-full items-center gap-1.5 rounded-xl px-2 py-1 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800"
							onclick={() => attachScope(vault, { tag }, `#${tag}`)}
						>
							{#if busy === key}<Loader class="size-3.5 animate-spin" />{:else}<Hash
									class="size-3.5 text-gray-500"
								/>{/if}
							<span class="line-clamp-1 flex-1">{tag}</span>
							<span class="text-xs text-gray-500 tabular-nums">{count}</span>
						</button>
					{/each}
					{#if trees[vault.id] && !trees[vault.id].folders.length && !tagsOf(trees[vault.id]).length}
						<div class="px-2 py-1 text-xs text-gray-500">{$i18n.t('No folders or tags.')}</div>
					{/if}
				</div>
			{/if}
		{/each}
		<div class="px-2.5 pt-1.5 pb-0.5 text-xs text-gray-500">{$i18n.t('Notes')}</div>
	</div>
{/if}
