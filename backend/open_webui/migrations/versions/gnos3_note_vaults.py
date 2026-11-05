"""Notes vaults: vaults, folders, note placement, link index (Gnos3).

Adds the tables behind the Notes vault (folders, [[links]], backlinks, graph, properties):
note_vault, note_placement, note_folder, note_index, note_link. Upstream's `note` table is
unchanged; every existing note lands in its owner's personal vault the first time that vault
is read (no data migration needed).

Revision ID: gnos3_note_vaults
Revises: phase4_k4mi_uid
Create Date: 2026-11-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'gnos3_note_vaults'
down_revision: Union[str, None] = 'phase4_k4mi_uid'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'note_vault',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('kind', sa.Text(), nullable=False),
        sa.Column('owner_id', sa.Text(), nullable=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.Text(), nullable=True),
        sa.Column('icon', sa.Text(), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
    )
    op.create_index('ix_note_vault_owner', 'note_vault', ['owner_id'])

    op.create_table(
        'note_placement',
        sa.Column('note_id', sa.Text(), primary_key=True),
        sa.Column('vault_id', sa.Text(), nullable=False),
        sa.Column('folder', sa.Text(), nullable=False, server_default=''),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
    )
    op.create_index('ix_note_placement_vault_id', 'note_placement', ['vault_id'])

    op.create_table(
        'note_folder',
        sa.Column('vault_id', sa.Text(), primary_key=True),
        sa.Column('path', sa.Text(), primary_key=True),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
    )

    op.create_table(
        'note_index',
        sa.Column('note_id', sa.Text(), primary_key=True),
        sa.Column('vault_id', sa.Text(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False, server_default=''),
        sa.Column('title_key', sa.Text(), nullable=False, server_default=''),
        sa.Column('note_type', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('aliases', sa.JSON(), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('excerpt', sa.Text(), nullable=True),
        sa.Column('note_updated_at', sa.BigInteger(), nullable=False),
        sa.Column('indexed_at', sa.BigInteger(), nullable=False),
    )
    op.create_index('ix_note_index_vault_id', 'note_index', ['vault_id'])

    op.create_table(
        'note_link',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('vault_id', sa.Text(), nullable=False),
        sa.Column('source_id', sa.Text(), nullable=False),
        sa.Column('kind', sa.Text(), nullable=False),
        sa.Column('target_id', sa.Text(), nullable=True),
        sa.Column('target_key', sa.Text(), nullable=True),
        sa.Column('target_title', sa.Text(), nullable=True),
        sa.Column('property_key', sa.Text(), nullable=True),
        sa.Column('entity_type', sa.Text(), nullable=True),
        sa.Column('entity_id', sa.Text(), nullable=True),
        sa.Column('label', sa.Text(), nullable=True),
        sa.Column('context', sa.Text(), nullable=True),
    )
    op.create_index('ix_note_link_vault', 'note_link', ['vault_id'])
    op.create_index('ix_note_link_source', 'note_link', ['source_id'])
    op.create_index('ix_note_link_target', 'note_link', ['target_id'])
    op.create_index('ix_note_link_target_key', 'note_link', ['vault_id', 'target_key'])


def downgrade() -> None:
    op.drop_index('ix_note_link_target_key', table_name='note_link')
    op.drop_index('ix_note_link_target', table_name='note_link')
    op.drop_index('ix_note_link_source', table_name='note_link')
    op.drop_index('ix_note_link_vault', table_name='note_link')
    op.drop_table('note_link')
    op.drop_index('ix_note_index_vault_id', table_name='note_index')
    op.drop_table('note_index')
    op.drop_table('note_folder')
    op.drop_index('ix_note_placement_vault_id', table_name='note_placement')
    op.drop_table('note_placement')
    op.drop_index('ix_note_vault_owner', table_name='note_vault')
    op.drop_table('note_vault')
