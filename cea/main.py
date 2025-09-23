import os
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI

from cea.api.routers import router
from cea.db.database import async_session
from cea.services.rate_loader import RateLoaderService


app = FastAPI(title='Currency Exchange Service')

app.include_router(router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    flag = os.getenv('LOAD_RATES_ON_STARTUP', 'true').lower()
    if flag:
        service = RateLoaderService()
        async with async_session() as session:
            await service.fetch_and_upsert_for_date(
                session, ondate=date.today()
            )
    yield
