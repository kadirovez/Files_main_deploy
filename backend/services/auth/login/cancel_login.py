
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.auth.login import login_crud
from backend.models.auth.login_session import Login
from backend.schemas.base import StatusResponseSchema


async def cancel_login(
        db: AsyncSession,
        login_session: Login,
) -> StatusResponseSchema:
    result = await login_crud.delete(
        db=db,
        id=login_session.id
    )
    if not result:
        raise HTTPException(
            status_code=404,
            detail='Session invalid'
        )
    return StatusResponseSchema(status=True)
