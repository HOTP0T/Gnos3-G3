"""Notes vaults: where a note sits (vault + folder) and what it links to.

Notes themselves stay in upstream's `note` table (`models/notes.py`): content, title, sharing and
live co-editing are unchanged. These tables add:

- `note_vault`     a set of notes that link to each other and share one graph. One *personal*
                   vault per user (id derived from the user id) and any number of *shared* vaults,
                   readable / writable by the groups given in `access_grant` rows
                   (resource_type 'note_vault').
- `note_placement` which vault and folder a note is in. A note without a row belongs to its
                   owner's personal vault, at the root (rows are added when the vault is read).
- `note_folder`    folders, so an empty folder survives.
- `note_index`     what the vault needs to know about each note without reading its body
                   (type, tags, aliases, size), rebuilt whenever the note's `updated_at` moves.
- `note_link`      every [[link]], typed relation (a note-valued property) and link to Gnos3 data,
                   rebuilt with the index.

Migration: `gnos3_note_vaults`.
"""

import time
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, Integer, JSON, Text, Index

from open_webui.internal.db import Base


class NoteVault(Base):
    __tablename__ = 'note_vault'

    id = Column(Text, primary_key=True)
    kind = Column(Text, nullable=False)  # 'personal' | 'shared'
    owner_id = Column(Text, nullable=True)  # personal: the user; shared: who created it
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(Text, nullable=True)
    icon = Column(Text, nullable=True)
    settings = Column(JSON, nullable=True)
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)


class NotePlacement(Base):
    __tablename__ = 'note_placement'

    note_id = Column(Text, primary_key=True)
    vault_id = Column(Text, nullable=False, index=True)
    folder = Column(Text, nullable=False, default='')
    updated_at = Column(BigInteger, nullable=False)


class NoteFolder(Base):
    __tablename__ = 'note_folder'

    vault_id = Column(Text, primary_key=True)
    path = Column(Text, primary_key=True)
    created_at = Column(BigInteger, nullable=False)


class NoteIndex(Base):
    __tablename__ = 'note_index'

    note_id = Column(Text, primary_key=True)
    vault_id = Column(Text, nullable=False, index=True)
    title = Column(Text, nullable=False, default='')
    title_key = Column(Text, nullable=False, default='')  # normalize_title(title)
    note_type = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    aliases = Column(JSON, nullable=True)
    word_count = Column(Integer, nullable=False, default=0)
    excerpt = Column(Text, nullable=True)
    note_updated_at = Column(BigInteger, nullable=False)  # the note's updated_at this row was built from
    indexed_at = Column(BigInteger, nullable=False)


class NoteLink(Base):
    __tablename__ = 'note_link'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vault_id = Column(Text, nullable=False)
    source_id = Column(Text, nullable=False)
    kind = Column(Text, nullable=False)  # 'link' | 'property' | 'entity'
    target_id = Column(Text, nullable=True)  # the linked note, when known
    target_key = Column(Text, nullable=True)  # normalize_title() of the title as written
    target_title = Column(Text, nullable=True)
    property_key = Column(Text, nullable=True)
    entity_type = Column(Text, nullable=True)
    entity_id = Column(Text, nullable=True)
    label = Column(Text, nullable=True)
    context = Column(Text, nullable=True)

    __table_args__ = (
        Index('ix_note_link_vault', 'vault_id'),
        Index('ix_note_link_source', 'source_id'),
        Index('ix_note_link_target', 'target_id'),
        Index('ix_note_link_target_key', 'vault_id', 'target_key'),
    )


class NoteVaultModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    kind: str
    owner_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    settings: Optional[dict] = None
    created_at: int
    updated_at: int


def now_ns() -> int:
    """Notes use nanosecond timestamps (upstream's convention)."""
    return int(time.time_ns())
