// ```mermaid code blocks draw as diagrams.
//
// The note keeps the plain fenced block, so Markdown, exports, co-editing and chat attachments see
// what they always saw. The picture is a widget right after the block and never enters the
// document. NotesApp's CSS collapses the block unless the widget carries data-source: the caret is
// in the block, or there is nothing to show instead of it (empty, or it cannot be drawn).

import { Extension } from '@tiptap/core';
import { Plugin, PluginKey, TextSelection } from '@tiptap/pm/state';
import { Decoration, DecorationSet } from '@tiptap/pm/view';
import { mount, unmount } from 'svelte';
import MermaidView from './MermaidView.svelte';
import { drawMermaid, isDarkTheme } from './mermaidDraw';

const TYPING_PAUSE_MS = 350;

const isMermaid = (node: any) =>
	node.type.name === 'codeBlock' && `${node.attrs.language ?? ''}`.toLowerCase() === 'mermaid';

const blocksIn = (doc: any) => {
	const blocks: { node: any; pos: number }[] = [];
	doc.descendants((node: any, pos: number) => {
		if (isMermaid(node)) blocks.push({ node, pos });
		return !node.isTextblock;
	});
	return blocks;
};

class Diagram {
	host = document.createElement('div');
	pos = 0;
	size = 0;
	private source: string | null = null;
	private timer: ReturnType<typeof setTimeout> | undefined;
	private run = 0;
	private instance: any;
	private props = $state({
		svg: '',
		error: '',
		drawing: false,
		empty: true,
		editable: false,
		editing: false,
		onEdit: () => {}
	});

	constructor(i18n: any, onEdit: (diagram: Diagram) => void) {
		this.host.className = 'note-mermaid';
		this.host.contentEditable = 'false';
		this.props.onEdit = () => onEdit(this);
		this.instance = mount(MermaidView, {
			target: this.host,
			props: this.props,
			context: new Map([['i18n', i18n]])
		});
	}

	update(code: string, pos: number, size: number, editing: boolean, editable: boolean) {
		this.pos = pos;
		this.size = size;
		this.props.editing = editing;
		this.props.editable = editable;
		if (code !== this.source) {
			this.source = code;
			this.props.empty = !code.trim();
			clearTimeout(this.timer);
			this.run++;
			if (this.props.empty) {
				this.props.svg = '';
				this.props.error = '';
				this.props.drawing = false;
			} else {
				if (!this.props.svg) this.props.drawing = true;
				this.timer = setTimeout(() => this.draw(), editing ? TYPING_PAUSE_MS : 0);
			}
		}
		this.showSource();
	}

	redraw() {
		if (this.source?.trim()) this.draw();
	}

	destroy() {
		clearTimeout(this.timer);
		this.run++;
		unmount(this.instance);
		this.host.remove();
	}

	private async draw() {
		const run = ++this.run;
		try {
			const svg = await drawMermaid(this.source ?? '');
			if (run !== this.run) return;
			this.props.svg = svg;
			this.props.error = '';
		} catch (e: any) {
			if (run !== this.run) return;
			this.props.error = `${e?.message ?? e}`;
		}
		this.props.drawing = false;
		this.showSource();
	}

	private showSource() {
		const { editing, error, empty } = this.props;
		this.host.toggleAttribute('data-source', editing || !!error || empty);
	}
}

export const MermaidBlocks = Extension.create<{ i18n: any }>({
	name: 'noteMermaidBlocks',

	addOptions() {
		return { i18n: null };
	},

	addProseMirrorPlugins() {
		const editor = this.editor;
		const { i18n } = this.options;
		const diagrams: Diagram[] = [];

		const openSource = (diagram: Diagram) => {
			const { view } = editor;
			const end = diagram.pos + diagram.size - 1;
			view.dispatch(
				view.state.tr.setSelection(TextSelection.create(view.state.doc, end)).scrollIntoView()
			);
			view.focus();
		};

		const diagramAt = (index: number) => {
			while (diagrams.length <= index) diagrams.push(new Diagram(i18n, openSource));
			return diagrams[index];
		};

		const widgets = (doc: any) =>
			DecorationSet.create(
				doc,
				blocksIn(doc).map(({ node, pos }, index) =>
					// The key keeps one element per block through typing, so the picture does not flicker.
					Decoration.widget(pos + node.nodeSize, () => diagramAt(index).host, {
						key: `note-mermaid-${index}`,
						side: -1,
						ignoreSelection: true,
						stopEvent: () => true
					})
				)
			);

		const sync = (view: any) => {
			const blocks = blocksIn(view.state.doc);
			const { from, to } = view.state.selection;
			const focused = view.editable && view.hasFocus();
			blocks.forEach(({ node, pos }, index) => {
				const editing = focused && from > pos && to < pos + node.nodeSize;
				diagramAt(index).update(node.textContent, pos, node.nodeSize, editing, view.editable);
			});
			for (const gone of diagrams.splice(blocks.length)) gone.destroy();
		};

		editor.on('destroy', () => {
			for (const diagram of diagrams.splice(0)) diagram.destroy();
		});

		return [
			new Plugin({
				key: new PluginKey('noteMermaidBlocks'),
				state: {
					init: (_, state) => widgets(state.doc),
					apply: (tr, old) => (tr.docChanged ? widgets(tr.doc) : old)
				},
				props: {
					decorations(state) {
						return this.getState(state);
					},
					handleDOMEvents: {
						focus: (view) => {
							sync(view);
							return false;
						},
						blur: (view) => {
							// The browser has not moved focus yet.
							setTimeout(() => {
								if (!view.isDestroyed) sync(view);
							});
							return false;
						}
					}
				},
				view: (view) => {
					let dark = isDarkTheme();
					const theme = new MutationObserver(() => {
						if (isDarkTheme() === dark) return;
						dark = isDarkTheme();
						diagrams.forEach((diagram) => diagram.redraw());
					});
					theme.observe(document.documentElement, {
						attributes: true,
						attributeFilter: ['class']
					});
					sync(view);
					return { update: (updated) => sync(updated), destroy: () => theme.disconnect() };
				}
			})
		];
	}
});
