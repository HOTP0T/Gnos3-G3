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

	// RBAC: client-side guard. Same pattern as /admin/+layout.svelte.
	// API enforces this server-side too — this is UX polish to avoid showing
	// the page chrome before the inevitable 403.
	onMount(async () => {
		const canAccess = $isAdmin || Boolean($user?.permissions?.modules?.invoices?.read);
		if (!canAccess) {
			await goto('/');
			return;
		}
		loaded = true;
	});
</script>

<svelte:head>
	<title>
		{$i18n.t('Invoices')} &bull; {$WEBUI_NAME}
	</title>
</svelte:head>

{#if loaded}
	<ModuleShell containerId="invoices-container">
		{#snippet nav()}<PrimaryDataNav />{/snippet}
		<ViewTabs
			label={$i18n.t('Invoices')}
			items={[
				{
					href: '/invoices/dashboard',
					label: $i18n.t('Dashboard'),
					active: $page.url.pathname.includes('/invoices/dashboard')
				},
				{
					href: '/invoices/data',
					label: $i18n.t('Table'),
					active: $page.url.pathname.includes('/invoices/data')
				}
			]}
		/>
		<div class="mt-4">
			{@render children?.()}
		</div>
	</ModuleShell>
{/if}
