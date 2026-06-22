import asyncio

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.deps.database import get_db
from backend.models.auth.login_session import Login


async def get_active_login_sessions(db: AsyncSession):

    result = await db.execute(
        select(func.count()).select_from(Login)
    )

    active_login_sessions = result.scalar_one()
    print(f"ACTIVE LOGIN SESSIONS = {active_login_sessions}")

    return active_login_sessions
