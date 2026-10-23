// i18next-parser.config.ts
import { getLanguages } from './src/lib/i18n/index.ts';

const getLangCodes = async () => {
	const languages = await getLanguages();
	return languages.map((l) => l.code);
};

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
	locales: await getLangCodes(),
	namespaceSeparator: false,
	output: 'src/lib/i18n/locales/$LOCALE/$NAMESPACE.json',
	pluralSeparator: '_',
	// Gnos3's own screens keep their strings in gnos3.json (npm run i18n:gnos3).
	input: [
		'src/**/*.{js,svelte}',
		'!src/lib/components/{accounting,invoices,business-cards,data-nav,gnos3-ui,ui,office,finances}/**',
		'!src/routes/(app)/{accounting,invoices,business-cards,office,finances}/**'
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
