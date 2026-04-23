from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# ─── Async engine (for FastAPI routes) ───────────────────────────────
_raw_url = settings.database_url
if _raw_url.startswith("postgresql://"):
    _async_url = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    _async_url = _raw_url

parsed = urlparse(_async_url)
query_params = parse_qs(parsed.query)

ssl_mode = query_params.pop("sslmode", [None])[0]
cleaned_query = urlencode({k: v[0] for k, v in query_params.items()})
ASYNC_DATABASE_URL = urlunparse(parsed._replace(query=cleaned_query))

connect_args = {}
if ssl_mode and ssl_mode != "disable":
    connect_args["ssl"] = ssl_mode

engine = create_async_engine(ASYNC_DATABASE_URL, echo=False, connect_args=connect_args)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

# ─── Sync engine (for LangGraph tools) ──────────────────────────────
# psycopg2 supports sslmode natively, so use the raw URL as-is
SYNC_DATABASE_URL = settings.database_url
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
)

# ─── Base ────────────────────────────────────────────────────────────
Base = declarative_base()


# ─── Async dependency (FastAPI routes) ───────────────────────────────
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ─── Sync dependency (LangGraph tools) ──────────────────────────────
def get_sync_db():
    db = SyncSessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise