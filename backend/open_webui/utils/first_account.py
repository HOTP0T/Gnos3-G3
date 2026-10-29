"""
The startup setup that waits for an account, run when the first one signs up.

The default groups, the Anonymise switch and the task model need an owner, so
on a new box they were skipped at startup and appeared only after Gnos3 was
restarted by hand (test box, 2026-10-28). The data sources follow them, as the
sync worker would within a minute.
"""

import asyncio
import logging

log = logging.getLogger(__name__)

_background_tasks: set[asyncio.Task] = set()


async def _setup(app) -> None:
    from open_webui.utils.anonymiser_seed import ensure_anonymise_filter
    from open_webui.utils.data_source_seed import ensure_default_data_sources
    from open_webui.utils.rbac_seed import ensure_default_rbac_groups
    from open_webui.utils.settings_upgrade import apply_settings_upgrades

    steps = [
        ('default groups', ensure_default_rbac_groups),
        ('Anonymise switch', lambda: ensure_anonymise_filter(app)),
        ('settings upgrade', lambda: apply_settings_upgrades(app)),
        ('data sources', ensure_default_data_sources),
    ]
    for name, step in steps:
        try:
            await step()
        except Exception as exc:
            log.warning(f'First account: {name} failed (non-fatal): {exc}')


def after_first_account(app) -> None:
    """Runs in the background: the sign-up answers without waiting for it."""
    task = asyncio.create_task(_setup(app))
    _background_tasks.add(task)  # an unreferenced task can be garbage-collected mid-run
    task.add_done_callback(_background_tasks.discard)
