<script lang="ts">
	// Quick action links: outline buttons with an icon, wrapping to the card width.
	import { getContext } from 'svelte';
	import Plus from '@lucide/svelte/icons/plus';
	import Wallet from '@lucide/svelte/icons/wallet';
	import ArrowLeftRight from '@lucide/svelte/icons/arrow-left-right';
	import FileSpreadsheet from '@lucide/svelte/icons/file-spreadsheet';
	import { Button } from '$lib/components/ui/button/index.js';

	export let companyId: number;
	export let options: Record<string, any> = {}; // unused; part of widget contract
	const i18n: any = getContext('i18n');
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);

	$: base = `/accounting/company/${companyId}`;
	$: actions = [
		{ href: `${base}/entries`, label: 'New Journal Entry', icon: Plus },
		{ href: `${base}/payments`, label: 'Record Payment', icon: Wallet },
		{ href: `${base}/bank`, label: 'Reconcile Bank', icon: ArrowLeftRight },
		{ href: `${base}/reports`, label: 'Reports', icon: FileSpreadsheet }
	];
</script>

<div class="flex h-full flex-wrap content-start gap-2 overflow-y-auto">
	{#each actions as a}
		<Button variant="outline" size="sm" href={a.href}>
			<svelte:component this={a.icon} />{T(a.label)}
		</Button>
	{/each}
</div>
