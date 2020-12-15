from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from apps.core.authentication.utils import get_current_user, oauth2_scheme, fake_users_db, fake_hash_password
from apps.core.authentication.models import User, UserInDB

router = APIRouter()


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@router.get("/users/me")
async def get_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@router.get("/")
async def get_api_root():
    return {"version": "0.1"}
