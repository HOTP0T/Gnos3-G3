import { ANONYMISER_API_BASE_URL } from '$lib/constants';
import { langHeader } from '$lib/utils/uiLocale';

export type AnonymiserKind =
	| 'PERSON'
	| 'EMAIL'
	| 'PHONE'
	| 'IBAN'
	| 'CARD'
	| 'ID'
	| 'IP'
	| 'ORG'
	| 'PLACE'
	| 'DATE'
	| 'URL'
	| 'CUSTOM';

export type AnonymiserLanguage = 'auto' | 'en' | 'fr' | 'es' | 'pt' | 'zh';

export type AnonymiserMode = 'labels' | 'mask' | 'remove' | 'hash';

export interface AnonymiserSettings {
	kinds: Partial<Record<AnonymiserKind, boolean>>;
	threshold: number;
	allow_list: string[];
	deny_list: string[];
}

export interface AnonymiserSettingsResponse {
	settings: AnonymiserSettings;
	kinds: AnonymiserKind[];
	languages: string[];
	can_edit: boolean;
}

export interface AnonymiserFinding {
	start: number;
	end: number;
	kind: AnonymiserKind;
	entity?: string;
	score?: number;
	text?: string;
}

export interface AnalyzeResponse {
	language: string;
	findings: AnonymiserFinding[];
}

export interface AnonymizeResponse {
	text: string;
	findings: AnonymiserFinding[];
	labels: Record<string, string>;
}

/** Per-run overrides; anything left out uses the admin's settings. */
export interface AnonymiserRunOptions {
	language?: AnonymiserLanguage;
	kinds?: Partial<Record<AnonymiserKind, boolean>>;
	threshold?: number;
	allow_list?: string[];
	deny_list?: string[];
}

function authHeaders(): Record<string, string> {
	const token = typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null;
	return {
		'Content-Type': 'application/json',
		...langHeader(),
		...(token ? { Authorization: `Bearer ${token}` } : {})
	};
}

// The service answers errors as {detail}, already in the reader's language.
async function asJson<T>(res: Response): Promise<T> {
	if (!res.ok) {
		const err = await res.json().catch(() => ({ detail: res.statusText }));
		throw new Error(typeof err?.detail === 'string' ? err.detail : res.statusText);
	}
	return res.json();
}

export const getAnonymiserSettings = async (): Promise<AnonymiserSettingsResponse> => {
	const res = await fetch(`${ANONYMISER_API_BASE_URL}/api/anonymiser/settings`, {
		method: 'GET',
		headers: authHeaders()
	});
	return asJson(res);
};

export const saveAnonymiserSettings = async (
	settings: AnonymiserSettings
): Promise<AnonymiserSettingsResponse> => {
	const res = await fetch(`${ANONYMISER_API_BASE_URL}/api/anonymiser/settings`, {
		method: 'PUT',
		headers: authHeaders(),
		body: JSON.stringify(settings)
	});
	return asJson(res);
};

export const analyzeText = async (
	text: string,
	options: AnonymiserRunOptions = {},
	signal?: AbortSignal
): Promise<AnalyzeResponse> => {
	const res = await fetch(`${ANONYMISER_API_BASE_URL}/api/anonymiser/analyze`, {
		method: 'POST',
		headers: authHeaders(),
		body: JSON.stringify({ text, language: options.language ?? 'auto', ...options }),
		signal
	});
	return asJson(res);
};

/** With `findings`, the service hides exactly those spans (the user's reviewed list). */
export const anonymizeText = async (
	text: string,
	mode: AnonymiserMode,
	options: AnonymiserRunOptions & {
		findings?: Pick<AnonymiserFinding, 'start' | 'end' | 'kind'>[];
	} = {},
	signal?: AbortSignal
): Promise<AnonymizeResponse> => {
	const res = await fetch(`${ANONYMISER_API_BASE_URL}/api/anonymiser/anonymize`, {
		method: 'POST',
		headers: authHeaders(),
		body: JSON.stringify({ text, mode, ...options }),
		signal
	});
	return asJson(res);
};
