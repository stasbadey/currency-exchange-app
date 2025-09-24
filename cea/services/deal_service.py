from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.ext.asyncio import AsyncSession

from cea.db.repositories import currency_rate_repository, deal_repository
from cea.enums import ConfirmActionEnum, DealStatusEnum
from cea.db.errors import RepositoryError, RepositoryIntegrityConflictError
from cea.services.errors import (
    ConflictError,
    DependencyError,
    NotFoundError,
    ValidationError,
)
from cea.schemas.deal import (
    DealReportItem,
    ExchangeConfirmIn,
    ExchangeConfirmOut,
    ExchangePreviewIn,
    ExchangePreviewOut,
    PendingDealOut,
)


class DealService:
    @staticmethod
    def _calc_amount_to(
        amount_from: Decimal,
        rate_from: Decimal,
        scale_from: int,
        rate_to: Decimal,
        scale_to: int,
    ) -> Decimal:
        byn_from = amount_from * (rate_from / Decimal(scale_from))
        amount_to = byn_from / (rate_to / Decimal(scale_to))
        return amount_to.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)

    async def preview(
        self, session: AsyncSession, payload: ExchangePreviewIn
    ) -> ExchangePreviewOut:
        # Basic input validations
        if payload.amount_from is None or payload.amount_from <= 0:
            raise ValidationError('amount_from must be a positive number')
        if payload.currency_from == payload.currency_to:
            raise ValidationError('currency_from and currency_to must differ')

        try:
            rate_from_row = (
                await currency_rate_repository.get_latest_by_abbreviation(
                    session, payload.currency_from
                )
            )
            rate_to_row = (
                await currency_rate_repository.get_latest_by_abbreviation(
                    session, payload.currency_to
                )
            )
        except Exception as e:
            raise DependencyError(str(e)) from e

        if not rate_from_row or not rate_to_row:
            raise ValidationError('Unknown currency abbreviation')

        # Defensive checks against invalid rate data
        if rate_from_row.scale == 0 or rate_to_row.scale == 0:
            raise DependencyError('Currency scale cannot be zero')
        if float(rate_to_row.rate) == 0.0:
            raise DependencyError('Target currency rate cannot be zero')

        amount_to = self._calc_amount_to(
            Decimal(str(payload.amount_from)),
            Decimal(str(rate_from_row.rate)),
            rate_from_row.scale,
            Decimal(str(rate_to_row.rate)),
            rate_to_row.scale,
        )

        try:
            deal = await deal_repository.create(
                session,
                amount_from=float(payload.amount_from),
                amount_to=float(amount_to),
                currency_from=payload.currency_from,
                currency_to=payload.currency_to,
                rate_from=float(rate_from_row.rate),
                scale_from=rate_from_row.scale,
                rate_to=float(rate_to_row.rate),
                scale_to=rate_to_row.scale,
                status=DealStatusEnum.PENDING,
            )
        except RepositoryIntegrityConflictError as e:
            # Should not normally happen for UUID PK, but map to conflict
            raise ConflictError(str(e)) from e
        except Exception as e:
            raise DependencyError(str(e)) from e

        return ExchangePreviewOut(
            deal_id=deal.id,
            amount_to=float(amount_to),
            rate_from=float(rate_from_row.rate),
            scale_from=rate_from_row.scale,
            rate_to=float(rate_to_row.rate),
            scale_to=rate_to_row.scale,
            status=DealStatusEnum.PENDING,
        )

    async def confirm(
        self, session: AsyncSession, payload: ExchangeConfirmIn
    ) -> ExchangeConfirmOut:
        try:
            deal = await deal_repository.get_by_id(session, payload.deal_id)
        except Exception as e:
            raise DependencyError(str(e)) from e
        if not deal:
            raise NotFoundError('Deal not found')
        if deal.status != DealStatusEnum.PENDING:
            raise ConflictError('Deal already finalized')

        new_status = (
            DealStatusEnum.CONFIRMED
            if payload.result == ConfirmActionEnum.CONFIRM
            else DealStatusEnum.REJECTED
        )
        try:
            updated = await deal_repository.update_by_id(
                session, payload.deal_id, status=new_status
            )
        except Exception as e:
            raise DependencyError(str(e)) from e
        # Our repository returns None when no 'returning' is specified; fetch it explicitly
        if updated is None:
            updated_model = await deal_repository.get_by_id(
                session, payload.deal_id
            )
        else:
            updated_model = updated  # type: ignore[assignment]
        if not updated_model:
            raise NotFoundError('Deal not found after update')
        return ExchangeConfirmOut(
            id=updated_model.id, status=updated_model.status
        )

    async def list_pending(
        self, session: AsyncSession
    ) -> list[PendingDealOut]:
        try:
            deals = await deal_repository.list_pending(session)
        except Exception as e:
            raise DependencyError(str(e)) from e
        return [
            PendingDealOut(
                id=d.id,
                created_at=d.created_at,
                amount_from=float(d.amount_from),
                amount_to=float(d.amount_to) 
                if d.amount_to is not None 
                else None,
                currency_from=d.currency_from,
                currency_to=d.currency_to,
                rate_from=float(d.rate_from) 
                if d.rate_from is not None 
                else None,
                scale_from=d.scale_from,
                rate_to=float(d.rate_to) if d.rate_to is not None else None,
                scale_to=d.scale_to,
            )
            for d in deals
        ]

    async def report(
        self,
        session: AsyncSession,
        *,
        date_from: datetime,
        date_to: datetime,
        currency: str | None = None,
    ) -> list[DealReportItem]:
        if date_from > date_to:
            raise ValidationError('date_from must be <= date_to')

        try:
            in_sum, out_sum, counts = await deal_repository.sums_by_currency(
                session, date_from=date_from, date_to=date_to, currency=currency
            )
        except RepositoryError as e:
            raise DependencyError(str(e)) from e
        currencies = (
            set(in_sum.keys()) | set(out_sum.keys()) | set(counts.keys())
        )
        if currency:
            currencies &= {currency}
        return [
            DealReportItem(
                currency=cur,
                in_amount=float(in_sum.get(cur, 0.0)),
                out_amount=float(out_sum.get(cur, 0.0)),
                count=int(counts.get(cur, 0)),
            )
            for cur in sorted(currencies)
        ]
