from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
)

password = "local"

# mysql
DATABASE_URL = (
    f"mysql+aiomysql://root:{password}@localhost/fastapi_proj"  # MySQL 데이터베이스 URL
)

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,  # Use AsyncSession for async operations
)

Base = declarative_base()
