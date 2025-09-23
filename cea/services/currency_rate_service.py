from __future__ import annotations

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from cea.db.models.currency_rate import CurrencyRate
from cea.db.repositories import currency_rate_repository


class CurrencyRateService:
    @staticmethod
    async def list_rates(
        session: AsyncSession, *, rate_date: date | None
    ) -> list[CurrencyRate]:
        return await currency_rate_repository.list_by_date(
            session, rate_date=rate_date
        )

    @staticmethod
    async def get_latest(
        session: AsyncSession, abbreviation: str
    ) -> CurrencyRate | None:
        return await currency_rate_repository.get_latest_by_abbreviation(
            session, abbreviation
        )
