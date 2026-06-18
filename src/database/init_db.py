# src/database/init_db.py
from .connection import engine, configure_sqlite_optimizations
from .models import Base

def init_database():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 应用 SQLite 优化
    configure_sqlite_optimizations()
    
    print("✓ Database initialized successfully!")

if __name__ == "__main__":
    init_database()