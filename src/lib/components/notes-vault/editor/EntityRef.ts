// Links from a note to Gnos3 data (a company in Accounting, an invoice, a business card, a K4mi
// document, a chat). Typing @ searches what the person can see; the link is stored as an inline
// node and written to Markdown as an ordinary link to the record's page.

import { Node, mergeAttributes } from '@tiptap/core';
import { PluginKey } from '@tiptap/pm/state';
import Suggestion from '@tiptap/suggestion';
import { mount, unmount } from 'svelte';
import {
	ENTITY_META,
	entityHref,
	entityMarkdown,
	opensOutside,
	type EntityType
} from '../entities';
import { menuRenderer, outsideCode, type SuggestItem } from './suggestionPopup.svelte';

export interface EntityRefOptions {
	i18n: any;
	search: (query: string) => Promise<SuggestItem[]>;
	open: (href: string, outside: boolean, event: MouseEvent) => void;
}

export const EntityRef = Node.create<EntityRefOptions>({
	name: 'entityRef',
	group: 'inline',
	inline: true,
	atom: true,
	selectable: true,

	addOptions() {
		return { i18n: null, search: async () => [], open: () => {} };
	},

	addAttributes() {
		return {
			entityType: {
				default: null,
				parseHTML: (el) => el.getAttribute('data-entity-type'),
				renderHTML: (attrs) => ({ 'data-entity-type': attrs.entityType })
			},
			entityId: {
				default: null,
				parseHTML: (el) => el.getAttribute('data-entity-id'),
				renderHTML: (attrs) => ({ 'data-entity-id': attrs.entityId })
			},
			label: {
				default: '',
				parseHTML: (el) => el.getAttribute('data-label') || el.textContent || '',
				renderHTML: (attrs) => ({ 'data-label': attrs.label })
			}
		};
	},

	parseHTML() {
		return [{ tag: 'span[data-type="entity-ref"]' }, { tag: 'a[data-type="entity-ref"]' }];
	},

	renderHTML({ node, HTMLAttributes }) {
		const { entityType, entityId, label } = node.attrs;
		return [
			'a',
			mergeAttributes(HTMLAttributes, {
				'data-type': 'entity-ref',
				'data-md': entityMarkdown(entityType, entityId, label || String(entityId)),
				href: entityHref(entityType, entityId),
				class: 'entity-ref'
			}),
			label
		];
	},

	renderText({ node }) {
		return node.attrs.label;
	},

	addNodeView() {
		const options = this.options;
		return ({ node }) => {
			let current = node;
			const dom = document.createElement('a');
			dom.className = 'entity-ref';
			dom.setAttribute('contenteditable', 'false');
			const iconHost = document.createElement('span');
			iconHost.className = 'entity-ref-icon';
			const text = document.createElement('span');
			dom.append(iconHost, text);
			let icon: any = null;

			const paint = () => {
				const { entityType, entityId, label } = current.attrs;
				const meta = ENTITY_META[entityType as EntityType];
				dom.href = entityHref(entityType, entityId);
				if (opensOutside(entityType)) dom.target = '_blank';
				dom.title = meta ? (options.i18n?.t(meta.label) ?? meta.label) : '';
				text.textContent = label || String(entityId);
				if (icon) unmount(icon);
				icon = meta ? mount(meta.icon, { target: iconHost, props: { class: 'size-3.5' } }) : null;
			};
			paint();

			dom.addEventListener('click', (event) => {
				if (event.metaKey || event.ctrlKey || event.button === 1) return;
				event.preventDefault();
				const { entityType, entityId } = current.attrs;
				options.open(entityHref(entityType, entityId), opensOutside(entityType), event);
			});

			return {
				dom,
				update: (updated) => {
					if (updated.type.name !== 'entityRef') return false;
					current = updated;
					paint();
					return true;
				},
				destroy: () => {
					if (icon) unmount(icon);
				},
				ignoreMutation: () => true
			};
		};
	},

	addProseMirrorPlugins() {
		const options = this.options;
		const type = this.type;
		// Debounced by waiting a moment and answering only the latest query. Every call settles
		// (the suggestion plugin waits for each one before it opens or updates the menu).
		let latest = '';
		return [
			Suggestion({
				editor: this.editor,
				pluginKey: new PluginKey('entityRefSuggestion'),
				char: '@',
				allowSpaces: true,
				allow: outsideCode,
				items: async ({ query }) => {
					latest = query;
					await new Promise((resolve) => setTimeout(resolve, 180));
					if (latest !== query) return [];
					return await options.search(query).catch(() => []);
				},
				render: menuRenderer(options.i18n, () =>
					options.i18n.t('Type a name: company, invoice, business card, document or chat')
				),
				command: ({ editor, range, props }) => {
					const item = props as SuggestItem;
					editor
						.chain()
						.focus()
						.insertContentAt(range, [
							{
								type: type.name,
								attrs: {
									entityType: item.data.entity_type,
									entityId: item.data.entity_id,
									label: item.data.label
								}
							},
							{ type: 'text', text: ' ' }
						])
						.run();
				}
			})
		];
	}
});
