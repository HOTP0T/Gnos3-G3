<!--
	Gnos3: the vault's home page is shown by the Notes vault in ./+layout.svelte (NotesApp).
	Kept from upstream: /notes?title=…&content=… asks, then creates a note (in the personal vault)
	and opens it. It asks because a link alone must not write into someone's notes.
-->
<script>
	import { getContext, onMount } from 'svelte';

	import dayjs from '$lib/dayjs';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { createNoteHandler } from '$lib/components/notes/utils';

	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';

	const i18n = getContext('i18n');
	const title = $page.url.searchParams.get('title') ?? dayjs().format('YYYY-MM-DD');
	const content = $page.url.searchParams.get('content') ?? '';
	let showConfirm = false;

	onMount(() => {
		if (
			$page.url.searchParams.get('content') !== null ||
			$page.url.searchParams.get('title') !== null
		) {
			showConfirm = true;
		}
	});
</script>

<ConfirmDialog
	bind:show={showConfirm}
	title={$i18n.t('Create a new note')}
	on:confirm={async () => {
		const res = await createNoteHandler(title, content);
		if (res) goto(`/notes/${res.id}`, { replaceState: true });
		else showConfirm = true;
	}}
>
	<div class="text-sm text-gray-500 whitespace-pre-wrap break-words max-h-60 overflow-auto">
		<div class="font-medium">{title}</div>
		{content}
	</div>
</ConfirmDialog>
