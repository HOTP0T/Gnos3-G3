<!--
	Decrypt: a text anonymised with "Encrypt" gets its details back with the same key.
	The service opens every [ENC:…] value the key fits and leaves the others as they are.
-->
<script lang="ts">
	import { getContext, onDestroy } from 'svelte';
	import { toast } from 'svelte-sonner';

	import Copy from '@lucide/svelte/icons/copy';
	import Eye from '@lucide/svelte/icons/eye';
	import EyeOff from '@lucide/svelte/icons/eye-off';
	import LockOpen from '@lucide/svelte/icons/lock-open';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import CircleCheck from '@lucide/svelte/icons/circle-check';

	import { decryptText, type DecryptResponse } from '$lib/apis/anonymiser';
	import { copyToClipboard } from '$lib/utils';

	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as InputGroup from '$lib/components/ui/input-group/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';

	const i18n: any = getContext('i18n');

	let text = $state('');
	let key = $state('');
	let showKey = $state(false);
	let busy = $state(false);
	let error = $state('');
	let res = $state<DecryptResponse | null>(null);
	let ctl: AbortController | null = null;

	const canDecrypt = $derived(text.trim().length > 0 && key.length >= 8 && !busy);

	const decrypt = async () => {
		ctl?.abort();
		ctl = new AbortController();
		busy = true;
		error = '';
		try {
			res = await decryptText(text, key, ctl.signal);
		} catch (err) {
			if ((err as Error)?.name === 'AbortError') return;
			res = null;
			error =
				err instanceof TypeError
					? $i18n.t('The Anonymiser service is not reachable.')
					: err instanceof Error
						? err.message
						: `${err}`;
		} finally {
			busy = false;
		}
	};

	onDestroy(() => ctl?.abort());

	const copyResult = async () => {
		if (res && (await copyToClipboard(res.text))) toast.success($i18n.t('Copied to clipboard'));
	};
</script>

<div class="flex flex-col gap-4">
	<div class="flex flex-col gap-1">
		<h1 class="text-2xl font-semibold tracking-tight">{$i18n.t('Decrypt')}</h1>
		<p class="text-sm text-muted-foreground">
			{$i18n.t(
				'Bring back the details of a text encrypted on the Anonymise page, with the same key.'
			)}
		</p>
	</div>

	{#if error}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Something went wrong')}</Alert.Title>
			<Alert.Description>{error}</Alert.Description>
		</Alert.Root>
	{/if}

	<div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
		<Card.Root class="min-w-0">
			<Card.Header>
				<Card.Title>{$i18n.t('Encrypted text')}</Card.Title>
				<Card.Description>{$i18n.t('Paste the text and enter its key.')}</Card.Description>
			</Card.Header>
			<Card.Content class="flex flex-col gap-3">
				<Textarea
					bind:value={text}
					rows={12}
					class="min-h-64 resize-y font-mono text-[0.8125rem]"
					aria-label={$i18n.t('Encrypted text')}
					placeholder={$i18n.t('Paste the text and enter its key.')}
				/>
				<div class="flex flex-col gap-1.5">
					<Label for="anon-decrypt-key">{$i18n.t('Encryption key')}</Label>
					<div class="flex flex-wrap items-center gap-2">
						<InputGroup.Root class="h-9 w-full sm:w-80">
							<InputGroup.Input
								id="anon-decrypt-key"
								type={showKey ? 'text' : 'password'}
								bind:value={key}
								autocomplete="off"
								spellcheck={false}
								class="font-mono"
								placeholder={$i18n.t('At least 8 characters')}
								onkeydown={(e: KeyboardEvent) => {
									if (e.key === 'Enter' && canDecrypt) decrypt();
								}}
							/>
							<InputGroup.Addon align="inline-end">
								<InputGroup.Button
									size="icon-xs"
									aria-label={showKey ? $i18n.t('Hide key') : $i18n.t('Show key')}
									onclick={() => (showKey = !showKey)}
								>
									{#if showKey}<EyeOff />{:else}<Eye />{/if}
								</InputGroup.Button>
							</InputGroup.Addon>
						</InputGroup.Root>
						<Button onclick={decrypt} disabled={!canDecrypt}>
							{#if busy}<Spinner />{:else}<LockOpen />{/if}
							{$i18n.t('Decrypt')}
						</Button>
					</div>
				</div>
			</Card.Content>
		</Card.Root>

		<Card.Root class="min-w-0">
			<Card.Header>
				<Card.Title>{$i18n.t('Restored text')}</Card.Title>
				<Card.Description>
					{#if res}
						{$i18n.t('{{restored}} restored, {{failed}} could not be opened with this key', {
							restored: res.restored,
							failed: res.failed
						})}
					{:else}
						{$i18n.t('The restored text appears here.')}
					{/if}
				</Card.Description>
				<Card.Action>
					<Tip content={$i18n.t('Copy')}>
						<Button
							variant="ghost"
							size="icon-sm"
							aria-label={$i18n.t('Copy')}
							disabled={!res}
							onclick={copyResult}><Copy /></Button
						>
					</Tip>
				</Card.Action>
			</Card.Header>
			<Card.Content class="flex flex-col gap-3">
				{#if !res}
					<Empty.Root class="min-h-64 border border-dashed">
						<Empty.Header>
							<Empty.Media variant="icon"><LockOpen /></Empty.Media>
							<Empty.Title>{$i18n.t('Nothing decrypted yet')}</Empty.Title>
							<Empty.Description>
								{$i18n.t('Only the person who has the key can bring the details back.')}
							</Empty.Description>
						</Empty.Header>
					</Empty.Root>
				{:else}
					{#if res.restored === 0 && res.failed === 0}
						<p class="text-sm text-muted-foreground">
							{$i18n.t('No encrypted details were found in this text.')}
						</p>
					{:else if res.failed > 0}
						<p class="flex items-start gap-1.5 text-sm text-warning">
							<CircleAlert class="mt-0.5 size-4 shrink-0" />
							{$i18n.t('Some details stay encrypted: they were made with another key.')}
						</p>
					{:else}
						<p class="flex items-start gap-1.5 text-sm text-success">
							<CircleCheck class="mt-0.5 size-4 shrink-0" />
							{$i18n.t('Every encrypted detail was restored.')}
						</p>
					{/if}
					<div
						class="min-h-64 rounded-md border border-input bg-muted/30 px-3 py-2 text-sm leading-7 break-words whitespace-pre-wrap"
					>
						{res.text}
					</div>
				{/if}
			</Card.Content>
		</Card.Root>
	</div>
</div>
