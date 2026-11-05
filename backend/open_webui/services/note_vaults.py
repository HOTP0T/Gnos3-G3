"""Notes vaults: access, placement, the link index, graph, backlinks, search, import / export.

How it fits on upstream's notes (models/notes.py, routers/notes.py, socket/main.py):

- A note's content, title, sharing and live co-editing stay upstream's. This module only adds where
  the note sits (vault, folder), its properties (`note.data['properties']`) and what it links to.
- **Shared vaults hand their access to their notes**: every note in a shared vault carries the
  vault's grants as its own `access_grant` rows (resource_type 'note'; write also grants read). So
  upstream's checks (opening a note, co-editing, attaching it in chat) answer correctly without a
  hook. `mirror_vault_grants()` keeps them equal; it runs when the vault's access changes, when a
  note enters or leaves the vault, and for every note the index rebuilds.
- **The index is rebuilt lazily**: reading a vault (tree, graph, links, search) re-reads every note
  whose `updated_at` differs from what was indexed. Edits made anywhere (editor, socket save, chat,
  API) are therefore picked up without hooks in upstream's save paths.
"""

from __future__ import annotations

import asyncio
import io
import logging
import re
import time
import uuid
import zipfile
import base64
from collections import defaultdict
from types import SimpleNamespace
from typing import Iterable, Optional

from sqlalchemy import and_, delete, func, or_, select

from open_webui.internal.db import get_async_db_context
from open_webui.models.access_grants import AccessGrant, AccessGrants, normalize_access_grants
from open_webui.models.groups import Groups
from open_webui.models.note_vaults import (
    NoteFolder,
    NoteIndex,
    NoteLink,
    NotePlacement,
    NoteVault,
    NoteVaultModel,
    now_ns,
)
from open_webui.models.notes import Note, NoteForm, NoteModel, Notes
from open_webui.utils import note_content as nc

log = logging.getLogger(__name__)

ADMIN_ROLES = ('admin', 'superadmin')
PERSONAL_NS = 'gnos3-notes-personal:'

# Graph colours are the design system's chart tokens (--chart-1 … --chart-5), resolved by the page.
DEFAULT_TYPES: list[dict] = [
    {
        'key': 'person',
        'name': 'Person',
        'icon': 'user',
        'color': 'chart-1',
        'builtin': True,
        'fields': [
            {'key': 'role', 'label': 'Role', 'kind': 'text'},
            {'key': 'organisation', 'label': 'Organisation', 'kind': 'note', 'note_type': 'organisation'},
            {'key': 'email', 'label': 'Email', 'kind': 'text'},
            {'key': 'phone', 'label': 'Phone', 'kind': 'text'},
        ],
    },
    {
        'key': 'organisation',
        'name': 'Organisation',
        'icon': 'building-2',
        'color': 'chart-2',
        'builtin': True,
        'fields': [
            {'key': 'website', 'label': 'Website', 'kind': 'url'},
            {'key': 'company', 'label': 'Company in Accounting', 'kind': 'entity', 'entity_type': 'company'},
        ],
    },
    {
        'key': 'project',
        'name': 'Project',
        'icon': 'folder-kanban',
        'color': 'chart-3',
        'builtin': True,
        'fields': [
            {
                'key': 'status',
                'label': 'Status',
                'kind': 'select',
                'options': ['Planned', 'Active', 'On hold', 'Done'],
            },
            {'key': 'owner', 'label': 'Owner', 'kind': 'note', 'note_type': 'person'},
            {'key': 'start', 'label': 'Start', 'kind': 'date'},
            {'key': 'due', 'label': 'Due', 'kind': 'date'},
            {'key': 'related', 'label': 'Related', 'kind': 'notes'},
        ],
    },
    {
        'key': 'meeting',
        'name': 'Meeting',
        'icon': 'calendar-days',
        'color': 'chart-4',
        'builtin': True,
        'fields': [
            {'key': 'date', 'label': 'Date', 'kind': 'date'},
            {'key': 'attendees', 'label': 'Attendees', 'kind': 'notes', 'note_type': 'person'},
            {'key': 'project', 'label': 'Project', 'kind': 'note', 'note_type': 'project'},
        ],
    },
    {
        'key': 'topic',
        'name': 'Topic',
        'icon': 'lightbulb',
        'color': 'chart-5',
        'builtin': True,
        'fields': [],
    },
]

FIELD_KINDS = ('text', 'number', 'date', 'checkbox', 'select', 'multiselect', 'url', 'note', 'notes', 'entity')


def default_settings() -> dict:
    return {
        'daily': {'folder': 'Daily notes', 'format': 'YYYY-MM-DD', 'template_id': None},
        'templates_folder': 'Templates',
        'types': [dict(t, fields=[dict(f) for f in t['fields']]) for t in DEFAULT_TYPES],
        'ai': {'knowledge': False},
    }


def vault_settings(vault: NoteVaultModel) -> dict:
    """Stored settings over the defaults (a vault created before a new setting existed gets it)."""
    settings = default_settings()
    stored = vault.settings or {}
    for key, value in stored.items():
        if isinstance(value, dict) and isinstance(settings.get(key), dict):
            settings[key] = {**settings[key], **value}
        else:
            settings[key] = value
    return settings


def is_admin(user) -> bool:
    return getattr(user, 'role', None) in ADMIN_ROLES


def personal_vault_id(user_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, PERSONAL_NS + user_id))


# ---------------------------------------------------------------------------
# Vaults and access
# ---------------------------------------------------------------------------

PERMISSION_RANK = {None: 0, 'read': 1, 'write': 2, 'manage': 3}


def satisfies(have: Optional[str], need: str) -> bool:
    return PERMISSION_RANK.get(have, 0) >= PERMISSION_RANK[need]


async def get_vault(vault_id: str, db=None) -> Optional[NoteVaultModel]:
    async with get_async_db_context(db) as db:
        row = await db.get(NoteVault, vault_id)
        return NoteVaultModel.model_validate(row) if row else None


