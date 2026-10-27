<script lang="ts">
	import { onMount, getContext, setContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { WEBUI_NAME, user, isAdmin } from '$lib/stores';
	import { getAnonymiserSettings } from '$lib/apis/anonymiser';
	import ModuleShell from '$lib/components/gnos3-ui/ModuleShell.svelte';
	import { ANONYMISER_CONTEXT, type AnonymiserState } from '$lib/components/anonymiser/kinds';

	let { children } = $props();

	const i18n: any = getContext('i18n');
	let loaded = $state(false);

	// Fetched once here, read by the tool and the settings page.
	const anon: AnonymiserState = $state({
		loading: true,
		error: '',
		settings: null,
		kinds: [],
		canEdit: false
	});
	setContext(ANONYMISER_CONTEXT, anon);

	// RBAC: client-side guard. The service enforces `modules.anonymiser.read` too.
	onMount(async () => {
		const canAccess = $isAdmin || Boolean($user?.permissions?.modules?.anonymiser?.read);
		if (!canAccess) {
			await goto('/');
			return;
		}
		loaded = true;
		try {
			const res = await getAnonymiserSettings();
			anon.settings = res.settings;
			anon.kinds = res.kinds;
			anon.canEdit = res.can_edit;
		} catch (err) {
			anon.error =
				err instanceof TypeError
					? $i18n.t('The Anonymiser service is not reachable.')
					: err instanceof Error
						? err.message
						: `${err}`;
		}
		anon.loading = false;
	});

	const tabs = $derived(
		anon.canEdit
			? [
					{
						href: '/anonymiser',
						label: $i18n.t('Anonymise'),
						active: $page.url.pathname === '/anonymiser'
					},
					{
						href: '/anonymiser/settings',
						label: $i18n.t('Settings'),
						active: $page.url.pathname.startsWith('/anonymiser/settings')
					}
				]
			: []
	);
</script>

<svelte:head>
	<title>{$i18n.t('Anonymiser')} &bull; {$WEBUI_NAME}</title>
</svelte:head>

{#if loaded}
	<ModuleShell containerId="anonymiser-container" label={$i18n.t('Anonymiser')} {tabs}>
		{@render children?.()}
	</ModuleShell>
{/if}
