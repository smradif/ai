from datetime import datetime, timedelta, timezone
import os
from typing import Literal
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import hmac
import hashlib
import secrets
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
secret_key = os.environ.get("JWT_SECRET_KEY")

def create_token(
    user_id: int,
    email: str,
    user_role: str,
    token_type: Literal["refresh", "access"],
    ttl: int
) -> str:
    if not secret_key or len(secret_key.encode("utf-8")) < 32:
        raise HTTPException(
            status_code=500,
            detail="JWT_SECRET_KEY must contain at least 32 bytes",
        )
    payload = {
        "sub": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ttl),
        "user_role": user_role,
        "user_id": user_id,
        "scopes": ["read", "write"] if user_role.strip() == "admin" else ["read"]
    }

    if token_type == "access":
        key = secret_key
    elif token_type == "refresh":
        key = secret_key

    encoded_jwt = jwt.encode(
        payload,
        key,
        "HS256"
    )

    return encoded_jwt

async def decode_access_token(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms="HS256",
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}"
        )
    return payload

async def decode_refresh_token(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms="HS256",
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}"
        )

    return payload

async def get_access_token(token: str = Depends(oauth2_scheme)) -> dict:
    return token

def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, salt_hex, hash_hex = encoded_hash.split("$", maxsplit=2)
        if algorithm != "scrypt":
            return False

        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        actual_hash = hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1
        )
    except ValueError:
        return False

    return hmac.compare_digest(actual_hash, expected_hash)

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1
    )
    return f"scrypt${salt.hex()}${password_hash.hex()}"
