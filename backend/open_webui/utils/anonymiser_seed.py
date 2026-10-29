"""
Install the Anonymiser's chat switch on startup.

The "Anonymise" filter (builtin_functions/anonymise.py) ships with Gnos3 and is
written to the function table as `gnos3_anonymise`:
  - first time: created active and global, so the switch shows under every
    model's message box. The frontend hides it unless the Anonymiser module is
    up and the person holds `modules.anonymiser.read`.
  - later: its code is refreshed when a Gnos3 version changes it. What an admin
    chose since (turned it off, attached it to chosen models only, valves) is kept.

Harmless without the Anonymiser module: the switch stays hidden, and if it is
used anyway the message is refused rather than sent unhidden.
Like rbac_seed, it waits for the first user (a function needs an owner): the
first sign-up runs it again (utils/first_account.py).
"""

import logging
from pathlib import Path

from open_webui.models.functions import FunctionForm, FunctionMeta, Functions
from open_webui.models.users import Users
from open_webui.utils.plugin import load_function_module_by_id, replace_imports

log = logging.getLogger(__name__)

FUNCTION_ID = 'gnos3_anonymise'
SOURCE = Path(__file__).resolve().parent.parent / 'builtin_functions' / 'anonymise.py'


async def ensure_anonymise_filter(app) -> None:
    content = replace_imports(SOURCE.read_text(encoding='utf-8'))
    existing = await Functions.get_function_by_id(FUNCTION_ID)
    if existing is not None and existing.content == content:
        return

    owner = await Users.get_first_user()
    if owner is None:
        log.info('Anonymiser seed: no users yet — the Anonymise switch is installed at the first sign-up.')
        return

    module, function_type, frontmatter = await load_function_module_by_id(FUNCTION_ID, content=content)
    app.state.FUNCTIONS[FUNCTION_ID] = module

    if existing is not None:
        meta = {**(existing.meta.model_dump() if existing.meta else {}), 'manifest': frontmatter}
        await Functions.update_function_by_id(FUNCTION_ID, {'content': content, 'meta': meta})
        log.info('Anonymiser seed: Anonymise switch updated to the shipped version')
        return

    await Functions.insert_new_function(
        owner.id,
        function_type,
        FunctionForm(
            id=FUNCTION_ID,
            name='Anonymise',
            content=content,
            meta=FunctionMeta(
                description='Hides names, contact details and ID or bank numbers from the AI, then puts them back in its answer.',
                manifest=frontmatter,
            ),
        ),
    )
    await Functions.update_function_by_id(FUNCTION_ID, {'is_active': True, 'is_global': True})
    await Functions.update_function_metadata_by_id(FUNCTION_ID, {'toggle': True})
    log.info('Anonymiser seed: Anonymise switch installed')
