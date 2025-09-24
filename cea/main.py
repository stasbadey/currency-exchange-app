import logging
import os
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from cea.api.routers import router
from cea.db.database import async_session
from cea.services.rate_loader import RateLoaderService
from cea.services.scheduler import DailyRatesScheduler, _parse_time_utc
from cea.services.errors import (
    ServiceError,
    ValidationError,
    NotFoundError,
    ConflictError,
    ExternalServiceError,
    DependencyError,
)

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
)


def _enabled(env_name: str, default: str = 'true') -> bool:
    return os.getenv(env_name, default).strip().lower() == 'true'


@asynccontextmanager
async def lifespan(app: FastAPI):
    # One-shot load on startup (idempotent upsert)
    if _enabled('LOAD_RATES_ON_STARTUP', 'true'):
        service = RateLoaderService()
        async with async_session() as session:
            try:
                await service.fetch_and_upsert_for_date(
                    session, ondate=date.today()
                )
            except ServiceError as e:
                logging.getLogger(__name__).warning(
                    'Startup rate load skipped due to service error: %s', e
                )

    # Daily scheduler
    scheduler: DailyRatesScheduler | None = None
    if _enabled('LOAD_RATES_DAILY', 'true'):
        time_str = os.getenv('LOAD_RATES_TIME_UTC', '21:00')
        scheduler = DailyRatesScheduler(
            async_session,
            RateLoaderService(),
            _parse_time_utc(time_str),
        )
        scheduler.start()
        app.state.rate_scheduler = scheduler

    try:
        yield
    finally:
        if scheduler is not None:
            await scheduler.stop()


app = FastAPI(title='Currency Exchange Service', lifespan=lifespan)

app.include_router(router)

# Exception handlers for service-layer errors

_ERROR_CODE_MAP: dict[type[ServiceError], int] = {
    ValidationError: 400,
    NotFoundError: 404,
    ConflictError: 409,
    ExternalServiceError: 502,
    DependencyError: 503,
}


@app.exception_handler(ServiceError)
async def handle_service_error(_, exc: ServiceError):
    status = _ERROR_CODE_MAP.get(type(exc), 500)
    return JSONResponse(status_code=status, content={"detail": str(exc)})
