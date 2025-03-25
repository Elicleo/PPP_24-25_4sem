import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from fastapi import APIRouter
from models.models import User
from secrets import token_urlsafe
from db.connect_db import Session
from sqlalchemy.future import select
from sqlalchemy import delete, update


router = APIRouter(prefix='/users', tags=['Работа с пользователями'])

current_user = {"id": None, "email": None}


@router.get("/", summary="Get all users in db")
async def get_all_students():
    async with Session() as session:
        query = select(User)
        result = await session.execute(query)
        users = result.scalars().all()
        return users


@router.post("/me", summary='Logged user')
async def login():
    return current_user


@router.post("/sign-up/", summary="Sign up")
async def sign_up(user_email: str, user_name: str, user_pass: str):
    async with Session() as session:
        res = await session.execute(select(User).filter(user_email == User.email))
        try:
            user = res.scalars().one()
            user_id, user_email = user.id, user.email
            current_user["id"], current_user["email"] = user_id, user_email
            return {"Message": "User with this email already exists"}
        except:
            new_user = User(username=user_name, email=user_email, password=user_pass)
            session.add(new_user)
            await session.commit()
            res = await session.execute(select(User).filter(user_email == User.email))
            user_id = res.scalars().one().id
            current_user["id"], current_user["email"] = user_id, user_email
            user_token = token_urlsafe()
            return {"id": user_id, "email": user_email, "token": user_token}


@router.post("/login/", summary="Login")
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
            return {"Message": "Incorrect email or password"}


@router.delete("/delete/")
async def delete_user(user_email: str):
    async with Session() as session:
        query = delete(User).filter(User.email == user_email)
        res = await session.execute(query)
        try:
            await session.commit()
            return {"Message": f"User {user_email} deleted"}
        except:
            return {"Message": "No such user in database"}


@router.put("/update/")
async def update_user_info(user_email: str, user_email_to_upd: str = None, user_name: str = None, user_pass_old: str = None, user_pass_new: str = None):
    async with Session() as session:
        query1 = select(User).filter(User.email == user_email)
        res1 = await session.execute(query1)
        try:
            user = res1.scalars().one()
            if not user_email_to_upd and not user_name and not user_pass_new:
                return {"Message": "Got nothing to update"}
            if not user_email_to_upd:
                user_email_to_upd = user.email
            if not user_name:
                user_name = user.username
            if user_pass_new:
                if user.password != user_pass_old:
                    return {"Message": "Incorrect password, attempt blocked"}
            if not user_pass_new:
                user_pass_new = user.password
            query2 = update(User).where(User.email == user_email).values(id=user.id, username=user_name,
                                                                         password=user_pass_new,
                                                                         email=user_email_to_upd)
            result = await session.execute(query2)
            try:
                await session.commit()
                return {"Message": f"User info for {user_email} updated"}
            except:
                return {"Message": "Error"}
        except:
            return {"Message": "No such user in database"}
