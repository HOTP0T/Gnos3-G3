#!/usr/bin/env node
// Keeps src/lib/i18n/locales/<locale>/gnos3.json in step with the code.
//
// Gnos3's own strings (accounting, invoices, business cards, Office, the
// design-system primitives…) live in gnos3.json, next to Open WebUI's
// translation.json, so upstream merges never touch them. The i18n loader
// merges both files (gnos3.json wins when it has a value).
//
// A key belongs in gnos3.json when it is used in the code and either
//   - Open WebUI does not have it (not in en-US/translation.json), or
//   - it is used by a Gnos3 screen and the locale's translation.json has no
//     translation for it.
// Besides literal t('…') calls the scan picks up label-like strings in Gnos3
// screens (`label: '…'`, `*_LABELS = { … }`) and the backend strings the UI
// passes through t() (role labels, closing checks, statement lines…).
// Keys are never removed automatically: a backend string can be in use without
// appearing in the frontend. `--unused` lists the candidates.
//
//   node scripts/i18n-gnos3.mjs            add new keys (empty) to every locale
//   node scripts/i18n-gnos3.mjs --check    exit 1 when a locale has untranslated keys
//   node scripts/i18n-gnos3.mjs --missing fr-FR   print fr-FR's untranslated keys as JSON
//   node scripts/i18n-gnos3.mjs --unused   keys in gnos3.json the scan no longer finds
//   node scripts/i18n-gnos3.mjs --prune    remove them (check --unused first: a key only
//                                          built at runtime looks unused too)

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LOCALES_DIR = path.join(ROOT, 'src/lib/i18n/locales');
export const LOCALES = ['fr-FR', 'es-ES', 'pt-PT', 'pt-BR', 'zh-CN', 'zh-TW'];

