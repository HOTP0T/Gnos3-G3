"""
One-time settings changes shipped with Gnos3 updates.

Settings are stored in the database at the first start, so a new default in
the appliance compose file never reaches a box that is already running. Each
step below runs once per box: the number of the last step applied is kept in
the config (`gnos3.settings_version`), and an admin's later changes are left
as they are.
"""

import asyncio
import logging
import os
from urllib.parse import urlsplit

from starlette.requests import Request

from open_webui.config import PersistentConfig
from open_webui.utils.model_roles import TASK_MODEL_ID

log = logging.getLogger(__name__)

SETTINGS_VERSION = PersistentConfig('GNOS3_SETTINGS_VERSION', 'gnos3.settings_version', 0)

# Retrieval sized for the appliance's 16,384-token context (deploy/ollama/
# memory-limits.conf): at most TOP_K chunks of CHUNK_SIZE tokens (~5k) leave
# room for the conversation, the model's reasoning and the answer. Chunks are
# counted in tokens so Chinese text gets the same budget as English.
#
# Hybrid search (keywords + meaning) finds invoice and reference numbers that
# vector search alone misses; without a reranker it keeps the fused order and
# takes ~0.2 s. The local reranker (a cross-encoder on the CPU) added 5-30 s
# per question for the same sources (measured 2026-10-26).
RETRIEVAL = {
    'RAG_FULL_CONTEXT': False,
    'BYPASS_EMBEDDING_AND_RETRIEVAL': False,
    'ENABLE_RAG_HYBRID_SEARCH': True,
    'TEXT_SPLITTER': 'token',
    'CHUNK_SIZE': 400,
    'CHUNK_OVERLAP': 50,
    'TOP_K': 12,
    'TOP_K_RERANKER': 6,
}
WEB_SEARCH = {
    'WEB_SEARCH_RESULT_COUNT': 3,
    # Without a timeout one slow site holds the whole search for 5 minutes.
    'WEB_LOADER_TIMEOUT': '10',
}
CHUNKING_KEYS = ('BYPASS_EMBEDDING_AND_RETRIEVAL', 'TEXT_SPLITTER', 'CHUNK_SIZE', 'CHUNK_OVERLAP')


def _set(config, values: dict) -> list[str]:
    changed = []
    for key, value in values.items():
        if getattr(config, key) != value:
            setattr(config, key, value)
            changed.append(key)
    return changed


async def _step_1(app) -> None:
    """Web search and document retrieval that fit a 16k-token context."""
    config = app.state.config
    changed = _set(config, RETRIEVAL | WEB_SEARCH)

    # Drop the in-process reranker; an external one (a GPU service an admin set
    # up on purpose) stays.
    if config.RAG_RERANKING_ENGINE == '' and config.RAG_RERANKING_MODEL:
        config.RAG_RERANKING_MODEL = ''
        app.state.rf = None
        app.state.RERANKING_FUNCTION = None
        changed.append('RAG_RERANKING_MODEL')

    # The appliance's SearXNG listens on 8080 inside the stack network; 8888
    # is only its port on the host (production had searxng:8888, refused).
    url = urlsplit(config.SEARXNG_QUERY_URL or '')
    if url.hostname == 'searxng' and url.port != 8080:
        config.SEARXNG_QUERY_URL = url._replace(netloc='searxng:8080').geturl()
        changed.append('SEARXNG_QUERY_URL')

    log.info(f'Settings upgrade 1 changed: {", ".join(changed) or "nothing"}')
    if any(key in changed for key in CHUNKING_KEYS):
        task = asyncio.create_task(reindex_knowledge_bases(app))
        _background_tasks.add(task)  # an unreferenced task can be garbage-collected mid-run
        task.add_done_callback(_background_tasks.discard)


_background_tasks: set[asyncio.Task] = set()


