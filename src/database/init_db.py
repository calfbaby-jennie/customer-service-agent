from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from src.database.connection import DATABASE_URL, configure_sqlite_optimizations, engine
    from src.database.models import Base
else:
    from .connection import DATABASE_URL, configure_sqlite_optimizations, engine
    from .models import Base


def init_database() -> None:
    """Initialize database tables and SQLite pragmas."""
    Base.metadata.create_all(bind=engine)
    configure_sqlite_optimizations()
    print(f"✓ Database initialized successfully: {DATABASE_URL}")


if __name__ == "__main__":
    init_database()
