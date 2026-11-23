import sqlite3

from fastapi import FastAPI
from fastapi.testclient import TestClient
import jwt

from users.router import router


def test_register_user_persists_hash_and_rejects_duplicate(tmp_path, monkeypatch):
    database_path = tmp_path / "users.db"
    jwt_secret = "test-signing-secret-with-at-least-32-bytes"
    monkeypatch.setenv("USERS_DB_PATH", str(database_path))
    monkeypatch.setenv("JWT_SECRET_KEY", jwt_secret)
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    payload = {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "password": "correct-horse",
    }

    response = client.post("/users/register", json=payload)

    assert response.status_code == 201
    assert response.json()["email"] == "ada@example.com"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()

    with sqlite3.connect(database_path) as connection:
        stored_user = connection.execute(
            "SELECT name, email, password_hash FROM users"
        ).fetchone()

    assert stored_user[0] == "Ada Lovelace"
    assert stored_user[1] == "ada@example.com"
    assert stored_user[2] != payload["password"]
    assert stored_user[2].startswith("scrypt$")

    login_response = client.post(
        "/users/login",
        json={"email": "ADA@example.com", "password": payload["password"]},
    )
    assert login_response.status_code == 200
    assert login_response.json()["token_type"] == "bearer"
    claims = jwt.decode(
        login_response.json()["access_token"], jwt_secret, algorithms=["HS256"]
    )
    assert claims["sub"] == str(response.json()["id"])
    assert claims["exp"] - claims["iat"] == 24 * 60 * 60

    failed_login = client.post(
        "/users/login", json={"email": payload["email"], "password": "wrong-password"}
    )
    assert failed_login.status_code == 401

    duplicate_response = client.post("/users/register", json=payload)
    assert duplicate_response.status_code == 409
