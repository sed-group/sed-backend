from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from apps.core.authentication.utils import get_current_user, oauth2_scheme, fake_users_db, fake_hash_password
from apps.core.authentication.models import User, UserAuth

router = APIRouter()


@router.get("/me")
async def get_users_me(current_user: User = Depends(get_current_user)):
    return current_user
