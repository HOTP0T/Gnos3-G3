"""
title: Anonymise
author: Gnos3
description: Hides names, contact details and ID or bank numbers from the AI, then puts them back in its answer. Runs on the box (Anonymiser module).
version: 0.1.0
"""

# Shipped with Gnos3 and installed on startup by utils/anonymiser_seed.py as the
# global toggle filter `gnos3_anonymise` (the "Anonymise" switch under the
# message box). Edits made in Admin → Functions are overwritten by the next
# Gnos3 version; change this file instead.
#
# What it covers: the text of the conversation (the person's messages, earlier
# answers, earlier tool results, the system prompt). It runs before Gnos3 adds
# document / knowledge excerpts, memories and web results, so those reach the
# model as they are. Web searches are written from the hidden text, so a
# hidden name is not searched for.
#
# How: inlet sends the texts to the Anonymiser (POST /api/anonymiser/pseudonymize),
# which replaces each detected value with a label — the same value always gets
# the same label, e.g. [PERSON_1] — and returns the label → value table. The
# model is told to copy labels verbatim. The answer is restored while it
# streams (stream) and once more when it is saved (outlet). The table is kept
# in memory for that one answer only; nothing is stored. A value found in one
# message is hidden in every message of the conversation.

import base64
import logging
import os
import re
import time
from datetime import timedelta
from typing import Optional

import httpx
from pydantic import BaseModel, Field

from open_webui.utils.auth import create_token

log = logging.getLogger(__name__)

LABEL_NAMES = 'PERSON|EMAIL|PHONE|IBAN|CARD|ID|IP|ORG|PLACE|DATE|URL|HIDDEN'
EXACT = re.compile(rf'\[(?:{LABEL_NAMES})_\d+\]')
# A label the model wrote a little differently: other brackets, a space or
# dash instead of the underscore, or no brackets at all.
LOOSE = re.compile(rf'[\[［【<]\s*({LABEL_NAMES})[\s_\-]?(\d+)\s*[\]］】>]|\b({LABEL_NAMES})_(\d+)\b')
# The start of a label cut off at the end of a streamed chunk: "[PER", "[PERSON_1".
PARTIAL = re.compile(r'[\[［【<][A-Z]{0,6}(?:_\d{0,3})?$')

INSTRUCTION = (
    "Some details in this conversation were replaced by placeholders such as [PERSON_1] or "
    "[EMAIL_1] to protect privacy. Treat each placeholder as the real value. When you need it "
    "in your answer, write the placeholder exactly as it appears, including the square brackets. "
    "Never guess or invent the hidden value."
)

# Shown in the chat when the Anonymiser can't be reached. The message is NOT
# sent to the model then: with the switch on, nothing leaves unhidden.
UNAVAILABLE = {
    'en': 'Anonymise is on, but the Anonymiser could not be reached, so your message was not sent. Try again, or turn Anonymise off.',
    'fr': "Anonymiser est activé, mais l'Anonymiseur est injoignable : votre message n'a pas été envoyé. Réessayez, ou désactivez Anonymiser.",
    'es': 'Anonimizar está activado, pero no se pudo contactar con el Anonimizador: su mensaje no se ha enviado. Inténtelo de nuevo o desactive Anonimizar.',
    'pt': 'Anonimizar está ativado, mas não foi possível contactar o Anonimizador: a sua mensagem não foi enviada. Tente novamente ou desative Anonimizar.',
    'zh-CN': '已开启匿名化，但无法连接匿名化工具，消息未发送。请重试，或关闭匿名化。',
    'zh-TW': '已開啟匿名化，但無法連線匿名化工具，訊息未傳送。請重試，或關閉匿名化。',
}

_ICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1'
    'c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>'
    '<path d="m9 12 2 2 4-4"/></svg>'
)

_TTL = 3600


def restore(text: str, labels: dict) -> str:
    """Put the original values back in place of the labels the model wrote."""
    if not text or not labels:
        return text
    text = EXACT.sub(lambda m: labels.get(m.group(0), m.group(0)), text)

    def loose(m: re.Match) -> str:
        name, num = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        return labels.get(f'[{name}_{num}]', m.group(0))

    return LOOSE.sub(loose, text)


def _reader_language(request) -> str:
    try:
        header = (request.headers.get('accept-language') or '').split(',')[0].strip().lower()
    except Exception:
        return 'en'
    if header.startswith('zh'):
        return 'zh-TW' if any(x in header for x in ('tw', 'hk', 'mo', 'hant')) else 'zh-CN'
    return header[:2] if header[:2] in UNAVAILABLE else 'en'


def _text_slots(messages: list, roles: tuple) -> list:
    """(message index, part index or None, text) for every text in those roles, in order."""
    out = []
    for i, message in enumerate(messages):
        if message.get('role') not in roles:
            continue
        content = message.get('content')
        if isinstance(content, str):
            out.append((i, None, content))
        elif isinstance(content, list):
            for j, part in enumerate(content):
                if isinstance(part, dict) and part.get('type') == 'text' and isinstance(part.get('text'), str):
                    out.append((i, j, part['text']))
    return out


