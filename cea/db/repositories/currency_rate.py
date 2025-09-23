from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cea.db.models.currency_rate import CurrencyRate
from cea.db.repository import BaseRepository


class CurrencyRateRepository(BaseRepository[CurrencyRate]):
    async def list_by_date(
        self, session: AsyncSession, *, rate_date: date | None
    ) -> list[CurrencyRate]:
        effective_date = rate_date or date.today()
        return (
            await self._read(
                session, where=self.model.rate_date == effective_date
            )
        ).scalars().all()

    async def get_latest_by_abbreviation(
        self, session: AsyncSession, abbreviation: str
    ) -> CurrencyRate | None:
        stmt = (
            select(CurrencyRate)
            .where(CurrencyRate.abbreviation == abbreviation)
            .order_by(CurrencyRate.rate_date.desc())
            .limit(1)
        )
        return (await session.execute(stmt)).scalar_one_or_none()
