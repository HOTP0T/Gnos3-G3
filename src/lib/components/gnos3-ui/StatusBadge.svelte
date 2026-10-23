<!--
	One badge for every status the app shows (design system → Status map).
	A lifecycle status is an outline badge with an icon; a problem is a soft tone. Never colour alone.

	<StatusBadge kind="entry" status="posted" />
	<StatusBadge kind="bank" status={line.match_status} />
	<StatusBadge kind="confidence" status={0.82} />      (a 0–1 score or a percentage)
	<StatusBadge kind="closing" status="warning" bare />  (icon + word, no badge: checklists)

	STATUS_MAP is exported for screens that need the icon or tone without a badge (e.g. a KPI tile).
-->
<script lang="ts" module>
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import CircleX from '@lucide/svelte/icons/circle-x';
	import CircleDashed from '@lucide/svelte/icons/circle-dashed';
	import CircleSlash from '@lucide/svelte/icons/circle-slash';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import Circle from '@lucide/svelte/icons/circle';
	import Clock from '@lucide/svelte/icons/clock';
	import Flag from '@lucide/svelte/icons/flag';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import Contrast from '@lucide/svelte/icons/contrast';
	import Sparkles from '@lucide/svelte/icons/sparkles';
	import Check from '@lucide/svelte/icons/check';
	import type { Component } from 'svelte';
	import type { BadgeVariant } from '$lib/components/ui/badge/index.js';

	export type StatusKind =
		| 'extraction'
		| 'entry'
		| 'booking'
		| 'bank'
		| 'tax'
		| 'expense'
		| 'closing'
		| 'role'
		| 'aging'
		| 'confidence';

	type Tone = 'success' | 'warning' | 'danger' | 'muted';
	type Spec = {
		label: string;
		icon?: Component;
		/** colour of the icon inside an outline status badge */
		tone?: Tone;
		/** badge variant; default 'status' (outline, muted text) */
		variant?: BadgeVariant;
		spin?: boolean;
		strike?: boolean;
	};

	const ok = (label: string): Spec => ({ label, icon: CircleCheck, tone: 'success' });

	export const STATUS_MAP: Record<Exclude<StatusKind, 'confidence'>, Record<string, Spec>> = {
		// invoices, business cards (processing_status, plus needs_review)
		extraction: {
			completed: ok('Completed'),
			processed: ok('Completed'),
			ok: ok('OK'),
			processing: { label: 'Processing', icon: LoaderCircle, spin: true },
			pending: { label: 'Pending', icon: Clock },
			failed: { label: 'Failed', icon: CircleX, tone: 'danger' },
			needs_review: { label: 'Needs review', icon: Flag, variant: 'warning' }
		},
		// journal entries
		entry: {
			draft: { label: 'Draft', icon: CircleDashed },
			posted: ok('Posted'),
			voided: { label: 'Voided', icon: CircleSlash, strike: true },
			incomplete: { label: 'Incomplete', icon: TriangleAlert, variant: 'warning' },
			unbalanced: { label: 'Unbalanced', icon: CircleAlert, variant: 'danger' }
		},
		// invoice booking / payment
		booking: {
			review: { label: 'Review', icon: Flag, variant: 'warning' },
			ready: ok('Ready'),
			booked: ok('Booked'),
			paid: ok('Paid'),
			partial: { label: 'Partly paid', icon: Contrast, tone: 'warning' },
			unpaid: { label: 'Unpaid', icon: Circle }
		},
		// bank statement lines
		bank: {
			unmatched: { label: 'Unmatched', icon: CircleDashed },
			partial_matched: { label: 'Partial', icon: Contrast, tone: 'warning' },
			partial: { label: 'Partial', icon: Contrast, tone: 'warning' },
			auto_matched: { label: 'Auto-matched', icon: Sparkles },
			manual_matched: ok('Matched'),
			matched: ok('Matched'),
			excluded: { label: 'Excluded', variant: 'secondary' }
		},
		// tax filings
		tax: {
			open: { label: 'Open', icon: Circle },
			draft: { label: 'Draft', icon: CircleDashed },
			filed: { label: 'Filed', icon: Clock },
			entry_posted: { label: 'Entry posted', icon: Clock },
			paid: ok('Paid'),
			overdue: { label: 'Overdue', icon: CircleAlert, variant: 'danger' }
		},
		// expense sheets
		expense: {
			draft: { label: 'Draft', icon: CircleDashed },
			submitted: { label: 'Submitted', icon: Clock },
			approved: { label: 'Approved', icon: Check, tone: 'success' },
			paid: ok('Paid'),
			reimbursed: ok('Reimbursed'),
			rejected: { label: 'Rejected', icon: CircleX, variant: 'danger' }
		},
		// closing checklist: shown bare (icon + word)
		closing: {
			ok: ok('OK'),
			pass: ok('OK'),
			warning: { label: 'Warning', icon: TriangleAlert, tone: 'warning' },
			warn: { label: 'Warning', icon: TriangleAlert, tone: 'warning' },
			pending: { label: 'Pending', icon: Clock },
			blocker: { label: 'Blocker', icon: CircleX, tone: 'danger' },
			error: { label: 'Blocker', icon: CircleX, tone: 'danger' }
		},
		// receivables / payables aging buckets: current is fine, 31–60 waits, 61–90 needs a look, 90+ is a problem
		aging: {
			current: ok('Current'),
			'31-60': { label: '31–60', icon: Clock },
			'61-90': { label: '61–90', icon: TriangleAlert, variant: 'warning' },
			'90+': { label: '90+', icon: CircleAlert, variant: 'danger' }
		},
		role: {
			superadmin: { label: 'superadmin', variant: 'default' },
			admin: { label: 'admin', variant: 'secondary' },
			user: { label: 'user', variant: 'outline' },
			pending: { label: 'pending', icon: Clock }
		}
	};

	const TONE_CLASS: Record<Tone, string> = {
		success: 'text-success',
		warning: 'text-warning',
		danger: 'text-destructive',
		muted: ''
	};

	/** Confidence: >= 70% success, 40–69% warning, < 40% danger (a score of 0–1 or 0–100). */
	export function confidenceSpec(value: number | string | null | undefined): Spec | null {
		const n = typeof value === 'string' ? parseFloat(value) : value;
		if (n === null || n === undefined || Number.isNaN(n)) return null;
		const pct = n <= 1 ? Math.round(n * 100) : Math.round(n);
		const variant: BadgeVariant = pct >= 70 ? 'success' : pct >= 40 ? 'warning' : 'danger';
		return { label: `${pct}%`, variant };
	}
</script>

<script lang="ts">
	import { getContext } from 'svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { cn } from '$lib/utils/shadcn.js';

	const i18n: any = getContext('i18n');

	let {
		kind,
		status,
		label = undefined,
		bare = false,
		class: className = ''
	}: {
		kind: StatusKind;
		status: string | number | null | undefined;
		/** overrides the mapped label (already translated) */
		label?: string;
		/** icon + word without the badge outline (closing checklist, dense lists) */
		bare?: boolean;
		class?: string;
	} = $props();

	const spec = $derived.by((): Spec => {
		if (kind === 'confidence') return confidenceSpec(status as number) ?? { label: '—' };
		const key = String(status ?? '').toLowerCase();
		return (
			STATUS_MAP[kind]?.[key] ?? {
				label: key ? key.replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase()) : '—',
				icon: Circle
			}
		);
	});
	const text = $derived(label ?? (kind === 'confidence' ? spec.label : $i18n.t(spec.label, { context: 'gnos3' })));
	const Icon = $derived(spec.icon);
	const iconClass = $derived(
		cn(spec.tone && TONE_CLASS[spec.tone], spec.spin && 'animate-spin motion-reduce:animate-none')
	);
</script>

{#if bare}
	<span class={cn('inline-flex items-center gap-1.5 whitespace-nowrap', className)}>
		{#if Icon}<Icon class={cn('size-4 shrink-0', iconClass)} aria-hidden="true" />{/if}
		<span class={spec.strike ? 'line-through' : ''}>{text}</span>
	</span>
{:else}
	<Badge
		variant={spec.variant ?? 'status'}
		class={cn(
			spec.strike && 'line-through',
			!Icon && (spec.variant ?? 'status') === 'status' && 'pl-2',
			className
		)}
	>
		{#if Icon}<Icon class={iconClass} aria-hidden="true" />{/if}
		{text}
	</Badge>
{/if}
