from datetime import datetime
from enum import Enum
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric
from cea.db.models.base import Base

class DealStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"

class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    amount_from: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    amount_to:   Mapped[float] = mapped_column(Numeric(18, 4), nullable=True)   # заполняется на preview
    cur_from:    Mapped[str] = mapped_column(String(8), nullable=False)
    cur_to:      Mapped[str] = mapped_column(String(8), nullable=False)

    rate_from:   Mapped[float] = mapped_column(nullable=True)  # BYN за scale_from
    scale_from:  Mapped[int]   = mapped_column(nullable=True)
    rate_to:     Mapped[float] = mapped_column(nullable=True)  # BYN за scale_to
    scale_to:    Mapped[int]   = mapped_column(nullable=True)

    status:      Mapped[str] = mapped_column(String(16), default=DealStatus.PENDING.value, nullable=False)
