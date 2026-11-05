"""Notes vaults API (`/api/v1/note-vaults`): vaults, folders, links, graph, search, import /
export, AI. Notes themselves are still read, saved, shared and deleted through upstream's
`/api/v1/notes` and the co-editing socket. How the pieces fit: services/note_vaults.py."""

import json
import logging
import re
from typing import Any, Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from open_webui.constants import ERROR_MESSAGES
from open_webui.models.access_grants import AccessGrants
from open_webui.models.notes import Notes
from open_webui.models.note_vaults import NoteVaultModel
from open_webui.services import note_vault_knowledge as knowledge
from open_webui.services import note_vaults as vaults
from open_webui.utils import note_content as nc
from open_webui.utils.access_control import has_permission
from open_webui.utils.auth import get_verified_user

log = logging.getLogger(__name__)

router = APIRouter()

IMPORT_BATCH_MAX = 200
SUGGEST_NUM_CTX = 16384


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


async def require_notes(request: Request, user) -> None:
    if not request.app.state.config.ENABLE_NOTES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.ACCESS_PROHIBITED)
    if vaults.is_admin(user):
        return
    if not await has_permission(user.id, 'features.notes', request.app.state.config.USER_PERMISSIONS):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.UNAUTHORIZED)


async def vault_for(request: Request, user, vault_id: str, need: str) -> tuple[NoteVaultModel, str]:
    await require_notes(request, user)
    vault = await vaults.get_vault(vault_id)
    if vault is None and vault_id == vaults.personal_vault_id(user.id):
        vault = await vaults.ensure_personal_vault(user)
    if vault is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND)
    permission = await vaults.vault_permission(user, vault)
    if not vaults.satisfies(permission, need):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.ACCESS_PROHIBITED)
    return vault, permission


async def note_for(request: Request, user, note_id: str, need: str = 'read'):
    await require_notes(request, user)
    note = await Notes.get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND)
    allowed = await (vaults.can_write_note(user, note) if need == 'write' else vaults.can_read_note(user, note))
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.ACCESS_PROHIBITED)
    return note


async def vault_out(vault: NoteVaultModel, permission: str, count: Optional[int] = None) -> dict:
    out = {
        **vault.model_dump(exclude={'settings'}),
        'settings': vaults.vault_settings(vault),
        'permission': permission,
        'note_count': count,
        'knowledge_id': knowledge.knowledge_id(vault.id)
        if ((vault.settings or {}).get('ai') or {}).get('knowledge')
        else None,
    }
    if vault.kind == 'shared' and permission == 'manage':
        out['access_grants'] = [
            g.model_dump() for g in await AccessGrants.get_grants_by_resource('note_vault', vault.id)
        ]
    return out


# ---------------------------------------------------------------------------
# Vaults
# ---------------------------------------------------------------------------


@router.get('/')
async def list_vaults(request: Request, user=Depends(get_verified_user)):
    await require_notes(request, user)
    pairs = await vaults.list_vaults(user)
    counts = await vaults.vault_counts([v.id for v, _ in pairs])
    return [await vault_out(v, p, counts.get(v.id, 0)) for v, p in pairs]


class VaultForm(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    access_grants: Optional[list[dict]] = None


@router.post('/create')
async def create_vault(request: Request, form: VaultForm, user=Depends(get_verified_user)):
    """Shared vaults are created by admins (they choose which groups read or write it)."""
    await require_notes(request, user)
    if not vaults.is_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.ACCESS_PROHIBITED)
    if not form.name.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='A vault needs a name.')
    vault = await vaults.create_shared_vault(
        user, form.name, form.description, form.color, form.icon, form.access_grants
    )
    return await vault_out(vault, 'manage', 0)


@router.get('/{vault_id}')
async def get_vault(request: Request, vault_id: str, user=Depends(get_verified_user)):
    vault, permission = await vault_for(request, user, vault_id, 'read')
    counts = await vaults.vault_counts([vault.id])
    return await vault_out(vault, permission, counts.get(vault.id, 0))


