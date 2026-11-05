<!--
	A drawn ```mermaid block in a note (mounted by MermaidBlocks.svelte.ts). Click the picture to
	edit its source; while the source has an error, the last good picture stays, dimmed.
-->
<script lang="ts">
	import { getContext } from 'svelte';
	import fileSaver from 'file-saver';
	import Download from '@lucide/svelte/icons/download';
	import Maximize2 from '@lucide/svelte/icons/maximize-2';
	import Pencil from '@lucide/svelte/icons/pencil';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import PanzoomContainer from '$lib/components/common/PanzoomContainer.svelte';
	import { OUTSIDE_CONTENT_REFUSED } from './mermaidDraw';

	const { saveAs } = fileSaver;
	const i18n: any = getContext('i18n');

	let {
		svg = '',
		error = '',
		drawing = false,
		empty = false,
		editable = false,
		editing = false,
		onEdit = () => {}
	}: {
		svg?: string;
		error?: string;
		drawing?: boolean;
		empty?: boolean;
		editable?: boolean;
		editing?: boolean;
		onEdit?: () => void;
	} = $props();

	let enlarged = $state(false);
	let panzoom: any = $state(null);

	const onPictureClick = (event: MouseEvent) => {
		if ((event.target as Element).closest('a')) return;
		if (editable) onEdit();
		else enlarged = true;
	};

	const download = () => saveAs(new Blob([svg], { type: 'image/svg+xml' }), 'diagram.svg');
</script>

<!-- mousedown keeps the caret where it is: this widget sits inside the editor. -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	class="note-mermaid-frame group relative rounded-lg border border-border bg-card p-3"
	onmousedown={(event) => event.preventDefault()}
>
	{#if error}
		<div class="mb-2 flex gap-2 text-sm text-destructive" role="alert">
			<TriangleAlert class="mt-0.5 size-4 shrink-0" />
			<div class="min-w-0">
				<div class="font-medium">{$i18n.t("This diagram can't be drawn")}</div>
				<div class="mt-1 font-mono text-xs break-words whitespace-pre-wrap">
					{error === OUTSIDE_CONTENT_REFUSED
						? $i18n.t("Diagrams can't load images or styles from other sites.")
						: error}
				</div>
			</div>
		</div>
	{/if}

	{#if svg}
		<button
			type="button"
			class="note-mermaid-picture block w-full cursor-pointer text-left {error ? 'opacity-40' : ''}"
			aria-label={editable ? $i18n.t('Edit diagram') : $i18n.t('Enlarge diagram')}
			onclick={onPictureClick}
		>
			{@html svg}
		</button>

		<div
			class="note-mermaid-tools absolute top-2 right-2 flex gap-1 opacity-0 transition-opacity group-focus-within:opacity-100 group-hover:opacity-100"
		>
			{#if editable && !editing}
				<Button
					variant="outline"
					size="icon"
					class="size-7"
					title={$i18n.t('Edit diagram')}
					aria-label={$i18n.t('Edit diagram')}
					onclick={() => onEdit()}
				>
					<Pencil class="size-3.5" />
				</Button>
			{/if}
			<Button
				variant="outline"
				size="icon"
				class="size-7"
				title={$i18n.t('Enlarge diagram')}
				aria-label={$i18n.t('Enlarge diagram')}
				onclick={() => (enlarged = true)}
			>
				<Maximize2 class="size-3.5" />
			</Button>
		</div>
	{:else if drawing}
		<p class="m-0 text-sm text-muted-foreground">{$i18n.t('Drawing the diagram…')}</p>
	{:else if empty}
		<p class="m-0 text-sm text-muted-foreground">
			{$i18n.t('Write the diagram in Mermaid in the block above.')}
		</p>
	{/if}
</div>

<Dialog.Root bind:open={enlarged}>
	<Dialog.Content class="flex h-[85vh] max-w-[92vw] flex-col sm:max-w-[92vw]">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Diagram')}</Dialog.Title>
			<Dialog.Description>{$i18n.t('Scroll to zoom, drag to move.')}</Dialog.Description>
		</Dialog.Header>
		<div
			class="note-mermaid-zoom min-h-0 flex-1 overflow-hidden rounded-lg border border-border bg-card"
		>
			{#if enlarged}
				<PanzoomContainer
					bind:this={panzoom}
					className="flex h-full w-full items-center justify-center"
				>
					{@html svg}
				</PanzoomContainer>
			{/if}
		</div>
		<Dialog.Footer>
			<Button variant="outline" onclick={() => panzoom?.reset()}>
				<RotateCcw class="size-4" />
				{$i18n.t('Reset view')}
			</Button>
			<Button variant="outline" onclick={download}>
				<Download class="size-4" />
				{$i18n.t('Download as SVG')}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<style>
	.note-mermaid-picture :global(svg) {
		display: block;
		height: auto;
		margin-inline: auto;
	}
	.note-mermaid-zoom :global(svg) {
		width: 100%;
		height: 100%;
		max-width: none !important;
	}
	@media (hover: none) {
		.note-mermaid-tools {
			opacity: 1;
		}
	}
</style>