async def ensure_personal_vault(user, db=None) -> NoteVaultModel:
    vault_id = personal_vault_id(user.id)
    async with get_async_db_context(db) as db:
        row = await db.get(NoteVault, vault_id)
        if not row:
            ts = now_ns()
            row = NoteVault(
                id=vault_id,
                kind='personal',
                owner_id=user.id,
                name='My notes',
                settings=None,
                created_at=ts,
                updated_at=ts,
            )
            db.add(row)
            try:
                await db.commit()
            except Exception:
                # Two first requests at once: the other one created it.
                await db.rollback()
                row = await db.get(NoteVault, vault_id)
        vault = NoteVaultModel.model_validate(row)
    await adopt_notes(user.id, vault.id)
    return vault


async def adopt_notes(user_id: str, vault_id: str, db=None) -> int:
    """Notes of `user_id` that sit in no vault yet (made before vaults, or through upstream's
    /notes/create, e.g. from chat) go to the root of their personal vault."""
    async with get_async_db_context(db) as db:
        result = await db.execute(
            select(Note.id).where(
                Note.user_id == user_id,
                ~Note.id.in_(select(NotePlacement.note_id)),
            )
        )
        ids = [row[0] for row in result.all()]
        if not ids:
            return 0
        ts = now_ns()
        for note_id in ids:
            db.add(NotePlacement(note_id=note_id, vault_id=vault_id, folder='', updated_at=ts))
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            return 0
        return len(ids)


async def vault_permission(user, vault: NoteVaultModel, user_group_ids: Optional[set] = None) -> Optional[str]:
    """'manage' | 'write' | 'read' | None."""
    if vault.kind == 'personal':
        return 'manage' if vault.owner_id == user.id else None
    if is_admin(user):
        return 'manage'
    if await AccessGrants.has_access(user.id, 'note_vault', vault.id, 'write', user_group_ids=user_group_ids):
        return 'write'
    if await AccessGrants.has_access(user.id, 'note_vault', vault.id, 'read', user_group_ids=user_group_ids):
        return 'read'
    return None


async def list_vaults(user) -> list[tuple[NoteVaultModel, str]]:
    personal = await ensure_personal_vault(user)
    out = [(personal, 'manage')]
    group_ids = {g.id for g in await Groups.get_groups_by_member_id(user.id)}
    async with get_async_db_context() as db:
        result = await db.execute(select(NoteVault).where(NoteVault.kind == 'shared').order_by(NoteVault.name))
        shared = [NoteVaultModel.model_validate(row) for row in result.scalars().all()]
    for vault in shared:
        permission = await vault_permission(user, vault, group_ids)
        if permission:
            out.append((vault, permission))
    return out


async def vault_counts(vault_ids: list[str]) -> dict[str, int]:
    if not vault_ids:
        return {}
    async with get_async_db_context() as db:
        result = await db.execute(
            select(NotePlacement.vault_id, func.count())
            .join(Note, Note.id == NotePlacement.note_id)
            .where(NotePlacement.vault_id.in_(vault_ids))
            .group_by(NotePlacement.vault_id)
        )
        return {vault_id: count for vault_id, count in result.all()}


async def create_shared_vault(
    user,
    name: str,
    description: Optional[str],
    color: Optional[str],
    icon: Optional[str],
    access_grants: Optional[list],
) -> NoteVaultModel:
    ts = now_ns()
    vault_id = str(uuid.uuid4())
    async with get_async_db_context() as db:
        db.add(
            NoteVault(
                id=vault_id,
                kind='shared',
                owner_id=user.id,
                name=name.strip()[:120] or 'Shared notes',
                description=(description or '').strip()[:500] or None,
                color=color,
                icon=icon,
                settings=None,
                created_at=ts,
                updated_at=ts,
            )
        )
        await db.commit()
    await AccessGrants.set_access_grants('note_vault', vault_id, vault_grants_only_groups(access_grants))
    return await get_vault(vault_id)


def vault_grants_only_groups(access_grants: Optional[list]) -> list[dict]:
    """A shared vault is shared with groups (and named users); never with everyone ('*')."""
    return [
        grant
        for grant in normalize_access_grants(access_grants)
        if grant['principal_id'] != '*' and grant['permission'] in ('read', 'write')
    ]


async def update_vault(vault: NoteVaultModel, **fields) -> NoteVaultModel:
    async with get_async_db_context() as db:
        row = await db.get(NoteVault, vault.id)
        for key, value in fields.items():
            if value is not None:
                setattr(row, key, value)
        row.updated_at = now_ns()
        await db.commit()
    return await get_vault(vault.id)


async def set_vault_grants(vault: NoteVaultModel, access_grants: Optional[list]) -> list:
    grants = await AccessGrants.set_access_grants('note_vault', vault.id, vault_grants_only_groups(access_grants))
    await mirror_vault_grants(vault)
    return grants


def _note_grants_for(vault_grants: Iterable) -> list[tuple[str, str, str]]:
    """Vault grants as note grants: write also reads (upstream checks each permission separately)."""
    out = set()
    for grant in vault_grants:
        principal_type = grant.principal_type if hasattr(grant, 'principal_type') else grant['principal_type']
        principal_id = grant.principal_id if hasattr(grant, 'principal_id') else grant['principal_id']
        permission = grant.permission if hasattr(grant, 'permission') else grant['permission']
        out.add((principal_type, principal_id, 'read'))
        if permission == 'write':
            out.add((principal_type, principal_id, 'write'))
    return sorted(out)


async def mirror_vault_grants(vault: NoteVaultModel, note_ids: Optional[list[str]] = None, db=None) -> None:
    """Give the notes of a shared vault exactly the vault's access (all its notes, or `note_ids`)."""
    if vault.kind != 'shared':
        return
    grants = _note_grants_for(await AccessGrants.get_grants_by_resource('note_vault', vault.id))
    async with get_async_db_context(db) as db:
        if note_ids is None:
            result = await db.execute(select(NotePlacement.note_id).where(NotePlacement.vault_id == vault.id))
            note_ids = [row[0] for row in result.all()]
        for start in range(0, len(note_ids), 200):
            chunk = note_ids[start : start + 200]
            await db.execute(
                delete(AccessGrant).where(AccessGrant.resource_type == 'note', AccessGrant.resource_id.in_(chunk))
            )
            ts = int(time.time())
            for note_id in chunk:
                for principal_type, principal_id, permission in grants:
                    db.add(
                        AccessGrant(
                            id=str(uuid.uuid4()),
                            resource_type='note',
                            resource_id=note_id,
                            principal_type=principal_type,
                            principal_id=principal_id,
                            permission=permission,
                            created_at=ts,
                        )
                    )
        await db.commit()


