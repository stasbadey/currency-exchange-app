from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from cea.db.models.currency_rate import CurrencyRate
from cea.db.repositories import currency_rate_repository


class CurrencyRateService:
    @staticmethod
    async def list_rates(
        session: AsyncSession, *, rate_date: date | None
    ) -> list[CurrencyRate]:
        rows = await currency_rate_repository.list_by_date(
            session, rate_date=rate_date
        )
        if rows:
            return rows
        latest_date = await session.scalar(select(func.max(CurrencyRate.rate_date)))
        if latest_date is None:
            return []
        return await currency_rate_repository.list_by_date(
            session, rate_date=latest_date
        )

    @staticmethod
    async def get_latest(
        session: AsyncSession, abbreviation: str
    ) -> CurrencyRate | None:
        return await currency_rate_repository.get_latest_by_abbreviation(
            session, abbreviation
        )
