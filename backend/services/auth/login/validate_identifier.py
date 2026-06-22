
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.auth.login import login_crud
from backend.models.auth.login_session import Login
from backend.schemas.auth.login import (
    LoginEmailRequest,
    LoginIdentificationRequest,
    LoginUsernameRequest,
    LoginUpdate,
)
from backend.services.auth.login.validate_email import validate_email
from backend.services.auth.login.validate_username import validate_username


async def validate_identifier(
        db: AsyncSession,
        login_session: Login,
        obj_in: LoginIdentificationRequest,
):

    identifier = obj_in.login.strip().lower()

    try:
        email_obj = LoginEmailRequest(email=identifier)
        await login_crud.update(
            db=db,
            id=login_session.id,
            obj_in=LoginUpdate(
                login_method='email'
            ),
        )
        login_session.login_method = 'email'
        return await validate_email(
            db=db,
            login_session=login_session,
            obj_in=email_obj,
        )

    except ValidationError:
        username_obj = LoginUsernameRequest(username=identifier)
        await login_crud.update(
            db=db,
            id=login_session.id,
            obj_in=LoginUpdate(
                login_method='username'
            ),
        )
        login_session.login_method = 'username'
        return await validate_username(
            db=db,
            login_session=login_session,
            obj_in=username_obj,
        )
