from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: int                
    role_id: Optional[int]
    company_id: int          # NEW: the user’s company
    exp: int
