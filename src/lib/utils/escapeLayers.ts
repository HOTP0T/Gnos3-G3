/** Escape closes the innermost thing first: a list, menu or popover (bits-ui) open
 *  inside a modal takes the key, and the modal stays open. bits-ui keeps its open
 *  layers in globalThis.bitsEscapeLayers and drops one as soon as it closes, so the
 *  map is read in the capture phase, before any handler runs. */
const takenByLayer = new WeakSet<Event>();

if (typeof window !== 'undefined') {
	window.addEventListener(
		'keydown',
		(event) => {
			const layers = (globalThis as { bitsEscapeLayers?: Map<unknown, unknown> }).bitsEscapeLayers;
			if (event.key === 'Escape' && layers?.size) {
				takenByLayer.add(event);
			}
		},
		true
	);
}

/** True when this Escape belongs to an open list, menu or popover, not to the modal. */
export const escapeTakenByLayer = (event: KeyboardEvent): boolean => takenByLayer.has(event);
