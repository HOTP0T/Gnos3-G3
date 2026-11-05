// The "/" menu: headings, lists, tasks, quote, code, diagram, table, divider, a link to a note or to Gnos3
// data, today's date, and the vault's templates.

import { Extension } from '@tiptap/core';
import { PluginKey } from '@tiptap/pm/state';
import Suggestion from '@tiptap/suggestion';
import Heading1 from '@lucide/svelte/icons/heading-1';
import Heading2 from '@lucide/svelte/icons/heading-2';
import Heading3 from '@lucide/svelte/icons/heading-3';
import List from '@lucide/svelte/icons/list';
import ListOrdered from '@lucide/svelte/icons/list-ordered';
import ListTodo from '@lucide/svelte/icons/list-todo';
import Quote from '@lucide/svelte/icons/quote';
import SquareCode from '@lucide/svelte/icons/square-code';
import Workflow from '@lucide/svelte/icons/workflow';
import Table from '@lucide/svelte/icons/table';
import Minus from '@lucide/svelte/icons/minus';
import Link2 from '@lucide/svelte/icons/link-2';
import AtSign from '@lucide/svelte/icons/at-sign';
import CalendarDays from '@lucide/svelte/icons/calendar-days';
import LayoutTemplate from '@lucide/svelte/icons/layout-template';
import { menuRenderer, outsideCode, type SuggestItem } from './suggestionPopup.svelte';

export interface SlashOptions {
	i18n: any;
	templates: () => { id: string; title: string }[];
	insertTemplate: (editor: any, templateId: string) => Promise<void>;
	today: () => string;
}

type Run = (editor: any) => void;

export const SlashCommands = Extension.create<SlashOptions>({
	name: 'noteSlashCommands',

	addOptions() {
		return { i18n: null, templates: () => [], insertTemplate: async () => {}, today: () => '' };
	},

	addProseMirrorPlugins() {
		const options = this.options;
		const t = (s: string) => options.i18n?.t(s) ?? s;

		// A Mermaid block with a small example, selected: typing or pasting replaces it.
		const insertDiagram: Run = (editor) => {
			const labels = { first: { label: 'Start' }, last: { label: 'End' } };
			const text = `flowchart TD\n    A[${t(labels.first.label)}] --> B[${t(labels.last.label)}]`;
			editor
				.chain()
				.focus()
				.insertContent({
					type: 'codeBlock',
					attrs: { language: 'mermaid' },
					content: [{ type: 'text', text }]
				})
				.run();
			const { $from } = editor.state.selection;
			if ($from.parent.type.name === 'codeBlock') {
				editor.commands.setTextSelection({ from: $from.start(), to: $from.end() });
			}
		};

		const items = (query: string): SuggestItem[] => {
			// Labels are translated where they are shown (t(label)); written as `label: '…'` so the
			// i18n scan finds them.
			const blocks: { key: string; label: string; icon: any; run: Run; hint?: string }[] = [
				{
					key: 'h1',
					label: 'Heading 1',
					icon: Heading1,
					run: (e) => e.chain().focus().toggleHeading({ level: 1 }).run(),
					hint: '#'
				},
				{
					key: 'h2',
					label: 'Heading 2',
					icon: Heading2,
					run: (e) => e.chain().focus().toggleHeading({ level: 2 }).run(),
					hint: '##'
				},
				{
					key: 'h3',
					label: 'Heading 3',
					icon: Heading3,
					run: (e) => e.chain().focus().toggleHeading({ level: 3 }).run(),
					hint: '###'
				},
				{
					key: 'bullet',
					label: 'Bulleted list',
					icon: List,
					run: (e) => e.chain().focus().toggleBulletList().run(),
					hint: '-'
				},
				{
					key: 'ordered',
					label: 'Numbered list',
					icon: ListOrdered,
					run: (e) => e.chain().focus().toggleOrderedList().run(),
					hint: '1.'
				},
				{
					key: 'task',
					label: 'Task list',
					icon: ListTodo,
					run: (e) => e.chain().focus().toggleTaskList().run(),
					hint: '[ ]'
				},
				{
					key: 'quote',
					label: 'Quote',
					icon: Quote,
					run: (e) => e.chain().focus().toggleBlockquote().run(),
					hint: '>'
				},
				{
					key: 'code',
					label: 'Code block',
					icon: SquareCode,
					run: (e) => e.chain().focus().toggleCodeBlock().run(),
					hint: '```'
				},
				{
					key: 'mermaid',
					label: 'Diagram',
					icon: Workflow,
					run: insertDiagram,
					hint: 'Mermaid'
				},
				{
					key: 'table',
					label: 'Table',
					icon: Table,
					run: (e) => e.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
				},
				{
					key: 'divider',
					label: 'Divider',
					icon: Minus,
					run: (e) => e.chain().focus().setHorizontalRule().run(),
					hint: '---'
				}
			];
			const inserts: { key: string; label: string; icon: any; run: Run; hint?: string }[] = [
				{
					key: 'link',
					label: 'Link to a note',
					icon: Link2,
					run: (e) => e.chain().focus().insertContent('[[').run(),
					hint: '[['
				},
				{
					key: 'entity',
					label: 'Link to Gnos3 data',
					icon: AtSign,
					run: (e) => e.chain().focus().insertContent('@').run(),
					hint: '@'
				},
				{
					key: 'date',
					label: "Today's date",
					icon: CalendarDays,
					run: (e) => e.chain().focus().insertContent(options.today()).run()
				}
			];
			const groups = {
				blocks: { label: 'Blocks' },
				insert: { label: 'Insert' },
				templates: { label: 'Templates' }
			};
			const all: SuggestItem[] = [
				...blocks.map((b) => ({
					key: b.key,
					label: t(b.label),
					icon: b.icon,
					hint: b.hint,
					group: t(groups.blocks.label),
					data: { run: b.run }
				})),
				...inserts.map((b) => ({
					key: b.key,
					label: t(b.label),
					icon: b.icon,
					hint: b.hint,
					group: t(groups.insert.label),
					data: { run: b.run }
				})),
				...options.templates().map((tpl) => ({
					key: `tpl:${tpl.id}`,
					label: tpl.title,
					icon: LayoutTemplate,
					group: t(groups.templates.label),
					data: { template: tpl.id }
				}))
			];
			const q = query.trim().toLocaleLowerCase();
			return q
				? all.filter((i) => i.label.toLocaleLowerCase().includes(q) || i.key.startsWith(q))
				: all;
		};

		return [
			Suggestion({
				editor: this.editor,
				pluginKey: new PluginKey('noteSlashCommands'),
				char: '/',
				startOfLine: false,
				allow: outsideCode,
				items: ({ query }) => items(query),
				render: menuRenderer(options.i18n),
				command: async ({ editor, range, props }) => {
					const item = props as SuggestItem;
					editor.chain().focus().deleteRange(range).run();
					if (item.data?.template) {
						await options.insertTemplate(editor, item.data.template);
					} else {
						item.data?.run?.(editor);
					}
				}
			})
		];
	}
});
