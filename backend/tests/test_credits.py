"""Tests for app.credits.consume_credit."""

import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.credits import consume_credit
from shared.user import User


@pytest.fixture(name="async_session_factory")
async def async_session_factory_fixture():
    """Fresh in-memory async SQLite engine shared across sessions for one test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest.fixture(name="seed_user")
async def seed_user_fixture(async_session_factory):
    """Insert a user with the given initial credits."""

    async def _seed(credits_value: int) -> int:
        async with async_session_factory() as session:
            user = User(username="u", credits=credits_value, max_credits=credits_value)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user.id  # type: ignore[return-value]

    return _seed


async def _read_credits(factory, user_id: int) -> int:
    async with factory() as session:
        user = await session.get(User, user_id)
        assert user is not None
        return user.credits


async def test_consume_credit_success_debits_once(async_session_factory, seed_user):
    """Successful body execution leaves the credit debited."""
    user_id = await seed_user(3)
    async with async_session_factory() as session:
        async with consume_credit(user_id, session):
            pass
    assert await _read_credits(async_session_factory, user_id) == 2


async def test_consume_credit_refunds_on_exception(async_session_factory, seed_user):
    """An exception inside the body refunds the credit."""
    user_id = await seed_user(3)
    with pytest.raises(RuntimeError):
        async with async_session_factory() as session:
            async with consume_credit(user_id, session):
                raise RuntimeError("agent failed")
    assert await _read_credits(async_session_factory, user_id) == 3


async def test_consume_credit_zero_credits_raises_403(async_session_factory, seed_user):
    """A user with zero credits gets 403 and no debit occurs."""
    user_id = await seed_user(0)
    with pytest.raises(HTTPException) as exc:
        async with async_session_factory() as session:
            async with consume_credit(user_id, session):
                pass
    assert exc.value.status_code == 403
    assert await _read_credits(async_session_factory, user_id) == 0


async def test_consume_credit_no_double_spend_under_concurrency(async_session_factory, seed_user):
    """
    Two concurrent calls against a user with exactly one credit: only one
    succeeds; the other gets 403. Final balance is 0.
    """
    user_id = await seed_user(1)

    async def run():
        async with async_session_factory() as session:
            async with consume_credit(user_id, session):
                await asyncio.sleep(0)
                return "ok"

    results = await asyncio.gather(run(), run(), return_exceptions=True)

    ok_count = sum(1 for r in results if r == "ok")
    http_403_count = sum(
        1 for r in results if isinstance(r, HTTPException) and r.status_code == 403
    )
    assert ok_count == 1
    assert http_403_count == 1
    assert await _read_credits(async_session_factory, user_id) == 0
