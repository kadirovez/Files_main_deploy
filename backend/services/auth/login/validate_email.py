
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.auth.login import login_crud
from backend.crud.auth.user import user_crud
from backend.models.auth.login_session import Login
from backend.schemas import LoginEmailRequest, LoginUpdate
from backend.schemas.base import StatusResponseSchema


async def validate_email(
        db: AsyncSession,
        login_session: Login,
        obj_in: LoginEmailRequest,
):
    if login_session.login_method != 'email':
        raise HTTPException(
            status_code=400,
            detail='Wrong login method'
        )

    await login_crud.reset(
        db=db,
        db_obj=login_session,
        keep_fields={
            'login_method':True
        }
    )

    incoming_email = str(obj_in.email)
    user = await user_crud.get_by_email(
        db=db,
        email=incoming_email
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )

    if user.is_locked:
        raise HTTPException(
            status_code=403,
            detail='User is locked'
        )

    await login_crud.update(
        db=db,
        id=login_session.id,
        obj_in=LoginUpdate(
            user_id=user.id,
            email_matched=True,
            email=incoming_email,
            username=user.username,
        )
    )

    return StatusResponseSchema(status=True)
