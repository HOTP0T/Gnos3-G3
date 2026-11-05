<!--
	"Save to notes" under a chat answer: the answer becomes a note in a vault and folder the person
	chooses, with a link back to the chat. Shown next to upstream's Copy button (ResponseMessage).
-->
<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import NotebookPen from '@lucide/svelte/icons/notebook-pen';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { config, isAdmin, user } from '$lib/stores';
	import { createVaultNote, getVaults, getVaultTree, type Vault } from '$lib/apis/note-vaults';
	import { canWrite, cleanTitle, prefs, vaultName } from '../vault';

	const i18n: any = getContext('i18n');

	let {
		content,
		chatId = '',
		chatTitle = '',
		buttonClass = ''
	}: { content: string; chatId?: string; chatTitle?: string; buttonClass?: string } = $props();

	const enabled = $derived(
		!!($config as any)?.features?.enable_notes &&
			($isAdmin || (($user as any)?.permissions?.features?.notes ?? true))
	);

	let open = $state(false);
	let vaults: Vault[] = $state([]);
	let vaultId = $state('');
	let folders: string[] = $state([]);
	let folder = $state('');
	let title = $state('');
	let linkChat = $state(true);
	let saving = $state(false);

	const guessTitle = (text: string) => {
		const heading = text.match(/^#{1,3}\s+(.+)$/m)?.[1];
		const first =
			heading ??
			text
				.split('\n')
				.find((l) => l.trim())
				?.replace(/[#*_`>\-]/g, '')
				.trim() ??
			'';
		return cleanTitle(first).slice(0, 80) || $i18n.t('Saved answer');
	};

	const start = async () => {
		title = guessTitle(content);
		open = true;
		vaults = (await getVaults(localStorage.token).catch(() => [])).filter((v) => canWrite(v));
		const remembered = prefs.get<string | null>('saveAnswer.vault', null);
		vaultId = vaults.find((v) => v.id === remembered)?.id ?? vaults[0]?.id ?? '';
		folder = prefs.get<string>('saveAnswer.folder', '');
	};

	$effect(() => {
		const id = vaultId;
		if (!id || !open) return;
		getVaultTree(localStorage.token, id)
			.then((t) => {
				folders = t.folders;
				if (folder && !folders.includes(folder)) folder = '';
			})
			.catch(() => (folders = []));
	});

	const save = async () => {
		if (!vaultId) return;
		saving = true;
		try {
			const source =
				linkChat && chatId
					? `\n\n---\n${$i18n.t('From the chat')}: [${(chatTitle || $i18n.t('Chat')).replace(/[\[\]]/g, '')}](/c/${chatId})`
					: '';
			const res = await createVaultNote(localStorage.token, vaultId, {
				title: title || guessTitle(content),
				folder,
				md: content + source
			});
			prefs.set('saveAnswer.vault', vaultId);
			prefs.set('saveAnswer.folder', folder);
			open = false;
			toast.success($i18n.t('Saved to notes'), {
				action: { label: $i18n.t('Open'), onClick: () => goto(`/notes/${res.id}`) }
			});
		} catch (e) {
			toast.error(`${e}`);
		}
		saving = false;
	};
</script>

{#if enabled}
	<button
		type="button"
		aria-label={$i18n.t('Save to notes')}
		title={$i18n.t('Save to notes')}
		class={buttonClass}
		onclick={start}
	>
		<NotebookPen class="size-4" />
	</button>

	<Dialog.Root bind:open>
		<Dialog.Content class="sm:max-w-md">
			<Dialog.Header>
				<Dialog.Title>{$i18n.t('Save to notes')}</Dialog.Title>
				<Dialog.Description
					>{$i18n.t('The answer becomes a note you can edit and link.')}</Dialog.Description
				>
			</Dialog.Header>
			<div class="space-y-4">
				<div class="space-y-1.5">
					<Label for="save-title">{$i18n.t('Title')}</Label>
					<Input id="save-title" bind:value={title} />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="space-y-1.5">
						<Label for="save-vault">{$i18n.t('Vault')}</Label>
						<NativeSelect.Root id="save-vault" class="w-full" bind:value={vaultId}>
							{#each vaults as v (v.id)}<NativeSelect.Option value={v.id}
									>{vaultName(v, $i18n)}</NativeSelect.Option
								>{/each}
						</NativeSelect.Root>
					</div>
					<div class="space-y-1.5">
						<Label for="save-folder">{$i18n.t('Folder')}</Label>
						<NativeSelect.Root id="save-folder" class="w-full" bind:value={folder}>
							<NativeSelect.Option value="">{$i18n.t('Vault root')}</NativeSelect.Option>
							{#each folders as f (f)}<NativeSelect.Option value={f}>{f}</NativeSelect.Option
								>{/each}
						</NativeSelect.Root>
					</div>
				</div>
				{#if chatId}
					<label class="flex items-center gap-2 text-sm">
						<Checkbox bind:checked={linkChat} />{$i18n.t('Add a link back to this chat')}
					</label>
				{/if}
			</div>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (open = false)}>{$i18n.t('Cancel')}</Button>
				<Button onclick={save} disabled={saving || !vaultId}>{$i18n.t('Save')}</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}
