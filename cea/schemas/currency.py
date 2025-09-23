import datetime

from pydantic import BaseModel, ConfigDict


class CurrencyRateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cur_abbr: str
    cur_scale: int
    cur_rate: float
    rate_date: datetime.date
