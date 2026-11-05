<!-- Admins: a shared vault for a team (the groups that read it, and those that also write). -->
<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import Users from '@lucide/svelte/icons/users';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import AccessControlModal from '$lib/components/workspace/common/AccessControlModal.svelte';
	import { createVault, type Vault } from '$lib/apis/note-vaults';

	const i18n: any = getContext('i18n');

	let {
		open = $bindable(false),
		onCreated
	}: { open?: boolean; onCreated: (vault: Vault) => void } = $props();

	let name = $state('');
	let description = $state('');
	let accessGrants: any[] = $state([]);
	let showAccess = $state(false);
	let saving = $state(false);

	$effect(() => {
		if (open) {
			name = '';
			description = '';
			accessGrants = [];
		}
	});

	const groups = $derived(accessGrants.filter((g) => g.principal_type === 'group').length);

	const create = async () => {
		if (!name.trim()) return;
		saving = true;
		try {
			const vault = await createVault(localStorage.token, {
				name: name.trim(),
				description,
				access_grants: accessGrants
			});
			open = false;
			onCreated(vault);
		} catch (e) {
			toast.error(`${e}`);
		}
		saving = false;
	};
</script>

<AccessControlModal
	bind:show={showAccess}
	bind:accessGrants
	accessRoles={['read', 'write']}
	share={true}
	sharePublic={false}
	shareUsers={true}
/>

<Dialog.Root bind:open>
	<Dialog.Content class="sm:max-w-md">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('New shared vault')}</Dialog.Title>
			<Dialog.Description>
				{$i18n.t(
					'Notes a team writes together, linked in one graph. You choose which groups read it and which also write.'
				)}
			</Dialog.Description>
		</Dialog.Header>
		<div class="space-y-4">
			<div class="space-y-1.5">
				<Label for="new-vault-name">{$i18n.t('Name')}</Label>
				<Input
					id="new-vault-name"
					bind:value={name}
					placeholder={$i18n.t('e.g. Accounting team')}
					autofocus
				/>
			</div>
			<div class="space-y-1.5">
				<Label for="new-vault-description">{$i18n.t('Description')}</Label>
				<Textarea id="new-vault-description" bind:value={description} rows={2} />
			</div>
			<div class="flex items-center justify-between gap-3 rounded-lg border p-3 text-sm">
				<span class="text-muted-foreground">
					{groups
						? $i18n.t('Shared with {{count}} groups', { count: groups })
						: $i18n.t('Not shared yet: only admins see it.')}
				</span>
				<Button variant="outline" size="sm" onclick={() => (showAccess = true)}
					><Users />{$i18n.t('Access')}</Button
				>
			</div>
		</div>
		<Dialog.Footer>
			<Button variant="outline" onclick={() => (open = false)}>{$i18n.t('Cancel')}</Button>
			<Button onclick={create} disabled={saving || !name.trim()}>{$i18n.t('Create vault')}</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
