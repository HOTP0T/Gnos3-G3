// State shared by the Notes vault screen: which vault is open, its tree (folders + every note's
// summary), and the person's view preferences. The tree is what the sidebar, the quick switcher,
// [[link]] completion, tags and live link titles read, so it is loaded once per vault and
// refreshed after each change.

import { derived, get, writable } from 'svelte/store';
import {
	getVaultTree,
	getVaults,
	type NoteType,
	type TreeNote,
	type Vault,
	type VaultTree
} from '$lib/apis/note-vaults';

export const vaults = writable<Vault[] | null>(null);
export const currentVaultId = writable<string | null>(null);
export const tree = writable<VaultTree | null>(null);
export const treeVaultId = writable<string | null>(null);
export const treeError = writable<string | null>(null);

/** Bumped whenever links may have changed (a note saved, renamed, moved): panels reload. */
export const linksVersion = writable(0);

export const currentVault = derived(
	[vaults, currentVaultId],
	([$vaults, $id]) => ($vaults ?? []).find((v) => v.id === $id) ?? null
);

export const notesById = derived(tree, ($tree) => {
	const map = new Map<string, TreeNote>();
	for (const note of $tree?.notes ?? []) map.set(note.id, note);
	return map;
});

export const normalizeTitle = (title: string | null | undefined) =>
	(title ?? '').trim().replace(/\s+/g, ' ').toLocaleLowerCase();

/** normalized title / alias -> note (the most recently edited wins a tie). */
export const notesByTitle = derived(tree, ($tree) => {
	const map = new Map<string, TreeNote>();
	const sorted = [...($tree?.notes ?? [])].sort((a, b) => a.updated_at - b.updated_at);
	for (const note of sorted) {
		for (const alias of note.aliases ?? []) map.set(normalizeTitle(alias), note);
	}
	for (const note of sorted) map.set(normalizeTitle(note.title), note);
	return map;
});

export const allTags = derived(tree, ($tree) => {
	const counts = new Map<string, number>();
	for (const note of $tree?.notes ?? []) {
		for (const tag of note.tags ?? []) counts.set(tag, (counts.get(tag) ?? 0) + 1);
	}
	return [...counts.entries()]
		.map(([tag, count]) => ({ tag, count }))
		.sort((a, b) => a.tag.localeCompare(b.tag));
});

export const canWrite = (vault: Vault | null) =>
	!!vault && (vault.permission === 'write' || vault.permission === 'manage');

export const noteTypes = (vault: Vault | null): NoteType[] => vault?.settings?.types ?? [];

export const typeOf = (vault: Vault | null, key: string | null | undefined): NoteType | null =>
	(key && noteTypes(vault).find((t) => t.key === key)) || null;

/** A built-in type's name follows the UI language unless the vault renamed it. */
export const typeName = (t: NoteType | null, i18n: any): string => {
	if (!t) return '';
	return t.builtin ? i18n.t(t.name) : t.name;
};

export const vaultName = (vault: Pick<Vault, 'kind' | 'name'> | null, i18n: any): string => {
	if (!vault) return '';
	if (vault.kind === 'personal' && vault.name === 'My notes') return i18n.t('My notes');
	return vault.name;
};

export const chartColor = (token: string | null | undefined) =>
	token ? `var(--${token})` : 'var(--muted-foreground)';

// --- loading ---------------------------------------------------------------

let treeRequest = 0;

export const loadVaults = async (token: string) => {
	const list = await getVaults(token);
	vaults.set(list);
	const current = get(currentVaultId);
	if (!current || !list.some((v) => v.id === current)) {
		const remembered = prefs.get('vault', null as string | null);
		const pick = list.find((v) => v.id === remembered) ?? list[0] ?? null;
		currentVaultId.set(pick?.id ?? null);
	}
	return list;
};

export const loadTree = async (token: string, vaultId: string) => {
	const request = ++treeRequest;
	try {
		const data = await getVaultTree(token, vaultId);
		if (request !== treeRequest) return;
		tree.set(data);
		treeVaultId.set(vaultId);
		treeError.set(null);
	} catch (e) {
		if (request !== treeRequest) return;
		treeError.set(`${e}`);
	}
};

export const refreshTree = async (token: string) => {
	const id = get(currentVaultId);
	if (id) await loadTree(token, id);
	linksVersion.update((n) => n + 1);
};

/** Updates one note in the loaded tree without a round trip (title typed, folder changed). */
export const patchTreeNote = (id: string, patch: Partial<TreeNote>) => {
	tree.update(($tree) => {
		if (!$tree) return $tree;
		return {
			...$tree,
			notes: $tree.notes.map((n) => (n.id === id ? { ...n, ...patch } : n))
		};
	});
};

// --- preferences (this browser only) ----------------------------------------

const PREFIX = 'gnos3.notes.';

export const prefs = {
	get<T>(key: string, fallback: T): T {
		try {
			const raw = localStorage.getItem(PREFIX + key);
			return raw === null ? fallback : (JSON.parse(raw) as T);
		} catch {
			return fallback;
		}
	},
	set(key: string, value: unknown) {
		try {
			localStorage.setItem(PREFIX + key, JSON.stringify(value));
		} catch {
			// private window / storage blocked: preferences just don't stick
		}
	}
};

// --- helpers -----------------------------------------------------------------

export const folderName = (path: string) => path.split('/').pop() ?? path;

export const parentFolder = (path: string) =>
	path.includes('/') ? path.slice(0, path.lastIndexOf('/')) : '';

export const joinFolder = (parent: string, name: string) =>
	[parent, name.trim()].filter(Boolean).join('/');

/** Characters a title cannot hold (they would break [[links]] and exported file names). */
export const cleanTitle = (title: string) =>
	title
		.replace(/[\[\]|#^\\/:*?"<>\n\r\t]/g, ' ')
		.replace(/\s+/g, ' ')
		.trim()
		.slice(0, 200);

export const relativeTime = (ns: number, dayjs: any) => dayjs(ns / 1_000_000).fromNow();
