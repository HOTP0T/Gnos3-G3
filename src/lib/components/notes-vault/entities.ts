// Links from a note to Gnos3 data: accounting companies, invoices, business cards, K4mi documents,
// chats. In Markdown they are ordinary links to the record's page (the backend reads them back
// with the same table: utils/note_content.py ENTITY_TYPES), so an exported vault keeps them.

import { get } from 'svelte/store';
import Building2 from '@lucide/svelte/icons/building-2';
import ReceiptText from '@lucide/svelte/icons/receipt-text';
import Contact from '@lucide/svelte/icons/contact';
import FileText from '@lucide/svelte/icons/file-text';
import MessageSquare from '@lucide/svelte/icons/message-square';

import { WEBUI_API_BASE_URL } from '$lib/constants';
import { enabledModules } from '$lib/stores/modules';
import { user } from '$lib/stores';
import { getCompanies } from '$lib/apis/accounting';
import { getInvoices } from '$lib/apis/invoices';
import { getBusinessCards } from '$lib/apis/business-cards';
import { getChatListBySearchText } from '$lib/apis/chats';
import { langHeader } from '$lib/utils/uiLocale';

export type EntityType = 'company' | 'invoice' | 'business_card' | 'document' | 'chat';

export const ENTITY_TYPES: EntityType[] = [
	'company',
	'invoice',
	'business_card',
	'document',
	'chat'
];

export const ENTITY_META: Record<EntityType, { label: string; icon: any }> = {
	company: { label: 'Company', icon: Building2 },
	invoice: { label: 'Invoice', icon: ReceiptText },
	business_card: { label: 'Business card', icon: Contact },
	document: { label: 'Document', icon: FileText },
	chat: { label: 'Chat', icon: MessageSquare }
};

export interface EntityHit {
	entity_type: EntityType;
	entity_id: string;
	label: string;
	detail?: string;
}

export const entityHref = (type: string, id: string | number): string => {
	switch (type) {
		case 'company':
			return `/accounting/company/${id}/dashboard`;
		case 'invoice':
			return `/invoices/data?invoice=${id}`;
		case 'business_card':
			return `/business-cards/data?card=${id}`;
		case 'document':
			return `/api/v1/auths/k4mi/open?doc_id=${id}`;
		case 'chat':
			return `/c/${id}`;
	}
	return '';
};

/** Same table as the backend's parse_entity_href: '/accounting/company/12/dashboard' → company 12. */
export const parseEntityHref = (
	href: string | null | undefined
): { type: EntityType; id: string } | null => {
	if (!href) return null;
	let url: URL;
	try {
		url = new URL(href, 'http://local');
	} catch {
		return null;
	}
	const path = url.pathname.replace(/\/+$/, '');
	let m = path.match(/^\/accounting\/company\/(\d+)(?:\/|$)/);
	if (m) return { type: 'company', id: m[1] };
	m = path.match(/^\/c\/([0-9a-fA-F-]{8,})$/);
	if (m) return { type: 'chat', id: m[1] };
	if (path === '/invoices/data' && url.searchParams.get('invoice'))
		return { type: 'invoice', id: url.searchParams.get('invoice')! };
	if (path === '/business-cards/data' && url.searchParams.get('card'))
		return { type: 'business_card', id: url.searchParams.get('card')! };
	if (path === '/api/v1/auths/k4mi/open' && url.searchParams.get('doc_id'))
		return { type: 'document', id: url.searchParams.get('doc_id')! };
	return null;
};

export const entityMarkdown = (type: string, id: string, label: string) =>
	`[${label.replace(/[\[\]]/g, '')}](${entityHref(type, id)})`;

/** Opens in a new tab: a K4mi document (another app). Everything else stays in Gnos3. */
export const opensOutside = (type: string) => type === 'document';

// --- which kinds this person can link to ------------------------------------

const moduleOn = (name: string) => get(enabledModules).some((m: any) => m.name === name);

