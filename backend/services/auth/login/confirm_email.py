
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.auth.login import login_crud
from backend.crud.auth.user import user_crud
from backend.models.auth.login_session import Login
from backend.schemas import LoginConfirmEmailRequest, LoginUpdate
from backend.schemas.base import StatusResponseSchema


async def confirm_email(
        db: AsyncSession,
        login_session: Login,
        obj_in: LoginConfirmEmailRequest,
) -> StatusResponseSchema:
    if login_session.login_method != 'username':
        raise HTTPException(
            status_code=400,
            detail='Use only in username flow'
        )

    if not login_session.user_id:
        raise HTTPException(
            status_code=400,
            detail='Identify user first'
        )

    user = await user_crud.get(db=db, id=login_session.user_id)
    incoming_email = str(obj_in.email).lower()

    if incoming_email != user.email.lower():
        raise HTTPException(
            status_code=401,
            detail='Wrong email address'
        )

    await login_crud.update(
        db=db,
        id=login_session.id,
        obj_in=LoginUpdate(
            email_matched=True
        ),
    )

    return StatusResponseSchema(status=True)
