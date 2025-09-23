import datetime

from pydantic import BaseModel, ConfigDict

from cea.enums import ConfirmActionEnum, DealStatusEnum


class DealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime.datetime

    amount_from: float
    amount_to: float | None
    currency_from: str
    currency_to: str

    rate_from: float | None
    scale_from: int | None
    rate_to: float | None
    scale_to: int | None

    status: DealStatusEnum


class ExchangePreviewIn(BaseModel):
    amount_from: float
    currency_from: str
    currency_to: str


class ExchangePreviewOut(BaseModel):
    deal_id: str
    amount_to: float
    rate_from: float
    scale_from: int
    rate_to: float
    scale_to: int
    status: DealStatusEnum


class ExchangeConfirmIn(BaseModel):
    deal_id: str
    result: ConfirmActionEnum


class ExchangeConfirmOut(BaseModel):
    id: str
    status: DealStatusEnum


class DealReportItem(BaseModel):
    currency: str
    in_amount: float
    out_amount: float
    count: int


class PendingDealOut(BaseModel):
    id: str
    created_at: datetime.datetime
    amount_from: float
    amount_to: float | None
    currency_from: str
    currency_to: str
    rate_from: float | None
    scale_from: int | None
    rate_to: float | None
    scale_to: int | None
