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
	mask: 'Mask the characters',
	remove: 'Remove',
	hash: 'Replace with codes',
	fake: 'Fake values',
	encrypt: 'Encrypt'
};

export const MODE_ORDER: AnonymiserMode[] = ['labels', 'mask', 'remove', 'hash', 'fake', 'encrypt'];

/** Readable names of the specific types the service reports (`entity`). */
export const ENTITY_LABELS: Record<string, string> = {
	PERSON: 'Name',
	EMAIL_ADDRESS: 'Email address',
	PHONE_NUMBER: 'Phone number',
	CN_MOBILE: 'Chinese mobile number',
	IBAN_CODE: 'IBAN',
	CREDIT_CARD: 'Card number',
	BANK_CARD: 'Bank card number',
	IP_ADDRESS: 'IP address',
	ORGANIZATION: 'Organisation',
	LOCATION: 'Place',
	DATE_TIME: 'Date',
	URL: 'Web address',
	CUSTOM: 'Word you hid',
	ID_NUMBER: 'Number next to an ID keyword',
	FR_NIR: 'French social security number',
	ES_NIF: 'Spanish DNI / NIF',
	ES_NIE: 'Spanish NIE',
	PT_NIF: 'Portuguese tax number (NIF)',
	BR_CPF: 'Brazilian CPF',
	UK_NINO: 'UK National Insurance number',
	UK_NHS: 'NHS number',
	US_SSN: 'US Social Security number',
	CN_ID: 'Chinese ID card number',
	HK_ID: 'Hong Kong ID card number',
	TW_ID: 'Taiwan ID number',
	TH_TNIN: 'Thai ID number',
	IT_FISCAL_CODE: 'Italian fiscal code',
	PL_PESEL: 'Polish PESEL',
	SG_NRIC_FIN: 'Singapore NRIC / FIN',
	KR_RRN: 'Korean resident registration number',
	IN_PAN: 'Indian PAN',
	IN_AADHAAR: 'Aadhaar number',
	SE_PERSONNUMMER: 'Swedish personal identity number',
	FI_PERSONAL_IDENTITY_CODE: 'Finnish personal identity code',
	DE_TAX_ID: 'German tax ID',
	DE_ID_CARD: 'German ID card number',
	TR_NATIONAL_ID: 'Turkish ID number',
	AU_TFN: 'Australian tax file number',
	ZA_ID_NUMBER: 'South African ID number'
};

/** Types that only repeat their kind ("Names" → "Name"): not shown again in the list. */
export const ENTITY_SAME_AS_KIND = new Set([
	'PERSON',
	'EMAIL_ADDRESS',
	'PHONE_NUMBER',
	'IBAN_CODE',
	'CREDIT_CARD',
	'IP_ADDRESS',
	'ORGANIZATION',
	'LOCATION',
	'DATE_TIME',
	'URL',
	'CUSTOM'
]);

// Each language in its own name, so it is never translated ("auto" is, in the component).
export const LANGUAGE_NAMES: Record<Exclude<AnonymiserLanguage, 'auto'>, string> = {
	en: 'English',
	fr: 'Français',
	es: 'Español',
	pt: 'Português',
	zh: '中文'
};