class VaultUpdateForm(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    settings: Optional[dict] = None


def clean_settings(settings: dict, current: dict) -> dict:
    """Only known settings, in the expected shapes."""
    out = dict(current)
    daily = settings.get('daily')
    if isinstance(daily, dict):
        out['daily'] = {
            'folder': nc.clean_folder(daily.get('folder', current.get('daily', {}).get('folder', ''))),
            'format': str(daily.get('format') or 'YYYY-MM-DD')[:40],
            'template_id': daily.get('template_id') or None,
        }
    if 'templates_folder' in settings:
        out['templates_folder'] = nc.clean_folder(settings.get('templates_folder') or '')
    types = settings.get('types')
    if isinstance(types, list):
        cleaned = []
        keys = set()
        for item in types[:40]:
            if not isinstance(item, dict):
                continue
            key = re.sub(r'[^a-z0-9_-]', '', str(item.get('key') or '').lower())[:40]
            if not key or key in keys:
                continue
            keys.add(key)
            fields = []
            field_keys = set()
            for field in (item.get('fields') or [])[:40]:
                if not isinstance(field, dict):
                    continue
                fkey = re.sub(r'[^A-Za-z0-9_-]', '', str(field.get('key') or ''))[:60]
                kind = field.get('kind') if field.get('kind') in vaults.FIELD_KINDS else 'text'
                if not fkey or fkey in field_keys or fkey in ('type', 'tags', 'aliases', 'title'):
                    continue
                field_keys.add(fkey)
                entry = {'key': fkey, 'label': str(field.get('label') or fkey)[:80], 'kind': kind}
                if kind in ('select', 'multiselect'):
                    entry['options'] = [str(o)[:80] for o in (field.get('options') or []) if str(o).strip()][:50]
                if kind in ('note', 'notes') and field.get('note_type'):
                    entry['note_type'] = str(field['note_type'])[:40]
                if kind == 'entity' and field.get('entity_type') in nc.ENTITY_TYPES:
                    entry['entity_type'] = field['entity_type']
                fields.append(entry)
            cleaned.append(
                {
                    'key': key,
                    'name': str(item.get('name') or key)[:60],
                    'icon': str(item.get('icon') or 'file-text')[:40],
                    'color': str(item.get('color') or 'chart-1')[:20],
                    'builtin': bool(item.get('builtin')) and key in {t['key'] for t in vaults.DEFAULT_TYPES},
                    'fields': fields,
                }
            )
        out['types'] = cleaned
    graph = settings.get('graph')
    if isinstance(graph, dict):
        out['graph'] = {k: v for k, v in graph.items() if isinstance(v, (bool, int, float, str))}
    return out


@router.post('/{vault_id}/update')
async def update_vault(request: Request, vault_id: str, form: VaultUpdateForm, user=Depends(get_verified_user)):
    """Settings (note types, daily notes, templates) need write access; name and look, manage."""
    vault, permission = await vault_for(request, user, vault_id, 'write')
    fields: dict[str, Any] = {}
    if any(v is not None for v in (form.name, form.description, form.color, form.icon)):
        if permission != 'manage':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.ACCESS_PROHIBITED)
        if form.name is not None and form.name.strip():
            fields['name'] = form.name.strip()[:120]
        if form.description is not None:
            fields['description'] = form.description.strip()[:500]
        if form.color is not None:
            fields['color'] = form.color[:20]
        if form.icon is not None:
            fields['icon'] = form.icon[:40]
    if form.settings is not None:
        stored = vault.settings or {}
        fields['settings'] = {**stored, **clean_settings(form.settings, vaults.vault_settings(vault))}
        # Keep what only the server sets.
        if 'ai' in stored:
            fields['settings']['ai'] = stored['ai']
    vault = await vaults.update_vault(vault, **fields)
    if 'name' in fields and ((vault.settings or {}).get('ai') or {}).get('knowledge'):
        await knowledge.ensure_knowledge(vault)
    return await vault_out(vault, permission)


class AccessForm(BaseModel):
    access_grants: list[dict]


@router.post('/{vault_id}/access')
async def update_vault_access(request: Request, vault_id: str, form: AccessForm, user=Depends(get_verified_user)):
    vault, permission = await vault_for(request, user, vault_id, 'manage')
    if vault.kind != 'shared':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='A personal vault is not shared as a whole.'
        )
    await vaults.set_vault_grants(vault, form.access_grants)
    if ((vault.settings or {}).get('ai') or {}).get('knowledge'):
        await knowledge.sync_access(vault)
    return await vault_out(vault, permission)


