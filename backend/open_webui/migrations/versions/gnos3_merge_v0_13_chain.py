"""Join our migrations with upstream's chain up to v0.13.0.

Upstream's 29 migrations since v0.9.2 descend from 56359461a091, as our first merge
revision does, which left two heads. A merge revision and nothing else: a box that has
already applied ours must still run upstream's, so no revision is re-pointed
(docs/05 section 1.5).

Revision ID: gnos3_merge_v0_13
Revises: gnos3_note_vaults, e42c8f710a36
"""

from typing import Sequence, Union

revision: str = 'gnos3_merge_v0_13'
down_revision: Union[str, Sequence[str], None] = ('gnos3_note_vaults', 'e42c8f710a36')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
