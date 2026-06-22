
from datetime import timedelta, datetime, timezone

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.settings import settings
from backend.crud.auth.login import login_crud
from backend.crud.auth.main import main_crud
from backend.models.auth.login_session import Login
from backend.schemas import LoginUpdate, Token
from backend.schemas.auth.main import MainCreate
from backend.utils.generator import generate_string
from backend.utils.ip_address import get_ip
from backend.utils.jwt_token import create_access_token


async def complete_login(
        request: Request,
        db: AsyncSession,
        login_session: Login,
) -> Token:

    # Check
    if login_session.is_completed:
        raise HTTPException(
            status_code=400,
            detail='Session already completed'
        )

    if not login_session.password_is_validated or not login_session.email_is_confirmed:
        raise HTTPException(
            status_code=400,
            detail='Complete login steps first'
        )

    await login_crud.update(
        db=db,
        id=login_session.id,
        obj_in=LoginUpdate(
            is_completed=True
        ),
    )

    ip_address = get_ip(request)
    session = generate_string(256, digits=True, lowercase=True, uppercase=True)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

    await main_crud.create(
        db=db,
        obj_in=MainCreate(
            user_id=login_session.user_id,
            ip_address=ip_address,
            session=session,
        ),
    )

    access_token = create_access_token(
        data={
            'session': session,
            'ip_address': ip_address,
        },
        expires_delta=access_token_expires,
    )

    return Token(
        access_token=access_token,
        token_type='bearer',
        expires_in=str(datetime.now(timezone.utc) + access_token_expires),
    )
