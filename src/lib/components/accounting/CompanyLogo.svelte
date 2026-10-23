<!--
	A company's logo, or its initials when it has none. Decorative: the company name is always
	shown next to it. Pass `src` to show a picked file before it is uploaded (null = no logo).
-->
<script lang="ts">
	import { cn } from '$lib/utils/shadcn.js';
	import { companyInitials, logoBlobUrl } from './companyLogo';

	let {
		company,
		src = undefined,
		size = 'default',
		class: className = ''
	}: {
		company: { id: number; name: string; logo_updated_at?: string | null };
		src?: string | null;
		size?: 'sm' | 'default' | 'lg';
		class?: string;
	} = $props();

	const BOX = {
		sm: 'size-8 text-xs',
		default: 'size-10 text-sm',
		lg: 'size-16 text-lg'
	};
	// logos are drawn for a white page, so they sit on white in both themes
	const PAD = { sm: 'p-0.5', default: 'p-1', lg: 'p-1.5' };

	const key = $derived(company?.logo_updated_at ? `${company.id}:${company.logo_updated_at}` : '');
	let fetched = $state<{ key: string; url: string | null } | null>(null);

	$effect(() => {
		if (!key || src !== undefined) return;
		const k = key;
		let live = true;
		logoBlobUrl(company).then((url) => {
			if (live) fetched = { key: k, url };
		});
		return () => {
			live = false;
		};
	});

	const url = $derived(src !== undefined ? src : fetched?.key === key ? fetched.url : null);
</script>

<span
	aria-hidden="true"
	class={cn(
		'flex shrink-0 items-center justify-center overflow-hidden rounded-lg border select-none',
		BOX[size],
		url ? ['bg-white', PAD[size]] : 'bg-muted font-medium text-muted-foreground',
		className
	)}
>
	{#if url}
		<img src={url} alt="" draggable="false" class="size-full object-contain" />
	{:else}
		{companyInitials(company?.name ?? '')}
	{/if}
</span>
