"""
docker-lab: a tiny API for learning Docker step by step.

It works ALONE (lessons 3-4), and gets more features when Redis (lesson 5)
and PostgreSQL (lesson 7) are connected through environment variables.

Endpoints:
  GET  /          -> hello + which container answered
  GET  /health    -> status of the app, database and redis
  GET  /visits    -> visit counter stored in Redis
  POST /notes     -> save a note in PostgreSQL
  GET  /notes     -> list notes
  GET  /docs      -> Swagger UI (try everything from the browser)
"""

import asyncio
import os
import platform
import socket
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

APP_NAME = os.getenv("APP_NAME", "docker-lab")
APP_VERSION = os.getenv("APP_VERSION", "1.0")
DATABASE_URL = os.getenv("DATABASE_URL")   # e.g. postgresql://lab:labpass@db:5432/lab
REDIS_URL = os.getenv("REDIS_URL")         # e.g. redis://redis:6379/0

state = {"db": None, "redis": None, "db_error": None}


async def connect_db():
    """PostgreSQL may need a few seconds to start, so retry."""
    import asyncpg
    for attempt in range(1, 11):
        try:
            pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
            async with pool.acquire() as conn:
                await conn.execute(
                    """CREATE TABLE IF NOT EXISTS notes (
                           id SERIAL PRIMARY KEY,
                           text TEXT NOT NULL,
                           created_at TIMESTAMPTZ DEFAULT now()
                       )"""
                )
            print(f"[db] connected (attempt {attempt})", flush=True)
            return pool
        except Exception as e:
            state["db_error"] = str(e)
            print(f"[db] not ready (attempt {attempt}/10): {e}", flush=True)
            await asyncio.sleep(2)
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[app] starting {APP_NAME} v{APP_VERSION} on {socket.gethostname()}", flush=True)
    if DATABASE_URL:
        state["db"] = await connect_db()
    if REDIS_URL:
        import redis.asyncio as aioredis
        state["redis"] = aioredis.from_url(REDIS_URL, decode_responses=True)
    yield
    if state["db"]:
        await state["db"].close()
    if state["redis"]:
        await state["redis"].aclose()


app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)


class NoteIn(BaseModel):
    text: str


@app.get("/")
async def root():
    return {
        "message": f"Hello from {APP_NAME}!",
        "version": APP_VERSION,
        "container_hostname": socket.gethostname(),   # = container ID inside Docker
        "python": platform.python_version(),
        "running_as_user": current_user(),             # root vs appuser (lesson 10)
    }


def current_user():
    try:
        import getpass
        return getpass.getuser()
    except Exception:
        return "?"


@app.get("/health")
async def health():
    result = {"app": "ok"}

    if not DATABASE_URL:
        result["database"] = "not configured (DATABASE_URL is empty)"
    elif state["db"] is None:
        result["database"] = f"error: {state['db_error']}"
    else:
        try:
            async with state["db"].acquire() as conn:
                await conn.fetchval("SELECT 1")
            result["database"] = "ok"
        except Exception as e:
            result["database"] = f"error: {e}"

    if not REDIS_URL:
        result["redis"] = "not configured (REDIS_URL is empty)"
    else:
        try:
            await state["redis"].ping()
            result["redis"] = "ok"
        except Exception as e:
            result["redis"] = f"error: {e}"

    # Lesson 10: return 503 when something is broken, so Docker's HEALTHCHECK
    # (which only looks at the HTTP status code) marks the container unhealthy.
    healthy = all(v == "ok" or v.startswith("not configured") for v in result.values())
    return JSONResponse(result, status_code=200 if healthy else 503)


@app.get("/visits")
async def visits():
    if not state["redis"]:
        raise HTTPException(503, "Redis is not configured - set REDIS_URL (lesson 5)")
    count = await state["redis"].incr("visits")
    return {"visits": count, "served_by": socket.gethostname()}


@app.get("/time")
async def server_time():
    """Lesson 8: added 'live' while the container was running (bind mount + --reload)."""
    import datetime
    return {"now": datetime.datetime.now().isoformat(), "served_by": socket.gethostname()}


@app.post("/notes")
async def add_note(note: NoteIn):
    if not state["db"]:
        raise HTTPException(503, "Database is not configured - set DATABASE_URL (lesson 7)")
    async with state["db"].acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO notes (text) VALUES ($1) RETURNING id, text, created_at", note.text
        )
    return dict(row)


@app.get("/notes")
async def list_notes():
    if not state["db"]:
        raise HTTPException(503, "Database is not configured - set DATABASE_URL (lesson 7)")
    async with state["db"].acquire() as conn:
        rows = await conn.fetch("SELECT id, text, created_at FROM notes ORDER BY id")
    return [dict(r) for r in rows]
