// Company logos: initials for companies without one, the authenticated fetch of the image,
// and the in-browser resize done before uploading.

import { companyLogoUrl } from '$lib/apis/accounting';
import { fetchAsBlobUrl, revokeBlobUrl } from '$lib/utils/blobPreview';

// The server stores at most this many pixels a side.
const MAX_SIDE = 256;
export const MAX_LOGO_FILE_BYTES = 10 * 1024 * 1024;
export const LOGO_ACCEPT = 'image/png,image/jpeg,image/webp,image/gif,image/svg+xml';

type LogoCompany = { id: number; logo_updated_at?: string | null };

// "ALMA (Shanghai) Trading Co., Ltd." → "AS"; "甲码工业软件贸易（上海）有限公司" → "甲码".
export const companyInitials = (name: string): string => {
	const words = (name || '').match(/[\p{L}\p{N}]+/gu) ?? [];
	const first = words[0];
	if (!first) return '?';
	// CJK names have no spaces: their first two characters read best.
	if (/^[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}]/u.test(first)) {
		return Array.from(first).slice(0, 2).join('');
	}
	return words
		.slice(0, 2)
		.map((w) => Array.from(w)[0])
		.join('')
		.toUpperCase();
};

// The logo endpoint needs the Bearer token, so an <img src> can't load it directly. One fetch
// per company and logo version for the life of the page; a new version frees the old blob.
const cache = new Map<number, { version: string; url: Promise<string | null> }>();

export const logoBlobUrl = (company: LogoCompany): Promise<string | null> => {
	const version = company.logo_updated_at ?? '';
	const hit = cache.get(company.id);
	if (hit?.version === version) return hit.url;
	hit?.url.then(revokeBlobUrl);

	const entry = {
		version,
		url: fetchAsBlobUrl(companyLogoUrl(company), localStorage.getItem('token')).then((r) => {
			// don't keep a failure: the next render tries again
			if (!r && cache.get(company.id) === entry) cache.delete(company.id);
			return r?.url ?? null;
		})
	};
	cache.set(company.id, entry);
	return entry.url;
};

const loadImage = async (src: string): Promise<HTMLImageElement> => {
	const img = new Image();
	img.src = src;
	await img.decode();
	return img;
};

// An SVG gets an explicit width and height at the target size before it is drawn: Firefox
// won't draw an SVG without them, and a vector should fill the box rather than keep its
// nominal size.
const sizedSvg = async (file: File): Promise<{ blob: Blob; width: number; height: number }> => {
	const doc = new DOMParser().parseFromString(await file.text(), 'image/svg+xml');
	const svg = doc.documentElement;
	if (svg.nodeName.toLowerCase() !== 'svg' || doc.querySelector('parsererror')) {
		throw new Error('Not an SVG file');
	}
	const box = (svg.getAttribute('viewBox') ?? '')
		.trim()
		.split(/[\s,]+/)
		.map(Number);
	const w0 = parseFloat(svg.getAttribute('width') ?? '');
	const h0 = parseFloat(svg.getAttribute('height') ?? '');
	let aspect = 1;
	if (box.length === 4 && box[2] > 0 && box[3] > 0) {
		aspect = box[2] / box[3];
	} else if (w0 > 0 && h0 > 0) {
		aspect = w0 / h0;
		// without a viewBox the drawing would stay at its own size instead of scaling
		svg.setAttribute('viewBox', `0 0 ${w0} ${h0}`);
	}
	const width = aspect >= 1 ? MAX_SIDE : Math.max(1, Math.round(MAX_SIDE * aspect));
	const height = aspect >= 1 ? Math.max(1, Math.round(MAX_SIDE / aspect)) : MAX_SIDE;
	svg.setAttribute('width', String(width));
	svg.setAttribute('height', String(height));
	const text = new XMLSerializer().serializeToString(doc);
	return { blob: new Blob([text], { type: 'image/svg+xml' }), width, height };
};

// The picked file as a PNG of at most MAX_SIDE a side: what gets uploaded and previewed.
export const prepareLogoFile = async (file: File): Promise<Blob> => {
	const isSvg = file.type === 'image/svg+xml' || /\.svg$/i.test(file.name);
	const svg = isSvg ? await sizedSvg(file) : null;
	const src = URL.createObjectURL(svg ? svg.blob : file);
	try {
		const img = await loadImage(src);
		let width = svg?.width ?? img.naturalWidth;
		let height = svg?.height ?? img.naturalHeight;
		if (!width || !height) throw new Error('The image has no size');
		// pictures are only ever made smaller
		const scale = Math.min(1, MAX_SIDE / Math.max(width, height));
		width = Math.max(1, Math.round(width * scale));
		height = Math.max(1, Math.round(height * scale));

		const canvas = document.createElement('canvas');
		canvas.width = width;
		canvas.height = height;
		const ctx = canvas.getContext('2d');
		if (!ctx) throw new Error('No canvas');
		ctx.imageSmoothingQuality = 'high';
		ctx.drawImage(img, 0, 0, width, height);
		const png = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/png'));
		if (!png) throw new Error('The image could not be encoded');
		return png;
	} finally {
		URL.revokeObjectURL(src);
	}
};