const allowed = (path: string[]) => {
	const u: any = get(user);
	if (!u) return false;
	if (u.role === 'admin' || u.role === 'superadmin') return true;
	let node = u.permissions;
	for (const key of path) node = node?.[key];
	return Boolean(node);
};

export const availableEntityTypes = (): EntityType[] => {
	const out: EntityType[] = [];
	if (moduleOn('invoices') && allowed(['modules', 'accounting', 'read'])) out.push('company');
	if (moduleOn('invoices') && allowed(['modules', 'invoices', 'read'])) out.push('invoice');
	if (moduleOn('business_cards') && allowed(['modules', 'business_cards', 'read']))
		out.push('business_card');
	out.push('document');
	out.push('chat');
	return out;
};

// --- search ------------------------------------------------------------------

let companyCache: { at: number; list: any[] } | null = null;

const searchCompanies = async (q: string): Promise<EntityHit[]> => {
	if (!companyCache || Date.now() - companyCache.at > 60_000) {
		const list = await getCompanies({ active: true });
		companyCache = {
			at: Date.now(),
			list: Array.isArray(list) ? list : (list?.companies ?? list?.items ?? [])
		};
	}
	const needle = q.toLocaleLowerCase();
	return companyCache.list
		.filter((c: any) => (c.name ?? '').toLocaleLowerCase().includes(needle))
		.slice(0, 6)
		.map((c: any) => ({
			entity_type: 'company',
			entity_id: String(c.id),
			label: c.name,
			detail: c.country ?? undefined
		}));
};

const searchInvoices = async (token: string, q: string): Promise<EntityHit[]> => {
	const res: any = await getInvoices(token, { q, limit: 6 });
	return (res?.invoices ?? []).map((i: any) => ({
		entity_type: 'invoice',
		entity_id: String(i.id),
		label: [i.vendor_name, i.invoice_number].filter(Boolean).join(' · ') || `#${i.id}`,
		detail: [
			i.invoice_date,
			i.total_amount != null ? `${i.total_amount} ${i.currency ?? ''}`.trim() : null
		]
			.filter(Boolean)
			.join(' · ')
	}));
};

const searchCards = async (token: string, q: string): Promise<EntityHit[]> => {
	const res = await getBusinessCards(token, { q, limit: 6 });
	return (res?.business_cards ?? []).map((c: any) => ({
		entity_type: 'business_card',
		entity_id: String(c.id),
		label: c.full_name || c.company_name || `#${c.id}`,
		detail: [c.job_title, c.company_name].filter(Boolean).join(' · ')
	}));
};

const searchDocuments = async (token: string, q: string): Promise<EntityHit[]> => {
	const res = await fetch(
		`${WEBUI_API_BASE_URL}/note-vaults/entities/documents?q=${encodeURIComponent(q)}`,
		{ headers: { authorization: `Bearer ${token}`, ...langHeader() } }
	);
	if (!res.ok) return [];
	return await res.json();
};

const searchChats = async (token: string, q: string): Promise<EntityHit[]> => {
	const res: any = await getChatListBySearchText(token, q, 1);
	return (res ?? []).slice(0, 6).map((c: any) => ({
		entity_type: 'chat',
		entity_id: String(c.id),
		label: c.title || '…'
	}));
};

/** Every kind this person may link to, searched at once; a module that does not answer is skipped. */
export const searchEntities = async (token: string, q: string, types?: EntityType[]) => {
	const query = q.trim();
	if (query.length < 2) return [] as EntityHit[];
	const kinds = (types ?? availableEntityTypes()).filter((t) => availableEntityTypes().includes(t));
	const jobs: Promise<EntityHit[]>[] = kinds.map((kind) => {
		const job =
			kind === 'company'
				? searchCompanies(query)
				: kind === 'invoice'
					? searchInvoices(token, query)
					: kind === 'business_card'
						? searchCards(token, query)
						: kind === 'document'
							? searchDocuments(token, query)
							: searchChats(token, query);
		return job.catch(() => [] as EntityHit[]);
	});
	return (await Promise.all(jobs)).flat();
};
