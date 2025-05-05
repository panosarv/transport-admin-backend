from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user import (
    get_user_by_id,
    get_all_users,
    create_user,
    update_user,
    delete_user
)
from app.dependencies import get_db, get_current_user
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserRead])
async def read_users(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all users in the current user's company."""
    users = await get_all_users(db, current_user.company_id)
    return users

@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a single user by ID, scoped to the company."""
    user = await get_user_by_id(db, user_id)
    if not user or user.company_id != current_user.company_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Admin-only: Create a new user in the same company."""
    if current_user.role_id != 1:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
    new_user = await create_user(db, user_in, current_user.company_id)
    return new_user

@router.patch("/{user_id}", response_model=UserRead)
async def update_existing_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Admin-only: Update username, email, password, or role for a user."""
    if current_user.role_id != 1:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
    user = await get_user_by_id(db, user_id)
    if not user or user.company_id != current_user.company_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    # Update fields
    if user_in.username is not None:
        user.username = user_in.username
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.password is not None:
        user.hashed_password = get_password_hash(user_in.password)
    if user_in.role_id is not None:
        user.role_id = user_in.role_id
    updated = await update_user(db, user)
    return updated

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Admin-only: Delete a user by ID."""
    if current_user.role_id != 1:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
    user = await get_user_by_id(db, user_id)
    if not user or user.company_id != current_user.company_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    await delete_user(db, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


