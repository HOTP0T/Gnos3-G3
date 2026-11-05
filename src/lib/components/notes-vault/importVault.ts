// Reading an Obsidian / Tolaria vault (a .zip of Markdown files, or loose .md files) for import.
// Folders become folders, each .md file a note (its frontmatter becomes properties on the server),
// images it shows are kept with the note. [[Links]] stay as written and resolve by title.

import JSZip from 'jszip';
import { v4 as uuidv4 } from 'uuid';

export interface ImportItem {
	folder: string;
	title: string;
	md: string;
	files?: { id: string; type: 'image'; url: string }[];
}

export interface ImportResult {
	items: ImportItem[];
	skipped: string[];
}

const IMAGE_TYPES: Record<string, string> = {
	png: 'image/png',
	jpg: 'image/jpeg',
	jpeg: 'image/jpeg',
	gif: 'image/gif',
	webp: 'image/webp',
	svg: 'image/svg+xml'
};
const MAX_IMAGE_BYTES = 3 * 1024 * 1024;

const isHidden = (path: string) =>
	path.split('/').some((p) => p.startsWith('.') || p === '__MACOSX' || p === 'node_modules');

const basename = (path: string) => path.split('/').pop() ?? path;
const extension = (path: string) => (basename(path).split('.').pop() ?? '').toLowerCase();

const dirname = (path: string) => (path.includes('/') ? path.slice(0, path.lastIndexOf('/')) : '');

const resolvePath = (from: string, relative: string) => {
	const parts = (from ? from.split('/') : []).concat(relative.split('/'));
	const out: string[] = [];
	for (const p of parts) {
		if (!p || p === '.') continue;
		if (p === '..') out.pop();
		else out.push(p);
	}
	return out.join('/');
};

export const readVaultFiles = async (files: File[]): Promise<ImportResult> => {
	const markdown: { path: string; text: () => Promise<string> }[] = [];
	const images = new Map<string, { path: string; size: number; data: () => Promise<string> }>();
	const skipped: string[] = [];

	for (const file of files) {
		if (file.name.toLowerCase().endsWith('.zip')) {
			const zip = await JSZip.loadAsync(file);
			zip.forEach((path, entry) => {
				if (entry.dir || isHidden(path)) return;
				const ext = extension(path);
				if (ext === 'md' || ext === 'markdown') {
					markdown.push({ path, text: () => entry.async('string') });
				} else if (IMAGE_TYPES[ext]) {
					const size = (entry as any)._data?.uncompressedSize ?? 0;
					images.set(path, { path, size, data: () => entry.async('base64') });
				} else {
					skipped.push(path);
				}
			});
		} else if (/\.(md|markdown)$/i.test(file.name)) {
			markdown.push({ path: file.name, text: () => file.text() });
		} else {
			skipped.push(file.name);
		}
	}

	// A zip of "MyVault/…" imports MyVault's content, not a folder called MyVault.
	const tops = new Set(markdown.map((m) => (m.path.includes('/') ? m.path.split('/')[0] : '')));
	const strip = tops.size === 1 && !tops.has('') ? [...tops][0] + '/' : '';

	const byName = new Map<string, string>();
	for (const path of images.keys()) byName.set(basename(path).toLowerCase(), path);

	const items: ImportItem[] = [];
	for (const m of markdown) {
		const path = m.path.startsWith(strip) ? m.path.slice(strip.length) : m.path;
		const folder = dirname(path);
		const title = basename(path).replace(/\.(md|markdown)$/i, '');
		let md = await m.text();
		const noteFiles: { id: string; type: 'image'; url: string }[] = [];

		const embed = async (target: string, alt: string) => {
			const clean = decodeURIComponent(target.split('|')[0].split('#')[0].trim());
			const key = images.has(resolvePath(dirname(m.path), clean))
				? resolvePath(dirname(m.path), clean)
				: byName.get(basename(clean).toLowerCase());
			const image = key ? images.get(key) : undefined;
			if (!image || image.size > MAX_IMAGE_BYTES) return null;
			const id = uuidv4();
			const url = `data:${IMAGE_TYPES[extension(image.path)]};base64,${await image.data()}`;
			noteFiles.push({ id, type: 'image', url });
			return `![${alt}](data://${id})`;
		};

		// ![[image.png]] (Obsidian) and ![alt](relative/image.png)
		const replacements: { from: string; to: string }[] = [];
		for (const match of md.matchAll(/!\[\[([^\]]+)\]\]/g)) {
			if (!IMAGE_TYPES[extension(match[1].split('|')[0])]) continue;
			const to = await embed(match[1], '');
			if (to) replacements.push({ from: match[0], to });
		}
		for (const match of md.matchAll(/!\[([^\]]*)\]\(([^)\s]+)\)/g)) {
			if (/^(https?:|data:)/i.test(match[2])) continue;
			const to = await embed(match[2], match[1]);
			if (to) replacements.push({ from: match[0], to });
		}
		for (const r of replacements) md = md.replace(r.from, r.to);

		items.push({ folder, title, md, files: noteFiles.length ? noteFiles : undefined });
	}
	return { items, skipped };
};
