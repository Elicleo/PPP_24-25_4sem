import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))

# from fastapi import FastAPI
# # from app.api.endpoints import router as router_users
# from sqlalchemy.ext.asyncio import async_sessionmaker
# from sqlalchemy import select
# from schemas.schemas import User
#
#
# app = FastAPI()
#
#
# @app.get("/")
# async def home_page():
#     return {"message": "Привет, Хабр!"}
#
#
# @app.get("/users", response_model=User, summary="Получить всех пользователей")
# async def get_all_students():
#     async with async_sessionmaker() as session:
#         query = select(User)
#         result = await session.execute(query)
#         users = result.scalars().all()
#         return users
#
# # app.include_router(router_users)


from fastapi import FastAPI
# from schemas.schemas import User
import uvicorn
from app.api.endpoints import router as router_users

app = FastAPI()


@app.get("/")
async def home_page():
    return {"message": "Hello, World!"}


app.include_router(router_users)


# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=12000)
