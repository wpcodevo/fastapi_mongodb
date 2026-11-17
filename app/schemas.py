from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class CreateUserSchema(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str


class UserResponseSchema(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)