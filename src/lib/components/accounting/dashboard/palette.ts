// Chart colours for the accounting dashboard (design system → Colour → Charts).
//
// CATEGORICAL is the guide's validated order, the same values as the --chart-1…8 tokens in
// src/tailwind.css: every neighbouring pair passes the colour-blindness check in both themes
// (dataviz validate_palette.js, 2026-10-19; the previous order failed on slots 7↔8). Assign slots
// in this order and never cycle: a ninth series folds into "Other" (OTHER_LIMIT). An entity keeps
// one colour everywhere: revenue aqua, expenses orange, net blue.
//
// ECharts draws on a canvas and cannot read CSS variables. The surfaces below are the design
// tokens' values (light · dark); chartTheme() swaps in the live computed token when the page has
// one, so the OLED theme (which repaints the dark grays) keeps matching cards.

export const CATEGORICAL = {
	light: ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948'],
	dark: ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#008300', '#9085e9', '#e66767']
};

/** Slot of each hue in CATEGORICAL — chart-1 … chart-8. */
export const SLOT = {
	blue: 0,
	orange: 1,
	aqua: 2,
	yellow: 3,
	magenta: 4,
	green: 5,
	violet: 6,
	red: 7
} as const;

/** Most named series a chart shows; the tail beyond (OTHER_LIMIT - 1) folds into "Other". */
export const OTHER_LIMIT = CATEGORICAL.light.length;

// Status palette (fixed — never themed, never used as a series color).
export const STATUS = {
	good: '#0ca30c',
	warning: '#fab219',
	serious: '#ec835a',
	critical: '#d03b3b'
};

// Design tokens as hex: card, background, foreground (Ink), muted-foreground, border, muted.
const SURFACES = {
	light: {
		card: '#ffffff',
		background: '#ffffff',
		foreground: '#0C1422',
		mutedForeground: '#56637A',
		border: '#DCE2EC',
		muted: '#F4F6FA'
	},
	dark: {
		card: '#121A28',
		background: '#0A1019',
		foreground: '#E8EDF5',
		mutedForeground: '#93A0B6',
		border: '#233047',
		muted: '#1A2436'
	}
};

// Chart chrome / ink, per mode.
export interface ChartTheme {
	isDark: boolean;
	/** the card the chart sits on (gaps between slices / stacked segments) */
	surface: string;
	/** tooltip surface (design system: popovers on --background) */
	background: string;
	/** Ink: values and emphasized labels */
	primary: string;
	/** legends, category names */
	secondary: string;
	/** axis labels */
	muted: string;
	grid: string;
	axis: string;
	/** hover band behind a column */
	band: string;
	/** the folded "Other" series: neutral, not an entity colour */
	other: string;
	series: string[];
	// Fixed entity colours: revenue aqua, expenses orange, net blue.
	revenue: string;
	expenses: string;
	net: string;
	good: string;
	critical: string;
	warning: string;
	serious: string;
}

/** Whether the page is dark right now: the <html> class, which the system and OLED themes set too.
 *  Pass the theme store's value so a reactive statement re-runs when the theme changes. */
export function pageIsDark(themeName: string = ''): boolean {
	if (typeof document !== 'undefined') return document.documentElement.classList.contains('dark');
	return themeName.includes('dark');
}

