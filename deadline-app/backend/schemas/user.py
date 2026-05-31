from pydantic import BaseModel, ConfigDict
from typing import Optional


class TokenData(BaseModel):
    email: Optional[str] = None


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str
