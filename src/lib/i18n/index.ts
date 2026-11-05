import i18next from 'i18next';
import resourcesToBackend from 'i18next-resources-to-backend';
import LanguageDetector from 'i18next-browser-languagedetector';
import type { i18n as i18nType } from 'i18next';
import { writable } from 'svelte/store';
import dayjs, { getDayjsLocale } from '$lib/dayjs';
import type { I18nOverrides } from '$lib/utils/translationDictionary';

import { assembleSettingsTranslations } from './settings-translations';
import languages from './locales/languages.json';

let overrides: I18nOverrides = {};

export const loadBundledResource = async (language: string): Promise<Record<string, string>> =>
	(await import(`./locales/${language}/translation.json`)).default;

// Gnos3's own strings (modules, accounting, design-system primitives) live in gnos3.json next to
// Open WebUI's translation.json, so upstream merges never touch them. Merged over upstream; an
// empty value keeps upstream's. Keep in step with the code: `node scripts/i18n-gnos3.mjs`.
// (The glob sits in the function, not at module level: i18next-parser imports this file under Node.)
const withGnos3Strings = async (language: string): Promise<Record<string, string>> => {
	// A language Open WebUI ships no file for (uz-Latn-UZ), or a bare language code i18next also
	// tries (fr for fr-CA), loads as empty instead of failing the load.
	const upstream = await loadBundledResource(language).catch(() => ({}));
	const own = import.meta.glob('./locales/*/gnos3.json')[`./locales/${language}/gnos3.json`];
	if (!own) return upstream;
	const ours = ((await own()) as { default: Record<string, string> }).default;
	return {
		...upstream,
		...Object.fromEntries(Object.entries(ours).filter(([, value]) => value))
	};
};

const loadResource = async (language: string) =>
	assembleSettingsTranslations(
		await withGnos3Strings(language),
		await loadBundledResource('en-US'),
		overrides[language],
		overrides['en-US']
	);

export const updateI18n = async (value: I18nOverrides = {}) => {
	overrides = value;
	const resources = await Promise.all(
		Object.keys(i18next.store?.data ?? {}).map(async (language) => ({
			language,
			resource: await loadResource(language)
		}))
	);
	for (const { language, resource } of resources) {
		i18next.removeResourceBundle(language, 'translation');
		i18next.addResourceBundle(language, 'translation', resource);
	}
	i18n.set(i18next);
};

const createI18nStore = (i18n: i18nType) => {
	const i18nWritable = writable(i18n);

	i18n.on('initialized', () => {
		i18nWritable.set(i18n);
	});
	i18n.on('loaded', () => {
		i18nWritable.set(i18n);
	});
	i18n.on('added', () => i18nWritable.set(i18n));
	i18n.on('languageChanged', (lang) => {
		dayjs.locale(getDayjsLocale(lang));
		i18nWritable.set(i18n);
		if (typeof document !== 'undefined') {
			document.documentElement.setAttribute('lang', lang);
		}
	});
	return i18nWritable;
};

const createIsLoadingStore = (i18n: i18nType) => {
	const isLoading = writable(false);

	// if loaded resources are empty || {}, set loading to true
	i18n.on('loaded', (resources) => {
		// console.log('loaded:', resources);
		isLoading.set(Object.keys(resources).length === 0);
	});

	// if resources failed loading, set loading to true
	i18n.on('failedLoading', () => {
		isLoading.set(true);
	});

	return isLoading;
};

const languageCodes = languages.map(({ code }) => code);

const toBundleCode = (code: string) => {
	const ownBundle = languageCodes.find((bundle) => bundle.toLowerCase() === code.toLowerCase());
	if (ownBundle) return ownBundle;
	const baseLanguage = code.split('-')[0].toLowerCase();
	const primaryBundle = `${baseLanguage}-${baseLanguage.toUpperCase()}`;
	if (languageCodes.includes(primaryBundle)) return primaryBundle;
	// the first sibling of a regional code can be another script (zh-HK would get zh-CN)
	if (code.includes('-')) return code;
	return languageCodes.find((bundle) => bundle.startsWith(`${baseLanguage}-`)) ?? code;
};

// Gnos3: every string a screen shows through t() says Gnos3, in any language, including keys with
// no translation. One hook here instead of edits to hundreds of upstream strings and catalogs,
// each of which would conflict at the next upgrade.
const gnos3Brand = {
	type: 'postProcessor' as const,
	name: 'gnos3Brand',
	process: (value: string) =>
		typeof value === 'string' ? value.replace(/Open ?WebUI/g, 'Gnos3') : value
};

export const initI18n = (defaultLocale?: string, value: I18nOverrides = {}) => {
	overrides = value;
	const detector = new LanguageDetector();
	detector.addDetector({ name: 'defaultLocale', lookup: () => defaultLocale });

	return i18next
		.use(resourcesToBackend(loadResource))
		.use(detector)
		.use(gnos3Brand)
		.init({
			debug: false,
			postProcess: ['gnos3Brand'],
			detection: {
				order: ['querystring', 'localStorage', 'defaultLocale', 'navigator'],
				caches: ['localStorage'],
				lookupQuerystring: 'lang',
				lookupLocalStorage: 'locale',
				convertDetectedLanguage: toBundleCode
			},
			// Untranslated strings show in English, never in the language the page was
			// loaded in: en-US's values are empty (the keys are the English text), so a
			// fallback to the starting language kept a French screen French after
			// switching to English in Settings, until a reload.
			fallbackLng: {
				fr: ['fr-FR'],
				default: ['en-US']
			},
			ns: 'translation',
			keySeparator: false,
			nsSeparator: false,
			returnEmptyString: false,
			interpolation: {
				escapeValue: false // not needed for svelte as it escapes by default
			}
		});
};

const i18n = createI18nStore(i18next);
const isLoadingStore = createIsLoadingStore(i18next);

export const getLanguages = async () => languages;
// Serialize switches so a slower download cannot overwrite a newer selection.
let languageChange = Promise.resolve();
export const changeLanguage = (lang: string) => {
	const change = languageChange.then(() => i18next.changeLanguage(toBundleCode(lang)));
	languageChange = change.then(
		() => {},
		() => {}
	);
	return change;
};

export default i18n;
export const isLoading = isLoadingStore;