@router.delete('/{vault_id}')
async def delete_vault(request: Request, vault_id: str, user=Depends(get_verified_user)):
    vault, permission = await vault_for(request, user, vault_id, 'manage')
    if vault.kind != 'shared' or not vaults.is_admin(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Only a shared vault can be deleted.')
    try:
        await knowledge.delete_knowledge(vault.id)
    except Exception as e:
        log.warning('Deleting the knowledge of vault %s failed: %s', vault.id, e)
    deleted = await vaults.delete_shared_vault(vault)
    return {'deleted_notes': deleted}


# ---------------------------------------------------------------------------
# Reading a vault
# ---------------------------------------------------------------------------


@router.get('/{vault_id}/tree')
async def vault_tree(request: Request, vault_id: str, user=Depends(get_verified_user)):
    vault, _ = await vault_for(request, user, vault_id, 'read')
    return await vaults.vault_tree(vault)


@router.get('/{vault_id}/graph')
async def vault_graph(request: Request, vault_id: str, user=Depends(get_verified_user)):
    vault, _ = await vault_for(request, user, vault_id, 'read')
    return await vaults.vault_graph(vault)


@router.get('/{vault_id}/search')
async def search_vault(request: Request, vault_id: str, q: str = '', user=Depends(get_verified_user)):
    vault, _ = await vault_for(request, user, vault_id, 'read')
    return await vaults.search_vault(vault, q[:200])


@router.get('/shared/notes')
async def shared_with_me(request: Request, user=Depends(get_verified_user)):
    await require_notes(request, user)
    return await vaults.shared_with_me(user)


# ---------------------------------------------------------------------------
# Folders
# ---------------------------------------------------------------------------


class FolderForm(BaseModel):
    path: str


class FolderRenameForm(BaseModel):
    from_path: str = Field(alias='from')
    to_path: str = Field(alias='to')


class FolderDeleteForm(BaseModel):
    path: str
    mode: str = 'move_up'


@router.post('/{vault_id}/folders')
async def create_folder(request: Request, vault_id: str, form: FolderForm, user=Depends(get_verified_user)):
    vault, _ = await vault_for(request, user, vault_id, 'write')
    path = nc.clean_folder(form.path)
    if not path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='A folder needs a name.')
    await vaults.ensure_folder(vault.id, path)
    return {'path': path}


@router.post('/{vault_id}/folders/rename')
async def rename_folder(request: Request, vault_id: str, form: FolderRenameForm, user=Depends(get_verified_user)):
    vault, _ = await vault_for(request, user, vault_id, 'write')
    try:
        moved = await vaults.rename_folder(vault, form.from_path, form.to_path)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {'moved': moved, 'path': nc.clean_folder(form.to_path)}


@router.post('/{vault_id}/folders/delete')
async def delete_folder(request: Request, vault_id: str, form: FolderDeleteForm, user=Depends(get_verified_user)):
    vault, _ = await vault_for(request, user, vault_id, 'write')
    if form.mode not in ('move_up', 'delete'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Unknown mode.')
    count = await vaults.delete_folder(vault, form.path, form.mode)
    return {'notes': count}


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------


class NoteCreateForm(BaseModel):
    title: str = ''
    folder: str = ''
    md: str = ''
    properties: Optional[dict] = None
    files: Optional[list] = None
    unique: bool = True


@router.post('/{vault_id}/notes')
async def create_note(request: Request, vault_id: str, form: NoteCreateForm, user=Depends(get_verified_user)):
    vault, _ = await vault_for(request, user, vault_id, 'write')
    note = await vaults.create_note(
        user,
        vault,
        title=form.title or 'Untitled',
        folder=form.folder,
        md=form.md,
        properties=form.properties,
        files=form.files,
        unique=form.unique,
    )
    return {'id': note.id, 'title': note.title, 'folder': nc.clean_folder(form.folder), 'vault_id': vault.id}


class ImportForm(BaseModel):
    items: list[dict]


@router.post('/{vault_id}/import')
async def import_notes(request: Request, vault_id: str, form: ImportForm, user=Depends(get_verified_user)):
    vault, _ = await vault_for(request, user, vault_id, 'write')
    if len(form.items) > IMPORT_BATCH_MAX:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f'At most {IMPORT_BATCH_MAX} notes per request.'
        )
    return await vaults.import_notes(user, vault, form.items)


@router.get('/{vault_id}/export')
async def export_vault(request: Request, vault_id: str, user=Depends(get_verified_user)):
    vault, _ = await vault_for(request, user, vault_id, 'read')
    data = await vaults.export_vault(vault)
    name = re.sub(r'[^\w\- ]', '', vault.name).strip() or 'notes'
    return Response(
        content=data,
        media_type='application/zip',
        headers={'Content-Disposition': f"attachment; filename*=UTF-8''{quote(name)}.zip"},
    )


