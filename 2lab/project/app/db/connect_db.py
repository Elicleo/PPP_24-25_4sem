from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine('sqlite+aiosqlite:///app/db/test.db', future=True)

Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
