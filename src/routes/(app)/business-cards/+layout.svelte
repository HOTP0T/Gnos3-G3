<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { WEBUI_NAME, user, isAdmin } from '$lib/stores';
	import ModuleShell from '$lib/components/gnos3-ui/ModuleShell.svelte';
	import ViewTabs from '$lib/components/gnos3-ui/ViewTabs.svelte';
	import PrimaryDataNav from '$lib/components/data-nav/PrimaryDataNav.svelte';

	let { children } = $props();

	const i18n: any = getContext('i18n');
	let loaded = $state(false);

	// RBAC: client-side guard. API enforces this too — this is UX polish.
	onMount(async () => {
		const canAccess = $isAdmin || Boolean($user?.permissions?.modules?.business_cards?.read);
		if (!canAccess) {
			await goto('/');
			return;
		}
		loaded = true;
	});
</script>

<svelte:head>
	<title>
		{$i18n.t('Business cards')} &bull; {$WEBUI_NAME}
	</title>
</svelte:head>

{#if loaded}
	<ModuleShell containerId="business-cards-container">
		{#snippet nav()}<PrimaryDataNav />{/snippet}
		<ViewTabs
			label={$i18n.t('Business cards')}
			items={[
				{
					href: '/business-cards/dashboard',
					label: $i18n.t('Dashboard'),
					active: $page.url.pathname.includes('/business-cards/dashboard')
				},
				{
					href: '/business-cards/data',
					label: $i18n.t('Table'),
					active: $page.url.pathname.includes('/business-cards/data')
				}
			]}
		/>
		<div class="mt-4">
			{@render children?.()}
		</div>
	</ModuleShell>
{/if}
