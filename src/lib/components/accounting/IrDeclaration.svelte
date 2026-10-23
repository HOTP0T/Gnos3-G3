<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import Info from '@lucide/svelte/icons/info';

	import { getTaxConfig } from '$lib/apis/accounting';
	import TaxFilingsList from './TaxFilingsList.svelte';

	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';

	const i18n: any = getContext('i18n');

	export let companyId: number;

	let cfg: any = null;
	let loaded = false;

	onMount(async () => {
		try {
			cfg = await getTaxConfig(companyId);
		} catch {
			cfg = null;
		}
		loaded = true;
	});

	const pctOf = (r: any) =>
		r === null || r === undefined ? '—' : `${(Number(r) * 100).toFixed(2)}%`;
</script>

<div class="flex flex-col gap-4">
	<h2 class="text-lg font-semibold">{$i18n.t('Individual income tax')}</h2>

	<Alert.Root variant="info">
		<Info />
		<Alert.Description>
			{$i18n.t(
				'The individual income tax worksheet is a scaffold. There is no reference calculation yet — provide a sample sheet and it will be built out like the other tax tabs.'
			)}
		</Alert.Description>
	</Alert.Root>

	<Card.Root size="sm" class="max-w-md">
		<Card.Header>
			<Card.Title>{$i18n.t('Configured individual income tax rate')}</Card.Title>
			<Card.Description>{$i18n.t('Set per country in Settings → Countries.')}</Card.Description>
			<Card.Action class="self-center">
				{#if loaded}
					<span class="text-lg font-semibold tabular-nums">{pctOf(cfg?.ir_rate)}</span>
				{:else}
					<Skeleton class="h-6 w-16" />
				{/if}
			</Card.Action>
		</Card.Header>
	</Card.Root>

	<TaxFilingsList {companyId} taxType="ir" on:gotoAccounts />
</div>
