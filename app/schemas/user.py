from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role_id: Optional[int] = None  # default to None if not supplied

class UserRead(UserBase):
    id: int
    role_id: int

    class Config:
        orm_mode = True
