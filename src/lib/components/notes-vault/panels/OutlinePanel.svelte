<!-- The note's headings; clicking one scrolls the editor to it. -->
<script lang="ts">
	import { getContext, onDestroy } from 'svelte';
	import { headingsOf, type Heading } from '../markdown';

	const i18n: any = getContext('i18n');

	let { editor }: { editor: any } = $props();

	let headings: Heading[] = $state([]);
	let active = $state(-1);

	const refresh = () => {
		headings = headingsOf(editor);
		if (!editor) return;
		const at = editor.state.selection.from;
		active = headings.reduce((found, h, i) => (h.pos <= at ? i : found), -1);
	};

	let bound: any = null;
	$effect(() => {
		const e = editor;
		if (bound === e) return;
		bound?.off?.('update', refresh);
		bound?.off?.('selectionUpdate', refresh);
		bound = e;
		e?.on?.('update', refresh);
		e?.on?.('selectionUpdate', refresh);
		refresh();
	});

	onDestroy(() => {
		bound?.off?.('update', refresh);
		bound?.off?.('selectionUpdate', refresh);
	});

	const jump = (h: Heading) => {
		if (!editor) return;
		editor
			.chain()
			.focus()
			.setTextSelection(h.pos + 1)
			.run();
		const dom = editor.view.nodeDOM(h.pos) as HTMLElement | null;
		dom?.scrollIntoView({ behavior: 'smooth', block: 'start' });
	};

	const minLevel = $derived(Math.min(...headings.map((h) => h.level), 6));
</script>

<div class="h-full overflow-y-auto px-2 py-2">
	{#each headings as h, i (i)}
		<button
			type="button"
			class="block w-full truncate rounded-md py-1 pr-2 text-left text-sm hover:bg-accent {i ===
			active
				? 'font-medium text-foreground'
				: 'text-muted-foreground'}"
			style="padding-left: {0.5 + (h.level - minLevel) * 0.85}rem"
			onclick={() => jump(h)}
		>
			{h.text || $i18n.t('Untitled')}
		</button>
	{:else}
		<p class="px-2 py-2 text-sm text-muted-foreground">
			{$i18n.t('Headings in the note appear here.')}
		</p>
	{/each}
</div>
