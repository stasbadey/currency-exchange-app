import httpx
from datetime import date
from typing import Any


class NBRBClient:
    """Minimal async client for NBRB exchange rates API."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or 'https://api.nbrb.by/exrates'
        self._timeout = timeout

    async def get_daily_rates(
        self, ondate: date | None = None
    ) -> list[dict[str, Any]]:
        """Fetch daily rates for a given date (or today if None).

        Returns a list of dicts; fields of interest:
        - Cur_Abbreviation (str)
        - Cur_Scale (int)
        - Cur_OfficialRate (float)
        - Date (ISO datetime)
        """

        params = {'periodicity': 0}
        if ondate is not None:
            params['ondate'] = ondate.isoformat()

        url = f'{self.base_url}/rates'
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list):
                raise ValueError(
                    'Unexpected NBRB response format: expected list'
                )
            return data
