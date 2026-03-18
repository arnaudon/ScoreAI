"""Users module."""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from sqlmodel import Session, func, select

from app.db import get_session
from app.rate_limit import limiter
from shared.scores import Score
from shared.user import User

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "...")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 1


router = APIRouter(prefix="", tags=["users"])


class Token(BaseModel):
    """Token model."""

    access_token: str
    token_type: str


class UserUpdateRequest(BaseModel):
    """User update request model."""

    instrument: str | None = None
    email: str | None = None


class PasswordChangeRequest(BaseModel):
    """Password change request model."""

    current_password: str
    new_password: str


class CreditUpdateRequest(BaseModel):
    """Credit update request model."""

    max_credits: int


password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    """Verify password."""
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Get password hash."""
    return password_hash.hash(password)


def get_user(username: str, session: Session):
    """Get user by username."""
    return session.exec(select(User).where(User.username == username)).first()


def authenticate_user(username: str, password: str, session: Session):
    """Authenticate user."""
    user = get_user(username, session)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/token")
@limiter.limit("10/minute")
def login_for_access_token(
    request: Request,  # pylint: disable=unused-argument
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
) -> Token:
    """Login for access token."""
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    session.refresh(user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
):
    """Get current user."""
    return get_current_user_from_token(token, session)


def get_current_user_from_token(token: str, session: Session):
    """Validate a token and return the corresponding user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError as exc:
        raise credentials_exception from exc
    user = get_user(username=username, session=session)
    if user is None:
        raise credentials_exception
    return user


def get_admin_user(user: User = Depends(get_current_user)):
    """Get admin user only."""
    if user.role == "admin":
        return user
    return None


@router.post("/users")
@limiter.limit("5/minute")
def add_user(
    request: Request,  # pylint: disable=unused-argument
    user: User,
    session: Session = Depends(get_session),
):
    """Add a user to the db."""
    hashed_password = get_password_hash(user.password)
    user.password = hashed_password
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/users")
def get_users(_: Annotated[User, Depends(get_admin_user)], session: Session = Depends(get_session)):
    """Get all users from the db."""
    users = session.exec(select(User)).all()
    result = []
    for user in users:
        # pylint: disable=not-callable
        count = session.exec(select(func.count(Score.id)).where(Score.user_id == user.id)).one()
        user_dict = user.model_dump()
        user_dict["score_count"] = count
        result.append(user_dict)
    return result


@router.get("/user")
def get_current_user_route(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get current user."""
    return current_user


@router.put("/user")
def update_user(
    req: UserUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """Update current user."""
    updated = False
    if req.instrument is not None:
        current_user.instrument = req.instrument
        updated = True

    if req.email is not None:
        current_user.email = req.email
        updated = True

    if updated:
        session.add(current_user)
        session.commit()
        session.refresh(current_user)

    return current_user


@router.get("/is_admin")
def is_admin(current_user: Annotated[User | None, Depends(get_admin_user)]):
    """Check if user is admin."""
    if current_user is not None:
        return True
    return False


@router.put("/user/password")
def update_password(
    req: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """Update user password."""
    if not verify_password(req.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )
    current_user.password = get_password_hash(req.new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Password updated successfully"}


@router.put("/users/{user_id}/credits")
def set_user_credits(
    user_id: int,
    request: CreditUpdateRequest,
    current_user: Annotated[User | None, Depends(get_admin_user)],
    session: Session = Depends(get_session),
):
    """Set max credits for a user (admin only)."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )

    user_to_update = session.get(User, user_id)
    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")

    user_to_update.max_credits = request.max_credits
    session.add(user_to_update)
    session.commit()
    session.refresh(user_to_update)
    return user_to_update


@router.post("/users/{user_id}/refill_credits")
def refill_user_credits(
    user_id: int,
    current_user: Annotated[User | None, Depends(get_admin_user)],
    session: Session = Depends(get_session),
):
    """Refill credits for a user to their max value (admin only)."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )

    user_to_update = session.get(User, user_id)
    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")

    user_to_update.credits = user_to_update.max_credits
    session.add(user_to_update)
    session.commit()
    session.refresh(user_to_update)
    return user_to_update


@router.delete("/user")
def delete_account(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """Delete current user."""
    session.delete(current_user)
    session.commit()
    return {"message": "Account deleted successfully"}
