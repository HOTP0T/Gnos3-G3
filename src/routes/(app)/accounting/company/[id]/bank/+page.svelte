<script lang="ts">
	import { page } from '$app/stores';
	import BankReconciliation from '$lib/components/accounting/BankReconciliation.svelte';

	$: companyId = parseInt($page.params.id ?? '', 10);
</script>

<BankReconciliation {companyId} />
