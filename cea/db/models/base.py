from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Declarative base class"""

    type_annotation_map = {dict[str, Any]: JSONB, list[Any]: JSONB}
    metadata = MetaData(
        naming_convention={
            'ix': '%(table_name)s_%(column_0_name)s_idx',
            'uq': '%(table_name)s_%(column_0_name)s_key',
            'ck': '%(table_name)s_%(column_0_name)s_check',
            'fk': (
                '%(table_name)s_%(column_0_name)s_%(referred_table_name)s_fkey'
            ),
            'pk': '%(table_name)s_pkey',
        }
    )
