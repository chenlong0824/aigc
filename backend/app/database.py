from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from app.config import DATABASE_URL

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 创建ORM基类
Base = declarative_base()


@contextmanager
def get_db_session():
    """
    获取数据库会话的上下文管理器（推荐使用）
    
    使用示例：
        with get_db_session() as db:
            db.query(...)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db():
    """
    获取数据库会话的生成器（用于FastAPI的Depends）
    
    使用示例：
        def some_func(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
