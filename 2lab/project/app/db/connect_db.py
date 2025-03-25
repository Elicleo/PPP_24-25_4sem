import os.path

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# abs = os.path.abspath()
engine = create_async_engine('sqlite+aiosqlite:///app/db/test.db', future=True)
# ///app/db/test.db
Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