async def clear_note_grants(note_id: str) -> None:
    await AccessGrants.set_access_grants('note', note_id, [])


async def delete_shared_vault(vault: NoteVaultModel) -> int:
    """Deletes the vault, its folders and every note in it."""
    async with get_async_db_context() as db:
        result = await db.execute(select(NotePlacement.note_id).where(NotePlacement.vault_id == vault.id))
        note_ids = [row[0] for row in result.all()]
    for note_id in note_ids:
        await Notes.delete_note_by_id(note_id)
    async with get_async_db_context() as db:
        for model in (NotePlacement, NoteIndex, NoteLink):
            await db.execute(delete(model).where(model.vault_id == vault.id))
        await db.execute(delete(NoteFolder).where(NoteFolder.vault_id == vault.id))
        await db.execute(delete(NoteVault).where(NoteVault.id == vault.id))
        await db.commit()
    await AccessGrants.revoke_all_access('note_vault', vault.id)
    return len(note_ids)


# ---------------------------------------------------------------------------
# Notes in vaults
# ---------------------------------------------------------------------------


async def note_placement(note_id: str, db=None) -> Optional[NotePlacement]:
    async with get_async_db_context(db) as db:
        return await db.get(NotePlacement, note_id)


async def vault_of_note(note: NoteModel) -> NoteVaultModel:
    placement = await note_placement(note.id)
    if placement:
        vault = await get_vault(placement.vault_id)
        if vault:
            return vault
    # Not placed yet: its owner's personal vault.
    vault_id = personal_vault_id(note.user_id)
    vault = await get_vault(vault_id)
    if vault is None:
        vault = await ensure_personal_vault(SimpleNamespace(id=note.user_id))
    else:
        await adopt_notes(note.user_id, vault_id)
    return vault


async def can_read_note(user, note: NoteModel) -> bool:
    return is_admin(user) or note.user_id == user.id or await AccessGrants.has_access(user.id, 'note', note.id, 'read')


async def can_write_note(user, note: NoteModel) -> bool:
    return is_admin(user) or note.user_id == user.id or await AccessGrants.has_access(user.id, 'note', note.id, 'write')


async def ensure_folder(vault_id: str, path: str, db=None) -> None:
    path = nc.clean_folder(path)
    if not path:
        return
    async with get_async_db_context(db) as db:
        existing = set(
            row[0]
            for row in (
                await db.execute(
                    select(NoteFolder.path).where(
                        NoteFolder.vault_id == vault_id, NoteFolder.path.in_(nc.folder_parents(path))
                    )
                )
            ).all()
        )
        ts = now_ns()
        for parent in nc.folder_parents(path):
            if parent not in existing:
                db.add(NoteFolder(vault_id=vault_id, path=parent, created_at=ts))
        await db.commit()


async def unique_title(vault_id: str, title: str, exclude_note_id: Optional[str] = None) -> str:
    """`title`, or `title 2`, `title 3`… so a new note never shadows an existing one in [[links]]."""
    base = nc.clean_title(title) or 'Untitled'
    async with get_async_db_context() as db:
        stmt = (
            select(Note.title)
            .join(NotePlacement, NotePlacement.note_id == Note.id)
            .where(NotePlacement.vault_id == vault_id)
        )
        if exclude_note_id:
            stmt = stmt.where(Note.id != exclude_note_id)
        taken = {nc.normalize_title(row[0]) for row in (await db.execute(stmt)).all()}
    if nc.normalize_title(base) not in taken:
        return base
    n = 2
    while nc.normalize_title(f'{base} {n}') in taken:
        n += 1
    return f'{base} {n}'


async def create_note(
    user,
    vault: NoteVaultModel,
    title: str,
    folder: str = '',
    md: str = '',
    properties: Optional[dict] = None,
    files: Optional[list] = None,
    unique: bool = True,
    html: str = '',
) -> NoteModel:
    """A note in `vault`/`folder`. The body is Markdown; the editor turns it into its own format
    the first time the note is opened (note.data.content.json stays empty until then)."""
    folder = nc.clean_folder(folder)
    title = await unique_title(vault.id, title) if unique else (nc.clean_title(title) or 'Untitled')
    data = {
        'content': {'json': None, 'html': html or '', 'md': md or ''},
        'versions': [],
        'files': files or None,
        'properties': clean_properties(properties or {}),
    }
    note = await Notes.insert_new_note(user.id, NoteForm(title=title, data=data, meta=None, access_grants=[]))
    async with get_async_db_context() as db:
        db.add(NotePlacement(note_id=note.id, vault_id=vault.id, folder=folder, updated_at=now_ns()))
        await db.commit()
    await ensure_folder(vault.id, folder)
    if vault.kind == 'shared':
        await mirror_vault_grants(vault, [note.id])
    await index_notes(vault, [note.id])
    return note


async def place_note(note: NoteModel, vault: NoteVaultModel, folder: str) -> None:
    folder = nc.clean_folder(folder)
    async with get_async_db_context() as db:
        row = await db.get(NotePlacement, note.id)
        previous_vault = row.vault_id if row else None
        if row:
            row.vault_id = vault.id
            row.folder = folder
            row.updated_at = now_ns()
        else:
            db.add(NotePlacement(note_id=note.id, vault_id=vault.id, folder=folder, updated_at=now_ns()))
        await db.commit()
    await ensure_folder(vault.id, folder)
    if previous_vault != vault.id:
        if vault.kind == 'shared':
            await mirror_vault_grants(vault, [note.id])
        else:
            # Back in a personal vault: only its owner (and whom they share it with later).
            await clear_note_grants(note.id)
        async with get_async_db_context() as db:
            await db.execute(delete(NoteLink).where(NoteLink.source_id == note.id))
            await db.execute(delete(NoteIndex).where(NoteIndex.note_id == note.id))
            await db.commit()
        await index_notes(vault, [note.id])


