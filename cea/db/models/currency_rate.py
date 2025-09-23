import datetime

from sqlalchemy import Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from cea.db.models.base import Base


class CurrencyRate(Base):
    __tablename__ = 'currency_rates'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    abbreviation: Mapped[str] = mapped_column(String(8), nullable=False)
    scale: Mapped[int] = mapped_column(nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    rate_date: Mapped[datetime.date] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint(
            'rate_date', 'abbreviation', name='uq_rate_date_abbr'
        ),
    )
