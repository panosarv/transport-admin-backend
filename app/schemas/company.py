from pydantic import BaseModel
from typing import Optional

class CompanyBase(BaseModel):
    name: str
    address: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyRead(CompanyBase):
    id: int

    class Config:
        from_attributes = True
        orm_mode = True
