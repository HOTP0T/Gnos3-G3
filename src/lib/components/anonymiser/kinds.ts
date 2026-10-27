import type {
	AnonymiserKind,
	AnonymiserLanguage,
	AnonymiserMode,
	AnonymiserSettings
} from '$lib/apis/anonymiser';

/** Shared by the /anonymiser layout and its pages: the settings are fetched once. */
export const ANONYMISER_CONTEXT = 'anonymiser';

export interface AnonymiserState {
	loading: boolean;
	error: string;
	settings: AnonymiserSettings | null;
	kinds: AnonymiserKind[];
	canEdit: boolean;
}

/** The kinds a switch turns on or off (CUSTOM is the user's own selection). */
export const KIND_ORDER: AnonymiserKind[] = [
	'PERSON',
	'EMAIL',
	'PHONE',
	'IBAN',
	'CARD',
	'ID',
	'IP',
	'ORG',
	'PLACE',
	'DATE',
	'URL'
];

export const KIND_LABELS: Record<AnonymiserKind, string> = {
	PERSON: 'Names',
	EMAIL: 'Email addresses',
	PHONE: 'Phone numbers',
	IBAN: 'IBANs',
	CARD: 'Card numbers',
	ID: 'ID numbers',
	IP: 'IP addresses',
	ORG: 'Organisations',
	PLACE: 'Places and addresses',
	DATE: 'Dates',
	URL: 'Web addresses',
	CUSTOM: 'Words you added'
};

// Literal class names so Tailwind keeps them. `mark` = a finding in the text, `dot` = the legend.
export const KIND_STYLE: Record<AnonymiserKind, { mark: string; dot: string }> = {
	PERSON: { mark: 'bg-chart-1/15 border-chart-1', dot: 'bg-chart-1' },
	EMAIL: { mark: 'bg-chart-2/15 border-chart-2', dot: 'bg-chart-2' },
	PHONE: { mark: 'bg-chart-3/15 border-chart-3', dot: 'bg-chart-3' },
	IBAN: { mark: 'bg-chart-4/15 border-chart-4', dot: 'bg-chart-4' },
	CARD: { mark: 'bg-chart-5/15 border-chart-5', dot: 'bg-chart-5' },
	ID: { mark: 'bg-chart-7/15 border-chart-7', dot: 'bg-chart-7' },
	IP: { mark: 'bg-chart-8/15 border-chart-8', dot: 'bg-chart-8' },
	ORG: { mark: 'bg-chart-6/15 border-chart-6', dot: 'bg-chart-6' },
	PLACE: { mark: 'bg-warning/15 border-warning', dot: 'bg-warning' },
	DATE: { mark: 'bg-info/15 border-info', dot: 'bg-info' },
	URL: { mark: 'bg-success/15 border-success', dot: 'bg-success' },
	CUSTOM: { mark: 'bg-primary/15 border-primary', dot: 'bg-primary' }
};

export const MODE_LABELS: Record<AnonymiserMode, string> = {
	labels: 'Replace with labels',
	mask: 'Mask with asterisks',
	remove: 'Remove',
	hash: 'Replace with codes'
};

export const MODE_ORDER: AnonymiserMode[] = ['labels', 'mask', 'remove', 'hash'];

// Each language in its own name, so it is never translated ("auto" is, in the component).
export const LANGUAGE_NAMES: Record<Exclude<AnonymiserLanguage, 'auto'>, string> = {
	en: 'English',
	fr: 'Français',
	es: 'Español',
	pt: 'Português',
	zh: '中文'
};
