<!--
	Anonymiser settings (admins): what is hidden by default — in the chat's Anonymise switch and
	as the starting point of the Anonymise page — how sure a detection must be, and two word lists.
-->
<script lang="ts">
	import { getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';

	import Save from '@lucide/svelte/icons/save';

	import { saveAnonymiserSettings, type AnonymiserKind } from '$lib/apis/anonymiser';

	import * as Card from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Switch } from '$lib/components/ui/switch/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';

	import {
		ANONYMISER_CONTEXT,
		KIND_LABELS,
		KIND_ORDER,
		KIND_STYLE,
		type AnonymiserState
	} from './kinds';

	const i18n: any = getContext('i18n');
	const anon: AnonymiserState = getContext(ANONYMISER_CONTEXT);

	let kinds = $state<Partial<Record<AnonymiserKind, boolean>>>({});
	let threshold = $state(0.35);
	let allowText = $state('');
	let denyText = $state('');
	let saving = $state(false);
	let ready = $state(false);

	const lines = (s: string) =>
		s
			.split('\n')
			.map((l) => l.trim())
			.filter(Boolean);

	const fill = () => {
		const s = anon.settings;
		if (!s) return;
		const next: Partial<Record<AnonymiserKind, boolean>> = {};
		for (const k of KIND_ORDER) next[k] = Boolean(s.kinds?.[k]);
		kinds = next;
		threshold = s.threshold ?? 0.35;
		allowText = (s.allow_list ?? []).join('\n');
		denyText = (s.deny_list ?? []).join('\n');
		ready = true;
	};

	$effect(() => {
		if (anon.loading) return;
		if (!anon.canEdit) {
			goto('/anonymiser');
			return;
		}
		if (!ready) fill();
	});

	const save = async () => {
		saving = true;
		try {
			const res = await saveAnonymiserSettings({
				kinds,
				threshold,
				allow_list: lines(allowText),
				deny_list: lines(denyText)
			});
			anon.settings = res.settings;
			ready = false;
			fill();
			toast.success($i18n.t('Settings saved'));
		} catch (err) {
			toast.error(err instanceof Error ? err.message : `${err}`);
		}
		saving = false;
	};
</script>

<div class="flex max-w-3xl flex-col gap-4">
	<div class="flex flex-col gap-1">
		<h1 class="text-2xl font-semibold tracking-tight">{$i18n.t('Anonymiser settings')}</h1>
		<p class="text-sm text-muted-foreground">
			{$i18n.t(
				'These defaults apply to the Anonymise switch in chat and to the Anonymise page, for everyone on this server.'
			)}
		</p>
	</div>

	{#if !ready}
		<Skeleton class="h-64 rounded-xl" />
		<Skeleton class="h-40 rounded-xl" />
	{:else}
		<Card.Root>
			<Card.Header>
				<Card.Title>{$i18n.t('What to hide')}</Card.Title>
				<Card.Description>
					{$i18n.t('Each kind of detail that is hidden unless someone switches it off.')}
				</Card.Description>
			</Card.Header>
			<Card.Content>
				<ul class="grid gap-x-8 gap-y-3 sm:grid-cols-2">
					{#each KIND_ORDER as k (k)}
						<li class="flex items-center justify-between gap-3">
							<Label for="anon-default-{k}" class="flex items-center gap-2 font-normal">
								<span class="size-2.5 shrink-0 rounded-full {KIND_STYLE[k].dot}"></span>
								{$i18n.t(KIND_LABELS[k])}
							</Label>
							<Switch
								id="anon-default-{k}"
								bind:checked={() => Boolean(kinds[k]), (v) => (kinds[k] = v)}
							/>
						</li>
					{/each}
				</ul>
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Header>
				<Card.Title>{$i18n.t('Detection')}</Card.Title>
				<Card.Description>
					{$i18n.t(
						'How sure the detection must be before a detail is hidden. Lower finds more, but also hides more by mistake.'
					)}
				</Card.Description>
			</Card.Header>
			<Card.Content class="flex items-center gap-4">
				<Label for="anon-threshold" class="sr-only">{$i18n.t('Confidence threshold')}</Label>
				<input
					id="anon-threshold"
					type="range"
					min="0.05"
					max="0.95"
					step="0.05"
					bind:value={threshold}
					class="h-2 w-full max-w-sm cursor-pointer accent-primary"
				/>
				<span class="w-12 text-sm tabular-nums">{Math.round(threshold * 100)}%</span>
			</Card.Content>
			<Card.Footer>
				<p class="text-xs text-muted-foreground">
					{$i18n.t('35% is a good start: at 50% and above, phone numbers are often missed.')}
				</p>
			</Card.Footer>
		</Card.Root>

		<Card.Root>
			<Card.Header>
				<Card.Title>{$i18n.t('Word lists')}</Card.Title>
				<Card.Description>{$i18n.t('One word or phrase per line.')}</Card.Description>
			</Card.Header>
			<Card.Content class="grid gap-4 sm:grid-cols-2">
				<div class="flex flex-col gap-1.5">
					<Label for="anon-allow">{$i18n.t('Never hide')}</Label>
					<Textarea
						id="anon-allow"
						bind:value={allowText}
						rows={6}
						class="font-mono text-[0.8125rem]"
					/>
					<p class="text-xs text-muted-foreground">
						{$i18n.t('For example your own company name, so it stays readable.')}
					</p>
				</div>
				<div class="flex flex-col gap-1.5">
					<Label for="anon-deny">{$i18n.t('Always hide')}</Label>
					<Textarea
						id="anon-deny"
						bind:value={denyText}
						rows={6}
						class="font-mono text-[0.8125rem]"
					/>
					<p class="text-xs text-muted-foreground">
						{$i18n.t('For example client code names that detection cannot know.')}
					</p>
				</div>
			</Card.Content>
		</Card.Root>

		<div class="flex justify-end">
			<Button onclick={save} disabled={saving}>
				{#if saving}<Spinner />{:else}<Save />{/if}
				{$i18n.t('Save')}
			</Button>
		</div>
	{/if}
</div>
