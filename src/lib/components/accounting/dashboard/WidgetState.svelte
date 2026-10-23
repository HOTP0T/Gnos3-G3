<!--
	Loading / empty / error states inside a dashboard widget (design system → Feedback):
	a skeleton in place while loading, a muted line with an icon when there is nothing to show,
	and an inline error with Retry when the widget's own request failed.

	<WidgetState state="loading" rows={6} />
	<WidgetState state="empty" icon={Receipt} message={T('No transactions')} />
	<WidgetState state="error" onretry={load} />
-->
<script lang="ts">
	import { getContext, type Component } from 'svelte';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import RotateCw from '@lucide/svelte/icons/rotate-cw';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { cn } from '$lib/utils/shadcn.js';

	const i18n: any = getContext('i18n');
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);

	let {
		state,
		message = '',
		icon = undefined,
		rows = 0,
		onretry = undefined,
		class: className = ''
	}: {
		state: 'loading' | 'empty' | 'error';
		message?: string;
		icon?: Component<any>;
		/** loading: list rows to sketch; 0 = one block (charts) */
		rows?: number;
		onretry?: () => void;
		/** padding when the widget body has none (flush lists) */
		class?: string;
	} = $props();

	const Icon = $derived(icon);
</script>

{#if state === 'loading'}
	{#if rows > 0}
		<div class={cn('flex flex-col gap-2', className)} aria-busy="true">
			{#each Array(rows) as _}<Skeleton class="h-6 w-full" />{/each}
		</div>
	{:else}
		<div class={cn('h-full', className)}>
			<Skeleton class="h-full min-h-16 w-full" aria-busy="true" />
		</div>
	{/if}
{:else if state === 'error'}
	<div
		role="alert"
		class={cn(
			'flex h-full flex-col items-center justify-center gap-2 text-center text-sm',
			className
		)}
	>
		<span class="inline-flex items-center gap-1.5">
			<CircleAlert class="size-4 shrink-0 text-destructive" aria-hidden="true" />
			{message || T("Couldn't load this widget.")}
		</span>
		{#if onretry}
			<Button variant="outline" size="xs" onclick={onretry}><RotateCw />{T('Retry')}</Button>
		{/if}
	</div>
{:else}
	<div
		class={cn(
			'flex h-full flex-col items-center justify-center gap-2 text-center text-sm text-muted-foreground',
			className
		)}
	>
		{#if Icon}<Icon class="size-5" aria-hidden="true" />{/if}
		<span>{message}</span>
	</div>
{/if}
