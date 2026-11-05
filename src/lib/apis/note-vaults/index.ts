// Notes vaults — Gnos3's backend `/api/v1/note-vaults` (routers/note_vaults.py).
// Notes themselves are still read, saved, shared and deleted through `$lib/apis/notes`.

import i18next from 'i18next';
import { WEBUI_API_BASE_URL } from '$lib/constants';
import { langHeader } from '$lib/utils/uiLocale';

export type VaultPermission = 'read' | 'write' | 'manage';

export type FieldKind =
	| 'text'
	| 'number'
	| 'date'
	| 'checkbox'
	| 'select'
	| 'multiselect'
	| 'url'
	| 'note'
	| 'notes'
	| 'entity';

export interface TypeField {
	key: string;
	label: string;
	kind: FieldKind;
	options?: string[];
	note_type?: string;
	entity_type?: string;
}

export interface NoteType {
	key: string;
	name: string;
	icon: string;
	color: string;
	builtin?: boolean;
	fields: TypeField[];
}

export interface VaultSettings {
	daily: { folder: string; format: string; template_id: string | null };
	templates_folder: string;
	types: NoteType[];
	ai: { knowledge: boolean };
	graph?: Record<string, unknown>;
}

export interface Vault {
	id: string;
	kind: 'personal' | 'shared';
	owner_id: string | null;
	name: string;
	description: string | null;
	color: string | null;
	icon: string | null;
	settings: VaultSettings;
	permission: VaultPermission;
	note_count: number | null;
	knowledge_id: string | null;
	access_grants?: any[];
	created_at: number;
	updated_at: number;
}

export interface TreeNote {
	id: string;
	title: string;
	user_id: string;
	is_pinned: boolean;
	created_at: number;
	updated_at: number;
	folder: string;
	type: string | null;
	tags: string[];
	aliases: string[];
	word_count: number;
	excerpt: string;
	links_in: number;
	links_out: number;
}

export interface VaultTree {
	folders: string[];
	notes: TreeNote[];
}

export interface GraphNode {
	id: string;
	kind: 'note' | 'ghost' | 'entity' | 'tag';
	title: string;
	type?: string | null;
	tags?: string[];
	words?: number;
	folder?: string;
	updated_at?: number;
	entity_type?: string;
	entity_id?: string;
	href?: string;
}

export interface GraphEdge {
	source: string;
	target: string;
	kind: 'link' | 'property' | 'entity' | 'tag';
	key?: string | null;
}

export interface NoteRef {
	id: string;
	title: string;
	type: string | null;
	folder: string;
}

export interface NoteLinks {
	outgoing: { kind: string; property: string | null; note: NoteRef | null; title: string | null }[];
	backlinks: { note: NoteRef; contexts: string[]; properties: string[] }[];
	unlinked: { note: NoteRef; contexts: string[] }[];
	entities: {
		entity_type: string;
		entity_id: string;
		label: string | null;
		href: string;
		property: string | null;
	}[];
}

export interface NotePlace {
	vault_id: string;
	vault_name: string;
	vault_kind: 'personal' | 'shared';
	folder: string;
	vault_permission: VaultPermission | null;
	settings: VaultSettings | null;
}

export interface SearchHit {
	id: string;
	title: string;
	folder: string;
	updated_at: number;
	snippet: string;
	score: number;
}

export interface LinkSuggestion {
	id: string;
	title: string;
	phrase: string;
	reason: string | null;
	source: 'mention' | 'ai';
}

const request = async <T>(
	token: string,
	method: string,
	path: string,
	body?: unknown
): Promise<T> => {
	const res = await fetch(`${WEBUI_API_BASE_URL}/note-vaults${path}`, {
		method,
		headers: {
			Accept: 'application/json',
			...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
			authorization: `Bearer ${token}`,
			...langHeader()
		},
		body: body !== undefined ? JSON.stringify(body) : undefined
	});
	if (!res.ok) {
		let detail: string = `${res.status}`;
		try {
			const json = await res.json();
			// Our fixed messages (routers/note_vaults.py) are translated in gnos3.json.
			detail = typeof json?.detail === 'string' ? i18next.t(json.detail) : detail;
		} catch {
			// not JSON
		}
		throw detail;
	}
	return (await res.json()) as T;
};

export const getVaults = (token: string) => request<Vault[]>(token, 'GET', '/');

export const getVault = (token: string, vaultId: string) =>
	request<Vault>(token, 'GET', `/${vaultId}`);

export const createVault = (
	token: string,
	form: { name: string; description?: string; color?: string; icon?: string; access_grants?: any[] }
) => request<Vault>(token, 'POST', '/create', form);

