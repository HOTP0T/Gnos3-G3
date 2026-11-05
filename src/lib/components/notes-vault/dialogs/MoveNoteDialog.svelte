<!--
	Move a note to another folder, or another vault the person can write in. A note moved into a
	shared vault takes that vault's access; back in a personal vault, only its author's.
-->
<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import Folder from '@lucide/svelte/icons/folder';
	import House from '@lucide/svelte/icons/house';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { getVaultTree, moveNote } from '$lib/apis/note-vaults';
	import { user } from '$lib/stores';
	import { canWrite, vaultName, vaults } from '../vault';

	const i18n: any = getContext('i18n');

	let {
		open = $bindable(false),
		noteId,
		noteOwner,
		currentVaultId,
		currentFolder,
		onMoved
	}: {
		open?: boolean;
		noteId: string;
		noteOwner: string;
		currentVaultId: string;
		currentFolder: string;
		onMoved: () => void;
	} = $props();

	let vaultId = $state('');
	let folder = $state('');
	let folders: string[] = $state([]);
	let saving = $state(false);

	// A personal vault is only for the notes its owner wrote.
	const targets = $derived(
		($vaults ?? []).filter(
			(v) =>
				canWrite(v) && (v.kind === 'shared' || v.owner_id === noteOwner || v.id === currentVaultId)
		)
	);

	$effect(() => {
		if (open) {
			vaultId = currentVaultId;
			folder = currentFolder;
		}
	});

	$effect(() => {
		const id = vaultId;
		if (!id || !open) return;
		getVaultTree(localStorage.token, id)
			.then((t) => (folders = t.folders))
			.catch(() => (folders = []));
	});

	const move = async () => {
		saving = true;
		try {
			await moveNote(localStorage.token, noteId, vaultId, folder);
			toast.success($i18n.t('Note moved'));
			open = false;
			onMoved();
		} catch (e) {
			toast.error(`${e}`);
		}
		saving = false;
	};
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="sm:max-w-md">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Move note')}</Dialog.Title>
			<Dialog.Description>
				{$i18n.t('A note in a shared vault can be read by everyone that vault is shared with.')}
			</Dialog.Description>
		</Dialog.Header>
		<div class="space-y-4">
			<div class="space-y-1.5">
				<Label for="move-vault">{$i18n.t('Vault')}</Label>
				<NativeSelect.Root id="move-vault" class="w-full" bind:value={vaultId}>
					{#each targets as v (v.id)}
						<NativeSelect.Option value={v.id}>{vaultName(v, $i18n)}</NativeSelect.Option>
					{/each}
				</NativeSelect.Root>
			</div>
			<div class="space-y-1.5">
				<Label>{$i18n.t('Folder')}</Label>
				<div class="max-h-64 overflow-y-auto rounded-md border p-1">
					<button
						type="button"
						class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm {folder ===
						''
							? 'bg-accent'
							: 'hover:bg-accent/60'}"
						onclick={() => (folder = '')}
					>
						<House class="size-4 text-muted-foreground" />{$i18n.t('Vault root')}
					</button>
					{#each folders as path (path)}
						<button
							type="button"
							class="flex w-full items-center gap-2 rounded-md py-1.5 pr-2 text-left text-sm {folder ===
							path
								? 'bg-accent'
								: 'hover:bg-accent/60'}"
							style="padding-left: {0.5 + (path.split('/').length - 1) * 1}rem"
							onclick={() => (folder = path)}
						>
							<Folder class="size-4 text-muted-foreground" />
							<span class="truncate">{path.split('/').pop()}</span>
						</button>
					{/each}
				</div>
			</div>
		</div>
		<Dialog.Footer>
			<Button variant="outline" onclick={() => (open = false)}>{$i18n.t('Cancel')}</Button>
			<Button
				onclick={move}
				disabled={saving || (vaultId === currentVaultId && folder === currentFolder)}
			>
				{$i18n.t('Move')}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
