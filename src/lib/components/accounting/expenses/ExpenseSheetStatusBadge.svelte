<!-- An expense sheet's status: the shared StatusBadge (design system → Status map). -->
<script lang="ts">
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';

	let { status }: { status: string } = $props();
</script>

<StatusBadge kind="expense" {status} />