def clean_properties(properties: dict) -> dict:
    """Property values as stored: JSON-safe, no empty values, tags and aliases normalised."""
    out: dict = {}
    for key, value in (properties or {}).items():
        key = str(key).strip()[:80]
        if not key or key == 'title':
            continue
        if key == 'tags':
            tags = nc.property_tags({'tags': value})
            if tags:
                out['tags'] = nc.dedupe(tags)
            continue
        if key == 'aliases':
            aliases = nc.property_aliases({'aliases': value})
            if aliases:
                out['aliases'] = nc.dedupe(aliases)
            continue
        if key == 'type':
            if value:
                out['type'] = str(value).strip()[:60]
            continue
        if value in (None, '', [], {}):
            continue
        out[key] = value
    return out


async def update_note_meta(
    note: NoteModel, title: Optional[str] = None, properties: Optional[dict] = None, files: Optional[list] = None
) -> NoteModel:
    """Rename and / or replace the properties. A rename rewrites [[Old title]] in notes that are
    still plain Markdown (notes saved by the editor link by id and show the new title themselves)."""
    from open_webui.models.notes import NoteUpdateForm

    vault = await vault_of_note(note)
    form: dict = {}
    renamed_from = None
    if title is not None:
        new_title = nc.clean_title(title) or 'Untitled'
        if new_title != note.title:
            renamed_from = note.title
            form['title'] = new_title
    data: dict = {}
    if properties is not None:
        data['properties'] = clean_properties(properties)
    if files is not None:
        data['files'] = [f for f in files if isinstance(f, dict)] or None
    if data:
        form['data'] = data
    if not form:
        return note
    updated = await Notes.update_note_by_id(note.id, NoteUpdateForm(**form))
    if renamed_from is not None:
        await rewrite_links_after_rename(vault, note.id, renamed_from, form['title'])
    await index_notes(vault, [note.id])
    return updated


async def rewrite_links_after_rename(vault: NoteVaultModel, note_id: str, old_title: str, new_title: str) -> None:
    from open_webui.models.notes import NoteUpdateForm

    old_key = nc.normalize_title(old_title)
    async with get_async_db_context() as db:
        result = await db.execute(
            select(NoteLink.source_id)
            .where(
                NoteLink.vault_id == vault.id,
                or_(NoteLink.target_id == note_id, NoteLink.target_key == old_key),
            )
            .distinct()
        )
        sources = [row[0] for row in result.all() if row[0] != note_id]
    for source_id in sources:
        source = await Notes.get_note_by_id(source_id)
        if not source:
            continue
        content = (source.data or {}).get('content') or {}
        if content.get('json'):
            continue  # links by id; the editor shows the current title
        md = content.get('md') or ''
        new_md = nc.markdown_with_link_titles(md, {old_key: new_title})
        if new_md != md:
            await Notes.update_note_by_id(
                source_id, NoteUpdateForm(data={'content': {**content, 'md': new_md, 'html': ''}})
            )


# ---------------------------------------------------------------------------
# Folders
# ---------------------------------------------------------------------------


async def rename_folder(vault: NoteVaultModel, old: str, new: str) -> int:
    old = nc.clean_folder(old)
    new = nc.clean_folder(new)
    if not old or old == new:
        return 0
    if new == old or new.startswith(old + '/'):
        raise ValueError('A folder cannot move into itself.')
    moved = 0
    async with get_async_db_context() as db:
        result = await db.execute(
            select(NotePlacement).where(
                NotePlacement.vault_id == vault.id,
                or_(NotePlacement.folder == old, NotePlacement.folder.like(old.replace('%', r'\%') + '/%')),
            )
        )
        for row in result.scalars().all():
            if row.folder == old or row.folder.startswith(old + '/'):
                row.folder = (new + row.folder[len(old) :]).strip('/')
                row.updated_at = now_ns()
                moved += 1
        folders = await db.execute(select(NoteFolder).where(NoteFolder.vault_id == vault.id))
        existing = {f.path for f in folders.scalars().all()}
        renamed = {p for p in existing if p == old or p.startswith(old + '/')}
        if renamed:
            await db.execute(delete(NoteFolder).where(NoteFolder.vault_id == vault.id, NoteFolder.path.in_(renamed)))
        ts = now_ns()
        targets = {(new + p[len(old) :]).strip('/') for p in renamed} | set(nc.folder_parents(new))
        for path in sorted(targets):
            if path and path not in (existing - renamed):
                db.add(NoteFolder(vault_id=vault.id, path=path, created_at=ts))
        await db.commit()
    return moved


async def delete_folder(vault: NoteVaultModel, path: str, mode: str) -> int:
    """mode 'move_up': notes and subfolders go to the parent folder. mode 'delete': its notes are
    deleted (the caller checked write access to the vault)."""
    path = nc.clean_folder(path)
    if not path:
        return 0
    parent = path.rsplit('/', 1)[0] if '/' in path else ''
    count = 0
    async with get_async_db_context() as db:
        result = await db.execute(
            select(NotePlacement).where(
                NotePlacement.vault_id == vault.id,
                or_(NotePlacement.folder == path, NotePlacement.folder.like(path.replace('%', r'\%') + '/%')),
            )
        )
        rows = [r for r in result.scalars().all() if r.folder == path or r.folder.startswith(path + '/')]
        note_ids = [r.note_id for r in rows]
        if mode == 'move_up':
            for row in rows:
                row.folder = (parent + '/' + row.folder[len(path) :].strip('/')).strip('/')
                row.updated_at = now_ns()
        folders = await db.execute(select(NoteFolder).where(NoteFolder.vault_id == vault.id))
        all_paths = {f.path for f in folders.scalars().all()}
        under = {p for p in all_paths if p == path or p.startswith(path + '/')}
        await db.execute(delete(NoteFolder).where(NoteFolder.vault_id == vault.id, NoteFolder.path.in_(under)))
        if mode == 'move_up':
            ts = now_ns()
            for p in sorted(under - {path}):
                moved = (parent + '/' + p[len(path) :].strip('/')).strip('/')
                if moved and moved not in all_paths:
                    db.add(NoteFolder(vault_id=vault.id, path=moved, created_at=ts))
        await db.commit()
    if mode == 'delete':
        for note_id in note_ids:
            await Notes.delete_note_by_id(note_id)
            count += 1
        async with get_async_db_context() as db:
            await db.execute(delete(NotePlacement).where(NotePlacement.note_id.in_(note_ids)))
            await db.execute(delete(NoteIndex).where(NoteIndex.note_id.in_(note_ids)))
            await db.execute(delete(NoteLink).where(NoteLink.source_id.in_(note_ids)))
            await db.commit()
    else:
        count = len(note_ids)
    return count


