// The chat's suggested prompts are stored in English: the defaults in the backend's
// config.py (DEFAULT_PROMPT_SUGGESTIONS), saved once into the box's settings. They are shown,
// searched and sent in the reader's UI language: each title line and prompt is looked up as a
// translation key (gnos3.json). A suggestion an admin wrote (Settings → Models, or a model's
// own suggestions) has no translation and is shown as written.

import type { i18n as I18n } from 'i18next';

// Read by scripts/i18n-gnos3.mjs so the defaults get translated; keep it in step with
// DEFAULT_PROMPT_SUGGESTIONS in backend/open_webui/config.py.
export const DEFAULT_SUGGESTION_COPY = {
	studyTitle: 'Help me study',
	studySubtitle: 'vocabulary for a college entrance exam',
	studyPrompt:
		"Help me study vocabulary: write a sentence for me to fill in the blank, and I'll try to pick the correct option.",
	ideasTitle: 'Give me ideas',
	ideasSubtitle: "for what to do with my kids' art",
	ideasPrompt:
		"What are 5 creative things I could do with my kids' art? I don't want to throw them away, but it's also so much clutter.",
	factTitle: 'Tell me a fun fact',
	factSubtitle: 'about the Roman Empire',
	factPrompt: 'Tell me a random fun fact about the Roman Empire',
	codeTitle: 'Show me a code snippet',
	codeSubtitle: "of a website's sticky header",
	codePrompt: "Show me a code snippet of a website's sticky header in CSS and JavaScript.",
	optionsTitle: 'Explain options trading',
	optionsSubtitle: "if I'm familiar with buying and selling stocks",
	optionsPrompt:
		"Explain options trading in simple terms if I'm familiar with buying and selling stocks.",
	procrastinationTitle: 'Overcome procrastination',
	procrastinationSubtitle: 'give me tips',
	procrastinationPrompt:
		'Could you start by asking me about instances when I procrastinate the most and then give me some suggestions to overcome it?'
};

type Suggestion = { title?: string[]; content: string; [key: string]: unknown };

// Only text with a translation goes through t(): an admin's own text could contain {{…}},
// which i18next would try to interpolate.
const translate = (i18n: I18n, text: string) => (text && i18n.exists(text) ? i18n.t(text) : text);

export const localizeSuggestion = <T extends Suggestion>(i18n: I18n, prompt: T): T => ({
	...prompt,
	title: prompt.title?.map((line) => translate(i18n, line)),
	content: translate(i18n, prompt.content)
});
