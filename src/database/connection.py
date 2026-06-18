# src/database/connection.py
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Mac 本地开发推荐：把数据库放在项目目录下
DB_DIR = Path.home() / ".local/share/customer-service-agent"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "app.db"

# SQLite 连接字符串
DATABASE_URL = f"sqlite:///{DB_PATH}"

print(f"✓ Database path: {DB_PATH}")

# SQLAlchemy 引擎配置（Mac SQLite 优化）
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # 改为 True 查看 SQL 语句
)

# Session 工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# SQLite 优化选项（for Mac）
def configure_sqlite_optimizations():
    """Mac SQLite 性能优化"""
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode = WAL"))       # 写入优化
        conn.execute(text("PRAGMA synchronous = NORMAL"))     # 平衡速度与安全
        conn.execute(text("PRAGMA cache_size = -64000"))      # 64MB 缓存
        conn.execute(text("PRAGMA foreign_keys = ON"))        # 外键约束
        conn.commit()

def get_db():
    """FastAPI 依赖注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()