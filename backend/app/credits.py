"""Atomic credit accounting for agent endpoints."""

from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import HTTPException
from sqlalchemy import update
from sqlmodel.ext.asyncio.session import AsyncSession

from app import config
from shared.user import User

logger = getLogger(__name__)


def _out_of_credits_detail() -> str:
    return (
        "You have run out of agent credits."
        f"Please contact {config.SUPPORT_EMAIL} to get more credits."
    )


@asynccontextmanager
async def consume_credit(user_id: int, session: AsyncSession):
    """
    Atomically debit one credit from the user; refund on exception.

    Uses a conditional UPDATE (credits > 0) so the check-and-debit is a
    single SQL statement, preventing the read-modify-write race of the
    previous implementation. On any exception raised inside the ``async
    with`` body, the credit is refunded in a separate transaction.
    """
    debit = await session.execute(
        update(User)
        .where(User.id == user_id, User.credits > 0)  # type: ignore[arg-type]
        .values(credits=User.credits - 1)
    )
    if debit.rowcount == 0:  # type: ignore[attr-defined]
        raise HTTPException(status_code=403, detail=_out_of_credits_detail())
    await session.commit()

    try:
        yield
    except Exception:
        try:
            await session.execute(
                update(User).where(User.id == user_id).values(credits=User.credits + 1)
            )
            await session.commit()
        except Exception:
            logger.exception("failed to refund credit for user %s", user_id)
        raise
