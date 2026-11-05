"""Notes vaults for chat: each vault can have a knowledge base the chat searches.

A vault's knowledge base ("Notes · <vault>", id derived from the vault id, `meta.gnos3_notes_vault`)
holds one text file per note (no stored file: `file.path = ''`, the text in `file.data.content`,
id derived from the note id). Each note is embedded twice: into the knowledge base's collection
(attaching the whole vault searches it) and into its own `file-<id>` collection (attaching a folder
or a tag searches only those notes, through upstream's `collection_names` item).

Who can read it: a personal vault's base is its owner's; a shared vault's base gets the vault's
groups as readers (`sync_access`). Upstream's retrieval access checks then apply unchanged.

A vault's base exists once somebody uses the vault in chat (`settings.ai.knowledge` becomes true);
from then on `note_vault_knowledge_worker` re-embeds changed notes every minute.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from fastapi import Request
from sqlalchemy import select

from open_webui.internal.db import get_async_db_context
from open_webui.models.access_grants import AccessGrants
from open_webui.models.files import File, FileForm, Files
from open_webui.models.knowledge import Knowledge, Knowledges
from open_webui.models.note_vaults import NotePlacement, NoteVault, NoteVaultModel
from open_webui.models.notes import Note
from open_webui.services import note_vaults as vaults
from open_webui.utils import note_content as nc

log = logging.getLogger(__name__)

KB_NS = 'gnos3-notes-vault-knowledge:'
FILE_NS = 'gnos3-notes-file:'
POLL_SECONDS = 60
# Notes embedded per vault per pass: a large import is spread over a few minutes instead of
# holding the embedding model for one long stretch.
BATCH = 40

_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='notes-kb')
_locks: dict[str, asyncio.Lock] = {}


def knowledge_id(vault_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, KB_NS + vault_id))


def note_file_id(note_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, FILE_NS + note_id))


def mock_request(app) -> Request:
    return Request(
        scope={
            'type': 'http',
            'asgi': {'version': '3.0', 'spec_version': '2.0'},
            'http_version': '1.1',
            'method': 'POST',
            'headers': [],
            'path': '/',
            'root_path': '',
            'scheme': 'http',
            'query_string': b'',
            'server': ('localhost', 8080),
            'app': app,
        }
    )


_DATA_IMAGE_RE = re.compile(r'!\[[^\]]*\]\((?:data:|data://)[^)]*\)')


def note_text(title: str, properties: dict, md: str) -> str:
    """What the chat reads for one note: its title, its properties, its text."""
    _, body = nc.split_frontmatter(md or '')
    body = _DATA_IMAGE_RE.sub('', body)
    lines = [f'# {title or "Untitled"}']
    for key, value in (properties or {}).items():
        if value in (None, '', [], {}):
            continue
        values = value if isinstance(value, list) else [value]
        shown = []
        for item in values:
            if isinstance(item, dict):
                shown.append(item.get('title') or item.get('label') or str(item.get('entity_id') or ''))
            else:
                shown.append(str(item))
        lines.append(f'{key}: {", ".join(s for s in shown if s)}')
    return '\n'.join(lines) + '\n\n' + body.strip()


async def ensure_knowledge(vault: NoteVaultModel) -> str:
    kb = knowledge_id(vault.id)
    name = f'Notes · {vault.name}'
    async with get_async_db_context() as db:
        row = await db.get(Knowledge, kb)
        if row and (row.meta or {}).get('gnos3_notes_vault') != vault.id:
            raise RuntimeError('Notes knowledge identity conflict')
        ts = int(time.time())
        if not row:
            db.add(
                Knowledge(
                    id=kb,
                    user_id=vault.owner_id,
                    name=name,
                    description='Kept in sync with the notes of this vault. Edit the notes in Notes, not here.',
                    meta={'gnos3_notes_vault': vault.id},
                    created_at=ts,
                    updated_at=ts,
                )
            )
            await db.commit()
        elif row.name != name:
            row.name = name
            row.updated_at = ts
            await db.commit()
    settings = vault.settings or {}
    if not (settings.get('ai') or {}).get('knowledge'):
        await vaults.update_vault(vault, settings={**settings, 'ai': {**(settings.get('ai') or {}), 'knowledge': True}})
    await sync_access(vault)
    return kb


async def sync_access(vault: NoteVaultModel) -> None:
    """The base reads like the vault: its groups read it (writing happens in Notes only)."""
    if vault.kind != 'shared':
        await AccessGrants.set_access_grants('knowledge', knowledge_id(vault.id), [])
        return
    grants = await AccessGrants.get_grants_by_resource('note_vault', vault.id)
    readers = {(g.principal_type, g.principal_id) for g in grants}
    await AccessGrants.set_access_grants(
        'knowledge',
        knowledge_id(vault.id),
        [{'principal_type': t, 'principal_id': i, 'permission': 'read'} for t, i in sorted(readers)],
    )


async def delete_knowledge(vault_id: str) -> None:
    from open_webui.retrieval.vector.factory import VECTOR_DB_CLIENT

    kb = knowledge_id(vault_id)
    if not await Knowledges.get_knowledge_by_id(kb):
        return
    for file in await Knowledges.get_files_by_id(kb):
        await _drop_file(kb, file.id)
    try:
        await asyncio.to_thread(VECTOR_DB_CLIENT.delete_collection, collection_name=kb)
    except Exception:
        pass
    await Knowledges.delete_knowledge_by_id(kb)


async def _drop_file(kb: str, file_id: str) -> None:
    from open_webui.retrieval.vector.factory import VECTOR_DB_CLIENT

    await Knowledges.remove_file_from_knowledge_by_id(kb, file_id)
    try:
        await asyncio.to_thread(VECTOR_DB_CLIENT.delete, collection_name=kb, filter={'file_id': file_id})
    except Exception:
        pass
    try:
        await asyncio.to_thread(VECTOR_DB_CLIENT.delete_collection, collection_name=f'file-{file_id}')
    except Exception:
        pass
    await Files.delete_file_by_id(file_id)


def _embed(request: Request, kb: str, file_id: str, title: str, text: str, owner_id: str, note_id: str) -> None:
    """Runs in a thread: save_docs_to_vector_db blocks on the event loop it was started from."""
    from langchain_core.documents import Document

    from open_webui.retrieval.vector.factory import VECTOR_DB_CLIENT
    from open_webui.routers.retrieval import save_docs_to_vector_db

    metadata = {
        'name': title,
        'file_id': file_id,
        'source': title,
        'created_by': owner_id,
        'note_id': note_id,
    }
    try:
        VECTOR_DB_CLIENT.delete(collection_name=kb, filter={'file_id': file_id})
    except Exception:
        pass
    docs = [Document(page_content=text, metadata=metadata)]
    save_docs_to_vector_db(
        request,
        docs=docs,
        collection_name=f'file-{file_id}',
        metadata={'file_id': file_id},
        overwrite=True,
        split=True,
        add=False,
    )
    save_docs_to_vector_db(
        request, docs=docs, collection_name=kb, metadata={'file_id': file_id}, overwrite=False, split=True, add=True
    )


async def sync_vault(
    request: Request, vault: NoteVaultModel, limit: Optional[int] = BATCH, only: Optional[set] = None
) -> dict:
    """Embed the notes that changed since their last embedding (at most `limit`, only the notes
    in `only` when given); drop the ones that left the vault.
    Returns {'knowledge_id', 'synced', 'pending'}."""
    lock = _locks.setdefault(vault.id, asyncio.Lock())
    async with lock:
        kb = await ensure_knowledge(vault)
        files = {f.id: f for f in await Knowledges.get_files_by_id(kb)}
        async with get_async_db_context() as db:
            rows = (
                await db.execute(
                    select(Note.id, Note.title, Note.updated_at)
                    .join(NotePlacement, NotePlacement.note_id == Note.id)
                    .where(NotePlacement.vault_id == vault.id)
                    .order_by(Note.updated_at.desc())
                )
            ).all()
        present = set()
        todo = []
        for note_id, title, updated_at in rows:
            file_id = note_file_id(note_id)
            present.add(file_id)
            file = files.get(file_id)
            if only is not None and note_id not in only:
                continue
            if not file or (file.meta or {}).get('note_updated_at') != updated_at:
                todo.append((note_id, file_id))
        for file_id in set(files) - present:
            await _drop_file(kb, file_id)

        batch = todo if limit is None else todo[:limit]
        loop = asyncio.get_running_loop()
        synced = 0
        for note_id, file_id in batch:
            async with get_async_db_context() as db:
                note = await db.get(Note, note_id)
                if not note:
                    continue
                data = note.data if isinstance(note.data, dict) else {}
                title = note.title or 'Untitled'
                updated_at = note.updated_at
            md = (data.get('content') or {}).get('md') or ''
            text = note_text(title, data.get('properties') or {}, md)
            meta = {
                'name': f'{title}.md',
                'content_type': 'text/markdown',
                'source': f'/notes/{note_id}',
                'note_id': note_id,
                'note_vault_id': vault.id,
                'note_updated_at': updated_at,
            }
            async with get_async_db_context() as db:
                row = await db.get(File, file_id)
                if row:
                    row.filename = f'{title}.md'
                    row.meta = meta
                    row.data = {**(row.data or {}), 'content': text, 'status': 'processing'}
                    row.updated_at = int(time.time())
                    await db.commit()
            if not row:
                await Files.insert_new_file(
                    vault.owner_id,
                    FileForm(
                        id=file_id,
                        filename=f'{title}.md',
                        path='',
                        data={'content': text, 'status': 'processing'},
                        meta=meta,
                    ),
                )
            if not await Knowledges.has_file(kb, file_id):
                await Knowledges.add_file_to_knowledge_by_id(kb, file_id, vault.owner_id)
            try:
                if text.strip():
                    await loop.run_in_executor(
                        _executor, _embed, request, kb, file_id, title, text, vault.owner_id, note_id
                    )
                await Files.update_file_data_by_id(file_id, {'status': 'completed'})
                synced += 1
            except Exception as e:
                log.warning('Notes knowledge: embedding note %s failed: %s', note_id, e)
                # Leave note_updated_at unset so the next pass tries again.
                async with get_async_db_context() as db:
                    row = await db.get(File, file_id)
                    if row:
                        row.meta = {**(row.meta or {}), 'note_updated_at': None}
                        await db.commit()
        return {'knowledge_id': kb, 'synced': synced, 'pending': max(0, len(todo) - len(batch))}


async def scope_collections(vault: NoteVaultModel, note_ids: list[str]) -> list[str]:
    """`file-<id>` collections of these notes (their embeddings must exist: see sync_vault)."""
    return [f'file-{note_file_id(note_id)}' for note_id in note_ids]


async def note_vault_knowledge_worker(app) -> None:
    """Keeps the knowledge bases of vaults used in chat current."""
    await asyncio.sleep(20)
    while True:
        try:
            async with get_async_db_context() as db:
                rows = (await db.execute(select(NoteVault))).scalars().all()
                used = [
                    NoteVaultModel.model_validate(r)
                    for r in rows
                    if ((r.settings or {}).get('ai') or {}).get('knowledge')
                ]
            for vault in used:
                try:
                    await sync_vault(mock_request(app), vault)
                except Exception as e:
                    log.warning('Notes knowledge: syncing vault %s failed: %s', vault.id, e)
        except Exception as e:
            log.warning('Notes knowledge worker: %s', e)
        await asyncio.sleep(POLL_SECONDS)
