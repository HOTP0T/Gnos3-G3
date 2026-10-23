<script lang="ts">
	// Recent activity — reuses the existing AuditTrail component (which keeps its own styling).
	import AuditTrail from '$lib/components/accounting/AuditTrail.svelte';
	export let companyId: number;
	export let options: { limit?: number } = {};
	$: limit = options?.limit ?? 12;
</script>

<div class="h-full overflow-y-auto border-t px-4 py-3">
	<AuditTrail {companyId} {limit} />
</div>
