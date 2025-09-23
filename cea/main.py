from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from cea.api.routers import router
from cea.db.database import get_db
from cea.db.models import CurrencyRate

app = FastAPI(title="Currency Exchange Service")

app.include_router(router)
