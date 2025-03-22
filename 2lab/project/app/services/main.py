import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))


from fastapi import FastAPI
from app.api.endpoints import router as router_users

app = FastAPI()


@app.get("/")
async def home_page():
    return {"message": "Hello, World!"}


app.include_router(router_users)