# ---------------------------------------------------------------------------
# The index
# ---------------------------------------------------------------------------

_index_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)


def _md_expr():
    return Note.data[('content', 'md')].as_string()


async def refresh_index(vault: NoteVaultModel) -> int:
    """Re-read every note of the vault that changed since it was indexed; forget deleted notes."""
    async with _index_locks[vault.id]:
        if vault.kind == 'personal' and vault.owner_id:
            await adopt_notes(vault.owner_id, vault.id)
        async with get_async_db_context() as db:
            # Placements of deleted notes, index rows of notes that left the vault.
            await db.execute(
                delete(NotePlacement).where(
                    NotePlacement.vault_id == vault.id, ~NotePlacement.note_id.in_(select(Note.id))
                )
            )
            in_vault = select(NotePlacement.note_id).where(NotePlacement.vault_id == vault.id)
            await db.execute(delete(NoteIndex).where(NoteIndex.vault_id == vault.id, ~NoteIndex.note_id.in_(in_vault)))
            await db.execute(delete(NoteLink).where(NoteLink.vault_id == vault.id, ~NoteLink.source_id.in_(in_vault)))
            await db.commit()

            result = await db.execute(
                select(Note.id, Note.updated_at, NoteIndex.note_updated_at, NoteIndex.vault_id)
                .join(NotePlacement, NotePlacement.note_id == Note.id)
                .outerjoin(NoteIndex, NoteIndex.note_id == Note.id)
                .where(NotePlacement.vault_id == vault.id)
            )
            stale = [
                note_id
                for note_id, updated_at, indexed_from, indexed_vault in result.all()
                if indexed_from is None or indexed_from != updated_at or indexed_vault != vault.id
            ]
        if stale:
            await _index(vault, stale)
        return len(stale)


async def index_notes(vault: NoteVaultModel, note_ids: list[str]) -> None:
    async with _index_locks[vault.id]:
        await _index(vault, note_ids)


async def _title_map(vault_id: str, db) -> dict[str, str]:
    """normalized title / alias -> note id (the most recently updated wins a tie)."""
    result = await db.execute(
        select(NoteIndex.note_id, NoteIndex.title_key, NoteIndex.aliases)
        .join(Note, Note.id == NoteIndex.note_id)
        .where(NoteIndex.vault_id == vault_id)
        .order_by(Note.updated_at.asc())
    )
    mapping: dict[str, str] = {}
    aliases: dict[str, str] = {}
    for note_id, key, note_aliases in result.all():
        if key:
            mapping[key] = note_id
        for alias in note_aliases or []:
            aliases.setdefault(nc.normalize_title(alias), note_id)
    for key, note_id in aliases.items():
        mapping.setdefault(key, note_id)
    return mapping


async def _index(vault: NoteVaultModel, note_ids: list[str]) -> None:
    for start in range(0, len(note_ids), 100):
        chunk = note_ids[start : start + 100]
        async with get_async_db_context() as db:
            result = await db.execute(select(Note.id, Note.title, Note.data, Note.updated_at).where(Note.id.in_(chunk)))
            notes = result.all()
            found = {row[0] for row in notes}
            # First the index rows (titles, aliases), so links between notes of this chunk resolve.
            parsed = {}
            ts = now_ns()
            for note_id, title, data, updated_at in notes:
                data = data if isinstance(data, dict) else {}
                properties = data.get('properties') or {}
                content = nc.read_note_content(data)
                tags = nc.dedupe(nc.property_tags(properties) + content['tags'])
                aliases = nc.property_aliases(properties)
                parsed[note_id] = (title, properties, content)
                row = await db.get(NoteIndex, note_id)
                values = dict(
                    vault_id=vault.id,
                    title=title or '',
                    title_key=nc.normalize_title(title),
                    note_type=(str(properties.get('type')).strip() or None) if properties.get('type') else None,
                    tags=tags,
                    aliases=aliases,
                    word_count=nc.word_count(content['text']),
                    excerpt=nc.excerpt(content['text']),
                    note_updated_at=updated_at,
                    indexed_at=ts,
                )
                if row:
                    for key, value in values.items():
                        setattr(row, key, value)
                else:
                    db.add(NoteIndex(note_id=note_id, **values))
            await db.flush()
            titles = await _title_map(vault.id, db)

            await db.execute(delete(NoteLink).where(NoteLink.source_id.in_(chunk)))
            for note_id, (title, properties, content) in parsed.items():
                seen = set()
                for link in content['links']:
                    key = nc.normalize_title(link['title'])
                    target = link.get('note_id') or titles.get(key)
                    marker = ('link', target or key)
                    if marker in seen:
                        continue
                    seen.add(marker)
                    db.add(
                        NoteLink(
                            vault_id=vault.id,
                            source_id=note_id,
                            kind='link',
                            target_id=target,
                            target_key=key or None,
                            target_title=link['title'] or None,
                            label=link.get('alias'),
                            context=(link.get('context') or '')[:300] or None,
                        )
                    )
                for prop_key, value in properties.items():
                    if prop_key in ('type', 'tags', 'aliases'):
                        continue
                    for ref in nc.property_note_refs(value):
                        key = nc.normalize_title(ref['title'])
                        target = ref['note_id'] or titles.get(key)
                        marker = ('property', prop_key, target or key)
                        if marker in seen:
                            continue
                        seen.add(marker)
                        db.add(
                            NoteLink(
                                vault_id=vault.id,
                                source_id=note_id,
                                kind='property',
                                target_id=target,
                                target_key=key or None,
                                target_title=ref['title'] or None,
                                property_key=prop_key,
                            )
                        )
                    values = value if isinstance(value, list) else [value]
                    for item in values:
                        if (
                            isinstance(item, dict)
                            and item.get('entity_type') in nc.ENTITY_TYPES
                            and item.get('entity_id')
                        ):
                            marker = ('entity', item['entity_type'], str(item['entity_id']))
                            if marker in seen:
                                continue
                            seen.add(marker)
                            db.add(
                                NoteLink(
                                    vault_id=vault.id,
                                    source_id=note_id,
                                    kind='entity',
                                    entity_type=item['entity_type'],
                                    entity_id=str(item['entity_id']),
                                    label=item.get('label'),
                                    property_key=prop_key,
                                )
                            )
                for entity in content['entities']:
                    marker = ('entity', entity['entity_type'], entity['entity_id'])
                    if marker in seen:
                        continue
                    seen.add(marker)
                    db.add(
                        NoteLink(
                            vault_id=vault.id,
                            source_id=note_id,
                            kind='entity',
                            entity_type=entity['entity_type'],
                            entity_id=entity['entity_id'],
                            label=entity.get('label'),
                            context=(entity.get('context') or '')[:300] or None,
                        )
                    )
            gone = [note_id for note_id in chunk if note_id not in found]
            if gone:
                await db.execute(delete(NoteIndex).where(NoteIndex.note_id.in_(gone)))
            await db.commit()
        if vault.kind == 'shared':
            # Re-applies the vault's access to these notes (a per-note share changed elsewhere does not stick).
            await mirror_vault_grants(vault, [n for n in chunk if n in found])


