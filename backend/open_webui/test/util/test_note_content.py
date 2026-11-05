"""Reading notes for the Notes vault (utils/note_content.py): links, tags, Gnos3 data, frontmatter.

Run: cd Gnos3/backend && ../venv/bin/python -m pytest open_webui/test/util/test_note_content.py -q
"""

from open_webui.utils import note_content as nc


def doc(*blocks):
    return {'type': 'doc', 'content': list(blocks)}


def p(*inline):
    return {'type': 'paragraph', 'content': list(inline)}


def text(value, *marks):
    node = {'type': 'text', 'text': value}
    if marks:
        node['marks'] = list(marks)
    return node


def wikilink(title, note_id=None, alias=None):
    return {'type': 'wikiLink', 'attrs': {'noteId': note_id, 'title': title, 'alias': alias}}


# --- titles and folders -----------------------------------------------------


def test_titles_compare_without_case_or_spaces():
    assert nc.normalize_title('  Alice   Martin ') == nc.normalize_title('alice martin')


def test_clean_title_drops_link_breaking_characters():
    assert nc.clean_title('a [b] | c # d / e') == 'a b c d e'


def test_clean_folder():
    assert nc.clean_folder('/Projects//2026/../Q4 ') == 'Projects/2026/Q4'
    assert nc.folder_parents('a/b/c') == ['a', 'a/b', 'a/b/c']


# --- tags --------------------------------------------------------------------


def test_tags_letters_any_script_nested_not_numbers_not_anchors():
    found = nc.find_tags('#client #项目 #project/alpha #2024 http://x.com/#anchor a#b (#paren)')
    assert found == ['client', '项目', 'project/alpha', 'paren']


def test_heading_is_not_a_tag():
    assert nc.find_tags('# Heading\n## Another') == []


# --- markdown ----------------------------------------------------------------


def test_markdown_wikilinks_with_heading_alias_and_folder():
    result = nc.read_markdown('See [[Projects/Alpha#Budget|the budget]] and [[Bob]].')
    assert [(l['title'], l['heading'], l['alias']) for l in result['links']] == [
        ('Alpha', 'Budget', 'the budget'),
        ('Bob', None, None),
    ]


def test_markdown_code_is_ignored():
    md = 'Text [[Real]]\n```\n[[Fake]] #fake\n```\nand `#inline [[NoLink]]` #real'
    result = nc.read_markdown(md)
    assert [l['title'] for l in result['links']] == ['Real']
    assert result['tags'] == ['real']


def test_markdown_frontmatter_is_not_body():
    md = '---\ntags: [a]\n---\n[[Linked]] #b'
    result = nc.read_markdown(md)
    assert [l['title'] for l in result['links']] == ['Linked']
    assert result['tags'] == ['b']


def test_markdown_gnos3_links():
    md = (
        '[Acme](/accounting/company/12/dashboard) [INV](/invoices/data?invoice=7) '
        '[Card](http://box:8080/business-cards/data?card=3) [Doc](/api/v1/auths/k4mi/open?doc_id=99) '
        '[Chat](/c/0f676820-d1c7-436c-a869-88ece3609698) [web](https://example.com)'
    )
    found = [(e['entity_type'], e['entity_id']) for e in nc.read_markdown(md)['entities']]
    assert found == [
        ('company', '12'),
        ('invoice', '7'),
        ('business_card', '3'),
        ('document', '99'),
        ('chat', '0f676820-d1c7-436c-a869-88ece3609698'),
    ]


def test_entity_href_round_trip():
    for entity_type in nc.ENTITY_TYPES:
        entity_id = '0f676820-d1c7-436c-a869-88ece3609698' if entity_type == 'chat' else '42'
        assert nc.parse_entity_href(nc.entity_href(entity_type, entity_id)) == (entity_type, entity_id)


def test_markdown_context_is_plain_text_with_links_kept():
    result = nc.read_markdown('- [ ] Call [[Bob|Robert]] about [Acme](/accounting/company/1/dashboard) **today**')
    assert result['links'][0]['context'] == 'Call [[Bob|Robert]] about Acme today'


# --- editor JSON -------------------------------------------------------------


