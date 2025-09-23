import datetime

from fastapi import APIRouter, Query

from cea.dependencies import SessionDep
from cea.schemas.deal import (
    DealReportItem,
    ExchangeConfirmIn,
    ExchangeConfirmOut,
    ExchangePreviewIn,
    ExchangePreviewOut,
    PendingDealOut,
)
from cea.services.processor import deal_service

router = APIRouter()


@router.post(
    '/exchange/preview', 
    response_model=ExchangePreviewOut,
    summary='Preview exchange',
)
async def preview_exchange(payload: ExchangePreviewIn, session: SessionDep):
    return await deal_service.preview(session, payload)


@router.post(
    '/exchange/confirm', 
    response_model=ExchangeConfirmOut, 
    summary='Confirm exchange',
)
async def confirm_exchange(payload: ExchangeConfirmIn, session: SessionDep):
    return await deal_service.confirm(session, payload)


@router.get(
    '/deals/pending', 
    response_model=list[PendingDealOut], 
    summary='List of Pending deals',
)
async def list_pending_deals(session: SessionDep):
    return await deal_service.list_pending(session)


@router.get(
    '/deals/report', 
    response_model=list[DealReportItem], 
    summary='Deal report'
)
async def deals_report(
    session: SessionDep,
    date_from: datetime.datetime = Query(
        ..., description='From (inclusive) in ISO format'
    ),
    date_to: datetime.datetime = Query(
        ..., description='To (inclusive) in ISO format'
    ),
    currency: str | None = Query(
        default=None, description='Optional currency code to filter'
    ),
):
    return await deal_service.report(
        session, date_from=date_from, date_to=date_to, currency=currency
    )
