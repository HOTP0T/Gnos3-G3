<script lang="ts">
	import { onMount, onDestroy, getContext } from 'svelte';
	import FullHeightIframe from '$lib/components/common/FullHeightIframe.svelte';
	import { FINANCES_BASE_URL } from '$lib/constants';
	import { getFinancesExchangeToken } from '$lib/apis/finances';

	const i18n: any = getContext('i18n');

	let iframeSrc: string | null = null;
	let error: string | null = null;
	let loading = true;
	let container: HTMLDivElement;

	// Finances shows no theme switch inside Gnos3: it gets the theme (and the UI language) at
	// sign-in (?theme=&lang=) and every later theme change (Settings → Theme, or the OS when the
	// theme is "System") through this message — the same handshake as Office (MODULE-GUIDE.md §2.4).
	const currentTheme = () =>
		document.documentElement.classList.contains('dark') ? 'dark' : 'light';
	let sentTheme = '';
	const sendTheme = () => {
		const theme = currentTheme();
		if (theme === sentTheme) return;
		sentTheme = theme;
		container
			?.querySelector('iframe')
			?.contentWindow?.postMessage({ type: 'gnos3:theme', theme }, new URL(FINANCES_BASE_URL).origin);
	};
	let themeObserver: MutationObserver | null = null;

	onMount(async () => {
		themeObserver = new MutationObserver(sendTheme);
		themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
		try {
			const token = localStorage.getItem('token');
			if (!token) {
				throw new Error('Not authenticated');
			}
			// Fetch a fresh 5-min exchange token at mount time (too short-lived to
			// pre-bake) and hand it to the module's /sso bootstrap route.
			const { token: exchangeToken } = await getFinancesExchangeToken(token);
			const theme = currentTheme();
			sentTheme = theme;
			const lang = localStorage.getItem('locale') || 'en-US';
			iframeSrc = `${FINANCES_BASE_URL}/sso?gnos3_token=${encodeURIComponent(exchangeToken)}&theme=${theme}&lang=${encodeURIComponent(lang)}`;
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	});

	onDestroy(() => themeObserver?.disconnect());
</script>

<div class="w-full h-full" bind:this={container}>
	{#if iframeSrc}
		<!-- The Finances module (ledger-sync) runs on its own origin (:8003).
		     allowSameOrigin lets the embedded SPA use its own localStorage/session;
		     it does NOT grant access to the Gnos3 origin (blocked by the same-origin
		     policy). -->
		<FullHeightIframe
			src={iframeSrc}
			title="Finances"
			allowScripts={true}
			allowForms={true}
			allowSameOrigin={true}
			allowPopups={true}
			allowDownloads={true}
			iframeClassName="w-full h-full rounded-2xl border-0"
		/>
	{:else if loading}
		<div class="flex items-center justify-center h-full text-muted-foreground text-sm">
			{$i18n.t('Loading Finances…')}
		</div>
	{:else}
		<div class="flex flex-col items-center justify-center h-full gap-2 text-muted-foreground text-sm">
			<div>{$i18n.t('Could not load Finances.')}</div>
			{#if error}<div class="text-xs">{error}</div>{/if}
		</div>
	{/if}
</div>
