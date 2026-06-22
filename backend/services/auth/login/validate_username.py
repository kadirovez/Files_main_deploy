
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.auth.login import login_crud
from backend.crud.auth.user import user_crud
from backend.models.auth.login_session import Login
from backend.schemas import LoginUsernameRequest, LoginUpdate, LoginMaskedEmailResponse
from backend.utils.mask_email import mask_email


async def validate_username(
        db: AsyncSession,
        login_session: Login,
        obj_in: LoginUsernameRequest,
):
    if login_session.login_method != 'username':
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

    user = await user_crud.get_by_username(
        db=db,
        username=obj_in.username
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
            username=user.username,
        ),
    )

    return LoginMaskedEmailResponse(masked_email=mask_email(user.email))

