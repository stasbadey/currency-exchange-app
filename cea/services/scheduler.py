from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cea.services.rate_loader import RateLoaderService

_logger = logging.getLogger(__name__)


def _parse_time_utc(hhmm: str) -> time:
    hh, mm = hhmm.split(":", 1)
    return time(int(hh), int(mm), tzinfo=timezone.utc)


def _next_run(now: datetime, at_utc: time) -> datetime:
    assert now.tzinfo is not None, 'now must be tz-aware'
    today_run = now.replace(
        hour=at_utc.hour, minute=at_utc.minute, second=0, microsecond=0
    )
    if now < today_run:
        return today_run
    return today_run + timedelta(days=1)


class DailyRatesScheduler:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        loader: RateLoaderService,
        run_time_utc: time,
    ) -> None:
        self._sf = session_factory
        self._loader = loader
        self._at = run_time_utc
        self._task: asyncio.Task | None = None
        self._stop_evt = asyncio.Event()

    def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(
            self._loop(), name='daily-rates-scheduler'
        )

    async def stop(self) -> None:
        self._stop_evt.set()
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _loop(self) -> None:
        while True:
            now = datetime.now(timezone.utc)
            nxt = _next_run(now, self._at)
            delay = (nxt - now).total_seconds()
            _logger.info(
                'Next daily rates load scheduled at %s UTC', nxt.isoformat()
            )
            try:
                await asyncio.wait_for(self._stop_evt.wait(), timeout=delay)
                _logger.info('Daily rates scheduler stopped')
                return
            except asyncio.TimeoutError:
                pass
            try:
                async with self._sf() as session:
                    await self._loader.fetch_and_upsert_for_date(
                        session, ondate=date.today()
                    )
                _logger.info('Daily rates loaded successfully')
            except Exception:
                _logger.exception('Daily rates load failed')
