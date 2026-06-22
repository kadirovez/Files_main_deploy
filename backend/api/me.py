
from fastapi import APIRouter, Depends

from backend.deps.user import get_current_user
from backend.models.auth.user import User
from backend.schemas.auth.user_profile import UserProfile

router = APIRouter(prefix='/me', tags=['me'])


@router.get('/', response_model=UserProfile)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