# ---------------------------------------------------------------------------
# Reading a vault
# ---------------------------------------------------------------------------


async def vault_tree(vault: NoteVaultModel, user_id: str) -> dict:
    """Every folder and every note's summary: what the sidebar, quick switcher and tags need.
    Pinning is per person (upstream's pinned_note), so `is_pinned` is this reader's."""
    await refresh_index(vault)
    async with get_async_db_context() as db:
        folders = [
            row[0]
            for row in (
                await db.execute(
                    select(NoteFolder.path).where(NoteFolder.vault_id == vault.id).order_by(NoteFolder.path)
                )
            ).all()
        ]
        result = await db.execute(
            select(
                Note.id,
                Note.title,
                Note.user_id,
                Note.created_at,
                Note.updated_at,
                NotePlacement.folder,
                NoteIndex.note_type,
                NoteIndex.tags,
                NoteIndex.aliases,
                NoteIndex.word_count,
                NoteIndex.excerpt,
            )
            .join(NotePlacement, NotePlacement.note_id == Note.id)
            .outerjoin(NoteIndex, NoteIndex.note_id == Note.id)
            .where(NotePlacement.vault_id == vault.id)
            .order_by(Note.title)
        )
        pinned = set(await Notes.get_pinned_note_ids(user_id, db=db))
        notes = [
            {
                'id': row[0],
                'title': row[1] or '',
                'user_id': row[2],
                'is_pinned': row[0] in pinned,
                'created_at': row[3],
                'updated_at': row[4],
                'folder': row[5] or '',
                'type': row[6],
                'tags': row[7] or [],
                'aliases': row[8] or [],
                'word_count': row[9] or 0,
                'excerpt': row[10] or '',
            }
            for row in result.all()
        ]
        link_counts = defaultdict(lambda: [0, 0])
        rows = await db.execute(
            select(NoteLink.source_id, NoteLink.target_id, NoteLink.target_key).where(
                NoteLink.vault_id == vault.id, NoteLink.kind.in_(('link', 'property'))
            )
        )
        titles = await _title_map(vault.id, db)
        for source_id, target_id, target_key in rows.all():
            link_counts[source_id][0] += 1
            # A link written by title counts for the note that now has that title.
            target = target_id or (titles.get(target_key) if target_key else None)
            if target:
                link_counts[target][1] += 1
    for note in notes:
        out_count, in_count = link_counts.get(note['id'], [0, 0])
        note['links_out'] = out_count
        note['links_in'] = in_count
    # Folders that only exist because a note is in them.
    all_folders = set(folders)
    for note in notes:
        if note['folder']:
            all_folders.update(nc.folder_parents(note['folder']))
    return {'folders': sorted(all_folders), 'notes': notes}


def _resolve(
    target_id: Optional[str], target_key: Optional[str], titles: dict[str, str], in_vault: set[str]
) -> Optional[str]:
    if target_id and target_id in in_vault:
        return target_id
    if target_key:
        return titles.get(target_key)
    return None


async def vault_graph(vault: NoteVaultModel) -> dict:
    await refresh_index(vault)
    async with get_async_db_context() as db:
        rows = (
            await db.execute(
                select(
                    NoteIndex.note_id,
                    NoteIndex.title,
                    NoteIndex.note_type,
                    NoteIndex.tags,
                    NoteIndex.word_count,
                    NotePlacement.folder,
                    Note.updated_at,
                )
                .join(NotePlacement, NotePlacement.note_id == NoteIndex.note_id)
                .join(Note, Note.id == NoteIndex.note_id)
                .where(NotePlacement.vault_id == vault.id)
            )
        ).all()
        links = (
            await db.execute(
                select(
                    NoteLink.source_id,
                    NoteLink.kind,
                    NoteLink.target_id,
                    NoteLink.target_key,
                    NoteLink.target_title,
                    NoteLink.property_key,
                    NoteLink.entity_type,
                    NoteLink.entity_id,
                    NoteLink.label,
                ).where(NoteLink.vault_id == vault.id)
            )
        ).all()
        titles = await _title_map(vault.id, db)

    in_vault = {row[0] for row in rows}
    nodes = [
        {
            'id': row[0],
            'kind': 'note',
            'title': row[1] or '',
            'type': row[2],
            'tags': row[3] or [],
            'words': row[4] or 0,
            'folder': row[5] or '',
            'updated_at': row[6],
        }
        for row in rows
    ]
    ghosts: dict[str, dict] = {}
    entities: dict[str, dict] = {}
    edges = []
    for source_id, kind, target_id, target_key, target_title, property_key, entity_type, entity_id, label in links:
        if source_id not in in_vault:
            continue
        if kind == 'entity':
            node_id = f'entity:{entity_type}:{entity_id}'
            if node_id not in entities:
                entities[node_id] = {
                    'id': node_id,
                    'kind': 'entity',
                    'title': label or entity_id,
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'href': nc.entity_href(entity_type, entity_id),
                }
            elif label and entities[node_id]['title'] == entity_id:
                entities[node_id]['title'] = label
            edges.append({'source': source_id, 'target': node_id, 'kind': 'entity', 'key': property_key})
            continue
        resolved = _resolve(target_id, target_key, titles, in_vault)
        if resolved:
            if resolved != source_id:
                edges.append({'source': source_id, 'target': resolved, 'kind': kind, 'key': property_key})
            continue
        if not target_key:
            continue
        ghost_id = f'ghost:{target_key}'
        ghosts.setdefault(ghost_id, {'id': ghost_id, 'kind': 'ghost', 'title': target_title or target_key})
        edges.append({'source': source_id, 'target': ghost_id, 'kind': kind, 'key': property_key})
    return {'nodes': nodes + list(ghosts.values()) + list(entities.values()), 'edges': edges}