class Filter:
    class Valves(BaseModel):
        priority: int = Field(default=-100, description='Runs before other filters.')
        anonymiser_url: str = Field(
            default=os.environ.get('ANONYMISER_MODULE_URL', 'http://anon-api:8005'),
            description='Anonymiser service, as Gnos3 reaches it.',
        )
        timeout_seconds: float = Field(default=30.0)

    def __init__(self):
        self.valves = self.Valves()
        self.toggle = True
        self.icon = 'data:image/svg+xml;base64,' + base64.b64encode(_ICON.encode()).decode()
        self._labels: dict = {}  # (chat_id, message_id) → (time, label table)
        self._held: dict = {}  # (chat_id, message_id, field) → text held back mid-label

    # ── helpers ──────────────────────────────────────────────────────────
    @staticmethod
    def _key(metadata: Optional[dict]) -> Optional[tuple]:
        if not metadata or not metadata.get('message_id'):
            return None
        return metadata.get('chat_id') or '', metadata['message_id']

    def _remember(self, key: Optional[tuple], labels: dict) -> None:
        now = time.time()
        for k in [k for k, (t, _) in self._labels.items() if now - t > _TTL]:
            self._labels.pop(k, None)
        if key:
            self._labels[key] = (now, labels)

    def _recall(self, key: Optional[tuple]) -> Optional[dict]:
        entry = self._labels.get(key) if key else None
        return entry[1] if entry else None

    async def _pseudonymize(self, texts: list, user: dict, request) -> dict:
        token = create_token({'id': user['id']}, timedelta(minutes=5))
        lang = _reader_language(request)
        try:
            async with httpx.AsyncClient(timeout=self.valves.timeout_seconds) as client:
                r = await client.post(
                    f"{self.valves.anonymiser_url.rstrip('/')}/api/anonymiser/pseudonymize",
                    json={'texts': texts},
                    headers={'Authorization': f'Bearer {token}', 'X-Gnos3-Lang': lang},
                )
        except Exception as exc:
            log.warning(f'Anonymise: Anonymiser unreachable: {exc}')
            raise Exception(UNAVAILABLE[lang])
        if r.status_code != 200:
            detail = ''
            try:
                detail = r.json().get('detail') or ''
            except Exception:
                pass
            log.warning(f'Anonymise: Anonymiser answered {r.status_code}')
            raise Exception(f'{UNAVAILABLE[lang]} {detail}'.strip())
        return r.json()

    # ── hooks ────────────────────────────────────────────────────────────
    async def inlet(self, body: dict, __user__: dict = None, __metadata__: dict = None, __request__=None) -> dict:
        messages = body.get('messages') or []
        # The person's messages first, the system prompt last: labels are
        # numbered in order of first appearance, so the person's values get the
        # low numbers.
        slots = (
            _text_slots(messages, ('user',))
            + _text_slots(messages, ('assistant', 'tool'))
            + _text_slots(messages, ('system', 'developer'))
        )
        if not any(text.strip() for _, _, text in slots):
            return body

        result = await self._pseudonymize([text for _, _, text in slots], __user__ or {}, __request__)
        for (i, j, _), text in zip(slots, result.get('texts') or []):
            if j is None:
                messages[i]['content'] = text
            else:
                messages[i]['content'][j]['text'] = text

        labels = result.get('labels') or {}
        if labels:
            system = next((m for m in messages if m.get('role') == 'system' and isinstance(m.get('content'), str)), None)
            if system is not None:
                system['content'] = f"{system['content']}\n\n{INSTRUCTION}"
            else:
                messages.insert(0, {'role': 'system', 'content': INSTRUCTION})
        self._remember(self._key(__metadata__), labels)
        log.info(f'Anonymise: {len(slots)} texts, {len(labels)} values hidden')
        return body

    def stream(self, event: dict, __metadata__: dict = None) -> dict:
        key = self._key(__metadata__)
        labels = self._recall(key)
        if not labels:
            return event
        for choice in event.get('choices') or []:
            delta = choice.get('delta') or {}
            for field in ('content', 'reasoning_content'):
                piece = delta.get(field)
                if not isinstance(piece, str):
                    continue
                text = self._held.pop((*key, field), '') + piece
                cut = PARTIAL.search(text)
                if cut and not choice.get('finish_reason'):
                    self._held[(*key, field)] = text[cut.start():]
                    text = text[: cut.start()]
                delta[field] = restore(text, labels)
            if choice.get('finish_reason'):
                held = self._held.pop((*key, 'content'), '')
                if held:
                    delta['content'] = (delta.get('content') or '') + restore(held, labels)
                    choice['delta'] = delta
        return event

    async def outlet(self, body: dict, __user__: dict = None, __metadata__: dict = None, __request__=None) -> dict:
        messages = body.get('messages') or []
        if not messages or messages[-1].get('role') != 'assistant':
            return body
        key = self._key(__metadata__) or ((body.get('chat_id') or ''), body.get('id'))
        labels = self._recall(key)
        if labels is None:
            # Inlet ran in another worker: the streamed answer was restored
            # there. Rebuilding the table could number labels differently and
            # put a wrong name back, so leave any label as it is.
            return body
        last = messages[-1]
        if isinstance(last.get('content'), str):
            last['content'] = restore(last['content'], labels)
        self._labels.pop(key, None)
        for field in ('content', 'reasoning_content'):
            self._held.pop((*key, field), None)
        return body
