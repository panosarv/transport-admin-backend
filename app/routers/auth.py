# File: app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.user import RegisterCompanyUser, UserCreate, UserRead
from app.schemas.token import Token
from app.schemas.company import CompanyCreate
from app.services.user import get_user_by_username, get_user_by_email, create_user
from app.services.auth import login
from app.services.company import create_company
from app.models.role import Role
from app.models.company import Company
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Company and Admin user",
)
async def register_company(
    reg_in: RegisterCompanyUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Allow anyone to register a new company by creating its first Admin user,
    provided the username, email, and company name are all unique.
    """
    # Check uniqueness of company name
    existing_company = await db.scalar(
        select(Company).where(Company.name == reg_in.company_name)
    )
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company '{reg_in.company_name}' already registered."
        )
    # Check uniqueness of username and email
    if await get_user_by_username(db, reg_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered."
        )
    if await get_user_by_email(db, reg_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    # Create the company
    company = await create_company(db, CompanyCreate(
        name=reg_in.company_name,
        address=None,
    ))

    # Resolve Admin role
    result = await db.execute(
        select(Role).where(Role.name == "Admin")
    )
    admin_role = result.scalars().first()
    if not admin_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin role missing in database."
        )

    # Create the admin user for this company
    user_in = UserCreate(
        username=reg_in.username,
        email=reg_in.email,
        password=reg_in.password,
        role_id=admin_role.id,
    )
    user = await create_user(db, user_in, company.id)
    return user


@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Admin adds a new user to their company",
)
async def signup(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Add a new user under the same company as the current Admin.
    """
    # Only Admins can add users
    if current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    # Check uniqueness
    if await get_user_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered."
        )
    from app.services.user import get_user_by_email
    if await get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    # Create user under current company
    user = await create_user(db, user_in, current_user.company_id)
    return user


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
    """
    access_token = await login(db, form_data.username, form_data.password)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the current authenticated user"
)
async def read_users_me(
    current_user = Depends(get_current_user)
):
    """
    Returns the User record for the JWT you provided.
    """
    return current_user
