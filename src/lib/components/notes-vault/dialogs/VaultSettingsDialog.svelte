<!--
	A vault's settings: name and access (shared vaults: who reads, who writes — admins), note types,
	daily notes and templates, import / export, and chat.
-->
<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import fileSaver from 'file-saver';
	import Users from '@lucide/svelte/icons/users';
	import Download from '@lucide/svelte/icons/download';
	import Upload from '@lucide/svelte/icons/upload';
	import Loader from '@lucide/svelte/icons/loader-circle';
	import MessageSquare from '@lucide/svelte/icons/message-square';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Tabs from '$lib/components/ui/tabs/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';
	import AccessControlModal from '$lib/components/workspace/common/AccessControlModal.svelte';
	import { isAdmin } from '$lib/stores';
	import {
		deleteVault,
		exportVault,
		importVaultNotes,
		prepareVaultKnowledge,
		updateVault,
		updateVaultAccess,
		type NoteType,
		type Vault
	} from '$lib/apis/note-vaults';
	import dayjs from '$lib/dayjs';
	import { canWrite, loadVaults, refreshTree, tree, vaultName } from '../vault';
	import { readVaultFiles } from '../importVault';
	import TypesEditor from './TypesEditor.svelte';

	const i18n: any = getContext('i18n');
	const { saveAs } = fileSaver;

	let {
		open = $bindable(false),
		vault,
		tab = $bindable('general'),
		onDeleted
	}: { open?: boolean; vault: Vault; tab?: string; onDeleted: () => void } = $props();

	let name = $state('');
	let description = $state('');
	let types: NoteType[] = $state([]);
	let dailyFolder = $state('');
	let dailyFormat = $state('');
	let dailyTemplate = $state('');
	let templatesFolder = $state('');
	let accessGrants: any[] = $state([]);
	let showAccess = $state(false);
	let showDelete = $state(false);
	let saving = $state(false);
	let importing = $state(false);
	let importProgress = $state('');
	let exporting = $state(false);
	let preparing = $state(false);

	const manage = $derived(vault.permission === 'manage');
	const writable = $derived(canWrite(vault));

	$effect(() => {
		if (!open) return;
		name = vaultName(vault, $i18n);
		description = vault.description ?? '';
		types = JSON.parse(JSON.stringify(vault.settings.types ?? []));
		dailyFolder = vault.settings.daily?.folder ?? '';
		dailyFormat = vault.settings.daily?.format ?? 'YYYY-MM-DD';
		dailyTemplate = vault.settings.daily?.template_id ?? '';
		templatesFolder = vault.settings.templates_folder ?? '';
		accessGrants = vault.access_grants ?? [];
	});

	const templateNotes = $derived(
		($tree?.notes ?? []).filter(
			(n) =>
				templatesFolder &&
				(n.folder === templatesFolder || n.folder.startsWith(templatesFolder + '/'))
		)
	);

	const save = async () => {
		saving = true;
		try {
			await updateVault(localStorage.token, vault.id, {
				...(manage
					? {
							name:
								name.trim() && name.trim() !== vaultName(vault, $i18n) ? name.trim() : undefined,
							description
						}
					: {}),
				settings: {
					types,
					daily: {
						folder: dailyFolder,
						format: dailyFormat || 'YYYY-MM-DD',
						template_id: dailyTemplate || null
					},
					templates_folder: templatesFolder
				}
			});
			await loadVaults(localStorage.token);
			toast.success($i18n.t('Saved'));
			open = false;
		} catch (e) {
			toast.error(`${e}`);
		}
		saving = false;
	};

	const doExport = async () => {
		exporting = true;
		try {
			const blob = await exportVault(localStorage.token, vault.id);
			saveAs(blob, `${vaultName(vault, $i18n)}.zip`);
		} catch (e) {
			toast.error(`${e}`);
		}
		exporting = false;
	};

	const doImport = () => {
		const input = document.createElement('input');
		input.type = 'file';
		input.multiple = true;
		input.accept = '.zip,.md,.markdown';
		input.onchange = async () => {
			const files = Array.from(input.files ?? []);
			if (!files.length) return;
			importing = true;
			try {
				importProgress = $i18n.t('Reading the files…');
				const { items, skipped } = await readVaultFiles(files);
				let done = 0;
				for (let i = 0; i < items.length; i += 40) {
					const batch = items.slice(i, i + 40);
					await importVaultNotes(localStorage.token, vault.id, batch);
					done += batch.length;
					importProgress = $i18n.t('{{done}} of {{total}} notes imported', {
						done,
						total: items.length
					});
				}
				await refreshTree(localStorage.token);
				await loadVaults(localStorage.token);
				toast.success($i18n.t('{{count}} notes imported', { count: items.length }));
				if (skipped.length)
					toast.info(
						$i18n.t('{{count}} other files were not imported (only notes and their images are).', {
							count: skipped.length
						})
					);
			} catch (e) {
				toast.error(`${e}`);
			}
			importing = false;
			importProgress = '';
		};
		input.click();
	};

	const prepareChat = async () => {
		preparing = true;
		try {
			const res = await prepareVaultKnowledge(localStorage.token, vault.id);
			toast.success(
				res.pending
					? $i18n.t('Ready for chat; {{count}} more notes will be read in the next minutes.', {
							count: res.pending
						})
					: $i18n.t('Ready for chat.')
			);
			await loadVaults(localStorage.token);
		} catch (e) {
			toast.error(`${e}`);
		}
		preparing = false;
	};
