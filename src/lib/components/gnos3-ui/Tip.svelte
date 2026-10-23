<!--
	A tooltip around any control (design system → neutral tooltip: foreground fill, 12px text).
	Icon-only buttons need one, plus an aria-label on the button itself.

	<Tip content={$i18n.t('Delete')}>
		<Button variant="ghost" size="icon-sm" aria-label={$i18n.t('Delete')}><Trash2 /></Button>
	</Tip>

	Needs a Tooltip.Provider above it; ModuleShell has one.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import * as Tooltip from '$lib/components/ui/tooltip/index.js';

	let {
		content,
		side = 'top',
		disabled = false,
		children
	}: {
		content: string | null | undefined;
		side?: 'top' | 'right' | 'bottom' | 'left';
		disabled?: boolean;
		children: Snippet;
	} = $props();
</script>

{#if content && !disabled}
	<Tooltip.Root>
		<Tooltip.Trigger>
			{#snippet child({ props })}
				<span {...props} class="inline-flex">{@render children()}</span>
			{/snippet}
		</Tooltip.Trigger>
		<Tooltip.Content {side} sideOffset={4}>{content}</Tooltip.Content>
	</Tooltip.Root>
{:else}
	{@render children()}
{/if}
