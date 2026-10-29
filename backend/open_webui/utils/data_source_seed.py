"""
Create the data sources a box needs for the modules it runs.

A data source (Workspace → Data Sources) keeps a knowledge base in step with
K4mi, the accounting or the business cards, so the chat can answer from them.
A new box had none until someone added them by hand (test box, 2026-10-29).
Each source below is created once per box:

  - when the box runs its module: the invoice and business-card modules answer
    on the stack network; K4mi, which every box runs, once the modules'
    K4MI_API_TOKEN is set (the connector reads it from the environment, so it
    never sits in the source's settings, which every signed-in user can read);
  - owned by the superadmin: syncs call the modules as the owner, and admins
    see every company;
  - its knowledge base readable by the groups whose permissions already show
    them that data (admins see every knowledge base anyway).

A source an admin deleted stays deleted, and a box that already has a source
of that type (added by hand) keeps its own. The sync worker calls this every
minute, so the sources appear after the first sign-up and when a module starts
later than Gnos3.
"""

import asyncio
import logging
import os

import httpx

from open_webui.config import PersistentConfig
from open_webui.models.data_connector import DataConnectorForm, DataConnectors
from open_webui.models.groups import Groups
from open_webui.models.users import Users
from open_webui.utils.rbac_seed import ensure_default_rbac_groups

log = logging.getLogger(__name__)

SEEDED = PersistentConfig('GNOS3_DATA_SOURCES_SEEDED', 'gnos3.data_sources_seeded', [])

# Where Gnos3 reaches the modules on an appliance's stack network.
K4MI_URL = os.environ.get('K4MI_MODULE_URL', 'http://k4mi:8000').rstrip('/')
INVOICES_URL = os.environ.get('INVOICES_MODULE_URL', 'http://invoice-api:8001').rstrip('/')
BUSINESS_CARDS_URL = os.environ.get('BUSINESS_CARDS_MODULE_URL', 'http://bc-api:8002').rstrip('/')

# connector type → the source as an admin would add it, and the permissions
# (all of them) a group needs to read its knowledge base.
SOURCES = {
    'k4mi': {
        'name': 'K4mi Documents',
        'description': 'All documents from K4mi (OCR text)',
        'sync_interval': 300,
        'readers': [('k4mi', 'documents', 'read')],
    },
    'invoice_db': {
        'name': 'Accounting & Invoices',
        'description': 'Invoices, journal entries, payments, and company data from the accounting system',
        'sync_interval': 1800,
        'readers': [('modules', 'invoices', 'read'), ('modules', 'accounting', 'read')],
    },
    'business_card_db': {
        'name': 'Business Card Database',
        'description': 'Contacts and notes from the business cards',
        'sync_interval': 300,
        'readers': [('modules', 'business_cards', 'read')],
    },
}

_lock = asyncio.Lock()


async def _answers(url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            return (await client.get(f'{url}/health')).status_code == 200
    except httpx.HTTPError:
        return False


async def _settings(kind: str):
    """The source's settings, or None while this box does not run its module."""
    if kind == 'k4mi':
        if not os.environ.get('K4MI_API_TOKEN'):
            return None
        # Links in the chat's citations: K4mi's own public address.
        link = os.environ.get('K4MI_LINK_URL') or K4MI_URL
        return {'base_url': K4MI_URL, 'public_url': link.rstrip('/'), 'use_ocr_text': True}
    if kind == 'invoice_db':
        if not await _answers(INVOICES_URL):
            return None
        return {
            'api_base_url': INVOICES_URL,
            'include_invoices': True,
            'include_transactions': True,
            'include_payments': True,
            'include_company_summaries': True,
        }
    if kind == 'business_card_db':
        if not await _answers(BUSINESS_CARDS_URL):
            return None
        return {'api_base_url': BUSINESS_CARDS_URL}
    return None


def _allows(permissions: dict, path: tuple) -> bool:
    value = permissions
    for key in path:
        value = value.get(key) if isinstance(value, dict) else None
    return value is True


def readers(groups, paths) -> list[dict]:
    return [
        {'principal_type': 'group', 'principal_id': group.id, 'permission': 'read'}
        for group in groups
        if all(_allows(group.permissions or {}, path) for path in paths)
    ]


async def _mark(kind: str) -> None:
    SEEDED.value = [*SEEDED.value, kind]
    await SEEDED.async_save()


async def ensure_default_data_sources() -> None:
    async with _lock:
        pending = [kind for kind in SOURCES if kind not in SEEDED.value]
        if not pending:
            return
        owner = await Users.get_super_admin_user()
        if owner is None:
            return

        from open_webui.services.data_connector import _ensure_knowledge_base

        existing = {c.connector_type for c in DataConnectors.get_connectors()}
        for kind in pending:
            if kind in existing:
                await _mark(kind)
                continue
            settings = await _settings(kind)
            if settings is None:
                continue

            # The groups its knowledge base is shared with; they are created at
            # the first sign-up, which may still be running.
            await ensure_default_rbac_groups()
            source = SOURCES[kind]
            connector = DataConnectors.insert_new_connector(
                user_id=owner.id,
                form_data=DataConnectorForm(
                    name=source['name'],
                    description=source['description'],
                    connector_type=kind,
                    config=settings,
                    sync_interval=source['sync_interval'],
                ),
            )
            if connector is None:
                log.warning(f'Data sources: could not create {source["name"]!r}; tried again in a minute')
                continue
            grants = readers(await Groups.get_all_groups(), source['readers'])
            await _ensure_knowledge_base(connector, owner.id, access_grants=grants)
            await _mark(kind)
            log.info(f'Data sources: created {source["name"]!r}, readable by {len(grants)} group(s)')
