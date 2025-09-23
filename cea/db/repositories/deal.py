import datetime
from typing import Any, Sequence

from sqlalchemy import Row, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from cea.db.models.deal import Deal
from cea.db.repository import BaseRepository
from cea.enums import DealStatusEnum


class DealRepository(BaseRepository[Deal]):
    async def list_pending(self, session: AsyncSession) -> Sequence[Deal]:
        return (
            await self._read(
                session, where=self.model.status == DealStatusEnum.PENDING
            )
        ).scalars().all()

    async def list_confirmed_between(
        self,
        session: AsyncSession,
        *,
        date_from: datetime.datetime,
        date_to: datetime.datetime,
    ) -> Sequence[Deal]:
        return (
            await self._read(
                session,
                where=(
                    and_(
                        self.model.status == DealStatusEnum.CONFIRMED,
                        self.model.created_at >= date_from,
                        self.model.created_at <= date_to,
                    )
                ),
                order_by=self.model.created_at,
            )
        ).scalars().all()

    def _base_where(
        self,
        *,
        date_from: datetime.datetime,
        date_to: datetime.datetime,
        currency: str | None = None,
    ) -> list[Any]:
        where_: list[Any] = [
            self.model.status == DealStatusEnum.CONFIRMED,
            self.model.created_at >= date_from,
            self.model.created_at <= date_to,
        ]
        if currency:
            where_.append(
                or_(
                    self.model.currency_from == currency, 
                    self.model.currency_to == currency,
                )
            )
        return where_

    async def sum_in_by_currency(
        self,
        session: AsyncSession,
        *,
        date_from: datetime.datetime,
        date_to: datetime.datetime,
        currency: str | None = None,
    ) -> dict[str, float]:
        """Sum amount_to grouped by currency_to."""
        base_where = self._base_where(
            date_from=date_from, date_to=date_to, currency=currency
        )
        stmt = (
            select(
                self.model.currency_to, 
                func.coalesce(func.sum(self.model.amount_to), 0),
            )
            .where(*base_where)
            .group_by(self.model.currency_to)
        )
        res = await session.execute(stmt)
        return {k: float(v or 0) for k, v in res.all()}

    async def sum_out_by_currency(
        self,
        session: AsyncSession,
        *,
        date_from: datetime.datetime,
        date_to: datetime.datetime,
        currency: str | None = None,
    ) -> dict[str, float]:
        """Sum amount_from grouped by currency_from."""
        base_where = self._base_where(
            date_from=date_from, date_to=date_to, currency=currency
        )
        stmt = (
            select(
                self.model.currency_from, 
                func.coalesce(func.sum(self.model.amount_from), 0),
            )
            .where(*base_where)
            .group_by(self.model.currency_from)
        )
        res = await session.execute(stmt)
        return {k: float(v or 0) for k, v in res.all()}

    async def count_by_currency(
        self,
        session: AsyncSession,
        *,
        date_from: datetime.datetime,
        date_to: datetime.datetime,
        currency: str | None = None,
    ) -> dict[str, int]:
        """Count confirmed deals per currency, counting either side participation."""
        base_where = self._base_where(
            date_from=date_from, date_to=date_to, currency=currency
        )
        stmt = select(
            self.model.currency_from, self.model.currency_to
        ).where(*base_where)
        res = await session.execute(stmt)
        counts: dict[str, int] = {}
        for c_from, c_to in res.all():
            counts[c_from] = counts.get(c_from, 0) + 1
            counts[c_to] = counts.get(c_to, 0) + 1
        return counts

    async def sums_by_currency(
        self,
        session: AsyncSession,
        *,
        date_from: datetime.datetime,
        date_to: datetime.datetime,
        currency: str | None = None,
    ) -> tuple[dict[str, float], dict[str, float], dict[str, int]]:
        """Combine atomic aggregations: (in_sum, out_sum, counts)."""
        in_sum = await self.sum_in_by_currency(
            session, date_from=date_from, date_to=date_to, currency=currency
        )
        out_sum = await self.sum_out_by_currency(
            session, date_from=date_from, date_to=date_to, currency=currency
        )
        counts = await self.count_by_currency(
            session, date_from=date_from, date_to=date_to, currency=currency
        )
        return in_sum, out_sum, counts
