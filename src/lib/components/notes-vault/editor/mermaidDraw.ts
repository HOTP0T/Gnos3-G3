// Draws Mermaid diagrams for notes, on the box, and returns SVG that is safe to show: a note can
// come from a shared vault or an imported zip, so nothing in it may run or fetch from outside.
//
// Mermaid is one global object shared with the chat, which draws with its own settings. Each draw
// here sets ours and puts the previous ones back; the sanitizer holds even if a chat draw lands
// in between.
//
// Mermaid draws in the page, so what it loads while drawing is fetched before the sanitizer runs.
// The direct ways are refused below. A determined author could still slip one through (CSS escapes,
// YAML escapes), which only isolating Mermaid in a sandboxed frame would stop; not worth it while a
// plain ![](https://…) image in a note does the same.

import DOMPurify from 'dompurify';
import { renderMermaidDiagram } from '$lib/utils';

export const isDarkTheme = () => document.documentElement.classList.contains('dark');

/** Mermaid's colour parser reads neither var() nor oklch(), so tokens are resolved to #rrggbb. */
const tokenReader = () => {
	const style = getComputedStyle(document.documentElement);
	const canvas = document.createElement('canvas');
	canvas.width = canvas.height = 1;
	const ctx = canvas.getContext('2d', { willReadFrequently: true })!;
	return (name: string) => {
		ctx.clearRect(0, 0, 1, 1);
		ctx.fillStyle = style.getPropertyValue(`--${name}`).trim() || '#000';
		ctx.fillRect(0, 0, 1, 1);
		const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data;
		return `#${[r, g, b].map((n) => n.toString(16).padStart(2, '0')).join('')}`;
	};
};

const themeVariables = () => {
	const token = tokenReader();
	const card = token('card');
	const foreground = token('foreground');
	const muted = token('muted');
	const mutedForeground = token('muted-foreground');
	const border = token('border');
	const primary = token('primary');
	const charts = [1, 2, 3, 4, 5, 6, 7, 8].map((n) => token(`chart-${n}`));

	const series: Record<string, string> = {};
	for (let i = 0; i < 12; i++) {
		const color = charts[i % charts.length];
		if (i < 8) {
			series[`pie${i + 1}`] = color;
			series[`git${i}`] = color;
			series[`gitBranchLabel${i}`] = '#ffffff';
			series[`fillType${i}`] = color;
		}
		series[`cScale${i}`] = color;
		series[`cScaleLabel${i}`] = '#ffffff';
	}

	return {
		darkMode: isDarkTheme(),
		fontSize: '14px',
		background: card,
		textColor: foreground,
		lineColor: mutedForeground,
		primaryColor: muted,
		primaryTextColor: foreground,
		primaryBorderColor: primary,
		secondaryColor: muted,
		secondaryTextColor: foreground,
		secondaryBorderColor: border,
		tertiaryColor: card,
		tertiaryTextColor: foreground,
		tertiaryBorderColor: border,
		mainBkg: muted,
		nodeBorder: primary,
		nodeTextColor: foreground,
		titleColor: foreground,
		clusterBkg: card,
		clusterBorder: border,
		edgeLabelBackground: card,
		actorBkg: muted,
		actorBorder: primary,
		actorTextColor: foreground,
		actorLineColor: mutedForeground,
		signalColor: foreground,
		signalTextColor: foreground,
		labelBoxBkgColor: muted,
		labelBoxBorderColor: border,
		labelTextColor: foreground,
		loopTextColor: foreground,
		noteBkgColor: muted,
		noteBorderColor: border,
		noteTextColor: foreground,
		activationBkgColor: muted,
		activationBorderColor: border,
		pieTitleTextColor: foreground,
		pieSectionTextColor: '#ffffff',
		pieLegendTextColor: foreground,
		pieStrokeColor: card,
		pieOuterStrokeColor: border,
		...series,
		xyChart: {
			backgroundColor: card,
			titleColor: foreground,
			xAxisLabelColor: foreground,
			xAxisTitleColor: foreground,
			xAxisTickColor: mutedForeground,
			xAxisLineColor: mutedForeground,
			yAxisLabelColor: foreground,
			yAxisTitleColor: foreground,
			yAxisTickColor: mutedForeground,
			yAxisLineColor: mutedForeground,
			plotColorPalette: charts.join(', ')
		}
	};
};

const noteConfig = () => {
	const variables = themeVariables();
	return {
		startOnLoad: false,
		securityLevel: 'strict' as const,
		suppressErrorRendering: true,
		theme: 'base' as const,
		fontFamily: getComputedStyle(document.body).fontFamily,
		themeVariables: variables,
		// Mermaid draws edge labels on a half-transparent background (the line strikes through the text)
		// and a timeline's axis in the label colour (white on white).
		themeCSS: `.edgeLabel rect { opacity: 1; } .lineWrapper line { stroke: ${variables.lineColor}; }`,
		// Laid out for the page and scaled down, a Gantt chart's text is too small to read.
		gantt: { useWidth: 800 },
		// SVG labels, not HTML: they survive the sanitizer and can be drawn into a PDF.
		htmlLabels: false,
		flowchart: { htmlLabels: false },
		// What %%{init}%% or front matter inside a note cannot change.
		secure: [
			'secure',
			'securityLevel',
			'startOnLoad',
			'maxTextSize',
			'suppressErrorRendering',
			'maxEdges',
			'htmlLabels',
			'themeCSS',
			'fontFamily',
			'altFontFamily'
		]
	};
};

