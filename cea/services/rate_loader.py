from datetime import date, datetime
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from cea.clients.nbrb import NBRBClient
from cea.db.models.currency_rate import CurrencyRate


class RateLoaderService:
    def __init__(self, client: NBRBClient | None = None) -> None:
        self.client = client or NBRBClient()

    @staticmethod
    def _map_nbrb_item(item: dict[str, Any]) -> dict[str, Any]:
        # NBRB fields: Cur_Abbreviation, Cur_Scale, Cur_OfficialRate, Date
        dt_raw = item.get('Date')
        if isinstance(dt_raw, str):
            # Typically 'YYYY-MM-DDTHH:MM:SS'
            dt = datetime.fromisoformat(dt_raw)
        elif isinstance(dt_raw, datetime):
            dt = dt_raw
        else:
            raise ValueError('NBRB item missing `Date`')

        return {
            'abbreviation': item['Cur_Abbreviation'],
            'scale': int(item['Cur_Scale']),
            'rate': float(item['Cur_OfficialRate']),
            'rate_date': dt.date(),
        }

    async def fetch_and_upsert_for_date(
        self, session: AsyncSession, *, ondate: date | None = None
    ) -> int:
        """Fetch rates and upsert into currency_rates. Returns affected rows count."""
        items = await self.client.get_daily_rates(ondate)
        if not items:
            return 0

        rows = [self._map_nbrb_item(it) for it in items]
        stmt = insert(CurrencyRate).values(rows)
        # Unique constraint on (rate_date, abbreviation)
        stmt = stmt.on_conflict_do_update(
            index_elements=[
                CurrencyRate.rate_date, CurrencyRate.abbreviation
            ],
            set_={
                'scale': stmt.excluded.scale,
                'rate': stmt.excluded.rate,
            },
        )
        await session.execute(stmt)
        await session.commit()
        return len(rows)
