# File: app/services/user.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate,UserUpdate
from app.core.security import get_password_hash

async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_in: UserCreate, company_id: int) -> User:
    hashed_pw = get_password_hash(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pw,
        role_id=user_in.role_id,
        company_id=company_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
async def update_user(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()
    return None

async def get_all_users(db: AsyncSession, company_id: int) -> list[User]:
    result = await db.execute(select(User).where(User.company_id == int(company_id)))
    return result.scalars().all()

async def update_user_admin(
    db: AsyncSession,
    user_id: int,
    user_in: UserUpdate,
    current_user
) -> User:
    if current_user.role_id != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    user = await get_user(db, user_id, current_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user_in.username:
        user.username = user_in.username
    if user_in.email:
        user.email = user_in.email
    if user_in.password:
        user.hashed_password = pwd_context.hash(user_in.password)
    if user_in.role_id is not None:
        user.role_id = user_in.role_id
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user_admin(
    db: AsyncSession,
    user_id: int,
    current_user
) -> None:
    if current_user.role_id != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    user = await get_user(db, user_id, current_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()

