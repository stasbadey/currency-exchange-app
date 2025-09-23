#!/usr/bin/env python3
"""
Local entrypoint to run the FastAPI app without Docker.

Usage:
  - Ensure virtualenv is active and deps are installed: pip install -r requirements.txt
  - Set up your database and .env (DB_HOST=localhost for local)
  - Apply migrations: alembic upgrade head
  - Run: python run.py

Env vars (optional):
  HOST   (default: 127.0.0.1)
  PORT   (default: 8000)
  RELOAD (default: true)
"""

import os

from dotenv import load_dotenv
import uvicorn


def main() -> None:
    # Load .env from project root if present
    load_dotenv()

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower()

    uvicorn.run("cea.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()