@router.get('/notes/{note_id}/place')
async def note_place(request: Request, note_id: str, user=Depends(get_verified_user)):
    """Where a note sits and what the person may do in that vault (the editor needs both)."""
    note = await note_for(request, user, note_id, 'read')
    vault = await vaults.vault_of_note(note)
    placement = await vaults.note_placement(note.id)
    permission = await vaults.vault_permission(user, vault)
    return {
        'vault_id': vault.id,
        'vault_name': vault.name,
        'vault_kind': vault.kind,
        'folder': placement.folder if placement else '',
        'vault_permission': permission,
        'settings': vaults.vault_settings(vault) if permission else None,
    }


@router.get('/notes/{note_id}/links')
async def note_links(request: Request, note_id: str, user=Depends(get_verified_user)):
    note = await note_for(request, user, note_id, 'read')
    vault = await vaults.vault_of_note(note)
    if not await vaults.vault_permission(user, vault):
        # A note shared alone: no vault to look through.
        return {'outgoing': [], 'backlinks': [], 'unlinked': [], 'entities': []}
    return await vaults.note_links(note, vault)


class MoveForm(BaseModel):
    vault_id: str
    folder: str = ''


@router.post('/notes/{note_id}/move')
async def move_note(request: Request, note_id: str, form: MoveForm, user=Depends(get_verified_user)):
    note = await note_for(request, user, note_id, 'write')
    current = await vaults.vault_of_note(note)
    target, _ = await vault_for(request, user, form.vault_id, 'write')
    if target.id != current.id:
        if not vaults.satisfies(await vaults.vault_permission(user, current), 'write'):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.ACCESS_PROHIBITED)
        if target.kind == 'personal' and note.user_id != target.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Only notes you wrote can go to your personal vault.',
            )
    await vaults.place_note(note, target, form.folder)
    return {'vault_id': target.id, 'folder': nc.clean_folder(form.folder)}


class MetaForm(BaseModel):
    title: Optional[str] = None
    properties: Optional[dict] = None
    files: Optional[list] = None


@router.post('/notes/{note_id}/meta')
async def update_note_meta(request: Request, note_id: str, form: MetaForm, user=Depends(get_verified_user)):
    from open_webui.socket.main import sio

    note = await note_for(request, user, note_id, 'write')
    updated = await vaults.update_note_meta(note, title=form.title, properties=form.properties, files=form.files)
    try:
        # What other open editors of this note need (not the whole note: its body travels by Yjs).
        await sio.emit(
            'note-events',
            {
                'id': updated.id,
                'title': updated.title,
                'data': {
                    'properties': (updated.data or {}).get('properties') or {},
                    'files': (updated.data or {}).get('files'),
                },
            },
            to=f'note:{updated.id}',
        )
    except Exception:
        pass
    return {'id': updated.id, 'title': updated.title, 'properties': (updated.data or {}).get('properties') or {}}


class MarkdownForm(BaseModel):
    md: str


@router.post('/notes/{note_id}/markdown')
async def set_note_markdown(request: Request, note_id: str, form: MarkdownForm, user=Depends(get_verified_user)):
    """Rewrites the Markdown of a note nobody has opened in the editor yet (turning a mention into
    a [[link]] from the Links panel). Not upstream's POST /notes/{id}/update: called without
    access_grants, that one deletes the note's sharing."""
    from open_webui.models.notes import NoteUpdateForm

    note = await note_for(request, user, note_id, 'write')
    content = (note.data or {}).get('content') or {}
    if content.get('json'):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='This note is edited in the editor.')
    await Notes.update_note_by_id(note.id, NoteUpdateForm(data={'content': {**content, 'md': form.md, 'html': ''}}))
    vault = await vaults.vault_of_note(note)
    await vaults.index_notes(vault, [note.id])
    return {'id': note.id}


# ---------------------------------------------------------------------------
# Gnos3 data
# ---------------------------------------------------------------------------


