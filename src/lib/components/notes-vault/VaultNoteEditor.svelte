<!--
	One note in the vault: title, properties, body (live co-editing, [[links]], @ Gnos3 data, #tags,
	/ commands) and the side panel (links, outline, local graph, AI chat).

	The body is saved by the co-editing socket (upstream). Title, properties and attached files go
	through POST /note-vaults/notes/{id}/meta — never upstream's /notes/{id}/update, which deletes a
	note's sharing when it is called without access_grants.
-->
<script lang="ts">
	import { getContext, onDestroy, onMount, tick, untrack } from 'svelte';
	import { get } from 'svelte/store';
	import { toast } from 'svelte-sonner';
	import { v4 as uuidv4 } from 'uuid';
	import fileSaver from 'file-saver';
	import YAML from 'yaml';
	import { goto } from '$app/navigation';

	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Undo2 from '@lucide/svelte/icons/undo-2';
	import Redo2 from '@lucide/svelte/icons/redo-2';
	import Sparkles from '@lucide/svelte/icons/sparkles';
	import Ellipsis from '@lucide/svelte/icons/ellipsis';
	import PanelRight from '@lucide/svelte/icons/panel-right';
	import Users from '@lucide/svelte/icons/users';
	import Lock from '@lucide/svelte/icons/lock';
	import Link2 from '@lucide/svelte/icons/link-2';
	import ListTree from '@lucide/svelte/icons/list-tree';
	import Orbit from '@lucide/svelte/icons/orbit';
	import Bot from '@lucide/svelte/icons/bot';
	import Mic from '@lucide/svelte/icons/mic';
	import Upload from '@lucide/svelte/icons/upload';
	import WandSparkles from '@lucide/svelte/icons/wand-sparkles';
	import Type from '@lucide/svelte/icons/type';
	import Pin from '@lucide/svelte/icons/pin';
	import PinOff from '@lucide/svelte/icons/pin-off';
	import Copy from '@lucide/svelte/icons/copy';
	import Download from '@lucide/svelte/icons/download';
	import FolderInput from '@lucide/svelte/icons/folder-input';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Paperclip from '@lucide/svelte/icons/paperclip';
	import X from '@lucide/svelte/icons/x';
	import Plus from '@lucide/svelte/icons/plus';
	import FileText from '@lucide/svelte/icons/file-text';
	import MoveHorizontal from '@lucide/svelte/icons/move-horizontal';
	import Loader from '@lucide/svelte/icons/loader-circle';

	import { Button } from '$lib/components/ui/button/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import ConfirmDialog from '$lib/components/gnos3-ui/ConfirmDialog.svelte';

	import RichTextInput from '$lib/components/common/RichTextInput.svelte';
	import AccessControlModal from '$lib/components/workspace/common/AccessControlModal.svelte';
	import VoiceRecording from '$lib/components/chat/MessageInput/VoiceRecording.svelte';
	import Chat from '$lib/components/notes/NoteEditor/Chat.svelte';
	import { downloadPdf } from '$lib/components/notes/utils';

	import {
		config,
		isAdmin,
		mobile,
		models,
		pinnedNotes,
		settings,
		socket,
		user
	} from '$lib/stores';
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { compressImage, convertHeicToJpeg, copyToClipboard, splitStream } from '$lib/utils';
	import { getFileById, uploadFile } from '$lib/apis/files';
	import { chatCompletion, generateOpenAIChatCompletion } from '$lib/apis/openai';
	import {
		deleteNoteById,
		getNoteById,
		getPinnedNoteList,
		toggleNotePinnedStatusById,
		updateNoteAccessGrants
	} from '$lib/apis/notes';
	import {
		createVaultNote,
		getNotePlace,
		suggestNoteLinks,
		updateNoteMeta,
		type LinkSuggestion,
		type NotePlace
	} from '$lib/apis/note-vaults';

	import {
		allTags,
		chartColor,
		cleanTitle,
		currentVault,
		linksVersion,
		normalizeTitle,
		notesById,
		notesByTitle,
		patchTreeNote,
		prefs,
		refreshTree,
		tree,
		typeName,
		typeOf,
		vaultName
	} from './vault';
	import TypeIcon from './TypeIcon.svelte';
	import {
		applyTemplate,
		markdownToEditorHtml,
		resolverFor,
		splitWikilink,
		stripFrontmatter
	} from './markdown';
	import { ENTITY_META, searchEntities } from './entities';
	import { WikiLink } from './editor/WikiLink';
	import { EntityRef } from './editor/EntityRef';
	import { Tags } from './editor/Tags';
	import { SlashCommands } from './editor/SlashCommands';
	import { MermaidBlocks } from './editor/MermaidBlocks.svelte';
	import { FencedPaste } from './editor/FencedPaste';
	import { htmlWithDiagrams } from './editor/mermaidDraw';
	import type { SuggestItem } from './editor/suggestionPopup.svelte';
	import PropertiesBlock from './editor/PropertiesBlock.svelte';
	import LinksPanel from './panels/LinksPanel.svelte';
	import OutlinePanel from './panels/OutlinePanel.svelte';
	import GraphView from './graph/GraphView.svelte';
	import MoveNoteDialog from './dialogs/MoveNoteDialog.svelte';

	import dayjs from '$lib/dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	import localizedFormat from 'dayjs/plugin/localizedFormat';
	dayjs.extend(relativeTime);
	dayjs.extend(localizedFormat);

	const { saveAs } = fileSaver;
	const i18n: any = getContext('i18n');

	let {
		noteId,
		onOpenNote,
		onCreateNote,
		onTag,
		onDeleted
	}: {
		noteId: string;
		onOpenNote: (id: string) => void;
		onCreateNote: (
			title: string,
			opts?: { folder?: string; type?: string | null; open?: boolean }
		) => Promise<{ id: string; title: string } | null>;
		onTag: (tag: string) => void;
		onDeleted: (id: string) => void;
	} = $props();

	// --- state -----------------------------------------------------------------

	let note: any = $state(null);
	let place = $state<NotePlace | null>(null);
	let loading = $state(true);
	let editor: any = $state(null);
	let inputElement: any = $state(null);
	// What the editor starts from. Never leave it null with `html` set: RichTextInput would then put
	// the html into the shared document in every browser that opens the note, doubling the note and
	// saving it doubled. As a value, only the first person in an empty session seeds it.
	let editorValue: any = $state('');
	let files: any[] = $state([]);
	let title = $state('');
	let wordCount = $state(0);

	let panelOpen = $state(get(mobile) ? false : prefs.get('panel.open', true));
	let panelTab: 'links' | 'outline' | 'graph' | 'ai' = $state(prefs.get('panel.tab', 'links'));
	let panelWidth = $state(prefs.get('panel.width', 340));
	let fullWidth = $state(prefs.get('editor.fullWidth', false));

	let showAccess = $state(false);
	let showDelete = $state(false);
	let showMove = $state(false);
	let showSuggestions = $state(false);
	let suggestions = $state<LinkSuggestion[]>([]);
	let suggesting = $state(false);

	let recording = $state(false);
	let displayMediaRecord = $state(false);

	// Upstream's AI chat panel
	let messages: any[] = $state([]);
	let selectedModelId = $state('');
	let selectedContent: any = $state(null);
	let editing = $state(false);
	let streaming = $state(false);
	let stopResponseFlag = $state(false);
	let titleGenerating = $state(false);

	const editable = $derived(!!note?.write_access && !editing);
	const vaultTitle = $derived(
		place ? vaultName({ kind: place.vault_kind, name: place.vault_name }, $i18n) : ''
	);
	const folderParts = $derived((place?.folder ?? '').split('/').filter(Boolean));
	const isShared = $derived(place?.vault_kind === 'shared');
	const ownsNote = $derived(note?.user_id === $user?.id || $isAdmin);
	const type = $derived(typeOf($currentVault, note?.data?.properties?.type));
	const otherFiles = $derived(
		files.filter((f) => f?.type !== 'image' && !(f?.content_type ?? '').startsWith('image/'))
	);

	// --- loading -------------------------------------------------------------------

	const noteEventHandler = async (incoming: any) => {
		if (!note || incoming?.id !== note.id) return;
		if (incoming.title && incoming.title !== note.title) {
			note.title = incoming.title;
			if (document.activeElement?.id !== 'note-title-input') title = incoming.title;
		}
		if (incoming.data?.properties !== undefined) {
			note.data.properties = incoming.data.properties ?? {};
		}
		if (incoming.data && 'files' in incoming.data) {
			files = incoming.data.files ?? [];
			note.data.files = files;
			if (editor) editor.storage.files = files;
		}
		if (incoming.access_grants) note.access_grants = incoming.access_grants;
	};

	const load = async (id: string) => {
		loading = true;
		note = null;
		place = null;
		messages = [];
		const [res, where] = await Promise.all([
			getNoteById(localStorage.token, id).catch((e) => {
				toast.error(`${e}`);
				return null;
			}),
			getNotePlace(localStorage.token, id).catch(() => null)
		]);
		if (id !== noteId) return;
		if (!res) {
			loading = false;
			return;
		}
		res.data = res.data ?? {};
		res.data.content = res.data.content ?? { json: null, html: '', md: '' };
		res.data.properties = res.data.properties ?? {};
		if (!Array.isArray(res.access_grants)) res.access_grants = [];
		const content = res.data.content;
		editorValue =
			content.json ||
			content.html ||
			(content.md ? markdownToEditorHtml(content.md, resolverFor(get(notesByTitle))) : '');
		files = res.data.files ?? [];
		title = res.title ?? '';
		note = res;
		place = where;
		loading = false;

		if (res.write_access) {
			$socket?.emit('join-note', { note_id: id, auth: { token: localStorage.token } });
		}
	};

	$effect(() => {
		const id = noteId;
		untrack(() => load(id));
	});

	onMount(() => {
		$socket?.on('note-events', noteEventHandler);
		const visible = $models.filter((m: any) => !(m?.info?.meta?.hidden ?? false));
		const wanted = $settings?.models?.[0] ?? ($config?.default_models ?? '').split(',')[0] ?? '';
		selectedModelId = visible.some((m: any) => m.id === wanted) ? wanted : (visible[0]?.id ?? '');
	});

	onDestroy(() => {
		$socket?.off('note-events', noteEventHandler);
		flushTitle();
	});

	// --- saving --------------------------------------------------------------------

	let titleTimer: ReturnType<typeof setTimeout> | null = null;
	let propsTimer: ReturnType<typeof setTimeout> | null = null;
	let contentTimer: ReturnType<typeof setTimeout> | null = null;

	const flushTitle = async () => {
		if (titleTimer) clearTimeout(titleTimer);
		titleTimer = null;
		if (!note || !note.write_access) return;
		const clean = cleanTitle(title) || $i18n.t('Untitled');
		if (clean === note.title) return;
		const id = note.id;
		try {
			const res = await updateNoteMeta(localStorage.token, id, { title: clean });
			if (note?.id === id) note.title = res.title;
			patchTreeNote(id, { title: res.title });
			linksVersion.update((n) => n + 1);
		} catch (e) {
			toast.error(`${e}`);
		}
	};

	const onTitleInput = () => {
		if (titleTimer) clearTimeout(titleTimer);
		titleTimer = setTimeout(flushTitle, 800);
	};

	const saveProperties = (props: Record<string, any>) => {
		if (!note) return;
		note.data.properties = props;
		if (propsTimer) clearTimeout(propsTimer);
		const id = note.id;
		propsTimer = setTimeout(async () => {
			try {
				await updateNoteMeta(localStorage.token, id, { properties: props });
				patchTreeNote(id, {
					type: props.type ?? null,
					aliases: Array.isArray(props.aliases) ? props.aliases : []
				});
				linksVersion.update((n) => n + 1);
				refreshTree(localStorage.token);
			} catch (e) {
				toast.error(`${e}`);
			}
		}, 500);
	};

	const saveFiles = async () => {
		if (!note) return;
		note.data.files = files.length ? files : null;
		if (editor) editor.storage.files = files;
		await updateNoteMeta(localStorage.token, note.id, { files: $state.snapshot(files) }).catch(
			(e) => toast.error(`${e}`)
		);
	};

	const onContentChange = (content: { html: string; md: string; json: any }) => {
		if (!note) return;
		note.data.content.html = content.html;
		note.data.content.md = content.md;
		if (editor) wordCount = editor.storage.characterCount.words();
		// Links and tags changed: refresh the tree and the panels once typing pauses.
		if (contentTimer) clearTimeout(contentTimer);
		contentTimer = setTimeout(() => refreshTree(localStorage.token), 2500);
	};

	// --- editor extensions -------------------------------------------------------------

	const T = (s: string, o?: any): string => (get(i18n) as any).t(s, o);
	const tr = { t: T, subscribe: (i18n as any).subscribe };

	const suggestNotes = (query: string): SuggestItem[] => {
		const parts = splitWikilink(query);
		const q = normalizeTitle(parts.title);
		const notes = (get(tree)?.notes ?? []).filter((n) => n.id !== noteId);
		const score = (n: any) => {
			const title = normalizeTitle(n.title);
			if (!q) return 3;
			if (title === q) return 0;
			if (title.startsWith(q)) return 1;
			if (title.includes(q) || (n.aliases ?? []).some((a: string) => normalizeTitle(a).includes(q)))
				return 2;
			return 9;
		};
		const hits: SuggestItem[] = notes
			.map((n) => ({ n, s: score(n) }))
			.filter((x) => x.s < 9)
			.sort((a, b) => a.s - b.s || b.n.updated_at - a.n.updated_at)
			.slice(0, 8)
			.map(({ n }) => {
				const nt = typeOf(get(currentVault), n.type);
				return {
					key: n.id,
					label: n.title || T('Untitled'),
					detail: n.folder || undefined,
					icon: FileText,
					color: nt ? chartColor(nt.color) : undefined,
					data: { id: n.id, title: n.title, parts }
				} as SuggestItem;
			});
		const exact = notes.some((n) => normalizeTitle(n.title) === q);
		if (parts.title.trim() && !exact && get(currentVault)?.permission !== 'read') {
			hits.push({
				key: '__create',
				label: T('Create “{{title}}”', { title: cleanTitle(parts.title) }),
				icon: Plus,
				create: true,
				data: { title: cleanTitle(parts.title), parts }
			} as SuggestItem);
		}
		return hits;
	};

	const suggestEntities = async (query: string): Promise<SuggestItem[]> => {
		const hits = await searchEntities(localStorage.token, query);
		return hits.slice(0, 15).map((h) => ({
			key: `${h.entity_type}:${h.entity_id}`,
			label: h.label,
			detail: h.detail,
			group: T(ENTITY_META[h.entity_type].label),
			icon: ENTITY_META[h.entity_type].icon,
			data: h
		}));
	};

	const suggestTags = (query: string): SuggestItem[] => {
		const q = query.toLocaleLowerCase();
		const list = get(allTags)
			.filter((x) => x.tag.toLocaleLowerCase().includes(q))
			.slice(0, 8);
		const items: SuggestItem[] = list.map((x) => ({
			key: x.tag,
			label: `#${x.tag}`,
			hint: String(x.count),
			data: { tag: x.tag }
		}));
		if (query && !list.some((x) => x.tag.toLocaleLowerCase() === q)) {
			items.push({ key: '__new', label: `#${query}`, hint: T('New tag'), data: { tag: query } });
		}
		return items;
	};

	const templates = () => {
		const folder = get(currentVault)?.settings?.templates_folder ?? 'Templates';
		return (get(tree)?.notes ?? [])
			.filter((n) => folder && (n.folder === folder || n.folder.startsWith(folder + '/')))
			.map((n) => ({ id: n.id, title: n.title }));
	};

	const insertTemplate = async (ed: any, templateId: string) => {
		const tpl = await getNoteById(localStorage.token, templateId).catch(() => null);
		if (!tpl) return;
		const md = applyTemplate(stripFrontmatter(tpl.data?.content?.md ?? ''), {
			title: note?.title ?? '',
			now: new Date(),
			dayjs
		});
		ed.chain()
			.focus()
			.insertContent(markdownToEditorHtml(md, resolverFor(get(notesByTitle))))
			.run();
		// The template's properties too, where this note has none.
		const tplProps = tpl.data?.properties ?? {};
		if (Object.keys(tplProps).length && note) {
			saveProperties({ ...tplProps, ...note.data.properties });
		}
	};

	const extensions = [
		WikiLink.configure({
			i18n: tr,
			notesById,
			lookupTitle: (title: string) => get(notesByTitle).get(normalizeTitle(title)),
			suggest: suggestNotes,
			createNote: (title: string) =>
				onCreateNote(title, { folder: place?.folder ?? '', open: false }),
			open: async (target, event) => {
				if (target.noteId) onOpenNote(target.noteId);
				else await onCreateNote(target.title, { folder: place?.folder ?? '', open: true });
			}
		}),
		EntityRef.configure({
			i18n: tr,
			search: suggestEntities,
			open: (href: string, outside: boolean) => (outside ? window.open(href, '_blank') : goto(href))
		}),
		Tags.configure({ i18n: tr, suggest: suggestTags, onTagClick: (tag: string) => onTag(tag) }),
		SlashCommands.configure({
			i18n: tr,
			templates,
			insertTemplate,
			today: () => dayjs().format(get(currentVault)?.settings?.daily?.format || 'YYYY-MM-DD')
		}),
		MermaidBlocks.configure({ i18n }),
		FencedPaste.configure({
			toHtml: (md: string) => markdownToEditorHtml(md, resolverFor(get(notesByTitle)))
		})
	];

	// --- files (ported from upstream's NoteEditor) ---------------------------------------

	const compressImageHandler = async (imageUrl: string) => {
		const s: any = $settings ?? {};
		const c: any = $config ?? {};
		const settingsCompression = s?.imageCompression ?? false;
		const configWidth = c?.file?.image_compression?.width ?? null;
		const configHeight = c?.file?.image_compression?.height ?? null;
		if (!settingsCompression && !configWidth && !configHeight) return imageUrl;
		let width = settingsCompression ? (s?.imageCompressionSize?.width ?? null) : null;
		let height = settingsCompression ? (s?.imageCompressionSize?.height ?? null) : null;
		if (configWidth && (width === null || width > configWidth)) width = configWidth;
		if (configHeight && (height === null || height > configHeight)) height = configHeight;
		return width || height ? await compressImage(imageUrl, width, height) : imageUrl;
	};

	const uploadFileHandler = async (file: File) => {
		if (file.size === 0) {
			toast.error($i18n.t('You cannot upload an empty file.'));
			return null;
		}
		const itemId = uuidv4();
		const item: any = {
			type: 'file',
			file: '',
			id: null,
			url: '',
			name: file.name,
			status: 'uploading',
			size: file.size,
			itemId
		};
		files = [...files, item];
		try {
			const metadata =
				(file.type.startsWith('audio/') || file.type.startsWith('video/')) &&
				$settings?.audio?.stt?.language
					? { language: $settings.audio.stt.language }
					: null;
			const uploaded = await uploadFile(localStorage.token, file, metadata);
			if (!uploaded) throw new Error($i18n.t('Upload failed'));
			if (uploaded.error) toast.warning(uploaded.error);
			const full = await getFileById(localStorage.token, uploaded.id).catch(() => null);
			files = files.map((f) =>
				f.itemId === itemId
					? {
							...f,
							status: 'uploaded',
							file: full,
							id: uploaded.id,
							url: `${uploaded.id}`,
							collection_name: uploaded?.meta?.collection_name
						}
					: f
			);
		} catch (e) {
			toast.error(`${e}`);
			files = files.filter((f) => f.itemId !== itemId);
		}
		await saveFiles();
		return files.find((f) => f.itemId === itemId) ?? null;
	};

	const inputFileHandler = async (file: File) => {
		const max = ($config as any)?.file?.max_size ?? null;
		if (max !== null && file.size > max * 1024 * 1024) {
			toast.error($i18n.t(`File size should not exceed {{maxSize}} MB.`, { maxSize: max }));
			return null;
		}
		if (file.type.startsWith('image/')) {
			const source = (file.type === 'image/heic' ? await convertHeicToJpeg(file) : file) as Blob;
			const url: string = await new Promise((resolve, reject) => {
				const reader = new FileReader();
				reader.onload = () => resolve(reader.result as string);
				reader.onerror = reject;
				reader.readAsDataURL(source);
			});
			const item = { id: uuidv4(), type: 'image', url: await compressImageHandler(url) };
			files = [...files, item];
			await saveFiles();
			return item;
		}
		return await uploadFileHandler(file);
	};

	const insertImage = (ed: any, pos: number, item: any) => {
		ed.chain()
			.insertContentAt(pos, { type: 'image', attrs: { src: `data://${item.id}` } })
			.focus()
			.run();
	};

	// --- AI --------------------------------------------------------------------------------

	const pickModel = () => {
		if (!selectedModelId) {
			toast.error($i18n.t('Please select a model.'));
			return null;
		}
		return selectedModelId;
	};

	const runSuggestions = async () => {
		const model = pickModel();
		if (!model || !note) return;
		showSuggestions = true;
		suggesting = true;
		suggestions = [];
		try {
			const res = await suggestNoteLinks(localStorage.token, note.id, model, $i18n.language);
			suggestions = res.suggestions;
			if (res.ai_error)
				toast.warning($i18n.t('The AI could not answer; showing the notes this one names.'));
		} catch (e) {
			toast.error(`${e}`);
		}
		suggesting = false;
	};

	/** Turn the suggested phrase into a link, or add the link at the end when there is no phrase. */
	const applySuggestion = (s: LinkSuggestion) => {
		if (!editor) return;
		const attrs = { noteId: s.id, title: s.title, alias: null as string | null, heading: null };
		let range: { from: number; to: number } | null = null;
		const needle = (s.phrase || '').toLocaleLowerCase();
		if (needle) {
			editor.state.doc.descendants((node: any, pos: number) => {
				if (range || !node.isText) return !range;
				const idx = node.text.toLocaleLowerCase().indexOf(needle);
				if (idx !== -1) range = { from: pos + idx, to: pos + idx + needle.length };
				return false;
			});
		}
		if (range) {
			const found = range as { from: number; to: number };
			const original = editor.state.doc.textBetween(found.from, found.to);
			if (normalizeTitle(original) !== normalizeTitle(s.title)) attrs.alias = original;
			editor.chain().focus().insertContentAt(found, { type: 'wikiLink', attrs }).run();
		} else {
			editor
				.chain()
				.focus('end')
				.insertContent([
					{
						type: 'paragraph',
						content: [
							{ type: 'text', text: `${$i18n.t('Related')}: ` },
							{ type: 'wikiLink', attrs }
						]
					}
				])
				.run();
		}
		suggestions = suggestions.filter((x) => x.id !== s.id);
	};

	const generateTitle = async () => {
		const model = pickModel();
		if (!model || !note) return;
		titleGenerating = true;
		const prompt = `### Task:
Generate a concise, 3-5 word title summarizing the content, in the content's primary language. No emoji, no quotation marks.
### Output:
JSON format: { "title": "your concise title here" }
### Content:
<content>
${(note.data.content.md ?? '').slice(0, 6000)}
</content>`;
		try {
			const res = await generateOpenAIChatCompletion(
				localStorage.token,
				{ model, stream: false, messages: [{ role: 'user', content: prompt }] },
				`${WEBUI_BASE_URL}/api`
			);
			const reply = res?.choices?.[0]?.message?.content ?? '';
			const json = reply.slice(reply.indexOf('{'), reply.lastIndexOf('}') + 1);
			const generated = JSON.parse(json)?.title;
			if (generated) {
				title = cleanTitle(generated);
				await flushTitle();
			}
		} catch {
			toast.error($i18n.t('Failed to generate title'));
		}
		titleGenerating = false;
	};

	const enhance = async () => {
		const model = pickModel();
		if (!model || !note) return;
		editing = true;
		stopResponseFlag = false;
		const systemPrompt = `Enhance existing notes using additional context provided from audio transcription or uploaded file content in the content's primary language. Make the notes more useful and comprehensive by incorporating relevant information from the provided context. Keep every [[link]] and every Markdown link exactly as written.

Input will be provided within <notes> and <context> XML tags.

# Output Format

Provide the enhanced notes in markdown format. Use markdown syntax for headings, lists, task lists ([ ]) where tasks or checklists are strongly implied, and emphasis to improve clarity and presentation. Return only the markdown formatted note.
`;
		const [res, controller] = await chatCompletion(
			localStorage.token,
			{
				model,
				stream: true,
				messages: [
					{ role: 'system', content: systemPrompt },
					{
						role: 'user',
						content:
							`<notes>${note.data.content.md}</notes>` +
							(otherFiles.length
								? `\n<context>${otherFiles.map((f) => `${f.name}: ${f?.file?.data?.content ?? ''}\n`).join('')}</context>`
								: '')
					}
				]
			},
			`${WEBUI_BASE_URL}/api`
		);
		streaming = true;
		let md = '';
		if (res && res.ok) {
			const reader = res
				.body!.pipeThrough(new TextDecoderStream())
				.pipeThrough(splitStream('\n'))
				.getReader();
			while (true) {
				const { value, done } = await reader.read();
				if (done || stopResponseFlag) {
					if (stopResponseFlag) controller.abort('User: Stop Response');
					break;
				}
				for (const line of value.split('\n')) {
					if (!line || line === 'data: [DONE]') continue;
					try {
						const data = JSON.parse(line.replace(/^data: /, ''));
						const delta = data?.choices?.[0]?.delta?.content;
						if (delta) md += delta;
					} catch {
						// partial line
					}
				}
			}
		}
		streaming = false;
		if (md.trim() && editor) {
			editor.commands.setContent(markdownToEditorHtml(md, resolverFor(get(notesByTitle))));
		}
		editing = false;
	};

	const onEdited = async () => {
		if (!editor || !note) return;
		editor.commands.setContent(
			note.data.content.html ||
				markdownToEditorHtml(note.data.content.md ?? '', resolverFor(get(notesByTitle)))
		);
	};

	// --- note actions ------------------------------------------------------------------

	const frontmatterFor = (props: Record<string, any>) => {
		const out: Record<string, any> = {};
		for (const [k, v] of Object.entries(props ?? {})) {
			if (v === null || v === undefined || v === '' || (Array.isArray(v) && !v.length)) continue;
			const conv = (x: any): any =>
				x && typeof x === 'object' && (x.id || x.title)
					? `[[${get(notesById).get(x.id)?.title ?? x.title}]]`
					: x && typeof x === 'object' && x.entity_type
						? (x.label ?? String(x.entity_id))
						: x;
			out[k] = Array.isArray(v) ? v.map(conv) : conv(v);
		}
		return Object.keys(out).length ? `---\n${YAML.stringify(out).trim()}\n---\n` : '';
	};

	const download = async (kind: 'md' | 'txt' | 'pdf') => {
		if (!note) return;
		const name = note.title || 'note';
		if (kind === 'md') {
			saveAs(
				new Blob([frontmatterFor(note.data.properties) + (note.data.content.md ?? '')], {
					type: 'text/markdown'
				}),
				`${name}.md`
			);
		} else if (kind === 'txt') {
			saveAs(new Blob([note.data.content.md ?? ''], { type: 'text/plain' }), `${name}.txt`);
		} else {
			const content = note.data.content;
			await htmlWithDiagrams(content.html ?? '')
				.then((html) =>
					downloadPdf({ ...note, data: { ...note.data, content: { ...content, html } } })
				)
				.catch((e: any) => toast.error(`${e}`));
		}
	};

	const togglePin = async () => {
		if (!note) return;
		await toggleNotePinnedStatusById(localStorage.token, note.id);
		note.is_pinned = !note.is_pinned;
		patchTreeNote(note.id, { is_pinned: note.is_pinned });
		pinnedNotes.set(await getPinnedNoteList(localStorage.token).catch(() => []));
	};

	const remove = async () => {
		if (!note) return;
		const id = note.id;
		const ok = await deleteNoteById(localStorage.token, id).catch((e) => {
			toast.error(`${e}`);
			return null;
		});
		if (ok) {
			toast.success($i18n.t('Note deleted'));
			onDeleted(id);
		}
	};

	// --- side panel ----------------------------------------------------------------------

	const showTab = (tab: typeof panelTab) => {
		if (panelOpen && panelTab === tab) {
			panelOpen = false;
		} else {
			panelOpen = true;
			panelTab = tab;
		}
		if (!$mobile) prefs.set('panel.open', panelOpen);
		prefs.set('panel.tab', panelTab);
	};

	const startResize = (event: PointerEvent) => {
		const startX = event.clientX;
		const startWidth = panelWidth;
		const move = (e: PointerEvent) => {
			panelWidth = Math.min(640, Math.max(260, startWidth + (startX - e.clientX)));
		};
		const up = () => {
			window.removeEventListener('pointermove', move);
			window.removeEventListener('pointerup', up);
			prefs.set('panel.width', panelWidth);
		};
		window.addEventListener('pointermove', move);
		window.addEventListener('pointerup', up);
	};

	const TABS = [
		{ key: 'links', label: 'Links', icon: Link2 },
		{ key: 'outline', label: 'Outline', icon: ListTree },
		{ key: 'graph', label: 'Local graph', icon: Orbit },
		{ key: 'ai', label: 'AI', icon: Bot }
	] as const;
