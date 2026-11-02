import i18next from 'i18next';
import resourcesToBackend from 'i18next-resources-to-backend';
import LanguageDetector from 'i18next-browser-languagedetector';
import type { i18n as i18nType } from 'i18next';
import { writable } from 'svelte/store';

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

export const initI18n = (defaultLocale?: string | undefined) => {
	const detectionOrder = defaultLocale
		? ['querystring', 'localStorage']
		: ['querystring', 'localStorage', 'navigator'];

	// Gnos3's own strings (modules, accounting, design-system primitives) live in
	// gnos3.json next to Open WebUI's translation.json, so upstream merges never
	// touch them. Merged over upstream; an empty value keeps upstream's.
	// Keep in step with the code: `node scripts/i18n-gnos3.mjs`. (The glob sits
	// here, not at module level: i18next-parser imports this file under Node.)
	const gnos3Locales = import.meta.glob('./locales/*/gnos3.json');
	const loadResource = async (language: string, namespace: string) => {
		// A language Open WebUI ships no file for (uz-Latn-UZ), or a bare language code
		// i18next also tries (fr for fr-CA), loads as empty instead of failing the load.
		const upstream = await import(`./locales/${language}/${namespace}.json`)
			.then((m) => m.default)
			.catch(() => ({}));
		const own = gnos3Locales[`./locales/${language}/gnos3.json`];
		if (namespace !== 'translation' || !own) return upstream;
		const ours = ((await own()) as { default: Record<string, string> }).default;
		return {
			...upstream,
			...Object.fromEntries(Object.entries(ours).filter(([, value]) => value))
		};
	};

	i18next
		.use(resourcesToBackend(loadResource))
		.use(LanguageDetector)
		.init({
			debug: false,
			detection: {
				order: detectionOrder,
				caches: ['localStorage'],
				lookupQuerystring: 'lang',
				lookupLocalStorage: 'locale'
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
			returnEmptyString: false,
			interpolation: {
				escapeValue: false // not needed for svelte as it escapes by default
			}
		});
};

const i18n = createI18nStore(i18next);
const isLoadingStore = createIsLoadingStore(i18next);

export const getLanguages = async () => {
	const languages = (await import(`./locales/languages.json`)).default;
	return languages;
};
export const changeLanguage = (lang: string) => {
	document.documentElement.setAttribute('lang', lang);
	i18next.changeLanguage(lang);
};

export default i18n;
export const isLoading = isLoadingStore;
