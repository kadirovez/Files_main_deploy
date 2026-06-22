
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.auth.register import registration_crud
from backend.models.auth.register_session import Registration
from backend.schemas.base import StatusResponseSchema


async def cancel_registration(
        db: AsyncSession,
        registration_session: Registration,
) -> StatusResponseSchema:
    ''' Deletes registration session '''

    result = await registration_crud.delete(
        db=db,
        id=registration_session.id,
    )
    if not result:
        raise HTTPException(
            status_code=401,
            detail='Something went wrong'
        )

    return StatusResponseSchema(status=True)
