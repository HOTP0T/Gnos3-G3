<!--
	The Anonymiser tool: paste a text, see what was found, adjust, copy the result.
	Findings come from the service (analyze, debounced); the user can unmark a finding or hide
	a selection of their own, and the result is the service's anonymize of exactly that list.
-->
<script lang="ts">
	import { getContext, onMount, onDestroy, untrack } from 'svelte';
	import { toast } from 'svelte-sonner';

	import Copy from '@lucide/svelte/icons/copy';
	import Download from '@lucide/svelte/icons/download';
	import Eye from '@lucide/svelte/icons/eye';
	import EyeOff from '@lucide/svelte/icons/eye-off';
	import Info from '@lucide/svelte/icons/info';
	import Pencil from '@lucide/svelte/icons/pencil';
	import ScanText from '@lucide/svelte/icons/scan-text';
	import ShieldCheck from '@lucide/svelte/icons/shield-check';
	import SlidersHorizontal from '@lucide/svelte/icons/sliders-horizontal';
	import Eraser from '@lucide/svelte/icons/eraser';
	import X from '@lucide/svelte/icons/x';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import KeyRound from '@lucide/svelte/icons/key-round';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';

	import {
		analyzeText,
		anonymizeText,
		type AnonymiserFinding,
		type AnonymiserKind,
		type AnonymiserLanguage,
		type AnonymiserMode,
		type AnonymiserModeOptions
	} from '$lib/apis/anonymiser';
	import { copyToClipboard } from '$lib/utils';

	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Popover from '$lib/components/ui/popover/index.js';
	import * as Tabs from '$lib/components/ui/tabs/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Switch } from '$lib/components/ui/switch/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import * as InputGroup from '$lib/components/ui/input-group/index.js';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';

	import {
		ANONYMISER_CONTEXT,
		ENTITY_LABELS,
		ENTITY_SAME_AS_KIND,
		KIND_LABELS,
		KIND_ORDER,
		KIND_STYLE,
		LANGUAGE_NAMES,
		MODE_LABELS,
		MODE_ORDER,
		type AnonymiserState
	} from './kinds';

	const i18n: any = getContext('i18n');
	const anon: AnonymiserState = getContext(ANONYMISER_CONTEXT);

	type Span = AnonymiserFinding & { custom: boolean; off: boolean };
	type Segment = { start: number; end: number; span: Span | null };

	let text = $state('');
	let language = $state<AnonymiserLanguage>('auto');
	let mode = $state<AnonymiserMode>('labels');
	let kinds = $state<Partial<Record<AnonymiserKind, boolean>>>({});
	let view = $state<'edit' | 'review'>('edit');

	// What the service found in `analyzedText`, what the user unmarked, what they added.
	let analyzedText = $state('');
	let detected = $state<AnonymiserFinding[]>([]);
	let detectedLanguage = $state('');
	let unmarked = $state<string[]>([]);
	let added = $state<AnonymiserFinding[]>([]);

	let result = $state('');
	let analyzing = $state(false);
	let anonymizing = $state(false);
	let error = $state('');
	let selection = $state<{ start: number; end: number } | null>(null);
	let reviewEl: HTMLElement | null = $state(null);

	// Per run, starting from the admin's defaults: how sure a detection must be, two word lists.
	let threshold = $state(0.35);
	let allowText = $state('');
	let denyText = $state('');
	let optionsReady = $state(false);
	let explain = $state(false);

	// Options of the hiding modes.
	let maskChar = $state('*');
	let maskCount = $state(0);
	let maskFromEnd = $state(false);
	let encKey = $state('');
	let showKey = $state(false);

	let lastText = '';
	let analyzeSeq = 0;
	let anonymizeSeq = 0;
	let analyzeCtl: AbortController | null = null;
	let anonymizeCtl: AbortController | null = null;

	const keyOf = (f: { start: number; end: number }) => `${f.start}:${f.end}`;
	const overlaps = (a: { start: number; end: number }, b: { start: number; end: number }) =>
		a.start < b.end && b.start < a.end;
	const messageOf = (err: unknown) =>
		err instanceof TypeError
			? $i18n.t('The Anonymiser service is not reachable.')
			: err instanceof Error
				? err.message
				: `${err}`;

	const lines = (s: string) =>
		s
			.split('\n')
			.map((l) => l.trim())
			.filter(Boolean);

	// The switches, threshold and word lists start from the admin's defaults; changing them here
	// only affects this text.
	const resetToDefaults = () => {
		const s = anon.settings;
		if (!s) return;
		const next: Partial<Record<AnonymiserKind, boolean>> = {};
		for (const k of KIND_ORDER) next[k] = Boolean(s.kinds?.[k]);
		kinds = next;
		threshold = s.threshold ?? 0.35;
		allowText = (s.allow_list ?? []).join('\n');
		denyText = (s.deny_list ?? []).join('\n');
		optionsReady = true;
	};

	$effect(() => {
		if (anon.settings && !untrack(() => optionsReady)) untrack(resetToDefaults);
	});

	// Find (debounced) whenever the text, the language or a per-run option changes.
	$effect(() => {
		const t = text;
		const lang = language;
		const k = JSON.stringify(kinds);
		const extra = optionsReady
			? {
					threshold,
					allow_list: lines(allowText),
					deny_list: lines(denyText),
					explain
				}
			: { explain };
		if (anon.loading) return;
		untrack(() => {
			if (t !== lastText) {
				// Offsets no longer match: drop the user's edits on the old text.
				lastText = t;
				unmarked = [];
				added = [];
				selection = null;
			}
		});
		if (!t.trim()) {
			analyzeCtl?.abort();
			analyzeSeq++;
			untrack(() => {
				analyzedText = '';
				detected = [];
				detectedLanguage = '';
				result = '';
				analyzing = false;
				error = '';
			});
			return;
		}
		const timer = setTimeout(() => runAnalyze(t, lang, JSON.parse(k), extra), 400);
		return () => clearTimeout(timer);
	});

	async function runAnalyze(
		t: string,
		lang: AnonymiserLanguage,
		k: Partial<Record<AnonymiserKind, boolean>>,
		extra: { threshold?: number; allow_list?: string[]; deny_list?: string[]; explain: boolean }
	) {
		const seq = ++analyzeSeq;
		analyzeCtl?.abort();
		analyzeCtl = new AbortController();
		analyzing = true;
		try {
			// No switches yet (settings not loaded): let the service use its defaults.
			const options = { language: lang, kinds: Object.keys(k).length ? k : undefined, ...extra };
			const res = await analyzeText(t, options, analyzeCtl.signal);
			if (seq !== analyzeSeq) return;
			detected = res.findings ?? [];
			detectedLanguage = res.language ?? '';
			analyzedText = t;
			error = '';
		} catch (err) {
			if (seq !== analyzeSeq || (err as Error)?.name === 'AbortError') return;
			error = messageOf(err);
		} finally {
			if (seq === analyzeSeq) analyzing = false;
		}
	}

	// What will be hidden: the findings the user kept, plus their own selections
	// (a selection replaces any finding it overlaps).
	const effective = $derived.by(() => {
		const auto = detected.filter(
			(f) => !unmarked.includes(keyOf(f)) && !added.some((c) => overlaps(c, f))
		);
		return [...auto, ...added].sort((a, b) => a.start - b.start);
	});

	// What the chosen mode needs besides the text.
	const modeOptions = $derived.by((): AnonymiserModeOptions => {
		if (mode === 'mask')
			return {
				mask_char: maskChar || '*',
				mask_count: Math.max(0, Math.floor(Number(maskCount) || 0)),
				mask_from_end: maskFromEnd
			};
		if (mode === 'encrypt') return { key: encKey };
		return {};
	});
	const keyTooShort = $derived(mode === 'encrypt' && encKey.length < 8);

	// The result follows every change of the list, the mode or its options.
	$effect(() => {
		const t = analyzedText;
		const m = mode;
		const opts = modeOptions;
		const list = effective.map(({ start, end, kind }) => ({ start, end, kind }));
		if (!t || t !== untrack(() => text)) return;
		if (keyTooShort && list.length > 0) {
			// No key yet: nothing to show rather than a result in the clear.
			anonymizeCtl?.abort();
			anonymizeSeq++;
			untrack(() => {
				result = '';
				anonymizing = false;
			});
			return;
		}
		if (list.length === 0) {
			anonymizeCtl?.abort();
			anonymizeSeq++;
			untrack(() => {
				result = t;
				anonymizing = false;
			});
			return;
		}
		const timer = setTimeout(() => runAnonymize(t, m, list, opts), 200);
		return () => clearTimeout(timer);
	});

	async function runAnonymize(
		t: string,
		m: AnonymiserMode,
		list: { start: number; end: number; kind: AnonymiserKind }[],
		opts: AnonymiserModeOptions
	) {
		const seq = ++anonymizeSeq;
		anonymizeCtl?.abort();
		anonymizeCtl = new AbortController();
		anonymizing = true;
		try {
			const res = await anonymizeText(t, m, { findings: list, ...opts }, anonymizeCtl.signal);
			if (seq !== anonymizeSeq) return;
			result = res.text;
			error = '';
		} catch (err) {
			if (seq !== anonymizeSeq || (err as Error)?.name === 'AbortError') return;
			error = messageOf(err);
		} finally {
			if (seq === anonymizeSeq) anonymizing = false;
		}
	}

	// The text cut into plain runs and findings, for the review view.
	const segments = $derived.by((): Segment[] => {
		const t = analyzedText;
		const spans: Span[] = [
			...detected
				.filter((f) => !added.some((c) => overlaps(c, f)))
				.map((f) => ({ ...f, custom: false, off: unmarked.includes(keyOf(f)) })),
			...added.map((f) => ({ ...f, custom: true, off: false }))
		].sort((a, b) => a.start - b.start);
		const out: Segment[] = [];
		let pos = 0;
		for (const s of spans) {
			if (s.start < pos || s.end > t.length) continue;
			if (s.start > pos) out.push({ start: pos, end: s.start, span: null });
			out.push({ start: s.start, end: s.end, span: s });
			pos = s.end;
		}
		if (pos < t.length) out.push({ start: pos, end: t.length, span: null });
		return out;
	});

	const listed = $derived(segments.filter((s) => s.span).map((s) => s.span as Span));
	const hiddenCount = $derived(effective.length);
	const kindsInText = $derived(
		[...new Set(listed.filter((s) => !s.off).map((s) => s.kind))].sort(
			(a, b) => KIND_ORDER.indexOf(a) - KIND_ORDER.indexOf(b)
		)
	);
	const kindsOn = $derived(KIND_ORDER.filter((k) => kinds[k]).length);
	const upToDate = $derived(analyzedText === text && !analyzing);

	const toggleSpan = (s: Span) => {
		if (s.custom) {
			added = added.filter((a) => keyOf(a) !== keyOf(s));
			return;
		}
		const key = keyOf(s);
		unmarked = unmarked.includes(key) ? unmarked.filter((k) => k !== key) : [...unmarked, key];
	};

	// --- Hide selection: map the DOM selection in the review view to text offsets.
	function boundary(node: Node, offset: number): number | null {
		if (!reviewEl) return null;
		if (node === reviewEl) {
			// Offset counts child nodes; take the next segment, or the end.
			let child: Node | null = reviewEl.childNodes[offset] ?? null;
			while (child && !(child instanceof HTMLElement && child.dataset.offset !== undefined))
				child = child.nextSibling;
			return child ? Number((child as HTMLElement).dataset.offset) : analyzedText.length;
		}
		const el = (node.nodeType === Node.TEXT_NODE ? node.parentElement : node) as HTMLElement | null;
		const seg = el?.closest<HTMLElement>('[data-offset]');
		if (!seg || !reviewEl.contains(seg)) return null;
		const base = Number(seg.dataset.offset);
		if (node.nodeType === Node.TEXT_NODE) return base + offset;
		return offset === 0 ? base : base + (seg.textContent?.length ?? 0);
	}

	function onSelectionChange() {
		const sel = window.getSelection();
		if (!sel || sel.isCollapsed || sel.rangeCount === 0 || !reviewEl) {
			selection = null;
			return;
		}
		const r = sel.getRangeAt(0);
		if (!reviewEl.contains(r.startContainer) || !reviewEl.contains(r.endContainer)) {
			selection = null;
			return;
		}
		let a = boundary(r.startContainer, r.startOffset);
		let b = boundary(r.endContainer, r.endOffset);
		if (a === null || b === null) {
			selection = null;
			return;
		}
		if (a > b) [a, b] = [b, a];
		const t = analyzedText;
		while (a < b && /\s/.test(t[a])) a++;
		while (b > a && /\s/.test(t[b - 1])) b--;
		selection = a < b ? { start: a, end: b } : null;
	}

	const hideSelection = () => {
		if (!selection) return;
		const s = selection;
		added = [
			...added.filter((c) => !overlaps(c, s)),
			{ start: s.start, end: s.end, kind: 'CUSTOM', text: analyzedText.slice(s.start, s.end) }
		];
		window.getSelection()?.removeAllRanges();
		selection = null;
	};

	onMount(() => document.addEventListener('selectionchange', onSelectionChange));
	onDestroy(() => {
		document.removeEventListener('selectionchange', onSelectionChange);
		analyzeCtl?.abort();
		anonymizeCtl?.abort();
	});

	const clearAll = () => {
		text = '';
		view = 'edit';
	};

	const copyResult = async () => {
		if (await copyToClipboard(result)) toast.success($i18n.t('Copied to clipboard'));
	};

	const downloadResult = () => {
		const blob = new Blob([result], { type: 'text/plain;charset=utf-8' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = 'anonymised.txt';
		a.click();
		URL.revokeObjectURL(url);
	};

	// Labels and encrypted values in the result read as tokens; the copied text is unchanged.
	const TOKEN_RE: Partial<Record<AnonymiserMode, RegExp>> = {
		labels: /(\[[A-Z]+_\d+\])/g,
		encrypt: /(\[ENC:[A-Za-z0-9_=-]+\])/g
	};
	const resultParts = $derived.by(() => {
		const re = TOKEN_RE[mode];
		return re ? result.split(re) : [result];
	});

	// A 24-character key from the browser's random generator (no look-alike characters).
	const generateKey = () => {
		const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789';
		const bytes = crypto.getRandomValues(new Uint8Array(24));
		encKey = Array.from(bytes, (b) => chars[b % chars.length]).join('');
		showKey = true;
	};

	const copyKey = async () => {
		if (encKey && (await copyToClipboard(encKey))) toast.success($i18n.t('Key copied'));
	};

	// The specific type, when it says more than the kind ("French social security number").
	const typeOf = (s: Span) =>
		s.entity && !ENTITY_SAME_AS_KIND.has(s.entity)
			? ENTITY_LABELS[s.entity]
				? $i18n.t(ENTITY_LABELS[s.entity])
				: s.entity
			: '';

	const modelName = (recognizer: string) =>
		/gliner/i.test(recognizer)
			? 'GLiNER'
			: /transformer|trf/i.test(recognizer)
				? 'spaCy transformer'
				: /spacy/i.test(recognizer)
					? 'spaCy'
					: recognizer;

	// One plain line saying how a detail was found.
	const howFound = (s: Span): string => {
		if (s.custom) return $i18n.t('Added by you');
		const e = s.explanation;
		if (!e) return '';
		const parts: string[] = [];
		if (e.source === 'name_model')
			parts.push($i18n.t('Name model ({{model}})', { model: modelName(e.recognizer) }));
		else if (e.source === 'always_hide') parts.push($i18n.t('Always-hide list'));
		else if (e.source === 'repeated_value')
			parts.push($i18n.t('Same value found elsewhere in the text'));
		else if (e.source === 'manual') parts.push($i18n.t('Added by you'));
		else
			parts.push(
				e.pattern
					? $i18n.t("Pattern '{{pattern}}'", { pattern: e.pattern })
					: $i18n.t('Pattern ({{recognizer}})', { recognizer: e.recognizer })
			);
		if (e.checksum === 'passed') parts.push($i18n.t('checksum passed'));
		if (e.keyword)
			parts.push($i18n.t("raised by the keyword '{{keyword}}'", { keyword: e.keyword }));
		return parts.join(' · ');
	};

	const languageName = (code: string) => (LANGUAGE_NAMES as Record<string, string>)[code] ?? code;
</script>

<div class="flex flex-col gap-4">
	<div class="flex flex-col gap-1">
		<h1 class="text-2xl font-semibold tracking-tight">{$i18n.t('Anonymiser')}</h1>
		<p class="text-sm text-muted-foreground">
			{$i18n.t('Find and hide personal details in a text before you share it.')}
		</p>
	</div>

	{#if anon.error}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Could not load the Anonymiser settings.')}</Alert.Title>
			<Alert.Description>{anon.error}</Alert.Description>
		</Alert.Root>
	{/if}

	<!-- Toolbar -->
	<div class="flex flex-wrap items-center gap-2">
		<NativeSelect.Root bind:value={language} aria-label={$i18n.t('Language')} class="min-w-40">
			<NativeSelect.Option value="auto">{$i18n.t('Auto-detect language')}</NativeSelect.Option>
			{#each Object.entries(LANGUAGE_NAMES) as [code, name] (code)}
				<NativeSelect.Option value={code}>{name}</NativeSelect.Option>
			{/each}
		</NativeSelect.Root>

		<NativeSelect.Root bind:value={mode} aria-label={$i18n.t('How to hide')} class="min-w-48">
			{#each MODE_ORDER as m (m)}
				<NativeSelect.Option value={m}>{$i18n.t(MODE_LABELS[m])}</NativeSelect.Option>
			{/each}
		</NativeSelect.Root>

		<Popover.Root>
			<Popover.Trigger>
				{#snippet child({ props })}
					<Button {...props} variant="outline" disabled={anon.loading || !anon.settings}>
						<SlidersHorizontal />
						{$i18n.t('What to hide')}
						<Badge variant="count">{kindsOn}</Badge>
					</Button>
				{/snippet}
			</Popover.Trigger>
			<Popover.Content
				align="start"
				class="max-h-[min(40rem,80dvh)] w-[min(22rem,calc(100vw-2rem))] gap-3 overflow-y-auto"
			>
				<div class="flex items-center justify-between gap-2">
					<p class="text-sm font-medium">{$i18n.t('What to hide')}</p>
					<Button variant="link" size="sm" onclick={resetToDefaults}>
						{$i18n.t('Reset to defaults')}
					</Button>
				</div>
				<ul class="grid gap-2.5">
					{#each KIND_ORDER as k (k)}
						<li class="flex items-center justify-between gap-3">
							<Label for="anon-kind-{k}" class="flex items-center gap-2 font-normal">
								<span class="size-2.5 shrink-0 rounded-full {KIND_STYLE[k].dot}"></span>
								{$i18n.t(KIND_LABELS[k])}
							</Label>
							<Switch
								id="anon-kind-{k}"
								bind:checked={() => Boolean(kinds[k]), (v) => (kinds[k] = v)}
							/>
						</li>
					{/each}
				</ul>
				<Separator />
				<div class="flex flex-col gap-2">
					<Label for="anon-run-threshold">{$i18n.t('Confidence threshold')}</Label>
					<div class="flex items-center gap-3">
						<input
							id="anon-run-threshold"
							type="range"
							min="0.05"
							max="0.95"
							step="0.05"
							bind:value={threshold}
							class="h-2 w-full cursor-pointer accent-primary"
						/>
						<span class="w-10 shrink-0 text-right text-sm tabular-nums"
							>{Math.round(threshold * 100)}%</span
						>
					</div>
					<p class="text-xs text-muted-foreground">
						{$i18n.t('Lower finds more, but also hides more by mistake.')}
					</p>
				</div>
				<Separator />
				<div class="flex flex-col gap-1.5">
					<Label for="anon-run-allow">{$i18n.t('Never hide')}</Label>
					<Textarea
						id="anon-run-allow"
						bind:value={allowText}
						rows={3}
						class="min-h-0 font-mono text-[0.8125rem]"
						placeholder={$i18n.t('One word or phrase per line.')}
					/>
				</div>
				<div class="flex flex-col gap-1.5">
					<Label for="anon-run-deny">{$i18n.t('Always hide')}</Label>
					<Textarea
						id="anon-run-deny"
						bind:value={denyText}
						rows={3}
						class="min-h-0 font-mono text-[0.8125rem]"
						placeholder={$i18n.t('One word or phrase per line.')}
					/>
				</div>
				<p class="text-xs text-muted-foreground">
					{$i18n.t('These settings only apply to this text.')}
				</p>
			</Popover.Content>
		</Popover.Root>

		<div class="ml-auto flex items-center gap-2">
			{#if analyzing || anonymizing}
				<span class="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
					<Spinner />{$i18n.t('Checking…')}
				</span>
			{/if}
			<Button variant="ghost" onclick={clearAll} disabled={!text}>
				<Eraser />{$i18n.t('Clear')}
			</Button>
		</div>
	</div>

	{#if mode === 'mask'}
		<div class="flex flex-wrap items-end gap-x-4 gap-y-3 rounded-lg border bg-muted/30 px-3 py-2.5">
			<div class="flex flex-col gap-1.5">
				<Label for="anon-mask-char">{$i18n.t('Mask character')}</Label>
				<Input id="anon-mask-char" bind:value={maskChar} maxlength={1} class="w-16 text-center" />
			</div>
			<div class="flex flex-col gap-1.5">
				<Label for="anon-mask-count">{$i18n.t('Characters to mask')}</Label>
				<Input id="anon-mask-count" type="number" min="0" bind:value={maskCount} class="w-28" />
			</div>
			<div class="flex h-9 items-center gap-2">
				<Switch id="anon-mask-end" bind:checked={maskFromEnd} />
				<Label for="anon-mask-end" class="font-normal">{$i18n.t('Start from the end')}</Label>
			</div>
			<p class="w-full text-xs text-muted-foreground">
				{$i18n.t('0 masks every character.')}
			</p>
		</div>
	{:else if mode === 'encrypt'}
		<div class="flex flex-col gap-2 rounded-lg border bg-muted/30 px-3 py-2.5">
			<Label for="anon-key">{$i18n.t('Encryption key')}</Label>
			<div class="flex flex-wrap items-center gap-2">
				<InputGroup.Root class="h-9 w-full sm:w-80">
					<InputGroup.Input
						id="anon-key"
						type={showKey ? 'text' : 'password'}
						bind:value={encKey}
						autocomplete="off"
						spellcheck={false}
						class="font-mono"
						placeholder={$i18n.t('At least 8 characters')}
						aria-invalid={encKey.length > 0 && encKey.length < 8}
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
				<Button variant="outline" onclick={generateKey}>
					<KeyRound />{$i18n.t('New key')}
				</Button>
				<Tip content={$i18n.t('Copy key')}>
					<Button
						variant="ghost"
						size="icon"
						aria-label={$i18n.t('Copy key')}
						disabled={!encKey}
						onclick={copyKey}><Copy /></Button
					>
				</Tip>
			</div>
			<p class="flex items-start gap-1.5 text-xs text-warning">
				<TriangleAlert class="mt-px size-3.5 shrink-0" />
				{$i18n.t('Keep this key: without it the text cannot be restored.')}
			</p>
		</div>
	{:else if mode === 'fake'}
		<p class="flex items-start gap-2 text-sm text-muted-foreground">
			<Info class="mt-0.5 size-4 shrink-0 text-info" />
			{$i18n.t('The values are invented: realistic, but they belong to no one.')}
		</p>
	{/if}

	{#if error}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Something went wrong')}</Alert.Title>
			<Alert.Description>{error}</Alert.Description>
		</Alert.Root>
	{/if}

	<div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
		<!-- Your text -->
		<Card.Root class="min-w-0">
			<Card.Header>
				<Card.Title>{$i18n.t('Your text')}</Card.Title>
				<Card.Description>
					{#if view === 'review'}
						{$i18n.t('Click a highlight to keep it visible. Select words to hide them too.')}
					{:else}
						{$i18n.t('Paste or type the text to anonymise.')}
					{/if}
				</Card.Description>
				<Card.Action>
					<Tabs.Root bind:value={view}>
						<Tabs.List>
							<Tabs.Trigger value="edit"><Pencil />{$i18n.t('Edit')}</Tabs.Trigger>
							<Tabs.Trigger value="review" disabled={!text.trim()}>
								<ScanText />{$i18n.t('Review')}
							</Tabs.Trigger>
						</Tabs.List>
					</Tabs.Root>
				</Card.Action>
			</Card.Header>
			<Card.Content class="flex flex-col gap-3">
				{#if view === 'edit'}
					<Textarea
						bind:value={text}
						rows={14}
						class="min-h-72 resize-y"
						aria-label={$i18n.t('Your text')}
						placeholder={$i18n.t('Paste or type the text to anonymise.')}
						onpaste={() => setTimeout(() => (view = 'review'), 0)}
					/>
				{:else if !analyzedText}
					{#if error}
						<p class="text-sm text-muted-foreground">{$i18n.t('Something went wrong')}</p>
					{:else}
						<div class="flex flex-col gap-2">
							<Skeleton class="h-4 w-11/12" />
							<Skeleton class="h-4 w-10/12" />
							<Skeleton class="h-4 w-9/12" />
						</div>
					{/if}
				{:else}
					<div
						bind:this={reviewEl}
						class="min-h-72 rounded-md border border-input px-3 py-2 text-sm leading-7 break-words whitespace-pre-wrap {upToDate
							? ''
							: 'opacity-60'}"
					>
						{#each segments as seg (seg.start)}{#if seg.span}{@const s = seg.span}<span
									role="button"
									tabindex="0"
									data-offset={seg.start}
									title={s.off
										? $i18n.t('Will stay visible. Click to hide it.')
										: `${$i18n.t(KIND_LABELS[s.kind])} — ${$i18n.t('Click to keep it visible.')}`}
									class="cursor-pointer rounded-sm border-b-2 box-decoration-clone px-0.5 transition-colors focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50 {s.off
										? 'border-dashed border-muted-foreground/50 text-muted-foreground'
										: KIND_STYLE[s.kind].mark}"
									onclick={() => toggleSpan(s)}
									onkeydown={(e) => {
										if (e.key === 'Enter' || e.key === ' ') {
											e.preventDefault();
											toggleSpan(s);
										}
									}}>{analyzedText.slice(seg.start, seg.end)}</span
								>{:else}<span data-offset={seg.start}>{analyzedText.slice(seg.start, seg.end)}</span
								>{/if}{/each}
					</div>
					<div class="flex flex-wrap items-center gap-x-3 gap-y-1.5">
						<Button
							variant="outline"
							size="sm"
							disabled={!selection}
							onclick={hideSelection}
							onmousedown={(e: MouseEvent) => e.preventDefault()}
						>
							<EyeOff />{$i18n.t('Hide selection')}
						</Button>
						{#each kindsInText as k (k)}
							<span class="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
								<span class="size-2 rounded-full {KIND_STYLE[k].dot}"></span>
								{$i18n.t(KIND_LABELS[k])}
							</span>
						{/each}
					</div>
				{/if}
				{#if detectedLanguage && language === 'auto' && text.trim()}
					<p class="text-xs text-muted-foreground">
						{$i18n.t('Language detected: {{language}}', {
							language: languageName(detectedLanguage)
						})}
					</p>
				{/if}
			</Card.Content>
		</Card.Root>

		<!-- Result -->
		<Card.Root class="min-w-0">
			<Card.Header>
				<Card.Title>{$i18n.t('Anonymised text')}</Card.Title>
				<Card.Description>
					{#if text.trim() && upToDate}
						{$i18n.t('{{count}} details hidden', { count: hiddenCount })}
					{:else}
						{$i18n.t('The result appears here as you type.')}
					{/if}
				</Card.Description>
				<Card.Action class="flex gap-1">
					<Tip content={$i18n.t('Copy')}>
						<Button
							variant="ghost"
							size="icon-sm"
							aria-label={$i18n.t('Copy')}
							disabled={!result}
							onclick={copyResult}><Copy /></Button
						>
					</Tip>
					<Tip content={$i18n.t('Download')}>
						<Button
							variant="ghost"
							size="icon-sm"
							aria-label={$i18n.t('Download')}
							disabled={!result}
							onclick={downloadResult}><Download /></Button
						>
					</Tip>
				</Card.Action>
			</Card.Header>
			<Card.Content>
				{#if !text.trim()}
					<Empty.Root class="min-h-72 border border-dashed">
						<Empty.Header>
							<Empty.Media variant="icon"><ShieldCheck /></Empty.Media>
							<Empty.Title>{$i18n.t('Nothing to anonymise yet')}</Empty.Title>
							<Empty.Description>
								{$i18n.t(
									'Names, contact details and numbers are found and hidden as you type. Everything stays on this server.'
								)}
							</Empty.Description>
						</Empty.Header>
					</Empty.Root>
				{:else if keyTooShort && hiddenCount > 0}
					<Empty.Root class="min-h-72 border border-dashed">
						<Empty.Header>
							<Empty.Media variant="icon"><KeyRound /></Empty.Media>
							<Empty.Title>{$i18n.t('Enter a key to encrypt')}</Empty.Title>
							<Empty.Description>
								{$i18n.t('The key needs at least 8 characters, or press New key.')}
							</Empty.Description>
						</Empty.Header>
					</Empty.Root>
				{:else}
					<div
						class="min-h-72 rounded-md border border-input bg-muted/30 px-3 py-2 text-sm leading-7 break-words whitespace-pre-wrap {upToDate &&
						!anonymizing
							? ''
							: 'opacity-60'}"
					>
						{#each resultParts as part, i (i)}{#if i % 2 === 1}<span
									class="rounded-sm bg-muted px-1 font-mono text-[0.8125rem] break-all">{part}</span
								>{:else}{part}{/if}{/each}
					</div>
				{/if}
			</Card.Content>
		</Card.Root>
	</div>

	<p class="flex items-start gap-2 text-sm text-muted-foreground">
		<Info class="mt-0.5 size-4 shrink-0 text-info" />
		{$i18n.t('Detection is automatic and can miss things. Check the result before you share it.')}
	</p>

	{#if listed.length > 0 && upToDate}
		<Card.Root>
			<Card.Header>
				<Card.Title>{$i18n.t('What was found')}</Card.Title>
				<Card.Description>
					{$i18n.t('Each detail hidden in the text, and how sure the detection is.')}
				</Card.Description>
				<Card.Action class="flex items-center gap-2">
					<Switch id="anon-explain" bind:checked={explain} />
					<Label for="anon-explain" class="font-normal">
						{$i18n.t('Show how each detail was found')}
					</Label>
				</Card.Action>
			</Card.Header>
			<Card.Content>
				<ul class="divide-y">
					{#each listed as s (keyOf(s))}
						{@const type = typeOf(s)}
						{@const how = explain ? howFound(s) : ''}
						<li class="flex items-center gap-3 py-2 text-sm first:pt-0 last:pb-0">
							<span
								class="size-2.5 shrink-0 self-start rounded-full mt-1.5 {KIND_STYLE[s.kind].dot}"
							></span>
							<span class="flex w-32 shrink-0 flex-col self-start sm:w-48">
								<span class="truncate text-muted-foreground">{$i18n.t(KIND_LABELS[s.kind])}</span>
								{#if type}
									<span class="truncate text-xs text-muted-foreground/80" title={type}>{type}</span>
								{/if}
							</span>
							<span class="flex min-w-0 flex-1 flex-col self-start">
								<span class="truncate {s.off ? 'line-through opacity-60' : ''}"
									>{analyzedText.slice(s.start, s.end)}</span
								>
								{#if how}
									<span class="text-xs text-muted-foreground">{how}</span>
								{/if}
							</span>
							<span class="w-14 shrink-0 text-right text-muted-foreground tabular-nums">
								{s.custom || s.score == null ? '' : `${Math.round(s.score * 100)}%`}
							</span>
							{#if s.custom}
								<Tip content={$i18n.t('Remove')}>
									<Button
										variant="ghost"
										size="icon-sm"
										aria-label={$i18n.t('Remove')}
										onclick={() => toggleSpan(s)}><X /></Button
									>
								</Tip>
							{:else}
								<Tip content={s.off ? $i18n.t('Hide') : $i18n.t('Keep visible')}>
									<Button
										variant="ghost"
										size="icon-sm"
										aria-label={s.off ? $i18n.t('Hide') : $i18n.t('Keep visible')}
										onclick={() => toggleSpan(s)}
									>
										{#if s.off}<EyeOff />{:else}<Eye />{/if}
									</Button>
								</Tip>
							{/if}
						</li>
					{/each}
				</ul>
			</Card.Content>
		</Card.Root>
	{/if}
</div>
