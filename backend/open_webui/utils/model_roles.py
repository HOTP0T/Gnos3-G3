"""
Gnos3 follows the appliance's choice of models (deploy/models.env in the stack).

Every update writes GNOS3_CHAT_MODEL and GNOS3_EMBEDDING_MODEL into the box's
.env and the compose file passes them to this container. Settings kept in the
database never see an env change, so when the chat model differs from the one
recorded at the previous start, what pointed at the old model moves to the new
one:

* the default chat model, if it was the old one;
* the hidden "Gnos3 tasks" preset (titles, tags, search queries) built on it;
* who may use it: the old model's access grants are copied to the new model,
  unless an admin already set the new one up;
* each person's own default model.

The old model stays installed, so earlier chats keep working on it.

A new embedding model is not switched here: every knowledge base would need
re-indexing, which an admin starts in Admin > Settings > Documents. Until then
each start logs a warning.

Without GNOS3_CHAT_MODEL (the dev box, a plain install) nothing happens.
"""

import logging
import os

from open_webui.utils.gnos3_settings import StoredValue

log = logging.getLogger(__name__)

# The hidden preset settings_upgrade step 2 creates for titles, tags and searches.
TASK_MODEL_ID = 'gnos3-tasks'

# The chat model recorded at the last start.
CHAT_MODEL_IN_USE = StoredValue('gnos3.models.chat', '')


def replace_model(models: list, old: str, new: str) -> list:
    """`models` with `old` replaced by `new`, order kept, no duplicates."""
    return list(dict.fromkeys(new if m == old else m for m in models))


def replace_in_csv(csv: str, old: str, new: str) -> str:
    return ','.join(replace_model([m.strip() for m in (csv or '').split(',') if m.strip()], old, new))


async def move_chat_model(config, old: str, new: str, models, users, ModelForm) -> list[str]:
    """Point everything that used `old` at `new`. Returns what changed."""
    changed = []

    default_models = await config.get('ui.default_models') or ''
    if old in [m.strip() for m in default_models.split(',')]:
        await config.upsert({'ui.default_models': replace_in_csv(default_models, old, new)})
        changed.append('default model')

    task = await models.get_model_by_id(TASK_MODEL_ID)
    if task is not None and task.base_model_id == old:
        await models.update_model_by_id(
            TASK_MODEL_ID,
            ModelForm(
                id=task.id,
                base_model_id=new,
                name=task.name,
                meta=task.meta,
                params=task.params,
                is_active=task.is_active,
            ),
        )
        changed.append('task model')

    # An entry for a base model holds who may use it (an admin's grant in
    # Workspace > Models). Carry it over, unless the new model has one.
    entry = await models.get_model_by_id(old)
    if entry is not None and entry.base_model_id is None and await models.get_model_by_id(new) is None:
        await models.insert_new_model(
            ModelForm(
                id=new,
                base_model_id=None,
                name=new,
                meta=entry.meta.model_copy(update={'description': None}),
                params=entry.params,
                access_grants=[
                    {'principal_type': g.principal_type, 'principal_id': g.principal_id, 'permission': g.permission}
                    for g in entry.access_grants
                ],
                is_active=entry.is_active,
            ),
            entry.user_id,
        )
        changed.append(f'access ({len(entry.access_grants)} grants)')

    moved = 0
    for user in (await users.get_users()).get('users', []):
        ui = dict((user.settings.ui if user.settings else None) or {})
        if isinstance(ui.get('models'), list) and old in ui['models']:
            ui['models'] = replace_model(ui['models'], old, new)
            await users.update_user_settings_by_id(user.id, {'ui': ui})
            moved += 1
    if moved:
        changed.append(f"{moved} people's default model")
    return changed


async def follow_model_roles(models=None, users=None, in_use=None, model_form=None, config=None) -> None:
    if config is None:
        from open_webui.models.config import Config as config

    chat = os.environ.get('GNOS3_CHAT_MODEL', '').strip()
    if chat:
        in_use = in_use or CHAT_MODEL_IN_USE
        previous = (await in_use.get() or '').strip()
        if previous and previous != chat:
            if models is None:
                from open_webui.models.models import Models as models
            if users is None:
                from open_webui.models.users import Users as users
            if model_form is None:
                from open_webui.models.models import ModelForm as model_form
            changed = await move_chat_model(config, previous, chat, models, users, model_form)
            log.info(f'Chat model {previous} -> {chat}: moved {", ".join(changed) or "nothing"}')
        if previous != chat:
            await in_use.set(chat)

    embedding = os.environ.get('GNOS3_EMBEDDING_MODEL', '').strip()
    current_embedding = await config.get('rag.embedding_model')
    if embedding and embedding != current_embedding:
        log.warning(
            f'models.env names {embedding} for embeddings, but knowledge bases use '
            f'{current_embedding}. Switch it in Admin > Settings > Documents '
            f'and re-index the knowledge bases.'
        )
