<!-- The icon of a note type (vault settings store the icon's name). -->
<script lang="ts" module>
	import User from '@lucide/svelte/icons/user';
	import Users from '@lucide/svelte/icons/users';
	import Building2 from '@lucide/svelte/icons/building-2';
	import FolderKanban from '@lucide/svelte/icons/folder-kanban';
	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import Lightbulb from '@lucide/svelte/icons/lightbulb';
	import FileText from '@lucide/svelte/icons/file-text';
	import BookOpen from '@lucide/svelte/icons/book-open';
	import Briefcase from '@lucide/svelte/icons/briefcase';
	import Target from '@lucide/svelte/icons/target';
	import Flag from '@lucide/svelte/icons/flag';
	import Star from '@lucide/svelte/icons/star';
	import MapPin from '@lucide/svelte/icons/map-pin';
	import Package from '@lucide/svelte/icons/package';
	import Scale from '@lucide/svelte/icons/scale';
	import Landmark from '@lucide/svelte/icons/landmark';
	import Handshake from '@lucide/svelte/icons/handshake';
	import ListChecks from '@lucide/svelte/icons/list-checks';
	import GraduationCap from '@lucide/svelte/icons/graduation-cap';
	import Bookmark from '@lucide/svelte/icons/bookmark';

	export const TYPE_ICONS: Record<string, any> = {
		user: User,
		users: Users,
		'building-2': Building2,
		'folder-kanban': FolderKanban,
		'calendar-days': CalendarDays,
		lightbulb: Lightbulb,
		'file-text': FileText,
		'book-open': BookOpen,
		briefcase: Briefcase,
		target: Target,
		flag: Flag,
		star: Star,
		'map-pin': MapPin,
		package: Package,
		scale: Scale,
		landmark: Landmark,
		handshake: Handshake,
		'list-checks': ListChecks,
		'graduation-cap': GraduationCap,
		bookmark: Bookmark
	};

	export const TYPE_COLORS = [
		'chart-1',
		'chart-2',
		'chart-3',
		'chart-4',
		'chart-5',
		'chart-6',
		'chart-7',
		'chart-8'
	];
</script>

<script lang="ts">
	let {
		icon = 'file-text',
		class: className = '',
		style = ''
	}: { icon?: string | null; class?: string; style?: string } = $props();
	const Icon = $derived(TYPE_ICONS[icon ?? ''] ?? FileText);
</script>

<Icon class={className} {style} />
