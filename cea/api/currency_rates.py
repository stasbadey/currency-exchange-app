import datetime

from fastapi import APIRouter, Query

from cea.dependencies import SessionDep
from cea.schemas.currency import CurrencyRateOut
from cea.services.currency_rate_service import CurrencyRateService

router = APIRouter()


@router.get(
    '/currencies', 
    response_model=list[CurrencyRateOut],
    summary='List of Currency Rates',
)
async def list_currency_rates(
    session: SessionDep,
    rate_date: datetime.date | None = Query(
        default=datetime.date.today(), 
        description='Filter by rate date (YYYY-MM-DD)',
    ),
):
    return await CurrencyRateService.list_rates(session, rate_date=rate_date)