async def reindex_knowledge_bases(app) -> None:
    """Re-chunk and re-embed every knowledge base for the current settings.

    Unlike Admin → Documents → Reindex, which empties each base first, every
    file's new chunks are added before its old ones are removed: a file that
    fails keeps its old vectors. Runs in the background after startup.
    """
    from open_webui.internal.db import get_async_db_context
    from open_webui.models.knowledge import Knowledges
    from open_webui.models.users import Users
    from open_webui.retrieval.vector.async_client import ASYNC_VECTOR_DB_CLIENT
    from open_webui.routers.retrieval import ProcessFileForm, process_file

    try:
        admin = await Users.get_super_admin_user() or await Users.get_first_user()
        if admin is None:
            return
        request = Request({'type': 'http', 'app': app, 'headers': []})

        knowledge_bases = await Knowledges.get_knowledge_bases()
        log.info(f'Reindexing {len(knowledge_bases)} knowledge bases for the new retrieval settings')
        for kb in knowledge_bases:
            files = await Knowledges.get_files_by_id(kb.id)
            failed = 0
            for file in files:
                try:
                    old = await ASYNC_VECTOR_DB_CLIENT.query(collection_name=kb.id, filter={'file_id': file.id})
                    old_ids = old.ids[0] if old and old.ids else []
                    # Reuses the file's stored chunks and splits them again to
                    # the new size, as the Reindex button does.
                    async with get_async_db_context() as db:
                        await process_file(
                            request, ProcessFileForm(file_id=file.id, collection_name=kb.id), user=admin, db=db
                        )
                    if old_ids:
                        await ASYNC_VECTOR_DB_CLIENT.delete(collection_name=kb.id, ids=old_ids)
                except Exception as e:
                    failed += 1
                    log.warning(f'Reindex: {kb.name} / {file.filename}: {e}')
            log.info(f'Reindex: {kb.name} done, {len(files) - failed}/{len(files)} files')
        log.info('Reindex finished.')
    except Exception:
        log.exception('Reindex stopped')


# The appliance's chat model (deploy/models.env); utils/model_roles.py moves
# the preset when it changes.
TASK_BASE_MODEL = os.environ.get('GNOS3_CHAT_MODEL') or 'qwen3.8:latest'


async def _step_2(app) -> None:
    """Titles, tags, follow-ups and search queries without the model's reasoning.

    The chat model reasoned for 150-500 tokens before a one-line title or three
    search queries: ~55 s of GPU around every answer, which the next question
    waited behind. A hidden preset of the same model with thinking off does
    each in 3-7 s, and being the same weights it needs no second model loaded
    (appliances keep two). Measured 2026-10-26: qwen3.5:0.8b was faster but
    wrote one generic search query; gemma4:e2b reasoned just as long.
    """
    from open_webui.models.models import ModelForm, ModelMeta, ModelParams, Models
    from open_webui.models.users import Users

    config = app.state.config
    if config.TASK_MODEL:
        log.info('Settings upgrade 2: a task model is already chosen, left as is')
        return
    if await Models.get_model_by_id(TASK_MODEL_ID) is None:
        owner = await Users.get_super_admin_user() or await Users.get_first_user()
        if owner is None:
            raise RuntimeError('no user yet; retried at the first sign-up')
        await Models.insert_new_model(
            ModelForm(
                id=TASK_MODEL_ID,
                base_model_id=TASK_BASE_MODEL,
                name='Gnos3 tasks',
                meta=ModelMeta(
                    description='Titles, tags, follow-ups and search queries: the chat model without its reasoning.',
                    hidden=True,
                ),
                params=ModelParams(think=False),
                # Tasks run as the chatting user, so everyone needs read access;
                # hidden keeps it out of the model menu.
                access_grants=[{'principal_type': 'user', 'principal_id': '*', 'permission': 'read'}],
            ),
            owner.id,
        )
    # Unused when TASK_BASE_MODEL is not installed: Gnos3 then lists no such
    # model and tasks fall back to the chat model.
    config.TASK_MODEL = TASK_MODEL_ID
    log.info(f'Settings upgrade 2: task model set to {TASK_MODEL_ID}')


STEPS = [(1, _step_1), (2, _step_2)]


async def apply_settings_upgrades(app) -> None:
    for number, step in STEPS:
        if SETTINGS_VERSION.value >= number:
            continue
        await step(app)
        SETTINGS_VERSION.value = number
        await SETTINGS_VERSION.async_save()
