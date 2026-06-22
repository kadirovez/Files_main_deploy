
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.auth.login import login_crud
from backend.deps.database import get_db
from backend.deps.session import get_login_session
from backend.models.auth.login_session import Login
from backend.schemas.addons import Token
from backend.schemas.auth.base import CreateSessionSchema
from backend.schemas.auth.login import (
    LoginConfirmEmailRequest,
    LoginPasswordRequest,
    LoginEmailOTPRequest,
    LoginIdentificationRequest,
)
from backend.services.auth.login import login_service
from backend.services.session import session_service
from backend.utils.ip_address import get_ip

router = APIRouter(prefix='/login', tags=['login'])


@router.get('/start', response_model=Token)
async def start_login(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    ''' Starts login session '''
    return await session_service.start_session(
        db=db,
        ip_address=get_ip(request),
        crud=login_crud,
        create_schema=CreateSessionSchema,
    )

@router.post('/identification')
async def identification(
        obj_in: LoginIdentificationRequest,
        login_session: Login = Depends(get_login_session),
        db: AsyncSession = Depends(get_db)
):
    '''
    Gets username or email as identifier, and validates it.
    Sets login_method marker to 'username' or 'email'
    '''
    return await login_service.validate_identifier(
        db=db,
        login_session=login_session,
        obj_in=obj_in
    )


@router.post('/password')
async def submit_password(
    obj_in: LoginPasswordRequest,
    login_session: Login = Depends(get_login_session),
    db: AsyncSession = Depends(get_db),
):
    ''' Validates password for both flows '''
    return await login_service.validate_password(
        db=db,
        login_session=login_session,
        obj_in=obj_in,
    )


@router.post('/confirm-email')
async def confirm_email(
    obj_in: LoginConfirmEmailRequest,
    login_session: Login = Depends(get_login_session),
    db: AsyncSession = Depends(get_db),
):
    ''' Matches masked email and entered email (use only in username flow) '''
    return await login_service.confirm_email(
        db=db,
        login_session=login_session,
        obj_in=obj_in,
    )


@router.get('/send-email-otp')
async def send_email_otp(
    login_session: Login = Depends(get_login_session),
    db: AsyncSession = Depends(get_db),
):
    ''' Sends email otp code to email address '''
    return await login_service.send_email_otp(
        db=db,
        login_session=login_session,
    )


@router.post('/confirm-email-otp')
async def confirm_email_otp(
    obj_in: LoginEmailOTPRequest,
    login_session: Login = Depends(get_login_session),
    db: AsyncSession = Depends(get_db),
):
    ''' Confirms email by OTP code '''
    return await login_service.confirm_email_otp(
        db=db,
        login_session=login_session,
        obj_in=obj_in,
    )

@router.post('/complete-login')
async def complete_login(
        request:Request,
        login_session: Login = Depends(get_login_session),
        db: AsyncSession = Depends(get_db),
):
    return await login_service.complete_login(
        request=request,
        db=db,
        login_session=login_session,
    )


@router.delete('/cancel')
async def cancel_login(
    login_session: Login = Depends(get_login_session),
    db: AsyncSession = Depends(get_db),
):
    return await login_service.cancel_login(
        db=db,
        login_session=login_session,
    )
