"""The "Anonymise" chat filter (builtin_functions/anonymise.py), without the Anonymiser service.

The service call is replaced by a fake that labels a few known values the way
the service does (same value → same label, numbered by first appearance).
"""

import asyncio
import importlib.util
import sys
import types
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[2] / 'builtin_functions' / 'anonymise.py'
KNOWN = {'Sophie Lefèvre': 'PERSON', 'Paul Rousseau': 'PERSON', 'sophie@lumen.fr': 'EMAIL'}


@pytest.fixture
def anon(monkeypatch):
    fake_auth = types.ModuleType('open_webui.utils.auth')
    fake_auth.create_token = lambda data, expires_delta=None: 'token'
    monkeypatch.setitem(sys.modules, 'open_webui.utils.auth', fake_auth)
    spec = importlib.util.spec_from_file_location('anonymise_under_test', SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_service(calls):
    async def pseudonymize(texts, user, request):
        calls.append(list(texts))
        labels, by_value, counts, out = {}, {}, {}, []
        for text in texts:
            for value, kind in sorted(KNOWN.items(), key=lambda kv: text.find(kv[0]) if kv[0] in text else 1e9):
                if value not in text:
                    continue
                if value not in by_value:
                    counts[kind] = counts.get(kind, 0) + 1
                    by_value[value] = f'[{kind}_{counts[kind]}]'
                    labels[by_value[value]] = value
                text = text.replace(value, by_value[value])
            out.append(text)
        return {'texts': out, 'labels': labels}

    return pseudonymize


def run(coro):
    return asyncio.get_event_loop_policy().new_event_loop().run_until_complete(coro)


META = {'chat_id': 'c1', 'message_id': 'm2'}


def test_restore_exact_loose_and_unknown(anon):
    labels = {'[PERSON_1]': 'Sophie Lefèvre', '[EMAIL_1]': 'sophie@lumen.fr'}
    assert anon.restore('Write to [PERSON_1] ([EMAIL_1]).', labels) == 'Write to Sophie Lefèvre (sophie@lumen.fr).'
    assert anon.restore('【PERSON_1】, ［PERSON 1］, PERSON_1', labels) == 'Sophie Lefèvre, Sophie Lefèvre, Sophie Lefèvre'
    assert anon.restore('[PERSON_9] and [Votre Nom] stay', labels) == '[PERSON_9] and [Votre Nom] stay'


def test_inlet_hides_numbers_users_first_and_adds_the_instruction(anon):
    f = anon.Filter()
    calls = []
    f._pseudonymize = fake_service(calls)
    body = {
        'messages': [
            {'role': 'system', 'content': 'You are helpful. Contact: Paul Rousseau.'},
            {'role': 'user', 'content': 'Email Sophie Lefèvre at sophie@lumen.fr'},
            {'role': 'assistant', 'content': 'Done for Sophie Lefèvre.'},
            {'role': 'user', 'content': [{'type': 'text', 'text': 'Thanks, Sophie Lefèvre will reply.'}, {'type': 'image_url', 'image_url': {'url': 'x'}}]},
        ]
    }
    out = run(f.inlet(body, {'id': 'u1'}, META, None))
    # the person's messages are sent first, the system prompt last
    assert calls[0][0].startswith('Email') and calls[0][-1].startswith('You are helpful')
    msgs = out['messages']
    assert msgs[1]['content'] == 'Email [PERSON_1] at [EMAIL_1]'
    assert msgs[2]['content'] == 'Done for [PERSON_1].'
    assert msgs[3]['content'][0]['text'] == 'Thanks, [PERSON_1] will reply.'
    assert msgs[0]['content'].startswith('You are helpful. Contact: [PERSON_2].') and anon.INSTRUCTION in msgs[0]['content']
    assert f._recall(('c1', 'm2'))['[PERSON_1]'] == 'Sophie Lefèvre'


def test_inlet_without_values_changes_nothing(anon):
    f = anon.Filter()
    f._pseudonymize = fake_service([])
    body = {'messages': [{'role': 'user', 'content': 'What is accrual accounting?'}]}
    out = run(f.inlet(body, {'id': 'u1'}, META, None))
    assert out['messages'] == [{'role': 'user', 'content': 'What is accrual accounting?'}]


def test_inlet_refuses_to_send_when_the_service_is_down(anon):
    f = anon.Filter()

    async def down(texts, user, request):
        raise Exception(anon.UNAVAILABLE['en'])

    f._pseudonymize = down
    with pytest.raises(Exception, match='was not sent'):
        run(f.inlet({'messages': [{'role': 'user', 'content': 'Email Sophie Lefèvre'}]}, {'id': 'u1'}, META, None))


def test_stream_restores_labels_split_across_chunks(anon):
    f = anon.Filter()
    f._remember(('c1', 'm2'), {'[PERSON_1]': 'Sophie Lefèvre'})
    chunks = ['Bonjour [PER', 'SON_1], voici [', 'un lien](x) pour [PERSON', '_1]', '']
    out = []
    for i, piece in enumerate(chunks):
        choice = {'delta': {'content': piece}}
        if i == len(chunks) - 1:
            choice['finish_reason'] = 'stop'
        event = f.stream({'choices': [choice]}, META)
        out.append(event['choices'][0]['delta'].get('content') or '')
    assert ''.join(out) == 'Bonjour Sophie Lefèvre, voici [un lien](x) pour Sophie Lefèvre'


def test_stream_flushes_a_held_tail_at_the_end(anon):
    f = anon.Filter()
    f._remember(('c1', 'm2'), {'[PERSON_1]': 'Sophie Lefèvre'})
    a = f.stream({'choices': [{'delta': {'content': 'Note ['}}]}, META)
    b = f.stream({'choices': [{'delta': {}, 'finish_reason': 'stop'}]}, META)
    assert a['choices'][0]['delta']['content'] + b['choices'][0]['delta']['content'] == 'Note ['


def test_outlet_restores_from_memory_then_forgets(anon):
    f = anon.Filter()
    f._remember(('c1', 'm2'), {'[PERSON_1]': 'Sophie Lefèvre'})
    body = {'messages': [{'role': 'user', 'content': 'x'}, {'role': 'assistant', 'content': 'Hi [PERSON_1]'}]}
    out = run(f.outlet(body, {'id': 'u1'}, META, None))
    assert out['messages'][-1]['content'] == 'Hi Sophie Lefèvre'
    assert f._recall(('c1', 'm2')) is None


def test_outlet_without_the_table_leaves_labels_alone(anon):
    f = anon.Filter()
    calls = []
    f._pseudonymize = fake_service(calls)
    body = {'messages': [{'role': 'user', 'content': 'Email Sophie Lefèvre'}, {'role': 'assistant', 'content': 'Mail for [PERSON_1]'}]}
    out = run(f.outlet(body, {'id': 'u1'}, META, None))
    assert calls == [] and out['messages'][-1]['content'] == 'Mail for [PERSON_1]'
