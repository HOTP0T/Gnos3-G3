// Pasted Markdown with a ``` code fence becomes a real code block (the editor would otherwise make
// each pasted line a paragraph, ``` included). Also covers ```mermaid typed without pressing Enter
// and the rest pasted after it.

import { Extension } from '@tiptap/core';
import { Plugin, PluginKey } from '@tiptap/pm/state';

const HAS_FENCE = /^ {0,3}(```|~~~)/m;
const TYPED_FENCE = /^ {0,3}```[\w-]*\s*$/;

export const FencedPaste = Extension.create<{ toHtml: (markdown: string) => string }>({
	name: 'noteFencedPaste',

	addOptions() {
		return { toHtml: () => '' };
	},

	addProseMirrorPlugins() {
		const editor = this.editor;
		const { toHtml } = this.options;
		return [
			new Plugin({
				key: new PluginKey('noteFencedPaste'),
				props: {
					handlePaste: (view, event) => {
						const text = (event.clipboardData?.getData('text/plain') ?? '').replace(/\r\n/g, '\n');
						const { $from, empty } = view.state.selection;
						if (!text || $from.parent.type.spec.code) return false;

						const typed = empty ? $from.parent.textBetween(0, $from.parentOffset) : '';
						const afterTypedFence =
							TYPED_FENCE.test(typed) && $from.parentOffset === $from.parent.content.size;
						if (!afterTypedFence && !HAS_FENCE.test(text)) return false;

						const html = toHtml(afterTypedFence ? `${typed.trim()}\n${text}` : text);
						const chain = editor.chain().focus();
						if (afterTypedFence) chain.deleteRange({ from: $from.start(), to: $from.pos });
						// Marked ends each code block with a newline the note should not keep.
						chain.insertContent(html.replace(/\n<\/code>/g, '</code>')).run();
						return true;
					}
				}
			})
		];
	}
});
