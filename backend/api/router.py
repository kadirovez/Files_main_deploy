
from fastapi import APIRouter

from backend.api.auth.login import router as login_router
from backend.api.auth.registration import router as registration_router
from backend.api.chats.chats import router as chats_router
from backend.api.me import router as me_router

api_router = APIRouter()
api_router.include_router(registration_router)
api_router.include_router(login_router)
api_router.include_router(me_router)
api_router.include_router(chats_router)
