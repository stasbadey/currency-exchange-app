from datetime import date
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from cea.db.models.base import Base

class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cur_abbr: Mapped[str] = mapped_column(nullable=False)     # USD, EUR, RUB ...
    cur_scale: Mapped[int] = mapped_column(nullable=False)    # 1 для USD/EUR, 100 для RUB
    cur_rate: Mapped[float] = mapped_column(nullable=False)   # BYN за cur_scale
    rate_date: Mapped[date] = mapped_column(nullable=False)   # дата курса НБ РБ

    __table_args__ = (
        UniqueConstraint("rate_date", "cur_abbr", name="uq_rate_date_abbr"),
    )
