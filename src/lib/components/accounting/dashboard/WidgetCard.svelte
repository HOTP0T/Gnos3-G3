<script lang="ts">
	// Shared frame for every dashboard widget: a plain Card (design system → Cards). IMPORTANT:
	// none of this component's props change when the dashboard enters/leaves edit mode — the
	// edit affordances (drag handle, remove button, dashed outline, drag cursor) are pure CSS
	// keyed off an ancestor `.grid-stack.is-editing` class. That's deliberate: mutating a
	// gridstack-owned item from Svelte makes gridstack lose track of it.
	import { createEventDispatcher, getContext } from 'svelte';
	import GripHorizontal from '@lucide/svelte/icons/grip-horizontal';
	import X from '@lucide/svelte/icons/x';
	import { Button } from '$lib/components/ui/button/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher();
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);

	export let title = '';
	export let href: string | null = null;
	export let linkLabel = '';
	export let padded = true;
</script>

<div
	class="wcard relative flex h-full w-full flex-col overflow-hidden rounded-xl border bg-card text-sm text-card-foreground shadow-sm"
>
	<!-- Edit-mode chrome — CSS-hidden unless the grid is editing. -->
	<span
		class="wcard-handle pointer-events-none absolute top-1 left-1/2 z-20 -translate-x-1/2 text-muted-foreground"
		aria-hidden="true"
	>
		<GripHorizontal class="size-4" />
	</span>
	<div class="wcard-remove absolute top-2 right-2 z-20">
		<Tip content={T('Remove widget')}>
			<Button
				variant="outline"
				size="icon-xs"
				class="bg-card hover:text-destructive"
				aria-label={T('Remove widget')}
				onpointerdown={(e: PointerEvent) => e.stopPropagation()}
				onclick={(e: MouseEvent) => {
					e.stopPropagation();
					dispatch('remove');
				}}
			>
				<X />
			</Button>
		</Tip>
	</div>

	{#if title}
		<div class="flex shrink-0 items-center gap-2 px-4 pt-4 pb-3">
			<h3 class="min-w-0 flex-1 truncate text-base leading-5 font-semibold">{title}</h3>
			{#if href}
				<a
					{href}
					class="wcard-link text-sm whitespace-nowrap text-link underline-offset-4 hover:underline"
				>
					{linkLabel || T('View all')}
				</a>
			{/if}
		</div>
	{/if}
	<div
		class="min-h-0 flex-1 overflow-hidden {padded ? 'px-4 pb-4' : ''} {title
			? ''
			: padded
				? 'pt-4'
				: ''}"
	>
		<slot />
	</div>
</div>
