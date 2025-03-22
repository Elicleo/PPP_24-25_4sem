import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from fastapi import APIRouter
from models.models import User
# from schemas import User
from secrets import token_urlsafe
from db.connect_db import Session
from sqlalchemy.future import select


router = APIRouter(prefix='/users', tags=['Работа с пользователями'])

current_user = {"id": None, "email": None}


@router.post("/me", summary='Logged user')
async def login():
    return current_user


@router.post("/login", summary="Login")
async def login(user_email: str, user_pass: str):
    async with Session() as session:
        query = select(User).filter(user_email == User.email, user_pass == User.password)
        res = await session.execute(query)
        try:
            user = res.scalars().one()
            user_token = token_urlsafe()
            user_id, user_email = user.id, user.email
            current_user["id"], current_user["email"] = user_id, user_email
            return {"id": user_id, "email": user_email, "token": user_token}
        except:
            return "Incorrect email or password"


@router.post("/sign-up/", summary="Sign up")
async def sign_up(user_email: str, user_name: str, user_pass: str):
    async with Session() as session:
        res = await session.execute(select(User).filter(user_email == User.email))
        try:
            user = res.scalars().one()
            user_id, user_email = user.id, user.email
            current_user["id"], current_user["email"] = user_id, user_email
            return "User with this email already exists"
        except:
            new_user = User(username=user_name, email=user_email, password=user_pass)
            session.add(new_user)
            await session.commit()
            res = await session.execute(select(User).filter(user_email == User.email))
            user_id = res.scalars().one().id
            current_user["id"], current_user["email"] = user_id, user_email
            user_token = token_urlsafe()
            return {"id": user_id, "email": user_email, "token": user_token}


@router.get("/", summary="Get all users in db")
async def get_all_students():
    async with Session() as session:
        query = select(User)
        result = await session.execute(query)
        users = result.scalars().all()
        return users
