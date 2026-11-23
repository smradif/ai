import asyncpg
from models.user import UserRegistration, User
from typing import Optional
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fname: str
    lname: str
    email: int
    password: int
    role: str


class UserDatabase:
    def __init__(self, pool: Optional[asyncpg.Pool]):
        self.pool = pool

    async def get_user(self, id: int):
        user = None
        sql = """SELECT * FROM users WHERE id=$1"""
        try:
            async with self.pool.acquire() as conn:
                user = await conn.fetchrow(sql, id)
                return User(**dict(user))
        except Exception as error:
            print(error)
        finally:
            return user

    async def get_user_by_email(self, email: str):
        user = None
        sql = """SELECT * FROM users WHERE email=$1"""
        try:
            async with self.pool.acquire() as conn:
                user = await conn.fetchrow(sql, email)
                return User(**dict(user))
        except Exception as error:
            print(error)
        finally:
            return user

    async def create_user(self, user: UserRegistration):
        new_user = None
        sql = """INSERT INTO users(fname, lname, email, password)
                     VALUES($1, $2, $3, $4) RETURNING id, fname, lname, email, created_at"""
        try:
            async with self.pool.acquire() as conn:
                new_user = await conn.fetchrow(
                    sql,
                    user.fname,
                    user.lname,
                    user.email,
                    user.password,
                )
                return User(**dict(new_user))
        except Exception as error:
            print(error)
        finally:
            return new_user
