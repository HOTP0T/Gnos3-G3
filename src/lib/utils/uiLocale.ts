import i18next from 'i18next';

/** The Gnos3 UI language, for Intl / toLocale* calls: month and weekday names
 *  follow the language the user picked, not the browser's. */
export const uiLocale = (): string | undefined => i18next.language || undefined;

/** Header for module API calls: the backend writes its messages (errors,
 *  warnings, check details) in this language — see invoice-processor
 *  app/services/ui_text.py. */
export const langHeader = (): Record<string, string> => ({
	'X-Gnos3-Lang': i18next.language || 'en-US'
});
