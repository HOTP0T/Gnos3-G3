<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { WEBUI_API_BASE_URL } from '$lib/constants';
	import FullHeightIframe from '$lib/components/common/FullHeightIframe.svelte';
	import { OFFICE_BASE_URL } from '$lib/constants';
	import { getOfficeExchangeToken } from '$lib/apis/office';

	const i18n = getContext('i18n');

	let iframeSrc: string | null = null;
	let error: string | null = null;
	let loading = true;
	let syncing = false;
	let syncMessage = '';
	let knowledgeId: string | null = null;
	let syncError = false;
	let container: HTMLDivElement;
	const publishSyncState = () => {
		container?.querySelector('iframe')?.contentWindow?.postMessage(
			{
				type: 'office-knowledge:state',
				syncing,
				message: syncMessage,
				error: syncError,
				hasKnowledge: Boolean(knowledgeId)
			},
			new URL(OFFICE_BASE_URL).origin
		);
	};
	const onOfficeMessage = (event: MessageEvent) => {
		if (
			event.origin !== new URL(OFFICE_BASE_URL).origin ||
			event.source !== container?.querySelector('iframe')?.contentWindow
		)
			return;
		if (event.data?.type === 'office-knowledge:ready') {
			publishSyncState();
			startAutoSync();
		}
		if (event.data?.type === 'office-knowledge:sync') void syncFiles();
		if (event.data?.type === 'office-knowledge:open' && knowledgeId)
			void goto(`/workspace/knowledge/${encodeURIComponent(knowledgeId)}`);
	};
	// Keeps the user's private "SmartOffice Files" knowledge base current without a
	// click: when Office has loaded, every few minutes while it is open, and once
	// more on leaving. Office is only usable inside this page, so every change
	// happens while it is mounted. Quiet: only the knowledge link is updated.
	const AUTO_SYNC_MS = 5 * 60 * 1000;
	let autoTimer: ReturnType<typeof setInterval> | null = null;
	let autoRun: Promise<void> | null = null;
	const autoSync = (keepalive = false) => {
		if (syncing || autoRun) return autoRun;
		autoRun = fetch(`${WEBUI_API_BASE_URL}/office-knowledge/sync?auto=true`, {
			method: 'POST',
			headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
			keepalive
		})
			.then(async (response) => {
				if (!response.ok) return;
				const result = await response.json().catch(() => ({}));
				if (result.knowledge_id && result.knowledge_id !== knowledgeId) {
					knowledgeId = result.knowledge_id;
					publishSyncState();
				}
			})
			.catch(() => {})
			.finally(() => {
				autoRun = null;
			});
		return autoRun;
	};
	const startAutoSync = () => {
		if (autoTimer) return;
		void autoSync();
		autoTimer = setInterval(() => void autoSync(), AUTO_SYNC_MS);
	};
	const syncFiles = async () => {
		if (syncing) return;
		// A background run holds the per-user lock; let it finish first.
		await autoRun;
		syncing = true;
		syncError = false;
		syncMessage = $i18n.t('Importing your saved SmartOffice files…');
		publishSyncState();
		try {
			const response = await fetch(`${WEBUI_API_BASE_URL}/office-knowledge/sync`, {
				method: 'POST',
				headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
			});
			const result = await response.json().catch(() => ({}));
			if (!response.ok)
				throw new Error(
					typeof result.detail === 'string'
						? $i18n.t(result.detail)
						: $i18n.t('SmartOffice import failed. Please try again.')
				);
			knowledgeId = result.knowledge_id || null;
			if (result.errors) {
				syncError = true;
				syncMessage = `${$i18n.t('{{files}} file(s) indexed; {{errors}} need attention.', {
					files: result.files,
					errors: result.errors
				})} ${result.failures?.[0]?.reason || $i18n.t('Try again.')}`;
			} else {
				syncMessage = result.files
					? $i18n.t('{{files}} file(s) available in SmartOffice Files.', { files: result.files })
					: $i18n.t('SmartOffice Files is ready. Saved documents are added automatically.');
			}
		} catch (error) {
			syncError = true;
			syncMessage = error instanceof Error ? error.message : $i18n.t('SmartOffice import failed.');
		} finally {
			syncing = false;
			publishSyncState();
		}
	};

	// Office has no theme switch of its own inside Gnos3: it gets the theme at
	// sign-in (?theme=) and every later change (Settings → Theme, or the OS when
	// the theme is "System") through this message.
	const currentTheme = () =>
		document.documentElement.classList.contains('dark') ? 'dark' : 'light';
	let sentTheme = '';
	const sendTheme = () => {
		const theme = currentTheme();
		if (theme === sentTheme) return;
		sentTheme = theme;
		container
			?.querySelector('iframe')
			?.contentWindow?.postMessage({ type: 'gnos3:theme', theme }, new URL(OFFICE_BASE_URL).origin);
	};
	onMount(() => {
		window.addEventListener('message', onOfficeMessage);
		const themeObserver = new MutationObserver(sendTheme);
		themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
		void (async () => {
			try {
				const token = localStorage.getItem('token');
				if (!token) {
					throw new Error('Not authenticated');
				}
				// Fetch a fresh 5-min exchange token at mount time (too short-lived to
				// pre-bake) and hand it to the module's /sso bootstrap route.
				const { token: exchangeToken } = await getOfficeExchangeToken(token);
				const theme = currentTheme();
				sentTheme = theme;
				const lang = localStorage.getItem('locale') || 'en-US';
				iframeSrc = `${OFFICE_BASE_URL}/sso?gnos3_token=${encodeURIComponent(exchangeToken)}&theme=${theme}&lang=${encodeURIComponent(lang)}`;
			} catch (err) {
				error = err instanceof Error ? err.message : String(err);
			} finally {
				loading = false;
			}
		})();
		return () => {
			window.removeEventListener('message', onOfficeMessage);
			themeObserver.disconnect();
			if (autoTimer) {
				clearInterval(autoTimer);
				void autoSync(true);
			}
		};
	});
</script>

<div bind:this={container} class="w-full h-full flex flex-col min-h-0">
	<div class="flex-1 min-h-0">
		{#if iframeSrc}
			<!-- Office runs on its own origin (:8004).
		     allowSameOrigin lets the embedded SPA use its own localStorage/session;
		     it does NOT grant access to the Gnos3 origin (blocked by the same-origin
		     policy). Modals: Print in the editors; popups escape the sandbox so links
		     open as normal tabs; clipboard + fullscreen: copy/paste and the slideshow. -->
			<FullHeightIframe
				src={iframeSrc}
				title="SmartOffice"
				allowScripts={true}
				allowForms={true}
				allowSameOrigin={true}
				allowPopups={true}
				allowDownloads={true}
				allowModals={true}
				allowPopupsToEscapeSandbox={true}
				allow="clipboard-read; clipboard-write; fullscreen"
				iframeClassName="w-full h-full rounded-2xl border-0"
			/>
		{:else if loading}
			<div class="flex items-center justify-center h-full text-gray-500 text-sm">
				{$i18n.t('Loading SmartOffice…')}
			</div>
		{:else}
			<div class="flex flex-col items-center justify-center h-full gap-2 text-gray-500 text-sm">
				<div>{$i18n.t('Could not load SmartOffice.')}</div>
				{#if error}<div class="text-xs text-gray-400">{error}</div>{/if}
			</div>
		{/if}
	</div>
</div>
