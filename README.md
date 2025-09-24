# Currency Exchange App

A simple currency exchange service built with FastAPI, PostgreSQL, and Alembic.

Core capabilities (as per spec):
- Fetch National Bank of the Republic of Belarus (NBRB) exchange rates on startup and daily (idempotent upsert).
- Two-step exchange flow: preview calculation and confirm/reject deal.
- Period report of deals (aggregated by currency).
- List of unfinished (PENDING) deals.


## Quick Start (Docker Compose)

Requirements: Docker, Docker Compose.

1) Copy environment variables and adjust if needed:

```
cp .env.example .env
```

2) Start PostgreSQL:

```
cd deploy
docker compose --env-file=../.env up db
```

3) Apply Alembic migrations (inside the app container):

```
docker compose --env-file=../.env run --rm app alembic upgrade head
```

4) Start the application:

```
docker compose --env-file=../.env up app
```


## Environment Variables

See `.env.example` (copy to `.env`). Notes:
- Database:
  - `DB_HOST`: use `db` in Docker Compose; use `localhost` for local runs without containers.
  - `DB_USERNAME`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`
  - `VOLUMES_ROOT`: host path for persistent data/logs if needed.
- Loader & Scheduler:
  - `LOAD_RATES_ON_STARTUP` (true/false) — one-shot load of today's rates on app startup.
  - `LOAD_RATES_DAILY` (true/false) — run daily scheduler.
  - `LOAD_RATES_TIME_UTC` (HH:MM) — daily load time in UTC.
- Local run (run.py) optional overrides:
  - `HOST` (default 127.0.0.1), `PORT` (default 8000), `RELOAD` (true/false).
  - Optional `LOG_LEVEL` for basic logging (e.g., INFO, DEBUG) if you configure logging.


## Local Development (without Docker)

Requirements: Python 3.12+, PostgreSQL.

1) Install dependencies (preferably in a virtualenv):

```
pip install -r requirements.txt
```

2) Create the database and fill `.env` (`DB_HOST=localhost`).

3) Apply migrations:

```
alembic upgrade head
```

4) Run the server (choose one):

- Via helper script (loads .env, enables reload by default):
  `python run.py`

- Directly with uvicorn:
  `uvicorn cea.main:app --host 0.0.0.0 --port 8000`


## Project Layout

- `cea/main.py` — FastAPI entry point (lifespan with loader + scheduler).
- `cea/db/database.py` — SQLAlchemy Async engine/session and DI.
- `cea/db/models/*` — ORM models.
- `cea/db/repository.py` — generic async CRUD base.
- `cea/db/repositories/*` — concrete repositories (deals, currency rates).
- `cea/schemas/*` — Pydantic schemas for API responses/requests.
- `cea/clients/nbrb.py` — async client for NBRB API.
- `cea/services/rate_loader.py` — idempotent rates loader (upsert).
- `cea/services/scheduler.py` — daily scheduler for rates loading.
- `migrations/` — Alembic migrations and config.
- `deploy/` — `Dockerfile` and `docker-compose.yml`.


## API Overview

- `GET /currencies?rate_date=YYYY-MM-DD` — list currency rates for a date; without `rate_date` uses today, or falls back to the latest available date.
  - Response item: `{ id, abbreviation, scale, rate, rate_date }`.
- `POST /exchange/preview` — preview conversion and create PENDING deal.
  - Body: `{ amount_from: number, currency_from: string, currency_to: string }`
  - Response: `{ deal_id, amount_to, rate_from, scale_from, rate_to, scale_to, status }`
- `POST /exchange/confirm` — confirm or reject a pending deal.
  - Body: `{ deal_id: string, result: "CONFIRM" | "REJECT" }`
  - Response: `{ id, status }`
- `GET /deals/report?date_from=ISO&date_to=ISO[&currency=CODE]` — aggregated report (confirmed deals only).
  - Response item: `{ currency, in_amount, out_amount, count }`
- `GET /deals/pending` — list of PENDING deals.


## Notes & Roadmap

- Implemented:
  - Infrastructure (Docker/Compose, .env.example), DB models & schemas, API endpoints, NBRB client, idempotent loader, daily scheduler, logging configuration, extra indices (e.g., deals.status), README API examples expansion.
