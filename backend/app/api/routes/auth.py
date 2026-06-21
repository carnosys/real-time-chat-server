from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from app.core.security import create_access_token
from app.schemas.user import UserCreate
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import Settings
from app.api.deps import get_db
from app.services import user as user_service
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(form : OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    email = form.username #OAuth2PasswordRequestForm only has username and password field so i am using "username" field for the email
    password = form.password
    user = await user_service.login_by_email(db, email, password)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    access_token = create_access_token(
        email,
        expires_delta=timedelta(minutes=Settings.TOKEN_EXPIRY_IN_MIN),
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register(formdata: UserCreate, db = Depends(get_db)):
    user = await user_service.register_user(
        db=db,
        display_name=formdata.display_name,
        username=formdata.username,
        password=formdata.password,
        email=formdata.email,
    )
    return RedirectResponse(url="/auth/login", status_code=303)