@router.get('/entities/documents')
async def search_documents(request: Request, q: str = '', user=Depends(get_verified_user)):
    """K4mi documents for a link in a note, searched as the person (K4mi decides what they see).
    Invoices, companies, business cards and chats are searched by the page through their own APIs."""
    import os

    import httpx

    from open_webui.internal.db import get_async_db_context
    from open_webui.routers.auths import _k4mi_token_groups
    from open_webui.utils.auth import create_k4mi_exchange_token

    await require_notes(request, user)
    query = q.strip()[:120]
    if len(query) < 2:
        return []
    base = (os.environ.get('K4MI_MODULE_URL') or 'http://k4mi:8000').rstrip('/')
    async with get_async_db_context() as db:
        groups = await _k4mi_token_groups(user, db)
    token, _ = create_k4mi_exchange_token(user, groups=groups, mfa_verified=False)
    try:
        async with httpx.AsyncClient(timeout=4) as client:
            response = await client.get(
                f'{base}/api/documents/',
                params={'title_content': query, 'page_size': 8, 'ordering': '-created', 'fields': 'id,title,created'},
                headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json; version=9'},
            )
            response.raise_for_status()
            results = response.json().get('results') or []
    except Exception as e:
        log.info('Notes: K4mi document search unavailable: %s', e)
        return []
    return [
        {
            'entity_type': 'document',
            'entity_id': str(r.get('id')),
            'label': r.get('title') or str(r.get('id')),
            'detail': (r.get('created') or '')[:10],
        }
        for r in results
        if r.get('id') is not None
    ]


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------


@router.post('/{vault_id}/knowledge')
async def vault_knowledge(request: Request, vault_id: str, user=Depends(get_verified_user)):
    """Makes the vault usable in chat: its knowledge base, with up to a batch of changed notes
    embedded now (the rest within minutes)."""
    vault, _ = await vault_for(request, user, vault_id, 'read')
    result = await knowledge.sync_vault(request, vault)
    vault = await vaults.get_vault(vault.id)
    return {**result, 'name': f'Notes · {vault.name}'}


class ScopeForm(BaseModel):
    folder: Optional[str] = None
    tag: Optional[str] = None
    note_ids: Optional[list[str]] = None


SCOPE_FULL_TEXT_CHARS = 24000  # about 6k tokens: read whole within the 16k context
SCOPE_MAX_NOTES = 60


@router.post('/{vault_id}/knowledge/scope')
async def vault_scope(request: Request, vault_id: str, form: ScopeForm, user=Depends(get_verified_user)):
    """A folder or a tag for chat. Small enough → the notes themselves (read whole); larger → their
    embeddings (searched), at most the SCOPE_MAX_NOTES most recently edited."""
    vault, _ = await vault_for(request, user, vault_id, 'read')
    tree = await vaults.vault_tree(vault)
    notes = tree['notes']
    if form.folder is not None:
        folder = nc.clean_folder(form.folder)
        notes = [n for n in notes if n['folder'] == folder or n['folder'].startswith(folder + '/')] if folder else notes
    if form.tag:
        tag = form.tag.lstrip('#').casefold()
        notes = [n for n in notes if any(t.casefold() == tag or t.casefold().startswith(tag + '/') for t in n['tags'])]
    if form.note_ids is not None:
        wanted = set(form.note_ids)
        notes = [n for n in notes if n['id'] in wanted]
    notes.sort(key=lambda n: -n['updated_at'])
    if not notes:
        return {'mode': 'empty', 'notes': []}
    approx_chars = sum(max(n['word_count'], 1) * 6 for n in notes)
    if approx_chars <= SCOPE_FULL_TEXT_CHARS:
        return {'mode': 'notes', 'notes': [{'id': n['id'], 'title': n['title']} for n in notes]}
    chosen = notes[:SCOPE_MAX_NOTES]
    # Embed the chosen notes now if they changed.
    kb = await knowledge.ensure_knowledge(vault)
    result = await knowledge.sync_vault(request, vault, limit=None, only={n['id'] for n in chosen})
    pending = result['pending']
    return {
        'mode': 'collections',
        'knowledge_id': kb,
        'collection_names': await knowledge.scope_collections(vault, [n['id'] for n in chosen]),
        'count': len(chosen),
        'total': len(notes),
        'pending': pending,
    }


class SuggestForm(BaseModel):
    model: str
    lang: Optional[str] = None


_JSON_RE = re.compile(r'\{.*\}', re.DOTALL)


