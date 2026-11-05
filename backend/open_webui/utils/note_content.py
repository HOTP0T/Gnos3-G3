"""Reading a note's content for the Notes vault: links, tags, Gnos3 data references, text.

A note's body is the editor's ProseMirror JSON (`data.content.json`) when the note was saved by the
editor, or only Markdown (`data.content.md`) when it was created by the server (import, a chat answer
saved as a note, a template) and not opened since. Both are read here into the same shape:

    {
        'links':    [{'note_id' | None, 'title', 'heading', 'alias', 'context'}],   # [[wikilinks]]
        'entities': [{'entity_type', 'entity_id', 'label', 'context'}],            # links to Gnos3 data
        'tags':     ['project/alpha', ...],
        'text':     'plain text',
    }

Markdown forms (what the editor writes, what export writes, what import reads):

    [[Title]]  [[Title|shown text]]  [[Title#Heading]]       wikilink
    [Label](/accounting/company/12/dashboard)                  Gnos3 data (see ENTITY_ROUTES)
    #tag  #nested/tag                                          tag
    ---\\nkey: value\\n---                                       frontmatter (properties)

This module imports nothing from the app so its tests load it alone.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Optional
from urllib.parse import parse_qs, urlparse

import yaml

# ---------------------------------------------------------------------------
# Titles
# ---------------------------------------------------------------------------

TITLE_MAX = 200
# Characters a title cannot carry in a [[link]] or a file name.
_TITLE_FORBIDDEN = re.compile(r'[\[\]|#^\\/:*?"<>\n\r\t]')


def normalize_title(title: Optional[str]) -> str:
    """The key two titles are compared by (case and surrounding spaces ignored)."""
    return re.sub(r'\s+', ' ', (title or '').strip()).casefold()


def clean_title(title: Optional[str]) -> str:
    """A title safe for [[links]] and exported file names."""
    cleaned = _TITLE_FORBIDDEN.sub(' ', title or '')
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned[:TITLE_MAX]


def clean_folder(path: Optional[str]) -> str:
    """'/a//b/ ' -> 'a/b'. Folders are plain paths; '' is the vault root."""
    parts = []
    for part in (path or '').replace('\\', '/').split('/'):
        part = _TITLE_FORBIDDEN.sub(' ', part)
        part = re.sub(r'\s+', ' ', part).strip()
        if part and part not in ('.', '..'):
            parts.append(part[:120])
    return '/'.join(parts)


def folder_parents(path: str) -> list[str]:
    """'a/b/c' -> ['a', 'a/b', 'a/b/c']."""
    parts = [p for p in path.split('/') if p]
    return ['/'.join(parts[: i + 1]) for i in range(len(parts))]


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

# A tag starts after the start of text, a space or an opening bracket/punctuation, so URL anchors
# (example.com/#part) and headings ("# Title") are not tags. Letters of any script, digits, _ - /.
_TAG_RE = re.compile(r'(?:^|(?<=[\s(\[{,;:!?。，、；：！？（【「]))#([^\W][\w\-/]*|_[\w\-/]*)', re.UNICODE)


def find_tags(text: str) -> list[str]:
    tags = []
    for match in _TAG_RE.finditer(text or ''):
        tag = match.group(1).strip('/').strip('-')
        if not tag or tag.replace('/', '').isdigit():
            continue
        tags.append(tag)
    return tags


def clean_tag(tag: Any) -> str:
    tag = str(tag or '').strip().lstrip('#').strip('/')
    tag = re.sub(r'\s+', '-', tag)
    return tag[:100]


# ---------------------------------------------------------------------------
# Gnos3 data references
# ---------------------------------------------------------------------------

# entity type -> how its app URL looks. The frontend has the same table (vault/entities.ts).
ENTITY_TYPES = ('company', 'invoice', 'business_card', 'document', 'chat')

_ENTITY_PATTERNS = [
    ('company', re.compile(r'^/accounting/company/(\d+)(?:/|$)')),
    ('chat', re.compile(r'^/c/([0-9a-fA-F-]{8,})$')),
]


def entity_href(entity_type: str, entity_id: str) -> str:
    if entity_type == 'company':
        return f'/accounting/company/{entity_id}/dashboard'
    if entity_type == 'invoice':
        return f'/invoices/data?invoice={entity_id}'
    if entity_type == 'business_card':
        return f'/business-cards/data?card={entity_id}'
    if entity_type == 'document':
        return f'/api/v1/auths/k4mi/open?doc_id={entity_id}'
    if entity_type == 'chat':
        return f'/c/{entity_id}'
    return ''


def parse_entity_href(href: Optional[str]) -> Optional[tuple[str, str]]:
    """'/accounting/company/12/dashboard' -> ('company', '12'). Absolute URLs on any host count too:
    a link copied from the browser carries the box's address."""
    if not href:
        return None
    parsed = urlparse(href.strip())
    path = parsed.path or ''
    query = parse_qs(parsed.query)
    for entity_type, pattern in _ENTITY_PATTERNS:
        match = pattern.match(path)
        if match:
            return entity_type, match.group(1)
    if path.rstrip('/') == '/invoices/data' and query.get('invoice'):
        return 'invoice', query['invoice'][0]
    if path.rstrip('/') == '/business-cards/data' and query.get('card'):
        return 'business_card', query['card'][0]
    if path.rstrip('/') == '/api/v1/auths/k4mi/open' and query.get('doc_id'):
        return 'document', query['doc_id'][0]
    return None


