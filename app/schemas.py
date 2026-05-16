from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class WaitlistCreate(BaseModel):
    email: EmailStr

class WaitlistResponse(BaseModel):
    id: int
    email: str
    signed_up_at: datetime
    is_confirmed: bool

    model_config = ConfigDict(from_attributes=True)