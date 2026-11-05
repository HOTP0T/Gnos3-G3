// Renders a TipTap suggestion (the [[, @, # and / menus) with SuggestionMenu.svelte, placed under
// the caret (above it when there is no room below).

import { mount, unmount } from 'svelte';
import SuggestionMenu from './SuggestionMenu.svelte';

export interface SuggestItem {
	key: string;
	label: string;
	detail?: string;
	hint?: string;
	group?: string;
	icon?: any;
	color?: string;
	create?: boolean;
	data?: any;
}

/** The [[, @, # and / menus stay out of code: `A[[x]]` is Mermaid, not a link. */
export const outsideCode = ({ state, range }: { state: any; range: { from: number } }) => {
	const at = state.doc.resolve(range.from);
	return !at.parent.type.spec.code && !at.marks().some((m: any) => m.type.spec.code);
};

export const menuRenderer = (i18n: any, emptyText?: () => string) => () => {
	let target: HTMLDivElement | null = null;
	let instance: any = null;
	let rect: (() => DOMRect | null) | null = null;
	const state = $state({
		items: [] as SuggestItem[],
		loading: false,
		emptyText: '',
		onSelect: (_item: SuggestItem) => {}
	});

	const place = () => {
		const r = rect?.();
		if (!target || !r) return;
		const height = target.offsetHeight || 240;
		const width = target.offsetWidth || 320;
		const below = r.bottom + 6 + height <= window.innerHeight;
		target.style.top = `${below ? r.bottom + 6 : Math.max(8, r.top - height - 6)}px`;
		target.style.left = `${Math.max(8, Math.min(r.left, window.innerWidth - width - 8))}px`;
	};

	return {
		onStart: (props: any) => {
			target = document.createElement('div');
			target.style.position = 'fixed';
			target.style.zIndex = '60';
			document.body.appendChild(target);
			state.items = props.items;
			state.emptyText = emptyText?.() ?? '';
			state.onSelect = (item) => props.command(item);
			rect = props.clientRect;
			instance = mount(SuggestionMenu, {
				target,
				props: state,
				context: new Map([['i18n', i18n]])
			});
			requestAnimationFrame(place);
		},
		onUpdate: (props: any) => {
			state.items = props.items;
			state.onSelect = (item) => props.command(item);
			rect = props.clientRect;
			requestAnimationFrame(place);
		},
		onKeyDown: (props: any) => {
			if (props.event.key === 'Escape') {
				target?.remove();
				return true;
			}
			return instance?.onKeyDown?.(props.event) ?? false;
		},
		onExit: () => {
			if (instance) {
				try {
					unmount(instance);
				} catch {
					// already gone
				}
			}
			instance = null;
			target?.remove();
			target = null;
		}
	};
};
