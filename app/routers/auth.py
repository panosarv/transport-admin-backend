# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, func
from app.models.company import Company
from app.schemas.company import CompanyCreate
from app.schemas.user import RegisterCompanyUser
from app.services.company import create_company
from app.schemas.user import UserCreate, UserRead
from app.services.user import create_user, get_user_by_username, get_user_by_id
from app.models.role import Role
from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token
from app.dependencies import get_db, get_current_user
from app.services.user import get_user_by_username, create_user
from app.services.auth import login


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserRead, status_code=201,
             summary="Admin adds another user to their company")
async def signup(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # only Admins may add users
    if current_user.role_id != 1:
        raise HTTPException(403, "Insufficient permissions")

    if await get_user_by_username(db, user_in.username):
        raise HTTPException(400, "Username already registered")

    # create user under the same company as current_user
    return await create_user(db, user_in, current_user.company_id)


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

@router.post(
    "/register",
    response_model=UserRead,
    status_code=201,
    summary="Create first company + Admin user",
)
async def register_company(
    reg_in: RegisterCompanyUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Only if no companies exist: create a Company and an Admin user.
    """
    # Check there’s no existing company
    cnt = await db.scalar(select(func.count()).select_from(Company))
    if cnt > 0:
        raise HTTPException(
            status_code=400,
            detail="Company already registered. Please log in as Admin to add users."
        )

    # 1) Create the company
    comp = await create_company(db, CompanyCreate(
        name=reg_in.company_name,
        address=None,
    ))

    # 2) Find the Admin role
    role = (await db.execute(select(Role).where(Role.name == "Admin"))).scalars().first()
    if not role:
        raise HTTPException(500, "Admin role missing—please seed roles")

    # 3) Create the user as Admin of that company
    user_in = UserCreate(
        username=reg_in.username,
        email=reg_in.email,
        password=reg_in.password,
        role_id=role.id,
    )
    # attach the new company
    user = await create_user(db, user_in, comp.id)
    return user
