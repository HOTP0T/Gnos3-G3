<!--
	Gnos3: the vault's home page is shown by the Notes vault in ./+layout.svelte (NotesApp).
	Kept from upstream: /notes?title=…&content=… creates a note (in the personal vault) and opens it.
-->
<script>
	import { onMount } from 'svelte';
	import dayjs from '$lib/dayjs';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { createNoteHandler } from '$lib/components/notes/utils';

	onMount(async () => {
		if (
			$page.url.searchParams.get('content') !== null ||
			$page.url.searchParams.get('title') !== null
		) {
			const title = $page.url.searchParams.get('title') ?? dayjs().format('YYYY-MM-DD');
			const content = $page.url.searchParams.get('content') ?? '';
			const res = await createNoteHandler(title, content);
			if (res) {
				goto(`/notes/${res.id}`);
			}
		}
	});
</script>
