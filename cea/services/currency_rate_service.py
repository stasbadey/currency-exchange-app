from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from cea.db.models.currency_rate import CurrencyRate
from cea.db.repositories import currency_rate_repository
from cea.db.errors import RepositoryError
from cea.services.errors import DependencyError


class CurrencyRateService:
    @staticmethod
    async def list_rates(
        session: AsyncSession, *, rate_date: date | None
    ) -> list[CurrencyRate]:
        try:
            rows = await currency_rate_repository.list_by_date(
                session, rate_date=rate_date
            )
        except Exception as e:  # repository/DB failure
            raise DependencyError(str(e)) from e
        if rows:
            return rows
        latest_date = await session.scalar(select(func.max(CurrencyRate.rate_date)))
        if latest_date is None:
            return []
        try:
            return await currency_rate_repository.list_by_date(
                session, rate_date=latest_date
            )
        except Exception as e:
            raise DependencyError(str(e)) from e

    @staticmethod
    async def get_latest(
        session: AsyncSession, abbreviation: str
    ) -> CurrencyRate | None:
        try:
            return await currency_rate_repository.get_latest_by_abbreviation(
                session, abbreviation
            )
        except Exception as e:
            raise DependencyError(str(e)) from e
