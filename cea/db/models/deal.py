import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from cea.db.models.base import Base
from cea.enums import DealStatusEnum


class Deal(Base):
    __tablename__ = 'deals'

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    amount_from: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    amount_to: Mapped[float] = mapped_column(Numeric(18, 4), nullable=True)
    currency_from: Mapped[str] = mapped_column(String(8), nullable=False)
    currency_to: Mapped[str] = mapped_column(String(8), nullable=False)

    rate_from: Mapped[float] = mapped_column(nullable=True)
    scale_from: Mapped[int] = mapped_column(nullable=True)
    rate_to: Mapped[float] = mapped_column(nullable=True)
    scale_to: Mapped[int] = mapped_column(nullable=True)

    status: Mapped[DealStatusEnum] = mapped_column(
        nullable=False, server_default=DealStatusEnum.PENDING
    )

    @declared_attr.directive
    @classmethod
    def __table_args__(cls) -> None:
        Index('deal_created_at_idx', cls.created_at.desc())
