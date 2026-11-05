// Markdown ↔ the Notes editor.
//
// A note created by the server (import, template, chat answer saved as a note, daily note) holds
// only Markdown until it is first opened. `markdownToEditorHtml` turns that Markdown into the HTML
// the editor parses, with [[links]] and links to Gnos3 data as the editor's own nodes. The editor
// writes them back as the same Markdown (data-md, see editor/WikiLink.ts and editor/EntityRef.ts).

import { Marked } from 'marked';
import DOMPurify from 'dompurify';
import { parseEntityHref } from './entities';
import type { TreeNote } from '$lib/apis/note-vaults';
import { normalizeTitle } from './vault';

export const escapeHtml = (s: string) =>
	s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export interface WikiTarget {
	title: string;
	heading: string | null;
	alias: string | null;
}

/** 'Folder/Title#Heading|shown' → parts (same rules as the backend's split_wikilink). */
export const splitWikilink = (inner: string): WikiTarget => {
	let rest = inner.replace(/\\\|/g, '|');
	let alias: string | null = null;
	const pipe = rest.indexOf('|');
	if (pipe !== -1) {
		alias = rest.slice(pipe + 1).trim() || null;
		rest = rest.slice(0, pipe);
	}
	let heading: string | null = null;
	const hash = rest.indexOf('#');
	if (hash !== -1) {
		heading = rest.slice(hash + 1).trim() || null;
		rest = rest.slice(0, hash);
	}
	let title = rest.trim();
	if (title.includes('/')) title = title.slice(title.lastIndexOf('/') + 1).trim();
	if (title.toLowerCase().endsWith('.md')) title = title.slice(0, -3);
	return { title, heading, alias };
};

export const formatWikilink = (title: string, heading?: string | null, alias?: string | null) => {
	let inner = title;
	if (heading) inner += `#${heading}`;
	if (alias && alias !== title) inner += `|${alias}`;
	return `[[${inner}]]`;
};

export const wikiLinkHtml = (
	noteId: string | null,
	title: string,
	alias: string | null = null,
	heading: string | null = null
) =>
	`<a data-type="wiki-link" data-note-id="${escapeHtml(noteId ?? '')}" data-title="${escapeHtml(title)}"` +
	` data-alias="${escapeHtml(alias ?? '')}" data-heading="${escapeHtml(heading ?? '')}">` +
	`${escapeHtml(alias || title)}</a>`;

export const entityRefHtml = (type: string, id: string, label: string) =>
	`<span data-type="entity-ref" data-entity-type="${escapeHtml(type)}" data-entity-id="${escapeHtml(id)}"` +
	` data-label="${escapeHtml(label)}">${escapeHtml(label)}</span>`;

type Resolver = (title: string) => TreeNote | undefined;

const makeMarked = (resolve: Resolver) => {
	const marked = new Marked({ gfm: true, breaks: true });
	marked.use({
		extensions: [
			{
				name: 'wikilink',
				level: 'inline',
				start(src: string) {
					const i = src.indexOf('[[');
					return i === -1 ? undefined : i;
				},
				tokenizer(src: string) {
					const match = /^!?\[\[([^\[\]\n]+?)\]\]/.exec(src);
					if (match) {
						return { type: 'wikilink', raw: match[0], inner: match[1] };
					}
					return undefined;
				},
				renderer(token: any) {
					const parts = splitWikilink(token.inner);
					const note = resolve(parts.title);
					return wikiLinkHtml(note?.id ?? null, parts.title, parts.alias, parts.heading);
				}
			}
		],
		renderer: {
			link(href: string, title: string | null | undefined, text: string) {
				const entity = parseEntityHref(href);
				if (entity) {
					const label = text.replace(/<[^>]+>/g, '');
					return entityRefHtml(entity.type, entity.id, label);
				}
				const t = title ? ` title="${escapeHtml(title)}"` : '';
				return `<a href="${escapeHtml(href)}"${t}>${text}</a>`;
			},
			list(body: string, ordered: boolean, start: number | '') {
				if (body.includes('data-checked=')) return `<ul data-type="taskList">${body}</ul>`;
				const type = ordered ? 'ol' : 'ul';
				const startAttr = ordered && start !== 1 && start !== '' ? ` start="${start}"` : '';
				return `<${type}${startAttr}>${body}</${type}>`;
			},
			listitem(text: string, task: boolean, checked: boolean) {
				if (task) {
					const cleaned = text.replace(/^<input[^>]*>\s*/, '');
					return `<li data-type="taskItem" data-checked="${checked ? 'true' : 'false'}">${cleaned}</li>`;
				}
				return `<li>${text}</li>`;
			}
		}
	} as any);
	return marked;
};

const FRONTMATTER = /^---[ \t]*\r?\n[\s\S]*?\r?\n---[ \t]*(?:\r?\n|$)/;

export const stripFrontmatter = (md: string) => md.replace(FRONTMATTER, '');

export const markdownToEditorHtml = (md: string, resolve: Resolver): string => {
	const html = makeMarked(resolve).parse(stripFrontmatter(md ?? '')) as string;
	return DOMPurify.sanitize(html, {
		ADD_ATTR: [
			'data-type',
			'data-note-id',
			'data-title',
			'data-alias',
			'data-heading',
			'data-entity-type',
			'data-entity-id',
			'data-label',
			'data-checked'
		]
	});
};

export const resolverFor =
	(byTitle: Map<string, TreeNote>): Resolver =>
	(title) =>
		byTitle.get(normalizeTitle(title));

// --- templates ---------------------------------------------------------------

/** {{title}}, {{date}}, {{date:YYYY-MM-DD}}, {{time}}, {{time:HH:mm}} — as in Obsidian templates. */
export const applyTemplate = (md: string, vars: { title: string; now: any; dayjs: any }): string =>
	(md ?? '').replace(/\{\{\s*(title|date|time)(?::([^}]+))?\s*\}\}/g, (_m, name, format) => {
		if (name === 'title') return vars.title;
		const fmt = (format ?? '').trim() || (name === 'date' ? 'YYYY-MM-DD' : 'HH:mm');
		return vars.dayjs(vars.now).format(fmt);
	});

// --- headings (outline) --------------------------------------------------------

export interface Heading {
	level: number;
	text: string;
	pos: number;
}

export const headingsOf = (editor: any): Heading[] => {
	const out: Heading[] = [];
	if (!editor) return out;
	editor.state.doc.descendants((node: any, pos: number) => {
		if (node.type.name === 'heading') {
			out.push({ level: node.attrs.level, text: node.textContent, pos });
			return false;
		}
		return true;
	});
	return out;
};