</script>

<svelte:head>
	<title>{note?.title ? `${note.title} · ` : ''}{$i18n.t('Notes')}</title>
</svelte:head>

{#if note}
	<AccessControlModal
		bind:show={showAccess}
		bind:accessGrants={note.access_grants}
		accessRoles={['read', 'write']}
		share={$user?.permissions?.sharing?.notes || $isAdmin}
		sharePublic={$user?.permissions?.sharing?.public_notes || $isAdmin}
		shareUsers={($user?.permissions?.access_grants?.allow_users ?? true) || $isAdmin}
		onChange={async () => {
			try {
				await updateNoteAccessGrants(localStorage.token, note.id, note.access_grants ?? []);
				toast.success($i18n.t('Saved'));
			} catch (e) {
				toast.error(`${e}`);
			}
		}}
	/>
	<ConfirmDialog
		bind:open={showDelete}
		title={$i18n.t('Delete this note?')}
		description={$i18n.t('“{{title}}” will be deleted. Links to it will show it as not created.', {
			title: note.title
		})}
		confirmLabel={$i18n.t('Delete note')}
		destructive
		onconfirm={remove}
	/>
	<MoveNoteDialog
		bind:open={showMove}
		noteId={note.id}
		noteOwner={note.user_id}
		currentVaultId={place?.vault_id ?? ''}
		currentFolder={place?.folder ?? ''}
		onMoved={async () => {
			place = await getNotePlace(localStorage.token, note.id).catch(() => place);
			await refreshTree(localStorage.token);
		}}
	/>
{/if}

<Dialog.Root bind:open={showSuggestions}>
	<Dialog.Content class="sm:max-w-lg">
		<Dialog.Header>
			<Dialog.Title>{$i18n.t('Suggested links')}</Dialog.Title>
			<Dialog.Description>
				{$i18n.t('Notes this one names or talks about. Nothing is linked until you choose.')}
			</Dialog.Description>
		</Dialog.Header>
		<div class="max-h-[60vh] space-y-2 overflow-y-auto">
			{#if suggesting}
				<div class="flex items-center gap-2 py-6 text-sm text-muted-foreground">
					<Loader class="size-4 animate-spin" />{$i18n.t('Reading the vault…')}
				</div>
			{:else if !suggestions.length}
				<p class="py-6 text-sm text-muted-foreground">
					{$i18n.t('No suggestion: this note does not seem to talk about your other notes.')}
				</p>
			{:else}
				{#each suggestions as s (s.id)}
					<div class="flex items-start gap-3 rounded-lg border p-3">
						<div class="min-w-0 flex-1">
							<button
								type="button"
								class="truncate text-sm font-medium hover:text-link"
								onclick={() => onOpenNote(s.id)}>{s.title}</button
							>
							<div class="mt-0.5 text-xs text-muted-foreground">
								{#if s.source === 'mention'}{$i18n.t('Named in this note')}{:else}{s.reason ??
										$i18n.t('Suggested by the AI')}{/if}
								{#if s.phrase}· “{s.phrase}”{/if}
							</div>
						</div>
						<Button
							size="sm"
							variant="outline"
							disabled={!editable}
							onclick={() => applySuggestion(s)}>{$i18n.t('Link')}</Button
						>
					</div>
				{/each}
			{/if}
		</div>
	</Dialog.Content>
</Dialog.Root>

<div class="flex h-full min-h-0 w-full">
	<!-- Editor column -->
	<div class="relative flex min-w-0 flex-1 flex-col">
		<!-- Header -->
		<div class="flex h-11 shrink-0 items-center gap-1 border-b px-3">
			<nav
				class="flex min-w-0 flex-1 items-center gap-1 text-sm text-muted-foreground"
				aria-label={$i18n.t('Location')}
			>
				{#if place}
					<span class="inline-flex shrink-0 items-center gap-1">
						{#if isShared}<Users class="size-3.5" />{:else}<Lock class="size-3.5" />{/if}
						<span class="max-w-36 truncate">{vaultTitle}</span>
					</span>
					{#each folderParts as part}
						<ChevronRight class="size-3.5 shrink-0" />
						<span class="max-w-32 truncate">{part}</span>
					{/each}
					<ChevronRight class="size-3.5 shrink-0" />
					<span class="truncate text-foreground">{note?.title || $i18n.t('Untitled')}</span>
				{/if}
			</nav>

			{#if note && editor && note.write_access}
				<Tip content={$i18n.t('Undo')}>
					<Button
						variant="ghost"
						size="icon-sm"
						disabled={!editor.can().undo()}
						onclick={() => editor.chain().focus().undo().run()}
						aria-label={$i18n.t('Undo')}><Undo2 /></Button
					>
				</Tip>
				<Tip content={$i18n.t('Redo')}>
					<Button
						variant="ghost"
						size="icon-sm"
						disabled={!editor.can().redo()}
						onclick={() => editor.chain().focus().redo().run()}
						aria-label={$i18n.t('Redo')}><Redo2 /></Button
					>
				</Tip>
			{/if}

			{#if note}
				<DropdownMenu.Root>
					<DropdownMenu.Trigger>
						{#snippet child({ props })}
							<Button {...props} variant="ghost" size="sm" aria-label={$i18n.t('AI')}>
								{#if editing || titleGenerating}<Loader class="animate-spin" />{:else}<Sparkles
									/>{/if}
								<span class="hidden sm:inline">{$i18n.t('AI')}</span>
							</Button>
						{/snippet}
					</DropdownMenu.Trigger>
					<DropdownMenu.Content align="end" class="w-60">
						<DropdownMenu.Item onSelect={runSuggestions}
							><Link2 />{$i18n.t('Suggest links')}</DropdownMenu.Item
						>
						<DropdownMenu.Item onSelect={() => showTab('ai')}
							><Bot />{$i18n.t('Chat about this note')}</DropdownMenu.Item
						>
						{#if note.write_access}
							<DropdownMenu.Item onSelect={enhance} disabled={editing}
								><WandSparkles />{$i18n.t('Enhance with AI')}</DropdownMenu.Item
							>
							<DropdownMenu.Item onSelect={generateTitle} disabled={titleGenerating}
								><Type />{$i18n.t('Suggest a title')}</DropdownMenu.Item
							>
							<DropdownMenu.Separator />
							<DropdownMenu.Item
								onSelect={async () => {
									displayMediaRecord = false;
									try {
										const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
										stream.getTracks().forEach((t) => t.stop());
										recording = true;
									} catch {
										toast.error($i18n.t('Permission denied when accessing microphone'));
									}
								}}><Mic />{$i18n.t('Record audio')}</DropdownMenu.Item
							>
							<DropdownMenu.Item
								onSelect={() => {
									const input = document.createElement('input');
									input.type = 'file';
									input.accept = 'audio/*';
									input.onchange = async () => {
										if (input.files?.[0]) await uploadFileHandler(input.files[0]);
									};
									input.click();
								}}><Upload />{$i18n.t('Upload audio')}</DropdownMenu.Item
							>
						{/if}
						{#if editing}
							<DropdownMenu.Separator />
							<DropdownMenu.Item onSelect={() => (stopResponseFlag = true)}
								><X />{$i18n.t('Stop')}</DropdownMenu.Item
							>
						{/if}
					</DropdownMenu.Content>
				</DropdownMenu.Root>

				{#if !isShared && ownsNote}
					<Tip content={$i18n.t('Share this note')}>
						<Button variant="ghost" size="sm" onclick={() => (showAccess = true)}>
							<Users /><span class="hidden lg:inline">{$i18n.t('Share')}</span>
						</Button>
					</Tip>
				{/if}

				<DropdownMenu.Root>
					<DropdownMenu.Trigger>
						{#snippet child({ props })}
							<Button {...props} variant="ghost" size="icon-sm" aria-label={$i18n.t('More')}
								><Ellipsis /></Button
							>
						{/snippet}
					</DropdownMenu.Trigger>
					<DropdownMenu.Content align="end" class="w-56">
						<DropdownMenu.Item onSelect={togglePin}>
							{#if note.is_pinned}<PinOff />{$i18n.t('Unpin')}{:else}<Pin />{$i18n.t('Pin')}{/if}
						</DropdownMenu.Item>
						{#if note.write_access}
							<DropdownMenu.Item onSelect={() => (showMove = true)}
								><FolderInput />{$i18n.t('Move to…')}</DropdownMenu.Item
							>
						{/if}
						<DropdownMenu.Item
							onSelect={async () => {
								(await copyToClipboard(`${window.location.origin}/notes/${note.id}`))
									? toast.success($i18n.t('Copied link to clipboard'))
									: toast.error($i18n.t('Failed to copy link'));
							}}><Link2 />{$i18n.t('Copy link')}</DropdownMenu.Item
						>
						<DropdownMenu.Item
							onSelect={async () => {
								(await copyToClipboard(note.data.content.md, note.data.content.html, true)) &&
									toast.success($i18n.t('Copied to clipboard'));
							}}><Copy />{$i18n.t('Copy text')}</DropdownMenu.Item
						>
						<DropdownMenu.Sub>
							<DropdownMenu.SubTrigger><Download />{$i18n.t('Download')}</DropdownMenu.SubTrigger>
							<DropdownMenu.SubContent>
								<DropdownMenu.Item onSelect={() => download('md')}
									>{$i18n.t('Markdown (.md)')}</DropdownMenu.Item
								>
								<DropdownMenu.Item onSelect={() => download('txt')}
									>{$i18n.t('Plain text (.txt)')}</DropdownMenu.Item
								>
								<DropdownMenu.Item onSelect={() => download('pdf')}
									>{$i18n.t('PDF document (.pdf)')}</DropdownMenu.Item
								>
							</DropdownMenu.SubContent>
						</DropdownMenu.Sub>
						<DropdownMenu.Item
							onSelect={() => {
								fullWidth = !fullWidth;
								prefs.set('editor.fullWidth', fullWidth);
							}}
							><MoveHorizontal />{fullWidth
								? $i18n.t('Readable width')
								: $i18n.t('Full width')}</DropdownMenu.Item
						>
						{#if note.write_access}
							<DropdownMenu.Separator />
							<DropdownMenu.Item variant="destructive" onSelect={() => (showDelete = true)}
								><Trash2 />{$i18n.t('Delete')}</DropdownMenu.Item
							>
						{/if}
					</DropdownMenu.Content>
				</DropdownMenu.Root>
			{/if}

			<Tip content={panelOpen ? $i18n.t('Hide side panel') : $i18n.t('Show side panel')}>
				<Button
					variant="ghost"
					size="icon-sm"
					onclick={() => {
						panelOpen = !panelOpen;
						if (!$mobile) prefs.set('panel.open', panelOpen);
					}}
					aria-label={$i18n.t('Side panel')}
					aria-pressed={panelOpen}
				>
					<PanelRight />
				</Button>
			</Tip>
		</div>

		<!-- Body -->
		<div class="min-h-0 flex-1 overflow-y-auto" id="note-content-container">
			{#if loading}
				<div class="mx-auto max-w-3xl space-y-3 px-6 py-10">
					<div class="h-8 w-2/3 animate-pulse rounded-md bg-muted"></div>
					<div class="h-4 w-1/3 animate-pulse rounded-md bg-muted"></div>
					<div class="h-24 animate-pulse rounded-md bg-muted"></div>
				</div>
			{:else if !note}
				<div class="flex h-full items-center justify-center p-6 text-sm text-muted-foreground">
					{$i18n.t('This note does not exist or you cannot open it.')}
				</div>
			{:else}
				<div class="mx-auto px-6 pt-8 pb-32 {fullWidth ? 'max-w-none' : 'max-w-3xl'}">
					<div class="flex items-start gap-2">
						{#if type}
							<span class="mt-2.5 shrink-0" title={typeName(type, $i18n)}>
								<TypeIcon icon={type.icon} class="size-5" style="color: {chartColor(type.color)}" />
							</span>
						{/if}
						<textarea
							id="note-title-input"
							rows="1"
							class="field-sizing-content w-full resize-none bg-transparent text-3xl leading-tight font-semibold tracking-tight outline-none placeholder:text-muted-foreground/60"
							placeholder={titleGenerating ? $i18n.t('Generating…') : $i18n.t('Untitled')}
							bind:value={title}
							disabled={!note.write_access || titleGenerating}
							oninput={onTitleInput}
							onblur={flushTitle}
							onkeydown={(e) => {
								if (e.key === 'Enter') {
									e.preventDefault();
									flushTitle();
									editor?.commands.focus('start');
								}
							}}
						></textarea>
					</div>
					<div
						class="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground"
					>
						<span title={dayjs(note.created_at / 1e6).format('LLL')}
							>{$i18n.t('Created {{when}}', { when: dayjs(note.created_at / 1e6).fromNow() })}</span
						>
						<span title={dayjs(note.updated_at / 1e6).format('LLL')}
							>{$i18n.t('Edited {{when}}', { when: dayjs(note.updated_at / 1e6).fromNow() })}</span
						>
						{#if editor}<span class="tabular-nums"
								>{$i18n.t('{{COUNT}} words', { COUNT: wordCount })}</span
							>{/if}
						{#if !note.write_access}<span class="rounded-md border px-1.5 py-0.5"
								>{$i18n.t('Read only')}</span
							>{/if}
					</div>

					<PropertiesBlock
						vault={$currentVault}
						noteId={note.id}
						properties={note.data.properties}
						editable={!!note.write_access}
						onChange={saveProperties}
						{onOpenNote}
						onCreateNote={(t, nt) =>
							onCreateNote(t, { folder: place?.folder ?? '', type: nt, open: false })}
					/>

					{#if otherFiles.length}
						<div class="mt-2 flex flex-wrap items-center gap-1.5">
							<Paperclip class="size-3.5 text-muted-foreground" />
							{#each otherFiles as f (f.itemId ?? f.id)}
								<span
									class="inline-flex max-w-64 items-center gap-1 rounded-md border px-1.5 py-0.5 text-xs"
								>
									{#if f.status === 'uploading'}<Loader class="size-3 animate-spin" />{/if}
									<span class="truncate">{f.name}</span>
									{#if note.write_access}
										<button
											type="button"
											class="opacity-60 hover:opacity-100"
											aria-label={$i18n.t('Remove')}
											onclick={() => {
												files = files.filter((x) => x !== f);
												saveFiles();
											}}><X class="size-3" /></button
										>
									{/if}
								</span>
							{/each}
						</div>
					{/if}

					<div class="note-vault-editor mt-4">
						{#key note.id}
							<RichTextInput
								bind:this={inputElement}
								bind:editor
								id={`note-${note.id}`}
								className="input-prose min-h-[50vh]"
								json={true}
								bind:value={editorValue}
								documentId={`note:${note.id}`}
								collaboration={true}
								socket={$socket as any}
								user={$user as any}
								dragHandle={true}
								link={true}
								image={true}
								{files}
								{extensions}
								placeholder={$i18n.t(
									'Write, or type / for blocks, [[ to link a note, @ for Gnos3 data'
								)}
								{editable}
								onSelectionUpdate={({ editor: ed }) => {
									const { from, to } = ed.state.selection;
									const text = ed.state.doc.textBetween(from, to, ' ');
									selectedContent = text ? { text, from, to } : null;
								}}
								onChange={onContentChange}
								fileHandler={true}
								onFileDrop={(ed, dropped, pos) => {
									dropped.forEach(async (file: File) => {
										const item = await inputFileHandler(file).catch(() => null);
										if (item?.type === 'image') insertImage(ed, pos, item);
									});
								}}
								onFilePaste={() => {}}
								on:paste={async (e) => {
									const event = e.detail?.event || e;
									for (const item of event.clipboardData?.items ?? []) {
										if (item.type.startsWith('image/')) {
											const fileItem = await inputFileHandler(item.getAsFile());
											if (fileItem && editor)
												insertImage(editor, editor.state.selection.$anchor.pos, fileItem);
										} else if (item.kind === 'file') {
											event.preventDefault();
											await inputFileHandler(item.getAsFile());
										}
									}
								}}
							/>
						{/key}
					</div>
				</div>
			{/if}
		</div>

		{#if recording}
			<div class="absolute right-4 bottom-4 z-20 w-80 max-w-[calc(100%-2rem)]">
				<VoiceRecording
					bind:recording
					className="p-1 w-full max-w-full"
					transcribe={false}
					displayMedia={displayMediaRecord}
					echoCancellation={false}
					noiseSuppression={false}
					onCancel={() => (recording = false)}
					onConfirm={(data) => {
						if (data?.file) uploadFileHandler(data.file);
						recording = false;
					}}
				/>
			</div>
		{/if}
	</div>

	<!-- Side panel -->
	{#if panelOpen && note}
		{#if $mobile}
			<button
				type="button"
				class="fixed inset-0 z-30 bg-black/30"
				aria-label={$i18n.t('Close')}
				onclick={() => (panelOpen = false)}
			></button>
		{/if}
		<aside
			class="flex min-h-0 flex-col border-l bg-background {$mobile
				? 'fixed inset-y-0 right-0 z-40 w-[min(100vw,22rem)] shadow-xl'
				: 'relative shrink-0'}"
			style={$mobile ? '' : `width: ${panelWidth}px`}
		>
			{#if !$mobile}
				<div
					role="separator"
					aria-orientation="vertical"
					class="absolute inset-y-0 -left-1 z-10 w-2 cursor-col-resize hover:bg-primary/10"
					onpointerdown={startResize}
				></div>
			{/if}
			<div class="flex h-11 shrink-0 items-center gap-0.5 border-b px-2" role="tablist">
				{#each TABS as tab (tab.key)}
					<Tip content={$i18n.t(tab.label)}>
						<button
							type="button"
							role="tab"
							aria-selected={panelTab === tab.key}
							class="inline-flex h-8 items-center gap-1.5 rounded-md px-2 text-sm {panelTab ===
							tab.key
								? 'bg-accent text-accent-foreground'
								: 'text-muted-foreground hover:bg-accent/60 hover:text-foreground'}"
							onclick={() => {
								panelTab = tab.key;
								prefs.set('panel.tab', panelTab);
							}}
						>
							<tab.icon class="size-4" />
							{#if panelTab === tab.key}<span>{$i18n.t(tab.label)}</span>{/if}
						</button>
					</Tip>
				{/each}
			</div>
			<div class="min-h-0 flex-1">
				{#if panelTab === 'links'}
					<LinksPanel
						noteId={note.id}
						noteTitle={note.title}
						{onOpenNote}
						onCreateNote={(t) => onCreateNote(t, { folder: place?.folder ?? '', open: true })}
					/>
				{:else if panelTab === 'outline'}
					<OutlinePanel {editor} />
				{:else if panelTab === 'graph'}
					{#if place?.vault_permission}
						<GraphView
							vaultId={place.vault_id}
							mode="local"
							focusId={note.id}
							{onOpenNote}
							onCreateNote={(t) => onCreateNote(t, { folder: place?.folder ?? '', open: true })}
							{onTag}
						/>
					{/if}
				{:else}
					<div class="flex h-full flex-col px-3">
						<Chat
							bind:show={panelOpen}
							bind:selectedModelId
							bind:messages
							bind:note
							bind:editing
							bind:streaming
							bind:stopResponseFlag
							{editor}
							{selectedContent}
							{files}
							onInsert={(content) => inputElement?.insertContent(content)}
							onStop={() => (stopResponseFlag = true)}
							{onEdited}
							insertNoteHandler={() => {}}
							scrollToBottomHandler={() => {
								const el = document.getElementById('note-content-container');
								if (el) el.scrollTop = el.scrollHeight;
							}}
						/>
					</div>
				{/if}
			</div>
		</aside>
	{/if}
</div>
