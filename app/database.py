from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from app.settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DB_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, 
                                       class_= AsyncSession, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass




