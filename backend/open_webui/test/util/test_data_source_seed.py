"""A new box gets the data sources of the modules it runs (utils/data_source_seed.py).

K4mi Documents, Accounting & Invoices and Business Card Database are created
once each, owned by the superadmin, their knowledge bases readable by the
groups that already see that data. A box that has one keeps it, a deleted one
stays deleted, and a module that starts later still gets its source.

No database: users, groups, connectors and the knowledge base are fakes.
"""

import asyncio
import sys
from types import ModuleType, SimpleNamespace

import pytest

from open_webui.connectors.k4mi import K4miConnector
from open_webui.utils import data_source_seed as seed
from open_webui.utils.rbac_seed import _GROUP_PERMS

GROUPS = [SimpleNamespace(id=f'g-{name}', name=name, permissions=perms) for name, perms in _GROUP_PERMS.items()]


class Seeded:
    def __init__(self, value=()):
        self.value = list(value)

    async def async_save(self):
        pass


class FakeConnectors:
    def __init__(self, *types):
        self.rows = [SimpleNamespace(id=f'c-{t}', connector_type=t, form=None) for t in types]

    def get_connectors(self):
        return list(self.rows)

    def insert_new_connector(self, user_id, form_data):
        row = SimpleNamespace(id=f'c-{form_data.connector_type}', connector_type=form_data.connector_type,
                              user_id=user_id, form=form_data)
        self.rows.append(row)
        return row


@pytest.fixture
def box(monkeypatch):
    """A box with a superadmin, the seed groups and every module answering."""
    state = SimpleNamespace(
        seeded=Seeded(), connectors=FakeConnectors(), knowledge={}, up={seed.INVOICES_URL, seed.BUSINESS_CARDS_URL},
        owner=SimpleNamespace(id='super-1'),
    )

    async def answers(url):
        return url in state.up

    async def ensure_knowledge_base(connector, user_id, access_grants=None):
        state.knowledge[connector.connector_type] = (user_id, access_grants)
        return f'kb-{connector.connector_type}'

    async def super_admin():
        return state.owner

    async def all_groups():
        return GROUPS

    async def no_op():
        pass

    services = ModuleType('open_webui.services.data_connector')
    services._ensure_knowledge_base = ensure_knowledge_base
    monkeypatch.setitem(sys.modules, 'open_webui.services.data_connector', services)
    monkeypatch.setattr(seed, 'SEEDED', state.seeded)
    monkeypatch.setattr(seed, 'DataConnectors', state.connectors)
    monkeypatch.setattr(seed, 'Users', SimpleNamespace(get_super_admin_user=super_admin))
    monkeypatch.setattr(seed, 'Groups', SimpleNamespace(get_all_groups=all_groups))
    monkeypatch.setattr(seed, 'ensure_default_rbac_groups', no_op)
    monkeypatch.setattr(seed, '_answers', answers)
    monkeypatch.setenv('K4MI_API_TOKEN', 'token-from-env')
    monkeypatch.setenv('K4MI_LINK_URL', 'http://box.local:8000/')
    return state


def run():
    asyncio.run(seed.ensure_default_data_sources())


def created(state):
    return {c.connector_type: c.form for c in state.connectors.rows if c.form}


def readers(state, kind):
    return sorted(g['principal_id'] for g in state.knowledge[kind][1])


def test_a_new_box_gets_the_three_sources(box):
    run()

    forms = created(box)
    assert set(forms) == {'k4mi', 'invoice_db', 'business_card_db'}
    assert forms['k4mi'].config == {'base_url': 'http://k4mi:8000', 'public_url': 'http://box.local:8000',
                                    'use_ocr_text': True}
    assert 'api_token' not in forms['k4mi'].config  # every signed-in user can read a source's settings
    assert forms['invoice_db'].config['api_base_url'] == 'http://invoice-api:8001'
    assert forms['business_card_db'].config == {'api_base_url': 'http://bc-api:8002'}
    assert all(c.user_id == 'super-1' for c in box.connectors.rows)
    assert box.seeded.value == ['k4mi', 'invoice_db', 'business_card_db']


def test_each_knowledge_base_is_read_by_the_groups_that_see_that_data(box):
    run()

    assert readers(box, 'k4mi') == ['g-Accountants', 'g-Admins', 'g-Document Operators', 'g-Viewers']
    # Journal entries and payments too: invoice readers without accounting do not get it.
    assert readers(box, 'invoice_db') == ['g-Accountants', 'g-Admins', 'g-Viewers']
    assert readers(box, 'business_card_db') == ['g-Admins', 'g-Document Operators', 'g-Viewers']
    assert all(g['permission'] == 'read' and g['principal_type'] == 'group'
               for kind in box.knowledge for g in box.knowledge[kind][1])


def test_nothing_before_the_first_account(box):
    box.owner = None
    run()
    assert created(box) == {} and box.seeded.value == []


def test_only_the_modules_the_box_runs(box, monkeypatch):
    box.up = {seed.INVOICES_URL}
    monkeypatch.delenv('K4MI_API_TOKEN')
    run()
    assert set(created(box)) == {'invoice_db'}

    # The business cards start later; the token arrives with the next update.
    box.up.add(seed.BUSINESS_CARDS_URL)
    monkeypatch.setenv('K4MI_API_TOKEN', 'token-from-env')
    run()
    assert set(created(box)) == {'invoice_db', 'business_card_db', 'k4mi'}


def test_a_source_added_by_hand_is_kept(box, monkeypatch):
    box.connectors = FakeConnectors('k4mi')
    monkeypatch.setattr(seed, 'DataConnectors', box.connectors)
    run()
    assert set(created(box)) == {'invoice_db', 'business_card_db'}
    assert 'k4mi' in box.seeded.value


def test_a_deleted_source_stays_deleted(box):
    box.seeded.value = ['k4mi', 'invoice_db', 'business_card_db']
    run()
    assert created(box) == {}


def test_the_k4mi_connector_reads_the_token_from_the_environment(monkeypatch):
    monkeypatch.setenv('K4MI_API_TOKEN', 'token-from-env')
    assert K4miConnector({'base_url': 'http://k4mi:8000'}).api_token == 'token-from-env'
    assert K4miConnector({'base_url': 'http://k4mi:8000', 'api_token': 'own'}).api_token == 'own'
    assert 'api_token' not in K4miConnector.config_schema()['required']