def test_document_links_tags_entities_and_contexts():
    content = doc(
        {
            'type': 'bulletList',
            'content': [
                {
                    'type': 'listItem',
                    'content': [
                        p(
                            text('Talk to '),
                            wikilink('Alice', 'n1', 'Al'),
                            text(' about #budget '),
                            {'type': 'entityRef', 'attrs': {'entityType': 'invoice', 'entityId': 5, 'label': 'INV-5'}},
                        )
                    ],
                }
            ],
        },
        {'type': 'heading', 'attrs': {'level': 1}, 'content': [text('Plan #q4')]},
        p(text('Acme', {'type': 'link', 'attrs': {'href': '/accounting/company/3/dashboard'}})),
    )
    result = nc.read_document(content)
    assert [(l['note_id'], l['title'], l['alias']) for l in result['links']] == [('n1', 'Alice', 'Al')]
    assert result['links'][0]['context'] == 'Talk to [[Alice|Al]] about #budget INV-5'
    assert sorted((e['entity_type'], e['entity_id']) for e in result['entities']) == [
        ('company', '3'),
        ('invoice', '5'),
    ]
    # Tags counted once, even inside a list item.
    assert result['tags'] == ['budget', 'q4']
    assert result['text'] == 'Talk to Al about #budget INV-5\nPlan #q4\nAcme'


def test_document_code_has_no_tags():
    content = doc(
        p(text('#real '), text('#code', {'type': 'code'})),
        {'type': 'codeBlock', 'content': [text('#block')]},
    )
    assert nc.read_document(content)['tags'] == ['real']


def test_note_content_prefers_json_and_adds_markdown_only_links():
    data = {
        'content': {
            'json': doc(p(wikilink('Alice', 'n1'), text(' and [[Pasted]]'))),
            'md': '[[Alice]] and [[Pasted]]',
        }
    }
    result = nc.read_note_content(data)
    assert [(l['note_id'], l['title']) for l in result['links']] == [('n1', 'Alice'), (None, 'Pasted')]


def test_note_content_markdown_only():
    data = {'content': {'json': None, 'md': '[[A]] #t'}}
    result = nc.read_note_content(data)
    assert [l['title'] for l in result['links']] == ['A'] and result['tags'] == ['t']


# --- properties --------------------------------------------------------------


def test_frontmatter_round_trip():
    props = {
        'type': 'project',
        'status': 'Active',
        'owner': {'id': 'n1', 'title': 'Old name'},
        'related': [{'id': 'n2', 'title': 'B'}],
        'company': {'entity_type': 'company', 'entity_id': '12', 'label': 'Acme'},
        'tags': ['x', 'y'],
        'empty': '',
    }
    block = nc.render_frontmatter(props, {'n1': 'New name'})
    parsed, body = nc.parse_frontmatter(block + 'Body')
    assert body == 'Body'
    assert parsed == {
        'type': 'project',
        'status': 'Active',
        'owner': '[[New name]]',
        'related': ['[[B]]'],
        'company': '/accounting/company/12/dashboard',
        'tags': ['x', 'y'],
    }
    assert nc.property_note_refs(parsed['owner']) == [{'note_id': None, 'title': 'New name'}]


def test_frontmatter_tags_as_text_and_bad_yaml_kept():
    props, _ = nc.parse_frontmatter('---\ntags: a, b c\naliases: Al\n---\n')
    assert props == {'tags': ['a', 'b', 'c'], 'aliases': ['Al']}
    md = '---\n: : bad\n  - [\n---\ntext'
    assert nc.parse_frontmatter(md) == ({}, md)


def test_frontmatter_dates_become_text():
    props, _ = nc.parse_frontmatter('---\ndue: 2026-11-03\n---\n')
    assert props == {'due': '2026-11-03'}


# --- mentions and renames ----------------------------------------------------


def test_mentions_whole_words_outside_links():
    found = nc.find_mentions('Alice Martinez is not [[Alice Martin]] but Alice Martin is', ['Alice Martin'])
    assert len(found) == 1


def test_mentions_cjk_titles_match_inside_text():
    assert nc.find_mentions('明天和王小明开会', ['王小明'])


def test_short_titles_are_not_searched():
    assert nc.mention_pattern('AI') is None


def test_rename_rewrites_links_keeping_heading_and_alias():
    md = 'x [[Old]] [[old#H|shown]] ![[Old]] [[Other]]'
    assert nc.markdown_with_link_titles(md, {'old': 'New'}) == 'x [[New]] [[New#H|shown]] ![[New]] [[Other]]'


def test_word_count_counts_cjk_characters():
    assert nc.word_count('Hello world 你好') == 4
