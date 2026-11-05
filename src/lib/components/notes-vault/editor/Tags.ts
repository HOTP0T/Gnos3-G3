// #tags: highlighted where they are written (not in code), clickable (the sidebar filters by
// the tag), and completed from the vault's existing tags after typing #.
// A tag is the same as the backend's find_tags(): letters of any script, digits, _ - /, not only
// digits, after a space or punctuation (so "# Heading" and URL anchors are not tags).

import { Extension } from '@tiptap/core';
import { Plugin, PluginKey } from '@tiptap/pm/state';
import { Decoration, DecorationSet } from '@tiptap/pm/view';
import Suggestion from '@tiptap/suggestion';
import { menuRenderer, outsideCode, type SuggestItem } from './suggestionPopup.svelte';

const TAG_RE = /(^|[\s(\[{,;:!?。，、；：！？（【「])#([\p{L}\p{N}_][\p{L}\p{N}_\-/]*)/gu;

export const findTagsIn = (text: string): { from: number; to: number; tag: string }[] => {
	const out: { from: number; to: number; tag: string }[] = [];
	for (const match of text.matchAll(TAG_RE)) {
		const tag = match[2].replace(/[/-]+$/, '');
		if (!tag || /^[\d/]+$/.test(tag)) continue;
		const from = (match.index ?? 0) + match[1].length;
		out.push({ from, to: from + 1 + tag.length, tag });
	}
	return out;
};

export interface TagOptions {
	i18n: any;
	suggest: (query: string) => SuggestItem[];
	onTagClick: (tag: string) => void;
}

const decorate = (doc: any) => {
	const decorations: Decoration[] = [];
	doc.descendants((node: any, pos: number) => {
		if (node.type.name === 'codeBlock') return false;
		if (!node.isTextblock) return true;
		// Text of the block with non-text inline nodes as spaces, so offsets match positions.
		let text = '';
		const offsets: number[] = [];
		node.forEach((child: any, offset: number) => {
			if (child.isText && !child.marks.some((m: any) => m.type.name === 'code')) {
				for (let i = 0; i < child.text.length; i++) offsets.push(pos + 1 + offset + i);
				text += child.text;
			} else {
				const size = child.isText ? child.text.length : 1;
				for (let i = 0; i < size; i++) offsets.push(-1);
				text += ' '.repeat(size);
			}
		});
		for (const hit of findTagsIn(text)) {
			const from = offsets[hit.from];
			const to = offsets[hit.to - 1];
			if (from < 0 || to < 0) continue;
			decorations.push(
				Decoration.inline(from, to + 1, {
					class: 'note-tag',
					'data-tag': hit.tag,
					nodeName: 'span'
				})
			);
		}
		return false;
	});
	return DecorationSet.create(doc, decorations);
};

export const Tags = Extension.create<TagOptions>({
	name: 'noteTags',

	addOptions() {
		return { i18n: null, suggest: () => [], onTagClick: () => {} };
	},

	addProseMirrorPlugins() {
		const options = this.options;
		return [
			new Plugin({
				key: new PluginKey('noteTagDecorations'),
				state: {
					init: (_, state) => decorate(state.doc),
					apply: (tr, old) => (tr.docChanged ? decorate(tr.doc) : old)
				},
				props: {
					decorations(state) {
						return this.getState(state);
					},
					handleClick(_view, _pos, event) {
						const target = (event.target as HTMLElement | null)?.closest?.('.note-tag');
						if (target && (event.metaKey || event.ctrlKey || event.altKey)) {
							options.onTagClick(target.getAttribute('data-tag') ?? '');
							return true;
						}
						return false;
					},
					handleDOMEvents: {
						dblclick(_view, event) {
							const target = (event.target as HTMLElement | null)?.closest?.('.note-tag');
							if (target) {
								options.onTagClick(target.getAttribute('data-tag') ?? '');
								return true;
							}
							return false;
						}
					}
				}
			}),
			Suggestion({
				editor: this.editor,
				pluginKey: new PluginKey('noteTagSuggestion'),
				char: '#',
				allowSpaces: false,
				// Not at the start of a line: there "# " makes a heading.
				allow: ({ state, range }) =>
					outsideCode({ state, range }) && state.doc.resolve(range.from).parentOffset > 0,
				items: ({ query }) => options.suggest(query),
				render: menuRenderer(options.i18n),
				command: ({ editor, range, props }) => {
					const item = props as SuggestItem;
					editor.chain().focus().insertContentAt(range, `#${item.data.tag} `).run();
				}
			})
		];
	}
});
