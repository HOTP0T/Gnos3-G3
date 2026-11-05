// [[Links]] between notes.
//
// A link is an inline node holding the target's id (so it survives a rename) and the title it was
// written with (so it still reads right, and exports as [[Title]], if the target is gone).
// It shows the target's current title, and quietly updates its stored title when the target was
// renamed. Typing [[ opens a list of the vault's notes; [[Title]] typed or pasted in full becomes
// a link too. A link to a note that does not exist yet ("ghost") creates it when clicked.

import { InputRule, Node, PasteRule, mergeAttributes } from '@tiptap/core';
import { PluginKey } from '@tiptap/pm/state';
import Suggestion from '@tiptap/suggestion';
import type { Readable } from 'svelte/store';
import type { TreeNote } from '$lib/apis/note-vaults';
import { formatWikilink, splitWikilink } from '../markdown';
import { menuRenderer, outsideCode, type SuggestItem } from './suggestionPopup.svelte';

export interface WikiLinkOptions {
	i18n: any;
	notesById: Readable<Map<string, TreeNote>>;
	lookupTitle: (title: string) => TreeNote | undefined;
	suggest: (query: string) => SuggestItem[];
	createNote: (title: string) => Promise<{ id: string; title: string } | null>;
	open: (
		target: { noteId: string | null; title: string; heading: string | null },
		event: MouseEvent
	) => void;
}

