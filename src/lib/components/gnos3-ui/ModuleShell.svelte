<!--
	The frame of a native module page (design system → Build a module, "Screens inside Gnos3"):
	the area right of the Gnos3 sidebar, the sidebar toggle on phones, the module's underline
	tabs, then the page body with 16px padding (24px from lg) that scrolls on its own.

	<ModuleShell containerId="business-cards-container" label="Data" tabs={[…]}>
		…page…
	</ModuleShell>

	When the tabs need their own logic (enabled modules, permissions), pass them as the `nav` snippet.
-->
<script lang="ts">
	import { getContext, type Snippet } from 'svelte';
	import PanelLeft from '@lucide/svelte/icons/panel-left';
	import { mobile, showSidebar } from '$lib/stores';
	import NavTabs from './NavTabs.svelte';
	import * as Tooltip from '$lib/components/ui/tooltip/index.js';
	import { cn } from '$lib/utils/shadcn.js';

	const i18n: any = getContext('i18n');

	let {
		tabs = [],
		label = undefined,
		containerId = undefined,
		class: className = '',
		nav = undefined,
		children
	}: {
		tabs?: { href: string; label: string; active?: boolean }[];
		label?: string;
		containerId?: string;
		class?: string;
		nav?: Snippet;
		children?: Snippet;
	} = $props();
</script>

<Tooltip.Provider delayDuration={300}>
	<div
		class="flex h-screen max-h-[100dvh] w-full max-w-full flex-1 flex-col bg-background text-foreground transition-width duration-200 ease-in-out {$showSidebar
			? 'md:max-w-[calc(100%-var(--sidebar-width))]'
			: 'md:max-w-[calc(100%-49px)]'}"
	>
		<div class="flex items-end gap-2 px-4 pt-2 lg:px-6 drag-region">
			{#if $mobile}
				<button
					id="sidebar-toggle-button"
					type="button"
					class="mb-1.5 inline-flex size-8 shrink-0 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
					aria-label={$showSidebar ? $i18n.t('Close Sidebar') : $i18n.t('Open Sidebar')}
					onclick={() => showSidebar.set(!$showSidebar)}
				>
					<PanelLeft class="size-4" />
				</button>
			{/if}
			{#if nav}
				<div class="min-w-0 flex-1">{@render nav()}</div>
			{:else if tabs.length}
				<NavTabs items={tabs} {label} class="min-w-0 flex-1" />
			{/if}
		</div>

		<div
			id={containerId}
			class={cn('flex-1 max-h-full overflow-y-auto px-4 pt-4 pb-6 lg:px-6 lg:pt-5', className)}
		>
			{@render children?.()}
		</div>
	</div>
</Tooltip.Provider>
