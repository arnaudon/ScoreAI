"""Tests for authentication and user utilities in app.users."""

from datetime import timedelta

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.users import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    get_user,
    verify_password,
)
from shared.user import User


@pytest.fixture
def user_in_db(session: Session, mocker) -> User:
    """Create a user in the same DB that app.users.get_user will use.

    We patch app.users.get_session to return the test session so helpers that
    call next(get_session()) see the in-memory test database.
    """

    def get_session_override():
        yield session

    mocker.patch("app.users.get_session", get_session_override)

    user = User(username="alice", email="alice@example.com")
    user.password = get_password_hash("secret")
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def test_password_hash_and_verify():
    """verify_password and get_password_hash work together."""

    password = "my-password"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_get_user_and_authenticate_user(user_in_db: User):
    """get_user and authenticate_user return the correct user or False."""

    # get_user finds the user by username
    fetched = get_user(user_in_db.username)
    assert fetched is not None
    assert fetched.id == user_in_db.id

    # authenticate_user succeeds with correct password
    assert authenticate_user(user_in_db.username, "secret")

    # and fails with wrong password or unknown user
    assert authenticate_user(user_in_db.username, "wrong") is False
    assert authenticate_user("unknown", "secret") is False


@pytest.mark.asyncio
async def test_create_access_token_and_get_current_user(user_in_db: User):
    """create_access_token embeds username and get_current_user resolves it."""

    # shorter expiry to exercise explicit expiry branch
    token = create_access_token(
        data={"sub": user_in_db.username},
        expires_delta=timedelta(minutes=5),
    )

    user = await get_current_user(token)
    assert user.id == user_in_db.id


@pytest.mark.asyncio
async def test_get_current_user_valid_invalid_and_missing_sub(user_in_db: User):
    """get_current_user returns user for valid token and raises for bad tokens."""

    # valid token
    token = create_access_token(data={"sub": user_in_db.username})
    user = await get_current_user(token)
    assert user.id == user_in_db.id

    # invalid token string
    with pytest.raises(HTTPException) as exc:
        await get_current_user("not-a-valid-token")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    # token without sub should also raise (exercises username is None branch)
    no_sub_token = create_access_token(data={})
    with pytest.raises(HTTPException) as exc2:
        await get_current_user(no_sub_token)
    assert exc2.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_missing_user_raises(session: Session, mocker):
    """If the token refers to a non-existing user, get_current_user raises 401."""

    def empty_session_override():
        # Provide an empty DB to ensure user lookup fails
        yield session

    mocker.patch("app.users.get_session", empty_session_override)

    # token with username that does not exist
    token = create_access_token(data={"sub": "does-not-exist"})
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_for_access_token_success(user_in_db: User, client: TestClient):
    """POST /token returns a bearer token for valid credentials."""

    response = client.post(
        "/token",
        data={"username": user_in_db.username, "password": "secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)


def test_login_for_access_token_wrong_credentials(client: TestClient, user_in_db: User):
    """/token returns 401 for wrong password."""

    response = client.post(
        "/token",
        data={"username": user_in_db.username, "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_add_user_endpoint(client: TestClient):
    """POST /users creates a user with hashed password (covers add_user)."""
    payload = {"username": "bob", "email": "bob@example.com", "password": "pw"}
    resp = client.post("/users", json=payload)
    assert resp.status_code == 200