@router.post('/notes/{note_id}/suggest-links')
async def suggest_links(request: Request, note_id: str, form: SuggestForm, user=Depends(get_verified_user)):
    """Notes this note could link to: first the ones it already names (no AI needed), then the
    model's picks among the vault's titles. Suggestions only; the person adds the links."""
    from open_webui.utils.chat import generate_chat_completion
    from open_webui.utils.task import get_task_model_id

    note = await note_for(request, user, note_id, 'read')
    vault = await vaults.vault_of_note(note)
    if not await vaults.vault_permission(user, vault):
        return {'suggestions': []}
    tree = await vaults.vault_tree(vault)
    links = await vaults.note_links(note, vault)
    linked = {o['note']['id'] for o in links['outgoing'] if o.get('note')}
    content = (note.data or {}).get('content') or {}
    text = nc.markdown_to_text(nc.split_frontmatter(content.get('md') or '')[1])
    others = [n for n in tree['notes'] if n['id'] != note.id and n['id'] not in linked and n['title'].strip()]

    suggestions: list[dict] = []
    named = set()
    for other in others:
        contexts = nc.find_mentions(text, [other['title']] + list(other.get('aliases') or []), limit=1)
        if contexts:
            pattern = nc.mention_pattern(other['title'])
            match = pattern.search(text) if pattern else None
            suggestions.append(
                {
                    'id': other['id'],
                    'title': other['title'],
                    'phrase': match.group(0) if match else '',
                    'reason': None,
                    'source': 'mention',
                }
            )
            named.add(other['id'])

    models = request.app.state.MODELS
    if form.model not in models or len(text.strip()) < 40:
        return {'suggestions': suggestions}

    # Candidates: titles sharing words with the note first, then the most recently edited.
    words = {w for w in re.findall(r'\w{4,}', text.casefold())}

    def overlap(n: dict) -> int:
        return len({w for w in re.findall(r'\w{3,}', (n['title'] + ' ' + ' '.join(n['tags'])).casefold())} & words)

    pool = sorted((n for n in others if n['id'] not in named), key=lambda n: (-overlap(n), -n['updated_at']))[:150]
    if not pool:
        return {'suggestions': suggestions}
    by_title = {n['title']: n for n in pool}
    task_model_id = get_task_model_id(
        form.model, request.app.state.config.TASK_MODEL, request.app.state.config.TASK_MODEL_EXTERNAL, models
    )
    language = form.lang or 'en'
    prompt = (
        'You help someone link their notes, like in a personal wiki.\n'
        'Below is a note, then the titles of other notes in the same notebook.\n'
        'Choose at most 6 titles this note should link to because it is clearly about the same person, '
        'organisation, project, meeting or topic. Choose none rather than a weak match.\n'
        'For each, copy the exact words of the note where the link belongs ("phrase", may be empty), '
        f'and give a reason of at most 12 words in the language whose code is "{language}".\n'
        'Answer with JSON only: {"links": [{"title": "...", "phrase": "...", "reason": "..."}]}\n\n'
        f'<note title="{note.title}">\n{text[:6000]}\n</note>\n\n<titles>\n'
        + '\n'.join(f'- {t}' for t in by_title)
        + '\n</titles>'
    )
    payload = {
        'model': task_model_id,
        'messages': [{'role': 'user', 'content': prompt}],
        'stream': False,
        'metadata': {'task': 'note_link_suggestions'},
    }
    if models[task_model_id].get('owned_by') == 'ollama':
        # Ollama reads format / think from options (utils/payload.py moves them to the root).
        payload['options'] = {
            'num_ctx': SUGGEST_NUM_CTX,
            'think': False,
            'format': {
                'type': 'object',
                'properties': {
                    'links': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'title': {'type': 'string', 'enum': list(by_title)},
                                'phrase': {'type': 'string'},
                                'reason': {'type': 'string'},
                            },
                            'required': ['title'],
                        },
                    }
                },
                'required': ['links'],
            },
        }
    try:
        response = await generate_chat_completion(request, form_data=payload, user=user, bypass_filter=True)
        if hasattr(response, 'body'):
            response = json.loads(response.body)
        reply = (((response or {}).get('choices') or [{}])[0].get('message') or {}).get('content') or ''
        found = _JSON_RE.search(reply)
        picks = json.loads(found.group(0)).get('links', []) if found else []
    except Exception as e:
        log.warning('Note link suggestions failed: %s', e)
        return {'suggestions': suggestions, 'ai_error': True}
    seen = {s['id'] for s in suggestions}
    for pick in picks[:6]:
        target = by_title.get((pick or {}).get('title'))
        if not target or target['id'] in seen:
            continue
        phrase = str(pick.get('phrase') or '').strip()
        if phrase and phrase.casefold() not in text.casefold():
            phrase = ''
        suggestions.append(
            {
                'id': target['id'],
                'title': target['title'],
                'phrase': phrase,
                'reason': str(pick.get('reason') or '').strip()[:160] or None,
                'source': 'ai',
            }
        )
        seen.add(target['id'])
    return {'suggestions': suggestions}
