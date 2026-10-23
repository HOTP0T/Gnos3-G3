<!--
	A confirmation (design system → Writing: the title asks the question, the body says what will
	be lost, the button repeats the verb). Use it instead of window.confirm().

	<ConfirmDialog bind:open title={$i18n.t('Delete invoice?')}
		description={$i18n.t('… cannot be undone.')} confirmLabel={$i18n.t('Delete')} destructive
		onconfirm={remove} />
-->
<script lang="ts">
	import { getContext } from 'svelte';
	import * as AlertDialog from '$lib/components/ui/alert-dialog/index.js';
	import { buttonVariants } from '$lib/components/ui/button/index.js';
	import Spinner from '$lib/components/ui/spinner/spinner.svelte';

	const i18n: any = getContext('i18n');

	let {
		open = $bindable(false),
		title,
		description = '',
		confirmLabel,
		cancelLabel = undefined,
		destructive = false,
		onconfirm,
		oncancel = undefined
	}: {
		open?: boolean;
		title: string;
		description?: string;
		confirmLabel: string;
		cancelLabel?: string;
		destructive?: boolean;
		onconfirm: () => void | Promise<void>;
		oncancel?: () => void;
	} = $props();

	let busy = $state(false);

	async function confirm(e: Event) {
		e.preventDefault();
		busy = true;
		try {
			await onconfirm();
			open = false;
		} finally {
			busy = false;
		}
	}
</script>

<AlertDialog.Root
	bind:open
	onOpenChange={(v) => {
		if (!v) oncancel?.();
	}}
>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>{title}</AlertDialog.Title>
			{#if description}<AlertDialog.Description>{description}</AlertDialog.Description>{/if}
		</AlertDialog.Header>
		<AlertDialog.Footer>
			<AlertDialog.Cancel class={buttonVariants({ variant: 'outline' })} disabled={busy}>
				{cancelLabel ?? $i18n.t('Cancel')}
			</AlertDialog.Cancel>
			<AlertDialog.Action
				class={buttonVariants({ variant: destructive ? 'destructive' : 'default' })}
				disabled={busy}
				onclick={confirm}
			>
				{#if busy}<Spinner />{/if}
				{confirmLabel}
			</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>
