<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { page } from '$app/stores';
	import Receipt from '@lucide/svelte/icons/receipt';
	import IdCard from '@lucide/svelte/icons/id-card';
	import { enabledModules, ensureModulesLoaded } from '$lib/stores/modules';
	import { user, isAdmin } from '$lib/stores';
	import NavTabs from '$lib/components/gnos3-ui/NavTabs.svelte';

	const i18n: any = getContext('i18n');

	// Module-name → href + active matcher + perm key + icon. Add new modules here as they ship.
	const TAB_FOR: Record<
		string,
		{ href: string; matches: (path: string) => boolean; permKey: string; icon: typeof Receipt }
	> = {
		invoices: {
			href: '/invoices/dashboard',
			matches: (p) => p.startsWith('/invoices'),
			permKey: 'invoices',
			icon: Receipt
		},
		business_cards: {
			href: '/business-cards/dashboard',
			matches: (p) => p.startsWith('/business-cards'),
			permKey: 'business_cards',
			icon: IdCard
		}
	};

	onMount(() => {
		ensureModulesLoaded();
	});

	// RBAC: only show modules the user has read access to. Admins see everything.
	const tabs = $derived(
		$enabledModules
			.filter((m) => TAB_FOR[m.name])
			.filter((m) => $isAdmin || Boolean($user?.permissions?.modules?.[TAB_FOR[m.name].permKey]?.read))
			.map((m) => ({
				href: TAB_FOR[m.name].href,
				label: $i18n.t(m.label || m.name),
				icon: TAB_FOR[m.name].icon,
				active: TAB_FOR[m.name].matches($page.url.pathname)
			}))
	);
</script>

<NavTabs items={tabs} label={$i18n.t('Data')} />
