from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import asyncio

engine = create_async_engine('sqlite+aiosqlite:///app/db/test.db', future=True)
# Base = declarative_base()
#
#
# class User(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     username = Column(String(255), unique=True, nullable=False)
#     password = Column(String(255), nullable=False)
#     email = Column(String(255), unique=True, nullable=False)
#
#
# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#
# asyncio.run(init_models())
#
#
# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
# init_db()

Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# engine = create_async_engine('sqlite+aiosqlite:///example1.db')
# Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# async with Session() as session:
#     user = select(User).filter(user_name == User.username, user_pass == User.password).first()
#     user = session.query()
#     result = await session.execute(user)
