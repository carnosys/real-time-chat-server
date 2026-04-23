from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import Settings

DATABASE_URL = Settings.get_url

engine = create_async_engine(DATABASE_URL, echo = True)

AsyncSessionLocal = sessionmaker(
    bind = engine,
    class_= AsyncSession,
    expire_on_commit = False
)

async def get_db():
    async with AsyncSessionLocal as session:
        yield session 




