# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token
from app.dependencies import get_db, get_current_user
from app.services.user import get_user_by_username, create_user
from app.services.auth import login

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def signup(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user with the given username, email, password, and optional role_id.
    If role_id is omitted, defaults to the 'Driver' role.
    """
    # Check username
    if await get_user_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    # Create and return
    return await create_user(db, user_in)


@router.post(
    "/login",
    response_model=Token,
    summary="Obtain a JWT for an existing user"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Exchange username & password for a JWT access token.
    Send credentials as `application/x-www-form-urlencoded`:
        username=<username>&password=<password>
    """
    access_token = await login(db, form_data.username, form_data.password)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the current authenticated user"
)
async def read_users_me(
    current_user=Depends(get_current_user)
):
    """
    Returns the User record for the JWT you provided in `Authorization: Bearer <token>`.
    """
    return current_user
