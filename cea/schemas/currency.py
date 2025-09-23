import datetime

from pydantic import BaseModel, ConfigDict


class CurrencyRateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    abbreviation: str
    scale: int
    rate: float
    rate_date: datetime.date