</script>

<AccessControlModal
	bind:show={showAccess}
	bind:accessGrants
	accessRoles={['read', 'write']}
	share={true}
	sharePublic={false}
	shareUsers={true}
	onChange={async () => {
		try {
			await updateVaultAccess(localStorage.token, vault.id, accessGrants);
			await loadVaults(localStorage.token);
			toast.success($i18n.t('Saved'));
		} catch (e) {
			toast.error(`${e}`);
		}
	}}
/>

<ConfirmDialog
	bind:open={showDelete}
	title={$i18n.t('Delete the vault “{{name}}”?', { name: vaultName(vault, $i18n) })}
	description={$i18n.t(
		'All its notes are deleted for everyone. Export it first if you may need them.'
	)}
	confirmLabel={$i18n.t('Delete vault')}
	destructive
	onconfirm={async () => {
		try {
			await deleteVault(localStorage.token, vault.id);
			open = false;
			onDeleted();
		} catch (e) {
			toast.error(`${e}`);
		}
	}}
/>

<Dialog.Root bind:open>
	<Dialog.Content class="max-h-[90vh] gap-4 overflow-y-auto sm:max-w-2xl">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Vault settings')}</Dialog.Title>
			<Dialog.Description>{vaultName(vault, $i18n)}</Dialog.Description>
		</Dialog.Header>

		<Tabs.Root bind:value={tab}>
			<Tabs.List class="w-full flex-wrap">
				<Tabs.Trigger value="general">{$i18n.t('General')}</Tabs.Trigger>
				<Tabs.Trigger value="types">{$i18n.t('Note types')}</Tabs.Trigger>
				<Tabs.Trigger value="daily">{$i18n.t('Daily notes & templates')}</Tabs.Trigger>
				<Tabs.Trigger value="data">{$i18n.t('Import & export')}</Tabs.Trigger>
			</Tabs.List>

			<Tabs.Content value="general" class="space-y-4 pt-3">
				<div class="space-y-1.5">
					<Label for="vault-name">{$i18n.t('Name')}</Label>
					<Input id="vault-name" bind:value={name} disabled={!manage} />
				</div>
				{#if vault.kind === 'shared'}
					<div class="space-y-1.5">
						<Label for="vault-description">{$i18n.t('Description')}</Label>
						<Textarea id="vault-description" bind:value={description} disabled={!manage} rows={2} />
					</div>
					<div class="flex items-center justify-between gap-3 rounded-lg border p-3">
						<div class="text-sm">
							<div class="font-medium">{$i18n.t('Who can use this vault')}</div>
							<div class="text-muted-foreground">
								{$i18n.t(
									'Groups that can read it, and groups that can also write in it. Every note in the vault follows this.'
								)}
							</div>
						</div>
						{#if manage}
							<Button variant="outline" size="sm" onclick={() => (showAccess = true)}
								><Users />{$i18n.t('Access')}</Button
							>
						{/if}
					</div>
				{:else}
					<p class="text-sm text-muted-foreground">
						{$i18n.t(
							'Your personal vault: only you see it. Share a single note from its page, or move it to a shared vault.'
						)}
					</p>
				{/if}
				<div class="flex items-center justify-between gap-3 rounded-lg border p-3">
					<div class="text-sm">
						<div class="font-medium">{$i18n.t('Use in chat')}</div>
						<div class="text-muted-foreground">
							{vault.knowledge_id
								? $i18n.t(
										'The chat can search this vault (attach it from the + menu, under Notes). Changes are picked up within a minute.'
									)
								: $i18n.t(
										'Let the chat search this vault: its notes are read once, then kept up to date.'
									)}
						</div>
					</div>
					<Button variant="outline" size="sm" onclick={prepareChat} disabled={preparing}>
						{#if preparing}<Loader class="animate-spin" />{:else}<MessageSquare />{/if}
						{vault.knowledge_id ? $i18n.t('Update now') : $i18n.t('Turn on')}
					</Button>
				</div>
				{#if vault.kind === 'shared' && $isAdmin}
					<div
						class="flex items-center justify-between gap-3 rounded-lg border border-destructive/30 p-3"
					>
						<div class="text-sm">
							<div class="font-medium">{$i18n.t('Delete this vault')}</div>
							<div class="text-muted-foreground">
								{$i18n.t('Deletes the vault and all its notes.')}
							</div>
						</div>
						<Button variant="destructive" size="sm" onclick={() => (showDelete = true)}
							>{$i18n.t('Delete')}</Button
						>
					</div>
				{/if}
			</Tabs.Content>

			<Tabs.Content value="types" class="pt-3">
				<TypesEditor bind:types editable={writable} />
			</Tabs.Content>

			<Tabs.Content value="daily" class="space-y-4 pt-3">
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="space-y-1.5">
						<Label for="daily-folder">{$i18n.t('Daily notes folder')}</Label>
						<Input
							id="daily-folder"
							bind:value={dailyFolder}
							disabled={!writable}
							placeholder={$i18n.t('Vault root')}
						/>
					</div>
					<div class="space-y-1.5">
						<Label for="daily-format">{$i18n.t('Title format')}</Label>
						<Input id="daily-format" bind:value={dailyFormat} disabled={!writable} />
						<p class="text-xs text-muted-foreground">
							{$i18n.t('Today: {{title}}', { title: dayjs().format(dailyFormat || 'YYYY-MM-DD') })}
						</p>
					</div>
				</div>
				<div class="space-y-1.5">
					<Label for="templates-folder">{$i18n.t('Templates folder')}</Label>
					<Input id="templates-folder" bind:value={templatesFolder} disabled={!writable} />
					<p class="text-xs text-muted-foreground">
						{$i18n.t(
							'Notes in this folder are offered as templates (type / in a note). They can use {{title}}, {{date}} and {{time}}.',
							{
								title: '{{title}}',
								date: '{{date}}',
								time: '{{time}}'
							}
						)}
					</p>
				</div>
				<div class="space-y-1.5">
					<Label for="daily-template">{$i18n.t('Daily note template')}</Label>
					<NativeSelect.Root
						id="daily-template"
						class="w-full"
						bind:value={dailyTemplate}
						disabled={!writable}
					>
						<NativeSelect.Option value="">{$i18n.t('None (empty note)')}</NativeSelect.Option>
						{#each templateNotes as t (t.id)}<NativeSelect.Option value={t.id}
								>{t.title}</NativeSelect.Option
							>{/each}
					</NativeSelect.Root>
				</div>
			</Tabs.Content>

			<Tabs.Content value="data" class="space-y-3 pt-3">
				<div class="flex items-center justify-between gap-3 rounded-lg border p-3">
					<div class="text-sm">
						<div class="font-medium">{$i18n.t('Export')}</div>
						<div class="text-muted-foreground">
							{$i18n.t(
								'A .zip of Markdown files in their folders, with properties as frontmatter and images. Opens in Obsidian or Tolaria.'
							)}
						</div>
					</div>
					<Button variant="outline" size="sm" onclick={doExport} disabled={exporting}>
						{#if exporting}<Loader class="animate-spin" />{:else}<Download />{/if}{$i18n.t(
							'Export'
						)}
					</Button>
				</div>
				{#if writable}
					<div class="flex items-center justify-between gap-3 rounded-lg border p-3">
						<div class="text-sm">
							<div class="font-medium">{$i18n.t('Import')}</div>
							<div class="text-muted-foreground">
								{importing
									? importProgress
									: $i18n.t(
											'An Obsidian or Tolaria vault (.zip), or Markdown files. Folders, [[links]], frontmatter and images are kept.'
										)}
							</div>
						</div>
						<Button variant="outline" size="sm" onclick={doImport} disabled={importing}>
							{#if importing}<Loader class="animate-spin" />{:else}<Upload />{/if}{$i18n.t(
								'Import'
							)}
						</Button>
					</div>
				{/if}
			</Tabs.Content>
		</Tabs.Root>

		<Dialog.Footer>
			<Button variant="outline" onclick={() => (open = false)}>{$i18n.t('Cancel')}</Button>
			{#if writable}
				<Button onclick={save} disabled={saving}>{$i18n.t('Save')}</Button>
			{/if}
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