async def note_links(note: NoteModel, vault: NoteVaultModel) -> dict:
    """Outgoing links, backlinks (with the sentence they are in), unlinked mentions, Gnos3 data."""
    await refresh_index(vault)
    async with get_async_db_context() as db:
        titles = await _title_map(vault.id, db)
        index_rows = {
            row[0]: {'id': row[0], 'title': row[1] or '', 'type': row[2], 'folder': row[3] or ''}
            for row in (
                await db.execute(
                    select(NoteIndex.note_id, NoteIndex.title, NoteIndex.note_type, NotePlacement.folder)
                    .join(NotePlacement, NotePlacement.note_id == NoteIndex.note_id)
                    .where(NotePlacement.vault_id == vault.id)
                )
            ).all()
        }
        in_vault = set(index_rows)
        me = await db.get(NoteIndex, note.id)
        my_keys = {nc.normalize_title(note.title)} | {
            nc.normalize_title(a) for a in ((me.aliases if me else None) or [])
        }
        my_keys.discard('')

        outgoing_rows = (
            (await db.execute(select(NoteLink).where(NoteLink.source_id == note.id).order_by(NoteLink.id)))
            .scalars()
            .all()
        )
        pointing_here = [NoteLink.target_id == note.id]
        if my_keys:
            pointing_here.append(and_(NoteLink.target_key.in_(my_keys), NoteLink.kind != 'entity'))
        incoming_rows = (
            (
                await db.execute(
                    select(NoteLink).where(
                        NoteLink.vault_id == vault.id,
                        NoteLink.source_id != note.id,
                        or_(*pointing_here),
                    )
                )
            )
            .scalars()
            .all()
        )

    outgoing = []
    entities = []
    for link in outgoing_rows:
        if link.kind == 'entity':
            entities.append(
                {
                    'entity_type': link.entity_type,
                    'entity_id': link.entity_id,
                    'label': link.label,
                    'href': nc.entity_href(link.entity_type, link.entity_id),
                    'property': link.property_key,
                }
            )
            continue
        resolved = _resolve(link.target_id, link.target_key, titles, in_vault)
        outgoing.append(
            {
                'kind': link.kind,
                'property': link.property_key,
                'note': index_rows.get(resolved) if resolved else None,
                'title': link.target_title,
            }
        )

    backlinks: dict[str, dict] = {}
    for link in incoming_rows:
        resolved = _resolve(link.target_id, link.target_key, titles, in_vault)
        if resolved != note.id or link.source_id not in index_rows:
            continue
        entry = backlinks.setdefault(
            link.source_id, {'note': index_rows[link.source_id], 'contexts': [], 'properties': []}
        )
        if link.kind == 'property' and link.property_key:
            if link.property_key not in entry['properties']:
                entry['properties'].append(link.property_key)
        elif link.context and link.context not in entry['contexts']:
            entry['contexts'].append(link.context)

    unlinked = await unlinked_mentions(
        note,
        vault,
        set(backlinks) | {note.id},
        index_rows,
        my_titles=[note.title] + ((me.aliases if me else None) or []),
    )
    return {
        'outgoing': outgoing,
        'backlinks': sorted(backlinks.values(), key=lambda b: b['note']['title'].casefold()),
        'unlinked': unlinked,
        'entities': entities,
    }


async def unlinked_mentions(
    note: NoteModel, vault: NoteVaultModel, exclude: set[str], index_rows: dict, my_titles: list[str]
) -> list[dict]:
    titles = [t for t in my_titles if t and nc.mention_pattern(t)]
    if not titles:
        return []
    md = _md_expr()
    async with get_async_db_context() as db:
        result = await db.execute(
            select(Note.id, md)
            .join(NotePlacement, NotePlacement.note_id == Note.id)
            .where(
                NotePlacement.vault_id == vault.id,
                ~Note.id.in_(exclude),
                or_(*[md.ilike(f'%{t}%') for t in titles]),
            )
            .limit(200)
        )
        candidates = result.all()
    out = []
    for note_id, text in candidates:
        contexts = nc.find_mentions(text or '', titles)
        if contexts and note_id in index_rows:
            out.append({'note': index_rows[note_id], 'contexts': contexts})
        if len(out) >= 50:
            break
    return sorted(out, key=lambda m: m['note']['title'].casefold())


async def search_vault(vault: NoteVaultModel, query: str, limit: int = 50) -> list[dict]:
    words = [w for w in (query or '').split() if w]
    if not words:
        return []
    md = _md_expr()
    async with get_async_db_context() as db:
        stmt = (
            select(Note.id, Note.title, md, NotePlacement.folder, Note.updated_at)
            .join(NotePlacement, NotePlacement.note_id == Note.id)
            .where(NotePlacement.vault_id == vault.id)
        )
        for word in words:
            stmt = stmt.where(or_(Note.title.ilike(f'%{word}%'), md.ilike(f'%{word}%')))
        rows = (await db.execute(stmt.order_by(Note.updated_at.desc()).limit(500))).all()
    results = []
    lowered = [w.casefold() for w in words]
    for note_id, title, text, folder, updated_at in rows:
        title = title or ''
        plain = nc.markdown_to_text(text or '')
        haystack = plain.casefold()
        score = sum(3 for w in lowered if w in title.casefold()) + sum(haystack.count(w) for w in lowered)
        snippets = []
        for w in lowered:
            pos = haystack.find(w)
            if pos != -1:
                lo = max(0, pos - 70)
                hi = min(len(plain), pos + len(w) + 110)
                snippets.append(
                    ('…' if lo else '') + plain[lo:hi].replace('\n', ' ') + ('…' if hi < len(plain) else '')
                )
                break
        results.append(
            {
                'id': note_id,
                'title': title,
                'folder': folder or '',
                'updated_at': updated_at,
                'snippet': snippets[0] if snippets else '',
                'score': score,
            }
        )
    results.sort(key=lambda r: (-r['score'], -r['updated_at']))
    return results[:limit]


