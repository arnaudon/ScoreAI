"""Tests for authentication and user utilities in app.users."""

from datetime import timedelta

import jwt
import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app import users
from shared.user import User


@pytest.fixture(name="user_in_db")
def user_in_db_fixture(test_user, session: Session) -> User:
    """Create a user in the same DB."""
    test_user.password = users.get_password_hash("secret")
    session.add(test_user)
    session.commit()
    session.refresh(test_user)

    return test_user


def test_password_hash_and_verify():
    """verify_password and get_password_hash work together."""

    password = "my-password"
    hashed = users.get_password_hash(password)
    assert hashed != password
    assert users.verify_password(password, hashed)


def test_get_user_and_authenticate_user(user_in_db: User, session: Session):
    """get_user and authenticate_user return the correct user or False."""

    # get_user finds the user by username
    fetched = users.get_user(user_in_db.username, session)
    assert fetched is not None
    assert fetched.id == user_in_db.id

    # authenticate_user succeeds with correct password
    assert users.authenticate_user(user_in_db.username, "secret", session)

    # and fails with wrong password or unknown user
    assert users.authenticate_user(user_in_db.username, "wrong", session) is False
    assert users.authenticate_user("unknown", "secret", session) is False


def test_create_access_token_default_expiry():
    """create_access_token uses default 15 minutes if expires_delta is None."""
    token = users.create_access_token(data={"sub": "test"})
    decoded = jwt.decode(token, users.SECRET_KEY, algorithms=[users.ALGORITHM])
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_create_access_token_and_get_current_user(user_in_db: User, session: Session):
    """create_access_token embeds username and get_current_user resolves it."""

    # shorter expiry to exercise explicit expiry branch
    token = users.create_access_token(
        data={"sub": user_in_db.username},
        expires_delta=timedelta(minutes=5),
    )

    user = await users.get_current_user(token, session=session)
    assert user.id == user_in_db.id


@pytest.mark.asyncio
async def test_get_current_user_valid_invalid_and_missing_sub(user_in_db: User, session: Session):
    """get_current_user returns user for valid token and raises for bad tokens."""

    # valid token
    token = users.create_access_token(data={"sub": user_in_db.username})
    user = await users.get_current_user(token, session=session)
    assert user.id == user_in_db.id

    # invalid token string
    with pytest.raises(HTTPException) as exc:
        await users.get_current_user("not-a-valid-token", session=session)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    # token without sub should also raise (exercises username is None branch)
    no_sub_token = users.create_access_token(data={})
    with pytest.raises(HTTPException) as exc2:
        await users.get_current_user(no_sub_token, session=session)
    assert exc2.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_missing_user_raises(session: Session):
    """If the token refers to a non-existing user, get_current_user raises 401."""
    # token with username that does not exist
    token = users.create_access_token(data={"sub": "does-not-exist"})
    with pytest.raises(HTTPException) as exc:
        await users.get_current_user(token, session=session)
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


def test_get_users(client: TestClient):
    """GET /users returns all users (covers get_users)."""
    resp = client.get("/users")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_is_admin(test_user):
    """is_admin returns True if user is admin (covers is_admin)."""
    assert await users.is_admin(test_user) is True
    assert await users.is_admin(None) is False


@pytest.mark.asyncio
async def test_get_admin_user(test_user):
    """get_admin_user returns admin user or None (covers get_admin_user)."""
    assert await users.get_admin_user(test_user) is None
    test_user.role = "other"
    assert await users.get_admin_user(test_user) is None
    test_user.role = "admin"
    assert await users.get_admin_user(test_user) is test_user


def test_get_current_user_route(client: TestClient):
    """GET /user returns current user (covers get_current_user)."""
    resp = client.get("/user")
    assert resp.status_code == 200


def test_update_password(user_in_db: User, client: TestClient):
    """PUT /user/password updates the password."""
    token = users.create_access_token(data={"sub": user_in_db.username})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Incorrect current password
    resp = client.put(
        "/user/password",
        json={"current_password": "wrong", "new_password": "new-secret"},
        headers=headers,
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Incorrect current password"

    # 2. Correct current password
    resp = client.put(
        "/user/password",
        json={"current_password": "secret", "new_password": "new-secret"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Password updated successfully"

    # 3. Verify new password works
    login_resp = client.post(
        "/token",
        data={"username": user_in_db.username, "password": "new-secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_resp.status_code == 200


def test_delete_account(user_in_db: User, client: TestClient):
    """DELETE /user deletes the account."""
    from app.main import app
    app.dependency_overrides.pop(users.get_current_user, None)

    token = users.create_access_token(data={"sub": user_in_db.username})
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.delete("/user", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Account deleted successfully"

    # The user should no longer be accessible
    resp_after = client.get("/user", headers=headers)
    assert resp_after.status_code == 401