// Gnos3 screens: every key they use must read in the user's language.
const GNOS3_DIRS = [
	'src/lib/components/accounting',
	'src/lib/components/invoices',
	'src/lib/components/business-cards',
	'src/lib/components/data-nav',
	'src/lib/components/gnos3-ui',
	'src/lib/components/ui',
	'src/lib/components/office',
	'src/lib/components/finances',
	'src/lib/components/anonymiser',
	'src/routes/(app)/accounting',
	'src/routes/(app)/invoices',
	'src/routes/(app)/business-cards',
	'src/routes/(app)/office',
	'src/routes/(app)/finances',
	'src/routes/(app)/anonymiser'
];
const GNOS3_FILES = [
	'src/lib/utils/taxTerms.ts',
	'src/lib/components/common/K4miDocLink.svelte',
	'src/lib/components/workspace/DataSources.svelte',
	'src/routes/(app)/workspace/datasources/+page.svelte',
	'src/routes/(app)/admin/permissions/companies/+page.svelte',
	'src/lib/components/admin/Users/Groups/Permissions.svelte'
];
// Backend modules whose label strings reach the UI through t().
const BACKEND_DIRS = ['../invoice-processor/app', '../business-card-processor/app'];
// Gnos3 backend routes we added: their fixed error details are shown through t().
const GNOS3_BACKEND_FILES = [
	'backend/open_webui/routers/office_knowledge.py',
	'backend/open_webui/routers/data_connectors.py'
];
const PY_DETAIL_RE =
	/HTTPException\(\s*(?:status\.\w+|\d+)\s*,\s*(?:detail=)?(['"])((?:(?!\1)[^{}\\])+)\1|detail=(['"])((?:(?!\3)[^{}\\])+)\3/g;

const walk = (dir, exts) => {
	if (!fs.existsSync(dir)) return [];
	return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
		const p = path.join(dir, e.name);
		if (e.isDirectory()) return e.name === 'node_modules' ? [] : walk(p, exts);
		return exts.includes(path.extname(e.name)) ? [p] : [];
	});
};

// Read a JS string literal starting at s[i] (a quote). Returns [value, end] or null.
const readString = (s, i) => {
	const q = s[i];
	let out = '';
	for (let j = i + 1; j < s.length; j++) {
		const c = s[j];
		if (c === '\\') {
			const n = s[j + 1];
			out += n === 'n' ? '\n' : n === 't' ? '\t' : n;
			j++;
		} else if (q === '`' && c === '$' && s[j + 1] === '{') {
			return [null, j]; // template with interpolation: not a static key
		} else if (c === q) {
			return [out, j + 1];
		} else {
			out += c;
		}
	}
	return null;
};

// String literals in the first argument of a call whose "(" is at s[i]:
// t('A'), t(cond ? 'A' : 'B'), t(x ?? 'A'). Also returns where the call ends.
const firstArgStrings = (s, i) => {
	const found = [];
	let depth = 0;
	let inFirst = true;
	let j = i;
	for (; j < s.length; j++) {
		const c = s[j];
		if (c === "'" || c === '"' || c === '`') {
			const r = readString(s, j);
			if (!r) break;
			if (r[0] !== null && depth === 1 && inFirst) found.push(r[0]);
			j = r[1] - 1;
			if (r[0] === null) {
				// skip the rest of an interpolated template
				const close = s.indexOf('`', r[1] + 1);
				if (close < 0) break;
				j = close;
			}
		} else if (c === '(' || c === '[' || c === '{') depth++;
		else if (c === ')' || c === ']' || c === '}') {
			depth--;
			if (depth === 0) break;
		} else if (c === ',' && depth === 1) inFirst = false;
	}
	return { found, end: j };
};

// Words whose Open WebUI translation means something else on Gnos3 screens
// (Account = a login there, a ledger account here) are called with
// `{ context: 'gnos3' }`; i18next looks up `Account_gnos3` first. Dynamic calls
// (t(col.label, { context: 'gnos3' })) can't be traced: their variants are listed here.
const DYNAMIC_CONTEXT_KEYS = [
	'Pending_gnos3',
	'pending_gnos3',
	'Name_gnos3',
	'Notes_gnos3',
	'Tax_tab',
	'Expenses_tab'
];
const CONTEXT_RE = /context:\s*(['"])(\w+)\1/;

const CALL_RE = /(?:\$i18n\.t|i18n\.t|\bT|\btr)\s*\(/g;
const LABEL_RE =
	/\b(label|title|description|hint|confirm|tooltip|placeholder|heading|subtitle|message|empty|emptyText|action|cta|short)\s*:\s*(['"])((?:\\.|(?!\2).)+?)\2/g;
const MAP_RE =
	/\b[A-Z][A-Z0-9_]*(?:LABELS?|TITLES?|NAMES?|TERMS|COPY)\b[^=\n]*=\s*\{([\s\S]*?)\n\s*\}/g;
const MAP_VALUE_RE = /:\s*(['"])((?:\\.|(?!\1).)+?)\1/g;

const unescape = (v) => v.replace(/\\(['"\\])/g, '$1');

const scanFrontend = (file, withLabels) => {
	const s = fs.readFileSync(file, 'utf8');
	const keys = new Set();
	for (const m of s.matchAll(CALL_RE)) {
		const open = m.index + m[0].length - 1;
		const { found, end } = firstArgStrings(s, open);
		const ctx = s.slice(open, end).match(CONTEXT_RE)?.[2];
		for (const k of found) keys.add(ctx ? `${k}_${ctx}` : k);
	}
	if (withLabels) {
		for (const m of s.matchAll(LABEL_RE)) keys.add(unescape(m[3]));
		for (const m of s.matchAll(MAP_RE))
			for (const v of m[1].matchAll(MAP_VALUE_RE)) keys.add(unescape(v[2]));
	}
	return keys;
};

// Backend: label-like literals only (role labels, check titles, statement lines).
const PY_LABEL_RE =
	/\b(label|label_en|title|gap|action_label|hint|name_en)\s*[=:]\s*(['"])((?:\\.|(?!\2).)+?)\2|["'](label|label_en|title|gap|action_label|hint)["']\s*:\s*(['"])((?:\\.|(?!\5).)+?)\5/g;
const PY_CTOR_RE =
	/\b(TaxRole|CheckResult|Line|StatementLine)\(\s*(['"])[^'"]*\2\s*,\s*(['"])((?:\\.|(?!\3).)+?)\3/g;
// Static warnings / blockers / line notes (f-strings with values can't be keys).
const PY_MESSAGE_RE =
	/\b(?:warnings|blockers|issues)\.append\(\s*(f?)"((?:[^"\\{}]|\\.)+)"\s*\)|\.note = (f?)"((?:[^"\\{}]|\\.)+)"/g;
// Statement lines: Line("key", line_no, "中文", "English", …) — the screen shows t(English).
const PY_STATEMENT_LINE_RE = /\bLine\(\s*"[^"]+",\s*(?:None|\d+|"[^"]*"),\s*"[^"]*",\s*"([^"]+)"/g;
const scanBackend = (file) => {
	const s = fs.readFileSync(file, 'utf8');
	const keys = new Set();
	for (const m of s.matchAll(PY_LABEL_RE)) {
		const v = m[3] ?? m[6];
		if (v && /[A-Za-z]/.test(v) && !/[{}]/.test(v)) keys.add(unescape(v));
	}
	for (const m of s.matchAll(PY_CTOR_RE)) if (!/[{}]/.test(m[4])) keys.add(unescape(m[4]));
	for (const m of s.matchAll(PY_STATEMENT_LINE_RE)) keys.add(unescape(m[1]));
	for (const m of s.matchAll(PY_MESSAGE_RE)) {
		const [isF, text] = m[2] !== undefined ? [m[1], m[2]] : [m[3], m[4]];
		if (!isF && text) keys.add(unescape(text));
	}
	return keys;
};

const readJson = (p) => (fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : {});
const sortObj = (o) =>
	Object.fromEntries(
		Object.keys(o)
			.sort((a, b) => a.localeCompare(b, 'en'))
			.map((k) => [k, o[k]])
	);

const inGnos3 = (rel) =>
	GNOS3_FILES.includes(rel) || GNOS3_DIRS.some((d) => rel === d || rel.startsWith(d + '/'));

export const collectKeys = () => {
	const upstream = readJson(path.join(LOCALES_DIR, 'en-US/translation.json'));
	const all = new Set(); // every key used anywhere in src
	const screens = new Set(); // keys used by Gnos3 screens
	for (const f of walk(path.join(ROOT, 'src'), ['.svelte', '.ts', '.js'])) {
		const rel = path.relative(ROOT, f).split(path.sep).join('/');
		if (rel.includes('/i18n/locales/')) continue;
		const own = inGnos3(rel);
		for (const k of scanFrontend(f, own)) {
			all.add(k);
			if (own) screens.add(k);
		}
	}
	for (const d of BACKEND_DIRS)
		for (const f of walk(path.resolve(ROOT, d), ['.py']))
			for (const k of scanBackend(f)) screens.add(k);
	for (const f of GNOS3_BACKEND_FILES) {
		const p = path.join(ROOT, f);
		if (!fs.existsSync(p)) continue;
		for (const m of fs.readFileSync(p, 'utf8').matchAll(PY_DETAIL_RE)) screens.add(m[2] ?? m[4]);
	}
	const clean = (k) => k.trim() !== '' && /\p{L}/u.test(k) && k.length < 600;
	for (const k of DYNAMIC_CONTEXT_KEYS) all.add(k);
	const ours = new Set([...all].filter((k) => !(k in upstream) && clean(k)));
	const used = new Set([...screens].filter(clean));
	return { upstream, ours, used };
};

const main = () => {
	const args = process.argv.slice(2);
	const { ours, used } = collectKeys();
	const report = [];
	let missingTotal = 0;

	if (args[0] === '--unused' || args[0] === '--prune') {
		const known = new Set([...ours, ...used]);
		for (const l of LOCALES) {
			const file = path.join(LOCALES_DIR, l, 'gnos3.json');
			const own = readJson(file);
			const gone = Object.keys(own).filter((k) => !known.has(k) && !k.includes('_'));
			console.log(`${l}: ${gone.length} keys not found by the scan`);
			if (args[0] === '--prune') {
				for (const k of gone) delete own[k];
				fs.writeFileSync(file, JSON.stringify(sortObj(own), null, '\t') + '\n');
			} else for (const k of gone) console.log(`  ${JSON.stringify(k)}`);
		}
		return;
	}

	for (const l of LOCALES) {
		const file = path.join(LOCALES_DIR, l, 'gnos3.json');
		const own = readJson(file);
		const theirs = readJson(path.join(LOCALES_DIR, l, 'translation.json'));
		const want = new Set(ours);
		for (const k of used) if (!theirs[k]) want.add(k);
		let added = 0;
		for (const k of want)
			if (!(k in own)) {
				own[k] = '';
				added++;
			}
		const missing = Object.keys(own).filter((k) => !own[k]);
		missingTotal += missing.length;
		report.push(
			`${l}: ${Object.keys(own).length} keys, ${missing.length} untranslated, ${added} new`
		);
		if (args[0] === '--missing' && args[1] === l) {
			console.log(JSON.stringify(missing, null, '\t'));
			return;
		}
		if (args[0] !== '--check' && args[0] !== '--missing')
			fs.writeFileSync(file, JSON.stringify(sortObj(own), null, '\t') + '\n');
	}
	console.error(report.join('\n'));
	if (args[0] === '--check' && missingTotal > 0) process.exit(1);
};

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