const OUTSIDE_FETCH = /@import[^;]*;?|url\(\s*(?!['"]?#)[^)]*\)/gi;

/** Removes scripts and anything that would load from outside the box. */
const sanitize = (svg: string): string => {
	const fragment = DOMPurify.sanitize(svg, {
		USE_PROFILES: { svg: true, svgFilters: true },
		ADD_TAGS: ['style'],
		RETURN_DOM_FRAGMENT: true
	}) as unknown as DocumentFragment;

	fragment.querySelectorAll('style').forEach((el) => {
		el.textContent = (el.textContent ?? '').replace(OUTSIDE_FETCH, 'none');
	});
	fragment.querySelectorAll('[style]').forEach((el) => {
		el.setAttribute('style', (el.getAttribute('style') ?? '').replace(OUTSIDE_FETCH, 'none'));
	});
	fragment.querySelectorAll('image').forEach((el) => {
		const href = el.getAttribute('href') ?? el.getAttribute('xlink:href') ?? '';
		if (!href.startsWith('data:image/')) el.remove();
	});
	fragment.querySelectorAll('a').forEach((el) => {
		el.setAttribute('target', '_blank');
		el.setAttribute('rel', 'noopener noreferrer');
	});
	return fragment.querySelector('svg')?.outerHTML ?? '';
};

export const OUTSIDE_CONTENT_REFUSED = 'outside-content';
const LOADS_FROM_OUTSIDE =
	/@\{[^}]*\bimg["']?\s*:(?!\s*["']?data:image\/)|url\(\s*(?!['"]?#)|@import|\$sprite\s*=/i;

const CACHE_SIZE = 50;
const cache = new Map<string, string>();
let queue: Promise<unknown> = Promise.resolve();
let drawCount = 0;

/** The diagram as sanitized SVG; rejects with Mermaid's message when the source has an error. */
export const drawMermaid = (code: string): Promise<string> => {
	const source = code.trim();
	if (LOADS_FROM_OUTSIDE.test(source)) return Promise.reject(new Error(OUTSIDE_CONTENT_REFUSED));
	const key = `${isDarkTheme()}:${source}`;
	const known = cache.get(key);
	if (known) return Promise.resolve(known);

	const job = queue.then(async () => {
		const { default: mermaid } = await import('mermaid');
		const previous = mermaid.mermaidAPI.getSiteConfig();
		mermaid.initialize(noteConfig());
		try {
			const raw = await renderMermaidDiagram(mermaid, source, `note-mermaid-${++drawCount}`);
			const svg = sanitize(raw);
			if (!svg) throw new Error('Mermaid returned no diagram');
			if (cache.size >= CACHE_SIZE) cache.delete(cache.keys().next().value as string);
			cache.set(key, svg);
			return svg;
		} finally {
			mermaid.initialize(previous);
		}
	});
	queue = job.catch(() => {});
	return job;
};

const svgToPng = async (svg: string): Promise<{ url: string; width: number }> => {
	const root = new DOMParser().parseFromString(svg, 'text/html').querySelector('svg');
	if (!root) throw new Error('No diagram');
	const [, , width, height] = (root.getAttribute('viewBox') ?? '0 0 800 600')
		.split(/\s+/)
		.map(Number);
	root.setAttribute('width', `${width}`);
	root.setAttribute('height', `${height}`);
	root.style.maxWidth = 'none';

	const image = new Image();
	await new Promise((resolve, reject) => {
		image.onload = resolve;
		image.onerror = () => reject(new Error('The diagram could not be converted'));
		image.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(new XMLSerializer().serializeToString(root))}`;
	});

	const scale = 2;
	const canvas = document.createElement('canvas');
	canvas.width = Math.ceil(width * scale);
	canvas.height = Math.ceil(height * scale);
	const ctx = canvas.getContext('2d')!;
	ctx.scale(scale, scale);
	ctx.drawImage(image, 0, 0, width, height);
	return { url: canvas.toDataURL('image/png'), width };
};

/** A note's HTML with each diagram as a picture, for the PDF. A broken one stays as its source. */
export const htmlWithDiagrams = async (html: string): Promise<string> => {
	const doc = new DOMParser().parseFromString(html, 'text/html');
	for (const code of Array.from(doc.querySelectorAll('pre > code.language-mermaid'))) {
		try {
			const { url, width } = await svgToPng(await drawMermaid(code.textContent ?? ''));
			const image = doc.createElement('img');
			image.src = url;
			image.style.width = `${width}px`;
			image.style.maxWidth = '100%';
			code.parentElement?.replaceWith(image);
		} catch {
			// keep the source
		}
	}
	return doc.body.innerHTML;
};
