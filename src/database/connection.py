import os
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):  # type: ignore[no-redef]
        return False


load_dotenv()


def _default_sqlite_url() -> str:
    db_dir = Path.home() / ".local/share/customer-service-agent"
    db_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_dir / 'app.db'}"


def _ensure_sqlite_parent(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return

    raw_path = database_url.replace("sqlite:///", "", 1)
    if raw_path in {":memory:", ""}:
        return

    db_path = Path(raw_path)
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)


DATABASE_URL = os.getenv("DATABASE_URL") or _default_sqlite_url()
_ensure_sqlite_parent(DATABASE_URL)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def configure_sqlite_optimizations() -> None:
    """Apply SQLite optimizations only when using SQLite."""
    if not urlparse(DATABASE_URL).scheme.startswith("sqlite"):
        return

    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode = WAL"))
        conn.execute(text("PRAGMA synchronous = NORMAL"))
        conn.execute(text("PRAGMA cache_size = -64000"))
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()


def get_db():
    """FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