// A token's computed colour as rgb(), or the fallback when it can't be read as one ECharts parses.
function liveToken(name: string, fallback: string): string {
	if (typeof document === 'undefined' || !document.body) return fallback;
	try {
		const probe = document.createElement('i');
		probe.style.cssText = `position:absolute;visibility:hidden;color:var(${name}, transparent)`;
		document.body.appendChild(probe);
		const color = getComputedStyle(probe).color;
		probe.remove();
		if (!/^(rgba?\(|#)/.test(color) || color === 'rgba(0, 0, 0, 0)') return fallback;
		return color;
	} catch {
		return fallback;
	}
}

export function chartTheme(isDark: boolean): ChartTheme {
	const base = isDark ? SURFACES.dark : SURFACES.light;
	// Read the live tokens only when the page is in the mode asked for, so surfaces and series agree.
	const live = typeof document !== 'undefined' && pageIsDark() === isDark;
	const tok = (name: string, fallback: string) => (live ? liveToken(name, fallback) : fallback);
	const s = {
		card: tok('--card', base.card),
		background: tok('--background', base.background),
		foreground: tok('--foreground', base.foreground),
		mutedForeground: tok('--muted-foreground', base.mutedForeground),
		border: tok('--border', base.border),
		muted: tok('--muted', base.muted)
	};
	const series = isDark ? CATEGORICAL.dark : CATEGORICAL.light;
	return {
		isDark,
		surface: s.card,
		background: s.background,
		primary: s.foreground,
		secondary: s.mutedForeground,
		muted: s.mutedForeground,
		grid: s.border,
		axis: s.border,
		band: s.muted,
		other: s.mutedForeground,
		series,
		revenue: series[SLOT.aqua],
		expenses: series[SLOT.orange],
		net: series[SLOT.blue],
		good: STATUS.good,
		critical: STATUS.critical,
		warning: STATUS.warning,
		serious: STATUS.serious
	};
}

// Shared tooltip styling for ECharts (design system: popover surface, 1px border, 10px radius,
// shadow-lg, 12px text).
export function tooltipStyle(t: ChartTheme) {
	return {
		// stays inside the chart, which sits in a card that clips its overflow
		confine: true,
		backgroundColor: t.background,
		borderColor: t.grid,
		borderWidth: 1,
		padding: [6, 10],
		textStyle: { color: t.primary, fontSize: 12, lineHeight: 16 },
		extraCssText:
			'border-radius: 10px; box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);'
	};
}

// Legend: 10px rounded squares, muted 12px text (the mark beside the text carries identity).
export function legendStyle(t: ChartTheme) {
	return {
		icon: 'roundRect',
		itemWidth: 10,
		itemHeight: 10,
		itemGap: 16,
		// a series' 2px surface border (slice gaps) must not hollow out its legend swatch
		itemStyle: { borderWidth: 0 },
		textStyle: { color: t.secondary, fontSize: 12 }
	};
}

/** Donut layout: legend at the right; on a narrow chart (phones, small cards) a smaller ring and
 *  shorter legend names (the tooltip has the full name). */
export function donutLayout(radius: [string, string]) {
	const clip = (n: number) => (name: string) =>
		name.length > n ? `${name.slice(0, n - 1)}…` : name;
	return {
		wide: { center: ['30%', '50%'], radius },
		legendFormatter: clip(28),
		narrow: {
			query: { maxWidth: 400 },
			option: {
				legend: { formatter: clip(18) },
				series: [{ center: ['22%', '50%'], radius: ['30%', '48%'] }]
			}
		}
	};
}

const esc = (s: unknown) =>
	String(s ?? '').replace(
		/[&<>"']/g,
		(c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c] as string
	);

/** Tooltip body: a heading, then one row per series (swatch, name, value at the right). */
export function tooltipHtml(
	t: ChartTheme,
	heading: string,
	rows: { color?: string; name: string; value: string }[]
): string {
	const head = heading
		? `<div style="font-weight:500;margin-bottom:4px">${esc(heading)}</div>`
		: '';
	const body = rows
		.map(
			(r) =>
				`<div style="display:flex;align-items:center;gap:8px;color:${t.secondary}">` +
				(r.color
					? `<i style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${r.color}"></i>`
					: '') +
				`<span>${esc(r.name)}</span>` +
				`<b style="margin-left:auto;padding-left:16px;color:${t.primary};font-weight:500;font-variant-numeric:tabular-nums">${esc(r.value)}</b>` +
				`</div>`
		)
		.join('');
	return head + body;
}
