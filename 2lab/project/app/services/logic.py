import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))


from fastapi import FastAPI
from api.endpoints import router as router_users
from services.image_bin import *
import uvicorn

app = FastAPI()


@app.get("/")
async def home_page():
    return {"message": "Hello, World!"}


@app.post("/binary_image")
async def binarize(im_raw_b64: str):
    return all_the_bradley(im_raw_b64)


app.include_router(router_users)

# print(*sys.path, sep='\n')
# from db import connect_db
# f = test.db

if __name__ == "__main__":
    uvicorn.run("project2.app.services.main:app", host="127.0.0.1", port=8000)
