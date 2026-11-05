<script lang="ts">
	import {
		canEditSystemPrompt as allowSystemPrompt,
		canEditParameters
	} from '$lib/utils/settings-access';
	import { createEventDispatcher, onMount, getContext } from 'svelte';
	import { getLanguages, changeLanguage } from '$lib/i18n';
	const dispatch = createEventDispatcher();

	import { config, models, settings, theme, user, isAdmin} from '$lib/stores';

	const i18n: any = getContext('i18n');

	import AdvancedParams from './Advanced/AdvancedParams.svelte';
	import Textarea from '$lib/components/common/Textarea.svelte';
	import * as Select from '$lib/components/ui/select/index.js';
	import UserSettingField from './UserSettingField.svelte';
	import UserSettingRow from './UserSettingRow.svelte';
	import UserSettingSection from './UserSettingSection.svelte';
	import SettingsSelect from '$lib/components/common/SettingsSelect.svelte';
	export let saveSettings: Function;
	export let getModels: Function;

	// General
	let themes = ['dark', 'light'];
	let selectedTheme = 'system';

	let languages: Awaited<ReturnType<typeof getLanguages>> = [];
	let lang = $i18n.language;
	let system = '';

	let showAdvanced = false;

	// Theme and language use the design system's list rather than a native <select>: the browser
	// draws a native list outside the page, and on a Wayland desktop Chrome let the 60 languages
	// run past the bottom of the screen. This one stays inside the window and scrolls.
	let themeLabels: Record<string, string>;
	$: themeLabels = {
		system: `⚙️ ${$i18n.t('System')}`,
		dark: `🌑 ${$i18n.t('Dark')}`,
		light: `☀️ ${$i18n.t('Light')}`
	};
	const selectTriggerClass =
		'h-auto gap-1 border-0 bg-transparent py-2 pr-1 pl-2 text-xs shadow-none dark:bg-transparent dark:hover:bg-transparent';
	// Above the settings modal (z-9999), and never taller than the room left in the window.
	const selectContentClass =
		'z-10000 max-h-[min(20rem,var(--bits-select-content-available-height))]';

	const systemPromptTextareaClass =
		'w-full resize-y rounded-lg border border-gray-100/50 bg-gray-50/40 px-2 py-1.5 text-xs text-gray-700 outline-hidden transition-colors placeholder:text-gray-300 focus:border-blue-400 dark:border-white/[0.04] dark:bg-white/[0.03] dark:text-gray-300 dark:placeholder:text-gray-700 dark:focus:border-blue-500';
	const actionButtonClass =
		'text-xs text-gray-500 transition-colors hover:text-gray-900 dark:text-gray-500 dark:hover:text-white';

	let params = {
		// Advanced
		stream_response: null,
		stream_delta_chunk_size: null,
		compact_token_threshold: null,
		function_calling: null,
		reasoning_tags: null,
		seed: null,
		temperature: null,
		reasoning_effort: null,
		logit_bias: null,
		frequency_penalty: null,
		presence_penalty: null,
		repeat_penalty: null,
		repeat_last_n: null,
		mirostat: null,
		mirostat_eta: null,
		mirostat_tau: null,
		top_k: null,
		top_p: null,
		min_p: null,
		stop: null,
		tfs_z: null,
		num_ctx: null,
		num_batch: null,
		num_keep: null,
		max_tokens: null,
		use_mmap: null,
		use_mlock: null,
		num_thread: null,
		num_gpu: null,
		think: null,
		format: null,
		keep_alive: null
	};

	$: canEditSystemPrompt = allowSystemPrompt({ user: $user, config: $config });
	$: canEditParams = canEditParameters({ user: $user, config: $config });

	const saveHandler = async () => {
		const updated: Record<string, any> = {};
		if (canEditSystemPrompt) {
			updated.system = system !== '' ? system : null;
		}
		if (canEditParams) {
			updated.params = {
				...$settings.params,
				stream_response: params.stream_response !== null ? params.stream_response : undefined,
				stream_delta_chunk_size:
					params.stream_delta_chunk_size !== null ? params.stream_delta_chunk_size : undefined,
				compact_token_threshold:
					params.compact_token_threshold !== null ? params.compact_token_threshold : undefined,
				function_calling: params.function_calling !== null ? params.function_calling : undefined,
				reasoning_tags: params.reasoning_tags !== null ? params.reasoning_tags : undefined,
				seed: (params.seed !== null ? params.seed : undefined) ?? undefined,
				stop: params.stop ? params.stop.split(',').filter((e) => e) : undefined,
				temperature: params.temperature !== null ? params.temperature : undefined,
				reasoning_effort: params.reasoning_effort !== null ? params.reasoning_effort : undefined,
				logit_bias: params.logit_bias !== null ? params.logit_bias : undefined,
				frequency_penalty: params.frequency_penalty !== null ? params.frequency_penalty : undefined,
				presence_penalty: params.presence_penalty !== null ? params.presence_penalty : undefined,
				repeat_penalty: params.repeat_penalty !== null ? params.repeat_penalty : undefined,
				repeat_last_n: params.repeat_last_n !== null ? params.repeat_last_n : undefined,
				mirostat: params.mirostat !== null ? params.mirostat : undefined,
				mirostat_eta: params.mirostat_eta !== null ? params.mirostat_eta : undefined,
				mirostat_tau: params.mirostat_tau !== null ? params.mirostat_tau : undefined,
				top_k: params.top_k !== null ? params.top_k : undefined,
				top_p: params.top_p !== null ? params.top_p : undefined,
				min_p: params.min_p !== null ? params.min_p : undefined,
				tfs_z: params.tfs_z !== null ? params.tfs_z : undefined,
				num_ctx: params.num_ctx !== null ? params.num_ctx : undefined,
				num_batch: params.num_batch !== null ? params.num_batch : undefined,
				num_keep: params.num_keep !== null ? params.num_keep : undefined,
				max_tokens: params.max_tokens !== null ? params.max_tokens : undefined,
				use_mmap: params.use_mmap !== null ? params.use_mmap : undefined,
				use_mlock: params.use_mlock !== null ? params.use_mlock : undefined,
				num_thread: params.num_thread !== null ? params.num_thread : undefined,
				num_gpu: params.num_gpu !== null ? params.num_gpu : undefined,
				think: params.think !== null ? params.think : undefined,
				keep_alive: params.keep_alive !== null ? params.keep_alive : undefined,
				format: params.format !== null ? params.format : undefined,
				custom_params:
					params.custom_params && Object.keys(params.custom_params).length > 0
						? params.custom_params
						: undefined
			};
		}
		try {
			await saveSettings(updated);
			dispatch('save');
		} catch {
			// The settings modal displays the save error; do not report success.
		}
	};

	onMount(async () => {
		selectedTheme = localStorage.theme ?? 'system';

		languages = await getLanguages();

		system = $settings.system ?? '';

		params = { ...params, ...$settings.params };
		params.stop = $settings?.params?.stop ? ($settings?.params?.stop ?? []).join(',') : null;
	});

	const applyTheme = (_theme: string) => {
		let themeToApply = _theme;

		if (_theme === 'system') {
			themeToApply = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
		}

		themes
			.filter((e) => e !== themeToApply)
			.forEach((e) => {
				e.split(' ').forEach((e) => {
					document.documentElement.classList.remove(e);
				});
			});

		themeToApply.split(' ').forEach((e) => {
			document.documentElement.classList.add(e);
		});

		const metaThemeColor = document.querySelector('meta[name="theme-color"]');
		if (metaThemeColor) {
			if (_theme.includes('system')) {
				const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
					? 'dark'
					: 'light';
				console.log('Setting system meta theme color: ' + systemTheme);
				metaThemeColor.setAttribute('content', systemTheme === 'light' ? '#ffffff' : '#0a1019');
			} else {
				console.log('Setting meta theme color: ' + _theme);
				metaThemeColor.setAttribute('content', _theme === 'dark' ? '#0a1019' : '#ffffff');
			}
		}

		if (typeof window !== 'undefined' && window.applyTheme) {
			window.applyTheme();
		}

		console.log(_theme);
	};

	const themeChangeHandler = (_theme: string) => {
		theme.set(_theme);
		localStorage.setItem('theme', _theme);
		applyTheme(_theme);
	};
