from app.database import AsyncSessionLocal, AsyncSession

from fastapi import Depends
from typing import Annotated

def get_async_session():
   
    from contextlib import asynccontextmanager
    @asynccontextmanager
    async def session_scope():
        async with AsyncSessionLocal() as session:
            yield session
    return session_scope()

async_db_dep = Annotated[AsyncSession, Depends(get_async_session)]