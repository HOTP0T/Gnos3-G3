"""Gnos3 follows the appliance's chat model (deploy/models.env).

When an update changes GNOS3_CHAT_MODEL (qwen3.8 -> qwen4, say), what pointed
at the old model moves to the new one at the next start: the default model,
the hidden task preset, who may use it, each person's own default. Nothing
moves on the first start with the setting, on an unchanged model, or on a box
without it.

No database: the model / user tables are fakes.
"""

import asyncio
from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from open_webui.utils.model_roles import TASK_MODEL_ID, follow_model_roles, replace_in_csv, replace_model


class Meta(BaseModel):
    description: str | None = None
    capabilities: dict | None = None


class Form(BaseModel):
    id: str
    base_model_id: str | None = None
    name: str
    meta: Meta
    params: dict
    access_grants: list | None = None
    is_active: bool = True


def entry(id, base=None, grants=(), user_id='admin-1'):
    return SimpleNamespace(
        id=id,
        base_model_id=base,
        name=id,
        meta=Meta(description=f'about {id}', capabilities={'vision': True}),
        params={},
        is_active=True,
        user_id=user_id,
        access_grants=[SimpleNamespace(principal_type=t, principal_id=p, permission=perm) for t, p, perm in grants],
    )


class FakeModels:
    def __init__(self, *entries):
        self.rows = {e.id: e for e in entries}
        self.inserted, self.updated = [], []

    async def get_model_by_id(self, id):
        return self.rows.get(id)

    async def update_model_by_id(self, id, form):
        self.updated.append(form)
        self.rows[id] = SimpleNamespace(**{**vars(self.rows[id]), 'base_model_id': form.base_model_id})

    async def insert_new_model(self, form, user_id):
        self.inserted.append((form, user_id))
        self.rows[form.id] = form


class FakeUsers:
    def __init__(self, *people):
        self.people = {p.id: p for p in people}
        self.saved = {}

    async def get_users(self):
        return {'users': list(self.people.values())}

    async def update_user_settings_by_id(self, id, updated):
        self.saved[id] = updated


def person(id, models):
    return SimpleNamespace(id=id, settings=SimpleNamespace(ui={'models': models, 'theme': 'dark'}))


class InUse:
    def __init__(self, value):
        self.value = value
        self.saves = 0

    async def async_save(self):
        self.saves += 1


def app(default='qwen3.8:latest', embedding='qwen3-embedding:latest'):
    return SimpleNamespace(state=SimpleNamespace(config=SimpleNamespace(
        DEFAULT_MODELS=default, RAG_EMBEDDING_MODEL=embedding)))


def run(a, models, users, in_use):
    asyncio.run(follow_model_roles(a, models=models, users=users, in_use=in_use, model_form=Form))


def test_replace_keeps_order_and_drops_duplicates():
    assert replace_model(['a', 'old', 'b'], 'old', 'new') == ['a', 'new', 'b']
    assert replace_model(['new', 'old'], 'old', 'new') == ['new']
    assert replace_in_csv('old, b', 'old', 'new') == 'new,b'


def test_a_new_chat_model_takes_over(monkeypatch):
    monkeypatch.setenv('GNOS3_CHAT_MODEL', 'qwen4:latest')
    models = FakeModels(
        entry(TASK_MODEL_ID, base='qwen3.8:latest'),
        entry('qwen3.8:latest', grants=[('group', 'g-accountants', 'read'), ('user', '*', 'read')]),
    )
    users = FakeUsers(person('u1', ['qwen3.8:latest']), person('u2', ['gemma4:latest']))
    in_use, a = InUse('qwen3.8:latest'), app()

    run(a, models, users, in_use)

    assert a.state.config.DEFAULT_MODELS == 'qwen4:latest'
    assert models.rows[TASK_MODEL_ID].base_model_id == 'qwen4:latest'
    form, owner = models.inserted[0]
    assert form.id == 'qwen4:latest' and owner == 'admin-1'
    assert form.access_grants == [
        {'principal_type': 'group', 'principal_id': 'g-accountants', 'permission': 'read'},
        {'principal_type': 'user', 'principal_id': '*', 'permission': 'read'},
    ]
    assert form.meta.capabilities == {'vision': True} and form.meta.description is None
    assert users.saved == {'u1': {'ui': {'models': ['qwen4:latest'], 'theme': 'dark'}}}
    assert in_use.value == 'qwen4:latest' and in_use.saves == 1


def test_an_admin_setup_of_the_new_model_is_kept(monkeypatch):
    monkeypatch.setenv('GNOS3_CHAT_MODEL', 'qwen4:latest')
    models = FakeModels(entry('qwen3.8:latest', grants=[('user', '*', 'read')]), entry('qwen4:latest'))
    run(app(), models, FakeUsers(), InUse('qwen3.8:latest'))
    assert models.inserted == []


def test_another_default_model_is_left_alone(monkeypatch):
    monkeypatch.setenv('GNOS3_CHAT_MODEL', 'qwen4:latest')
    a = app(default='gemma4:latest')
    run(a, FakeModels(), FakeUsers(), InUse('qwen3.8:latest'))
    assert a.state.config.DEFAULT_MODELS == 'gemma4:latest'


def test_first_start_only_records_the_model(monkeypatch):
    monkeypatch.setenv('GNOS3_CHAT_MODEL', 'qwen3.8:latest')
    models, users, in_use = FakeModels(entry(TASK_MODEL_ID, base='qwen3.8:latest')), FakeUsers(), InUse('')
    run(app(), models, users, in_use)
    assert models.updated == [] and models.inserted == [] and users.saved == {}
    assert in_use.value == 'qwen3.8:latest' and in_use.saves == 1


def test_unchanged_model_does_nothing(monkeypatch):
    monkeypatch.setenv('GNOS3_CHAT_MODEL', 'qwen3.8:latest')
    in_use = InUse('qwen3.8:latest')
    run(app(), FakeModels(), FakeUsers(), in_use)
    assert in_use.saves == 0


def test_without_the_setting_nothing_happens(monkeypatch):
    monkeypatch.delenv('GNOS3_CHAT_MODEL', raising=False)
    monkeypatch.delenv('GNOS3_EMBEDDING_MODEL', raising=False)
    in_use = InUse('qwen3.8:latest')
    run(app(), FakeModels(), FakeUsers(), in_use)
    assert in_use.saves == 0


def test_a_new_embedding_model_only_warns(monkeypatch, caplog):
    monkeypatch.delenv('GNOS3_CHAT_MODEL', raising=False)
    monkeypatch.setenv('GNOS3_EMBEDDING_MODEL', 'qwen4-embedding:latest')
    a = app()
    with caplog.at_level('WARNING'):
        run(a, FakeModels(), FakeUsers(), InUse(''))
    assert a.state.config.RAG_EMBEDDING_MODEL == 'qwen3-embedding:latest'
    assert 're-index' in caplog.text