</script>

<div class="flex flex-col h-full justify-between text-sm" id="tab-general">
	<h2 class="text-sm font-medium text-gray-900 dark:text-white mb-4">
		{$i18n.t('settings.personal.general.title')}
	</h2>

	<div class="flex-1 min-h-0 overflow-y-auto scrollbar-hover pr-1.5">
		<UserSettingSection
			title={$i18n.t('settings.personal.general.sections.webuiSettings.title')}
			first
		>
			<UserSettingRow
				label={$i18n.t('settings.personal.general.theme.label')}
				description={$i18n.t('settings.personal.general.theme.description')}
			>
				<Select.Root
					type="single"
					bind:value={selectedTheme}
					onValueChange={(value) => themeChangeHandler(value)}
				>
					<Select.Trigger
						class={selectTriggerClass}
						aria-label={$i18n.t('settings.personal.general.theme.label')}
					>
						{themeLabels[selectedTheme] ?? themeLabels.system}
					</Select.Trigger>
					<Select.Content class={selectContentClass} align="end">
						{#each Object.entries(themeLabels) as [value, label]}
							<Select.Item {value} {label} class="text-xs" />
						{/each}
					</Select.Content>
				</Select.Root>
			</UserSettingRow>

			<UserSettingRow
				label={$i18n.t('settings.personal.general.language.label')}
				description={$i18n.t('settings.personal.general.language.description')}
			>
				<Select.Root
					type="single"
					bind:value={lang}
					onValueChange={(value) => changeLanguage(value)}
				>
					<Select.Trigger
						class={selectTriggerClass}
						aria-label={$i18n.t('settings.personal.general.language.label')}
					>
						{languages.find((language) => language.code === lang)?.title ?? lang}
					</Select.Trigger>
					<Select.Content class={selectContentClass} align="end">
						{#each languages as language}
							<Select.Item value={language.code} label={language.title} class="text-xs" />
						{/each}
					</Select.Content>
				</Select.Root>
			</UserSettingRow>
		</UserSettingSection>

		{#if canEditSystemPrompt}
			<UserSettingSection title={$i18n.t('settings.personal.general.sections.systemPrompt.title')}>
				<UserSettingField
					description={$i18n.t('settings.personal.general.sections.systemPrompt.description')}
				>
					<Textarea
						bind:value={system}
						className={systemPromptTextareaClass}
						rows="4"
						placeholder={$i18n.t('Enter system prompt here')}
					/>
				</UserSettingField>
			</UserSettingSection>
		{/if}

		{#if canEditParams}
			<UserSettingSection
				title={$i18n.t('settings.personal.general.sections.advancedParameters.title')}
			>
				<UserSettingRow
					let:labelId
					description={$i18n.t('settings.personal.general.modelParameters.description')}
				>
					<span slot="label">{$i18n.t('settings.personal.general.modelParameters.label')}</span>
					<button
						id={`${labelId}-control`}
						class={actionButtonClass}
						type="button"
						aria-expanded={showAdvanced}
						on:click={() => {
							showAdvanced = !showAdvanced;
						}}>{showAdvanced ? $i18n.t('Hide') : $i18n.t('Show')}</button
					>
				</UserSettingRow>

				{#if showAdvanced}
					<AdvancedParams admin={$isAdmin} custom={true} bind:params />
				{/if}
			</UserSettingSection>
		{/if}
	</div>

	<div class="shrink-0 flex justify-end pt-3 text-sm font-normal">
		<button
			class="flex h-7 shrink-0 items-center justify-center gap-1.5 rounded-lg bg-gray-900 px-2.5 text-xs font-normal text-white transition hover:bg-black disabled:opacity-60 dark:bg-gray-100 dark:text-gray-900 dark:hover:bg-white"
			on:click={() => {
				saveHandler();
			}}
		>
			{$i18n.t('Save')}
		</button>
	</div>
</div>