export const updateVault = (
	token: string,
	vaultId: string,
	form: {
		name?: string;
		description?: string;
		color?: string;
		icon?: string;
		settings?: Partial<VaultSettings>;
	}
) => request<Vault>(token, 'POST', `/${vaultId}/update`, form);

export const updateVaultAccess = (token: string, vaultId: string, accessGrants: any[]) =>
	request<Vault>(token, 'POST', `/${vaultId}/access`, { access_grants: accessGrants });

export const deleteVault = (token: string, vaultId: string) =>
	request<{ deleted_notes: number }>(token, 'DELETE', `/${vaultId}`);

export const getVaultTree = (token: string, vaultId: string) =>
	request<VaultTree>(token, 'GET', `/${vaultId}/tree`);

export const getVaultGraph = (token: string, vaultId: string) =>
	request<{ nodes: GraphNode[]; edges: GraphEdge[] }>(token, 'GET', `/${vaultId}/graph`);

export const searchVault = (token: string, vaultId: string, q: string) =>
	request<SearchHit[]>(token, 'GET', `/${vaultId}/search?q=${encodeURIComponent(q)}`);

export const getSharedWithMe = (token: string) =>
	request<{ id: string; title: string; user_id: string; updated_at: number }[]>(
		token,
		'GET',
		'/shared/notes'
	);

export const createFolder = (token: string, vaultId: string, path: string) =>
	request<{ path: string }>(token, 'POST', `/${vaultId}/folders`, { path });

export const renameFolder = (token: string, vaultId: string, from: string, to: string) =>
	request<{ moved: number; path: string }>(token, 'POST', `/${vaultId}/folders/rename`, {
		from,
		to
	});

export const deleteFolder = (
	token: string,
	vaultId: string,
	path: string,
	mode: 'move_up' | 'delete'
) => request<{ notes: number }>(token, 'POST', `/${vaultId}/folders/delete`, { path, mode });

export const createVaultNote = (
	token: string,
	vaultId: string,
	form: {
		title?: string;
		folder?: string;
		md?: string;
		properties?: Record<string, unknown>;
		files?: any[];
		unique?: boolean;
	}
) =>
	request<{ id: string; title: string; folder: string; vault_id: string }>(
		token,
		'POST',
		`/${vaultId}/notes`,
		form
	);

export const importVaultNotes = (token: string, vaultId: string, items: any[]) =>
	request<{ created: number }>(token, 'POST', `/${vaultId}/import`, { items });

export const exportVault = async (token: string, vaultId: string): Promise<Blob> => {
	const res = await fetch(`${WEBUI_API_BASE_URL}/note-vaults/${vaultId}/export`, {
		headers: { authorization: `Bearer ${token}`, ...langHeader() }
	});
	if (!res.ok) throw `${res.status}`;
	return await res.blob();
};

export const getNotePlace = (token: string, noteId: string) =>
	request<NotePlace>(token, 'GET', `/notes/${noteId}/place`);

export const getNoteLinks = (token: string, noteId: string) =>
	request<NoteLinks>(token, 'GET', `/notes/${noteId}/links`);

export const moveNote = (token: string, noteId: string, vaultId: string, folder: string) =>
	request<{ vault_id: string; folder: string }>(token, 'POST', `/notes/${noteId}/move`, {
		vault_id: vaultId,
		folder
	});

export const updateNoteMeta = (
	token: string,
	noteId: string,
	form: { title?: string; properties?: Record<string, unknown>; files?: any[] }
) =>
	request<{ id: string; title: string; properties: Record<string, unknown> }>(
		token,
		'POST',
		`/notes/${noteId}/meta`,
		form
	);

/** Only for a note still in Markdown (never opened in the editor); 409 otherwise. */
export const setNoteMarkdown = (token: string, noteId: string, md: string) =>
	request<{ id: string }>(token, 'POST', `/notes/${noteId}/markdown`, { md });

export const suggestNoteLinks = (token: string, noteId: string, model: string, lang: string) =>
	request<{ suggestions: LinkSuggestion[]; ai_error?: boolean }>(
		token,
		'POST',
		`/notes/${noteId}/suggest-links`,
		{ model, lang }
	);

export const prepareVaultKnowledge = (token: string, vaultId: string) =>
	request<{ knowledge_id: string; synced: number; pending: number; name: string }>(
		token,
		'POST',
		`/${vaultId}/knowledge`
	);

export const prepareVaultScope = (
	token: string,
	vaultId: string,
	scope: { folder?: string; tag?: string; note_ids?: string[] }
) =>
	request<{
		mode: 'empty' | 'notes' | 'collections';
		notes?: { id: string; title: string }[];
		knowledge_id?: string;
		collection_names?: string[];
		count?: number;
		total?: number;
		pending?: number;
	}>(token, 'POST', `/${vaultId}/knowledge/scope`, scope);
