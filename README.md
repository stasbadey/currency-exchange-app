# Currency Exchange App

A simple currency exchange service built with FastAPI, PostgreSQL, and Alembic.

Core capabilities (as per spec):
- Fetch National Bank of the Republic of Belarus (NBRB) exchange rates on startup and daily (idempotent).
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
docker compose -f deploy/docker-compose.yml up -d db
```

3) Apply Alembic migrations (inside the app container):

```
docker compose -f deploy/docker-compose.yml run --rm app alembic upgrade head
```

4) Start the application:

```
docker compose -f deploy/docker-compose.yml up -d app
```

5) Health check:

```
curl http://localhost:8000/ping
```


## Environment Variables

See `.env.example` (copy to `.env`). Notes:
- `DB_HOST`: use `db` in Docker Compose; use `localhost` for local runs without containers.
- `DB_USERNAME`, `DB_PASSWORD`, `DB_NAME`: created in the DB container as per `.env`.
- `VOLUMES_ROOT`: host path for project location.


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

4) Run the server:

```
uvicorn cea.main:app --host 0.0.0.0 --port 8000
```


## Project Layout

- `cea/main.py` — FastAPI entry point.
- `cea/db/database.py` — SQLAlchemy Async engine/session and DI.
- `cea/db/models/*` — ORM models.
- `migrations/` — Alembic migrations and config.
- `deploy/` — `Dockerfile` and `docker-compose.yml`.


## API Overview (initial)

- `GET /` — service greeting.
- `GET /ping` — health check.
- `GET /currencies` — list currency rates (to be improved with response models and filters).
- Coming next: `POST /exchange/preview`, `POST /exchange/confirm`, `GET /deals/report`, `GET /deals/pending`.


## Roadmap

- Package 1 (infrastructure):
  - ✅ `.env.example`, Docker/Compose instructions in README.
- Package 2 (DB and schemas):
  - Export `Base` from `cea/db` for Alembic; add Pydantic schemas and `response_model`.
- Next:
  - NBRB client and daily background loader (idempotent).
  - Endpoints: preview/confirm, report, pending deals.
