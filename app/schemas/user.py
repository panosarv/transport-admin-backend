from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class RegisterCompanyUser(UserBase):
    """
    Payload for the very first signup:
    creates a new Company and an Admin user.
    """
    password: str
    company_name: str

class UserCreate(UserBase):
    """
    Payload for subsequent user creation by an Admin.
    The company_id is taken from the current_user.
    """
    password: str
    role_id: int

class UserRead(UserBase):
    id: int
    role_id: int
    company_id: int

    class Config:
        from_attributes = True
        orm_mode = True
