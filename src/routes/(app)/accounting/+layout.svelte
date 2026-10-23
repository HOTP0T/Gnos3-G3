<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { WEBUI_NAME, user, isAdmin } from '$lib/stores';
	import ModuleShell from '$lib/components/gnos3-ui/ModuleShell.svelte';

	let { children } = $props();

	const i18n: any = getContext('i18n');
	let loaded = $state(false);

	// A company draws its own frame (company header + section tabs) in company/[id]/+layout.svelte.
	// `page` from $app/state, not the $app/stores store: the store catches up one render after
	// `children`, so leaving a company rendered the next page without ModuleShell (and its
	// Tooltip.Provider) and the first Tip threw.
	const inCompany = $derived(page.url.pathname.startsWith('/accounting/company/'));

	// RBAC: client-side guard. API enforces this too — this is UX polish.
	onMount(async () => {
		const canAccess = $isAdmin || Boolean($user?.permissions?.modules?.accounting?.read);
		if (!canAccess) {
			await goto('/');
			return;
		}
		loaded = true;
	});
</script>

<svelte:head>
	<!-- Inside a company its layout sets the title; this one only mounts again on leaving, so
	     the company name doesn't stay in the browser tab. -->
	{#if !inCompany}
		<title>
			{$i18n.t('Accounting')} &bull; {$WEBUI_NAME}
		</title>
	{/if}
</svelte:head>

{#if loaded}
	{#if inCompany}
		{@render children?.()}
	{:else}
		<ModuleShell
			containerId="accounting-container"
			label={$i18n.t('Accounting')}
			tabs={[
				{
					href: '/accounting/companies',
					label: $i18n.t('Companies'),
					active: page.url.pathname.startsWith('/accounting/compan')
				},
				{
					href: '/accounting/settings',
					label: $i18n.t('Settings'),
					active: page.url.pathname.startsWith('/accounting/settings')
				}
			]}
		>
			{@render children?.()}
		</ModuleShell>
	{/if}
{/if}
