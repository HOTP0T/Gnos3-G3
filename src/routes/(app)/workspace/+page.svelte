<script lang="ts">
	import { goto } from '$app/navigation';
	import { config, user, isAdmin } from '$lib/stores';
	import { onMount } from 'svelte';

	onMount(() => {
		if (!$isAdmin) {
			if ($user?.permissions?.workspace?.models) {
				goto('/workspace/models', { replaceState: true });
			} else if ($user?.permissions?.workspace?.knowledge) {
				goto('/workspace/knowledge', { replaceState: true });
			} else if ($user?.permissions?.workspace?.prompts) {
				goto('/workspace/prompts', { replaceState: true });
			} else if ($config?.features?.enable_tools && $user?.permissions?.workspace?.tools) {
				goto('/workspace/tools', { replaceState: true });
			} else if ($user?.permissions?.workspace?.skills) {
				goto('/workspace/skills', { replaceState: true });
			} else {
				goto('/', { replaceState: true });
			}
		} else {
			goto('/workspace/models', { replaceState: true });
		}
	});
</script>