# ---------------------------------------------------------------------------
# Wikilinks in Markdown
# ---------------------------------------------------------------------------

_WIKILINK_RE = re.compile(r'(!?)\[\[([^\[\]\n]+?)\]\]')
_MD_LINK_RE = re.compile(r'(?<!!)\[([^\]\n]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
_FENCE_RE = re.compile(r'^(```|~~~).*?^\1[ \t]*$', re.MULTILINE | re.DOTALL)
_INLINE_CODE_RE = re.compile(r'`[^`\n]*`')


def split_wikilink(inner: str) -> dict:
    """'Title#Heading|shown' -> {'title': 'Title', 'heading': 'Heading', 'alias': 'shown'}.
    A pipe escaped for a Markdown table (\\|) counts as a pipe."""
    inner = inner.replace('\\|', '|')
    alias = None
    if '|' in inner:
        inner, alias = inner.split('|', 1)
        alias = alias.strip() or None
    heading = None
    if '#' in inner:
        inner, heading = inner.split('#', 1)
        heading = heading.strip() or None
    title = inner.strip()
    # A link to a file in a vault folder ("Projects/Alpha") points at the note "Alpha".
    if '/' in title:
        title = title.rsplit('/', 1)[1].strip()
    if title.lower().endswith('.md'):
        title = title[:-3]
    return {'title': title, 'heading': heading, 'alias': alias}


def format_wikilink(title: str, heading: Optional[str] = None, alias: Optional[str] = None) -> str:
    inner = title
    if heading:
        inner += f'#{heading}'
    if alias and alias != title:
        inner += f'|{alias}'
    return f'[[{inner}]]'


def _strip_code(md: str) -> str:
    md = _FENCE_RE.sub(' ', md)
    return _INLINE_CODE_RE.sub(' ', md)


def _shorten(line: str, limit: int = 240) -> str:
    line = re.sub(r'\s+', ' ', line).strip()
    return line if len(line) <= limit else line[: limit - 1].rstrip() + '…'


def clean_context(line: str) -> str:
    """A Markdown line as plain text, keeping [[links]] (the page highlights them)."""
    line = re.sub(r'^\s{0,3}(#{1,6}|>|[-*+]\s+\[[ xX]\]|[-*+]|\d+[.)])\s+', '', line)
    line = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', line)
    line = _MD_LINK_RE.sub(lambda m: m.group(1), line)
    line = re.sub(r'(\*\*|__|~~|==)(\S.*?\S|\S)\1', r'\2', line)
    return line.strip()


def _context_around(text: str, start: int, end: int, width: int = 110) -> str:
    left = text.rfind('\n', 0, start)
    right = text.find('\n', end)
    line = text[left + 1 : right if right != -1 else len(text)]
    offset = start - (left + 1)
    if len(line) > width * 2:
        lo = max(0, offset - width)
        line = ('…' if lo else '') + line[lo : offset + width] + ('…' if offset + width < len(line) else '')
    return _shorten(clean_context(line))


def read_markdown(md: str) -> dict:
    """Links, Gnos3 data references and tags written in Markdown."""
    md = md or ''
    _, body = split_frontmatter(md)
    scan = _strip_code(body)

    links = []
    for match in _WIKILINK_RE.finditer(scan):
        parts = split_wikilink(match.group(2))
        if not parts['title']:
            continue
        links.append(
            {
                'note_id': None,
                **parts,
                'embed': bool(match.group(1)),
                'context': _context_around(scan, match.start(), match.end()),
            }
        )

    entities = []
    for match in _MD_LINK_RE.finditer(scan):
        found = parse_entity_href(match.group(2))
        if found:
            entities.append(
                {
                    'entity_type': found[0],
                    'entity_id': found[1],
                    'label': match.group(1).strip() or None,
                    'context': _context_around(scan, match.start(), match.end()),
                }
            )

    # Tags: not inside link targets or wikilinks.
    tag_scan = _WIKILINK_RE.sub(' ', _MD_LINK_RE.sub(lambda m: m.group(1), scan))
    tags = find_tags(tag_scan)
    text = markdown_to_text(body)
    return {'links': links, 'entities': entities, 'tags': tags, 'text': text}


def markdown_to_text(md: str) -> str:
    text = _FENCE_RE.sub(lambda m: m.group(0).strip('`~'), md or '')
    text = _WIKILINK_RE.sub(lambda m: split_wikilink(m.group(2))['alias'] or split_wikilink(m.group(2))['title'], text)
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', text)
    text = _MD_LINK_RE.sub(lambda m: m.group(1), text)
    text = re.sub(r'^\s{0,3}(#{1,6}|>|[-*+]\s+\[[ xX]\]|[-*+]|\d+[.)])\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'(\*\*|__|~~|==|\*|_)(\S.*?\S|\S)\1', r'\2', text)
    text = re.sub(r'<[^>\n]+>', ' ', text)
    return re.sub(r'[ \t]+', ' ', text).strip()


# ---------------------------------------------------------------------------
# ProseMirror JSON (what the editor saves)
# ---------------------------------------------------------------------------

# Blocks whose children are inline content (text, links). Containers (lists, quotes, tables) only
# hold these, so walking them is enough.
_TEXT_BLOCKS = {'paragraph', 'heading', 'codeBlock'}


def read_document(doc: Optional[dict]) -> dict:
    """Links, Gnos3 data references, tags and text from the editor's JSON."""
    links: list[dict] = []
    entities: list[dict] = []
    tags: list[str] = []
    blocks: list[str] = []

    def inline(node: dict, parts: list, found: list, in_code: bool, ctx: list) -> None:
        node_type = node.get('type')
        attrs = node.get('attrs') or {}
        if node_type == 'text':
            marks = node.get('marks') or []
            text = node.get('text') or ''
            for mark in marks:
                if mark.get('type') == 'link':
                    hit = parse_entity_href((mark.get('attrs') or {}).get('href'))
                    if hit:
                        item = {'entity_type': hit[0], 'entity_id': hit[1], 'label': text, 'context': None}
                        entities.append(item)
                        found.append(item)
            ctx.append(text)
            if in_code or any(mark.get('type') == 'code' for mark in marks):
                # Code is shown, but a #word inside it is not a tag.
                text = text.replace('#', '\uff03')
            parts.append(text)
        elif node_type == 'wikiLink':
            title = (attrs.get('title') or '').strip()
            item = {
                'note_id': attrs.get('noteId') or None,
                'title': title,
                'heading': attrs.get('heading') or None,
                'alias': attrs.get('alias') or None,
                'embed': False,
                'context': None,
            }
            if title or item['note_id']:
                links.append(item)
                found.append(item)
            # Kept out of the tag scan: a title may contain '#'.
            parts.append((attrs.get('alias') or title).replace('#', '\uff03'))
            ctx.append(format_wikilink(title, None, attrs.get('alias')) if title else '')
        elif node_type == 'entityRef':
            entity_type = attrs.get('entityType')
            entity_id = attrs.get('entityId')
            if entity_type in ENTITY_TYPES and entity_id not in (None, ''):
                item = {
                    'entity_type': entity_type,
                    'entity_id': str(entity_id),
                    'label': attrs.get('label') or None,
                    'context': None,
                }
                entities.append(item)
                found.append(item)
            parts.append((attrs.get('label') or '').replace('#', '\uff03'))
            ctx.append(attrs.get('label') or '')
        elif node_type == 'hardBreak':
            parts.append(' ')
            ctx.append(' ')
        else:
            for child in node.get('content') or []:
                inline(child, parts, found, in_code, ctx)

    def walk(node: dict) -> None:
        node_type = node.get('type')
        if node_type in _TEXT_BLOCKS:
            parts: list[str] = []
            ctx: list[str] = []
            found: list[dict] = []
            for child in node.get('content') or []:
                inline(child, parts, found, node_type == 'codeBlock', ctx)
            text = ''.join(parts).strip()
            context = ''.join(ctx).strip()
            for item in found:
                item['context'] = _shorten(context)
            if node_type != 'codeBlock':
                tags.extend(find_tags(text))
            if text:
                blocks.append(text)
            return
        for child in node.get('content') or []:
            if isinstance(child, dict):
                walk(child)

    if isinstance(doc, dict):
        walk(doc)

    text = '\n'.join(blocks).replace('\uff03', '#')
    return {'links': links, 'entities': entities, 'tags': tags, 'text': text}


def read_note_content(data: Optional[dict]) -> dict:
    """The editor's JSON when present, else the Markdown."""
    content = ((data or {}).get('content') or {}) if isinstance(data, dict) else {}
    doc = content.get('json')
    if isinstance(doc, dict) and doc.get('type') == 'doc':
        result = read_document(doc)
        # Frontmatter is never in the editor's JSON; Markdown-only links (pasted text the editor did not
        # turn into nodes) still count.
        md_result = read_markdown(content.get('md') or '')
        known = {(link['note_id'], normalize_title(link['title'])) for link in result['links']}
        for link in md_result['links']:
            if (None, normalize_title(link['title'])) not in known and not any(
                normalize_title(existing['title']) == normalize_title(link['title']) for existing in result['links']
            ):
                result['links'].append(link)
        return result
    return read_markdown(content.get('md') or '')


def word_count(text: str) -> int:
    """Words in Latin scripts; each CJK character counts as a word, as in most editors."""
    cjk = len(re.findall(r'[぀-ヿ㐀-䶿一-鿿가-힯]', text or ''))
    latin = len(re.findall(r'[^\s぀-ヿ㐀-䶿一-鿿가-힯]+', text or ''))
    return cjk + latin


def excerpt(text: str, length: int = 180) -> str:
    text = re.sub(r'\s+', ' ', text or '').strip()
    return text if len(text) <= length else text[: length - 1].rstrip() + '…'


def dedupe(items: Iterable[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        key = item.casefold()
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


# ---------------------------------------------------------------------------
# Properties and frontmatter
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r'\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)', re.DOTALL)


def split_frontmatter(md: str) -> tuple[Optional[str], str]:
    match = _FRONTMATTER_RE.match(md or '')
    if not match:
        return None, md or ''
    return match.group(1), (md or '')[match.end() :]


def property_note_refs(value: Any) -> list[dict]:
    """Note references held by a property value: {'id', 'title'} objects, or "[[Title]]" strings
    (as imported from a vault before resolution)."""
    refs = []
    values = value if isinstance(value, list) else [value]
    for item in values:
        if isinstance(item, dict) and (item.get('id') or item.get('title')):
            refs.append({'note_id': item.get('id') or None, 'title': (item.get('title') or '').strip()})
        elif isinstance(item, str):
            match = _WIKILINK_RE.fullmatch(item.strip())
            if match:
                parts = split_wikilink(match.group(2))
                refs.append({'note_id': None, 'title': parts['title']})
    return [ref for ref in refs if ref['note_id'] or ref['title']]


def _yaml_value(value: Any, titles: dict[str, str]) -> Any:
    """A property value as written in exported frontmatter."""
    if isinstance(value, list):
        return [_yaml_value(item, titles) for item in value]
    if isinstance(value, dict) and (value.get('id') or value.get('title')):
        title = titles.get(value.get('id') or '', value.get('title') or '')
        return format_wikilink(title)
    if isinstance(value, dict) and value.get('entity_type'):
        return entity_href(value['entity_type'], str(value.get('entity_id')))
    return value


def render_frontmatter(properties: Optional[dict], titles: Optional[dict[str, str]] = None) -> str:
    """Properties as a YAML block ('' when there are none). `titles` maps note ids to current
    titles so a relation exports as the target's current name."""
    props = {key: value for key, value in (properties or {}).items() if value not in (None, '', [], {})}
    if not props:
        return ''
    titles = titles or {}
    out = {key: _yaml_value(value, titles) for key, value in props.items()}
    body = yaml.safe_dump(out, allow_unicode=True, sort_keys=False, default_flow_style=False).strip()
    return f'---\n{body}\n---\n'


_RESERVED_KEYS = {'title'}


def parse_frontmatter(md: str) -> tuple[dict, str]:
    """(properties, body). Unreadable YAML is kept in the body rather than lost."""
    block, body = split_frontmatter(md)
    if block is None:
        return {}, md or ''
    try:
        loaded = yaml.safe_load(block)
    except yaml.YAMLError:
        return {}, md or ''
    if not isinstance(loaded, dict):
        return {}, body
    props: dict = {}
    for key, value in loaded.items():
        key = str(key).strip()
        if not key or key in _RESERVED_KEYS:
            continue
        if key in ('tags', 'tag'):
            values = value if isinstance(value, list) else re.split(r'[,\s]+', str(value or ''))
            props['tags'] = dedupe([clean_tag(v) for v in values if clean_tag(v)])
            continue
        if key in ('aliases', 'alias'):
            values = value if isinstance(value, list) else [value]
            props['aliases'] = [str(v).strip() for v in values if str(v or '').strip()]
            continue
        props[key] = _plain(value)
    return props, body


def _plain(value: Any) -> Any:
    """YAML dates and other objects as JSON-safe values."""
    if isinstance(value, list):
        return [_plain(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return str(value)


def property_tags(properties: Optional[dict]) -> list[str]:
    value = (properties or {}).get('tags') or []
    values = value if isinstance(value, list) else [value]
    return [clean_tag(v) for v in values if clean_tag(v)]


def property_aliases(properties: Optional[dict]) -> list[str]:
    value = (properties or {}).get('aliases') or []
    values = value if isinstance(value, list) else [value]
    return [str(v).strip() for v in values if str(v or '').strip()]


# ---------------------------------------------------------------------------
# Mentions of a title in text (unlinked mentions)
# ---------------------------------------------------------------------------

_CJK_RE = re.compile(r'[぀-ヿ㐀-䶿一-鿿가-힯]')


def mention_pattern(title: str) -> Optional[re.Pattern]:
    """A pattern finding `title` as a whole word (CJK titles: anywhere, scripts without spaces)."""
    title = (title or '').strip()
    if len(title) < 3 and not _CJK_RE.search(title):
        return None
    if len(title) < 2:
        return None
    escaped = re.escape(title)
    if _CJK_RE.search(title):
        return re.compile(escaped, re.IGNORECASE)
    return re.compile(rf'(?<![\w]){escaped}(?![\w])', re.IGNORECASE)


def find_mentions(text: str, titles: list[str], limit: int = 3) -> list[str]:
    """Context snippets where any of `titles` appears in `text` outside a [[link]]."""
    text = _WIKILINK_RE.sub(lambda m: ' ' * len(m.group(0)), text or '')
    contexts = []
    for title in titles:
        pattern = mention_pattern(title)
        if not pattern:
            continue
        for match in pattern.finditer(text):
            contexts.append(_context_around(text, match.start(), match.end()))
            if len(contexts) >= limit:
                return contexts
    return contexts


def markdown_with_link_titles(md: str, renamed: dict[str, str]) -> str:
    """Rewrite [[Old title...]] to [[New title...]] (keys normalized old titles)."""
    if not renamed:
        return md

    def repl(match: re.Match) -> str:
        parts = split_wikilink(match.group(2))
        new = renamed.get(normalize_title(parts['title']))
        if not new:
            return match.group(0)
        return match.group(1) + format_wikilink(new, parts['heading'], parts['alias'])

    return _WIKILINK_RE.sub(repl, md or '')