export const WikiLink = Node.create<WikiLinkOptions>({
	name: 'wikiLink',
	group: 'inline',
	inline: true,
	atom: true,
	selectable: true,
	draggable: false,

	addOptions() {
		return {
			i18n: null,
			notesById: null as any,
			lookupTitle: () => undefined,
			suggest: () => [],
			createNote: async () => null,
			open: () => {}
		};
	},

	addAttributes() {
		return {
			noteId: {
				default: null,
				parseHTML: (el) => el.getAttribute('data-note-id') || null,
				renderHTML: (attrs) => ({ 'data-note-id': attrs.noteId ?? '' })
			},
			title: {
				default: '',
				parseHTML: (el) => el.getAttribute('data-title') || el.textContent || '',
				renderHTML: (attrs) => ({ 'data-title': attrs.title ?? '' })
			},
			alias: {
				default: null,
				parseHTML: (el) => el.getAttribute('data-alias') || null,
				renderHTML: (attrs) => (attrs.alias ? { 'data-alias': attrs.alias } : {})
			},
			heading: {
				default: null,
				parseHTML: (el) => el.getAttribute('data-heading') || null,
				renderHTML: (attrs) => (attrs.heading ? { 'data-heading': attrs.heading } : {})
			}
		};
	},

	parseHTML() {
		return [{ tag: 'a[data-type="wiki-link"]' }, { tag: 'span[data-type="wiki-link"]' }];
	},

	renderHTML({ node, HTMLAttributes }) {
		const { title, alias, heading, noteId } = node.attrs;
		return [
			'a',
			mergeAttributes(HTMLAttributes, {
				'data-type': 'wiki-link',
				'data-md': formatWikilink(title, heading, alias),
				href: noteId ? `/notes/${noteId}` : '#',
				class: 'wiki-link'
			}),
			alias || title
		];
	},

	renderText({ node }) {
		return node.attrs.alias || node.attrs.title;
	},

	addNodeView() {
		const options = this.options;
		return ({ node, editor, getPos }) => {
			let current = node;
			const dom = document.createElement('a');
			dom.setAttribute('data-type', 'wiki-link');
			dom.setAttribute('contenteditable', 'false');
			dom.className = 'wiki-link';

			const paint = (byId: Map<string, TreeNote>) => {
				const { noteId, title, alias, heading } = current.attrs;
				const target = (noteId && byId.get(noteId)) || options.lookupTitle(title);
				const shown = alias || target?.title || title;
				dom.textContent = heading ? `${shown} › ${heading}` : shown;
				dom.classList.toggle('wiki-link-ghost', !target);
				dom.href = target ? `/notes/${target.id}` : '#';
				dom.title = target
					? target.excerpt || target.title
					: (options.i18n.t('Not created yet — click to create it') ?? '');
				// Renamed target: store the new title so Markdown and exports read right.
				if (
					target &&
					editor.isEditable &&
					typeof getPos === 'function' &&
					(target.title !== title || target.id !== noteId)
				) {
					setTimeout(() => {
						const pos = getPos();
						if (typeof pos !== 'number') return;
						const at = editor.state.doc.nodeAt(pos);
						if (!at || at.type.name !== 'wikiLink') return;
						editor.view.dispatch(
							editor.state.tr
								.setNodeMarkup(pos, undefined, {
									...at.attrs,
									noteId: target.id,
									title: target.title
								})
								.setMeta('addToHistory', false)
						);
					}, 0);
				}
			};

			let latest = new Map<string, TreeNote>();
			const unsubscribe = options.notesById?.subscribe((map) => {
				latest = map;
				paint(map);
			});

			dom.addEventListener('click', (event) => {
				if (event.metaKey || event.ctrlKey || event.button === 1) return; // browser opens the href
				event.preventDefault();
				const { noteId, title, heading } = current.attrs;
				const target = (noteId && latest.get(noteId)) || options.lookupTitle(title);
				options.open({ noteId: target?.id ?? null, title: target?.title ?? title, heading }, event);
			});

			return {
				dom,
				update: (updated) => {
					if (updated.type.name !== 'wikiLink') return false;
					current = updated;
					paint(latest);
					return true;
				},
				destroy: () => unsubscribe?.(),
				ignoreMutation: () => true
			};
		};
	},

	addInputRules() {
		return [
			new InputRule({
				find: /\[\[([^\[\]\n]+)\]\]$/,
				handler: ({ state, range, match }) => {
					const parts = splitWikilink(match[1]);
					if (!parts.title) return null;
					const note = this.options.lookupTitle(parts.title);
					state.tr.replaceWith(
						range.from,
						range.to,
						this.type.create({
							noteId: note?.id ?? null,
							title: note?.title ?? parts.title,
							alias: parts.alias,
							heading: parts.heading
						})
					);
				}
			})
		];
	},

	addPasteRules() {
		return [
			new PasteRule({
				find: /\[\[([^\[\]\n]+)\]\]/g,
				handler: ({ state, range, match }) => {
					const parts = splitWikilink(match[1]);
					if (!parts.title) return null;
					const note = this.options.lookupTitle(parts.title);
					state.tr.replaceWith(
						range.from,
						range.to,
						this.type.create({
							noteId: note?.id ?? null,
							title: note?.title ?? parts.title,
							alias: parts.alias,
							heading: parts.heading
						})
					);
				}
			})
		];
	},

	addProseMirrorPlugins() {
		const options = this.options;
		const type = this.type;
		return [
			Suggestion({
				editor: this.editor,
				pluginKey: new PluginKey('wikiLinkSuggestion'),
				char: '[[',
				allowSpaces: true,
				allowedPrefixes: null,
				allow: outsideCode,
				items: ({ query }) => options.suggest(query),
				render: menuRenderer(options.i18n, () => options.i18n.t('Type a note title')),
				command: ({ editor, range, props }) => {
					const item = props as SuggestItem;
					const parts = item.data?.parts ?? { alias: null, heading: null };
					const title: string = item.data.title;
					// Insert now (typing goes on); a new note is created in the background and the
					// link, written by title, finds it as soon as it exists.
					const after = editor.state.doc.textBetween(
						range.to,
						Math.min(range.to + 2, editor.state.doc.content.size)
					);
					const to = after === ']]' ? range.to + 2 : range.to;
					editor
						.chain()
						.focus()
						.insertContentAt({ from: range.from, to }, [
							{
								type: type.name,
								attrs: {
									noteId: item.create ? null : item.data.id,
									title,
									alias: parts.alias ?? null,
									heading: parts.heading ?? null
								}
							},
							{ type: 'text', text: ' ' }
						])
						.run();
					if (item.create) options.createNote(title);
				}
			})
		];
	}
});
