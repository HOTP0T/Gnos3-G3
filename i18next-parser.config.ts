// i18next-parser.config.ts
import languages from './src/lib/i18n/locales/languages.json';

export default {
	contextSeparator: '_',
	createOldCatalogs: false,
	defaultNamespace: 'translation',
	defaultValue: '',
	indentation: 2,
	keepRemoved: false,
	keySeparator: false,
	lexers: {
		svelte: ['JavascriptLexer'],
		js: ['JavascriptLexer'],
		ts: ['JavascriptLexer'],

		default: ['JavascriptLexer']
	},
	lineEnding: 'auto',
	locales: languages.map(({ code }) => code),
	namespaceSeparator: false,
	output: 'src/lib/i18n/locales/$LOCALE/$NAMESPACE.json',
	pluralSeparator: '_',
	// Gnos3's own screens keep their strings in gnos3.json (npm run i18n:gnos3).
	input: [
		'src/**/*.{js,ts,svelte}',
		'!src/lib/components/{accounting,invoices,business-cards,data-nav,gnos3-ui,ui,office,finances,anonymiser,notes-vault}/**',
		'!src/routes/(app)/{accounting,invoices,business-cards,office,finances,anonymiser}/**'
	],
	sort: true,
	verbose: true,
	failOnWarnings: false,
	failOnUpdate: false,
	customValueTemplate: null,
	resetDefaultValueLocale: null,
	i18nextOptions: null,
	yamlOptions: null
};