async def shared_with_me(user) -> list[dict]:
    """Notes others shared with this user one by one (not through a shared vault)."""
    group_ids = [g.id for g in await Groups.get_groups_by_member_id(user.id)]
    async with get_async_db_context() as db:
        stmt = (
            select(Note.id, Note.title, Note.user_id, Note.updated_at)
            .outerjoin(NotePlacement, NotePlacement.note_id == Note.id)
            .outerjoin(NoteVault, NoteVault.id == NotePlacement.vault_id)
            .where(Note.user_id != user.id, or_(NoteVault.kind.is_(None), NoteVault.kind == 'personal'))
        )
        stmt = AccessGrants.has_permission_filter(
            db=db,
            query=stmt,
            DocumentModel=Note,
            filter={'user_id': user.id, 'group_ids': group_ids},
            resource_type='note',
            permission='read',
        )
        rows = (await db.execute(stmt.order_by(Note.updated_at.desc()).limit(200))).all()
    return [{'id': r[0], 'title': r[1] or '', 'user_id': r[2], 'updated_at': r[3]} for r in rows]


# ---------------------------------------------------------------------------
# Export / import
# ---------------------------------------------------------------------------

_SAFE_NAME = re.compile(r'[\\/:*?"<>|\n\r\t]')
_DATA_IMAGE_RE = re.compile(r'!\[([^\]]*)\]\(data://([0-9a-zA-Z_-]+)\)')
_DATA_URL_RE = re.compile(r'^data:([a-z]+/[a-z0-9.+-]+);base64,(.*)$', re.DOTALL | re.IGNORECASE)
_EXT = {'image/png': 'png', 'image/jpeg': 'jpg', 'image/gif': 'gif', 'image/webp': 'webp', 'image/svg+xml': 'svg'}


async def export_vault(vault: NoteVaultModel) -> bytes:
    """The vault as a zip of Markdown files with frontmatter, in its folders, with images under
    `_attachments/`. Opens as an Obsidian / Tolaria vault."""
    tree = await vault_tree(vault, vault.owner_id)
    async with get_async_db_context() as db:
        titles = {
            row[0]: row[1] or ''
            for row in (
                await db.execute(select(NoteIndex.note_id, NoteIndex.title).where(NoteIndex.vault_id == vault.id))
            ).all()
        }
        links = (
            await db.execute(
                select(NoteLink.source_id, NoteLink.target_id, NoteLink.target_key, NoteLink.target_title).where(
                    NoteLink.vault_id == vault.id, NoteLink.kind == 'link', NoteLink.target_id.is_not(None)
                )
            )
        ).all()
    renames: dict[str, dict[str, str]] = defaultdict(dict)
    for source_id, target_id, target_key, target_title in links:
        current = titles.get(target_id)
        if current and target_key and nc.normalize_title(current) != target_key:
            renames[source_id][target_key] = current

    buffer = io.BytesIO()
    used: set[str] = set()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for folder in tree['folders']:
            archive.writestr(folder.rstrip('/') + '/', b'')
        for item in tree['notes']:
            note = await Notes.get_note_by_id(item['id'])
            if not note:
                continue
            data = note.data or {}
            md = ((data.get('content') or {}).get('md') or '').replace('\r\n', '\n')
            md = nc.markdown_with_link_titles(md, renames.get(note.id, {}))
            files = {f.get('id'): f for f in (data.get('files') or []) if isinstance(f, dict) and f.get('id')}

            def attach(match: re.Match) -> str:
                file = files.get(match.group(2))
                url = (file or {}).get('url') or ''
                found = _DATA_URL_RE.match(url)
                if not found:
                    return match.group(0)
                ext = _EXT.get(found.group(1).lower(), 'bin')
                name = f'_attachments/{match.group(2)}.{ext}'
                if name not in used:
                    try:
                        archive.writestr(name, base64.b64decode(found.group(2)))
                        used.add(name)
                    except Exception:
                        return match.group(0)
                depth = item['folder'].count('/') + 1 if item['folder'] else 0
                return f'![{match.group(1)}]({"../" * depth}{name})'

            md = _DATA_IMAGE_RE.sub(attach, md)
            frontmatter = nc.render_frontmatter(data.get('properties') or {}, titles)
            name = _SAFE_NAME.sub(' ', note.title or 'Untitled').strip() or 'Untitled'
            path = (item['folder'] + '/' if item['folder'] else '') + name
            candidate = path + '.md'
            n = 2
            while candidate.casefold() in used:
                candidate = f'{path} ({n}).md'
                n += 1
            used.add(candidate.casefold())
            archive.writestr(candidate, (frontmatter + md).encode('utf-8'))
    return buffer.getvalue()


async def import_notes(user, vault: NoteVaultModel, items: list[dict]) -> dict:
    """Notes read from a vault export (the page unzips and parses it): [{folder, title, md,
    properties, files}]. Links stay [[Title]] and resolve by title, as in the source vault."""
    created = 0
    for item in items:
        properties, body = nc.parse_frontmatter(item.get('md') or '')
        properties = {**properties, **(item.get('properties') or {})}
        await create_note(
            user,
            vault,
            title=item.get('title') or 'Untitled',
            folder=item.get('folder') or '',
            md=body,
            properties=properties,
            files=item.get('files') or None,
            unique=False,
        )
        created += 1
    for folder in {nc.clean_folder(i.get('folder') or '') for i in items}:
        await ensure_folder(vault.id, folder)
    return {'created': created}
