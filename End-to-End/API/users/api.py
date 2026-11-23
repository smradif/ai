import re
import os
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from models.user import (
    UserRegistration,
    User,
    UserLogin,
    TokenResponse,
    DuplicateEmailError,
)
from auth.jwt import create_token, verify_password, hash_password
import asyncpg
from database.postgres import get_postgres
from .db import UserDatabase

router = APIRouter(prefix="/users", tags=["users"])
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def user_api_builder(app):

    @router.post(
        "/register",
        response_model=User,
        status_code=status.HTTP_201_CREATED,
    )
    async def register_user(
        user: UserRegistration, db_pool: asyncpg.Pool = Depends(get_postgres)
    ) -> User:
        email = user.email.strip()
        if not EMAIL_PATTERN.fullmatch(email):
            raise HTTPException(
                status_code=422, detail="A valid email address is required"
            )
        try:
            db = UserDatabase(db_pool)
            user.password = hash_password(user.password)
            saved_user = await db.create_user(user)
        except DuplicateEmailError:
            raise HTTPException(
                status_code=409, detail="An account with this email already exists"
            )
        return User(**saved_user)

    @router.post("/login", response_model=TokenResponse)
    async def login_user(
        credentials: UserLogin, db_pool: asyncpg.Pool = Depends(get_postgres)
    ) -> TokenResponse:
        secret_key = os.environ.get("JWT_SECRET_KEY")
        if not secret_key or len(secret_key.encode("utf-8")) < 32:
            raise HTTPException(
                status_code=500,
                detail="JWT_SECRET_KEY must contain at least 32 bytes",
            )
        db = UserDatabase(db_pool)
        user = await db.get_user_by_email(credentials.email)
        if user is None or not verify_password(
            credentials.password, str(user["password"])
        ):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        access_token = create_token(
            user_id=user["id"],
            email=credentials.email,
            user_role=user["role"],
            token_type="access",
            ttl=60,
        )
        return TokenResponse(access_token=access_token)

    app.include_router(router)
