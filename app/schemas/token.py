from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str             # <— string, not int
    role_id: Optional[int]
    company_id: int
    exp: int

