import { writable } from 'svelte/store';
import { getModules, type ModuleInfo } from '$lib/apis/modules';

/** Modules enabled on this deployment, populated from the dispatcher's
 * /api/modules endpoint at app boot. Empty until the first fetch resolves. */
export const enabledModules = writable<ModuleInfo[]>([]);

/** True once the first fetch has answered (even with an empty list). */
export const modulesLoaded = writable(false);

let initialized = false;

export const refreshEnabledModules = async () => {
	const mods = await getModules();
	enabledModules.set(mods);
	modulesLoaded.set(true);
	return mods;
};

export const ensureModulesLoaded = async () => {
	if (initialized) return;
	initialized = true;
	await refreshEnabledModules();
};
