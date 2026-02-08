from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr

# Base schema with common fields
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr = Field(max_length=100)
    first_name: str | None = Field(default=None, max_length=70)
    last_name: str | None = Field(default=None, max_length=100)


class UserCreate(UserBase):
    """For user registration"""
    password: str = Field(min_length=8)


class UserPublic(BaseModel):
    """Public profile - what OTHER users see"""
    model_config = ConfigDict(from_attributes=True)

    username: str
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime


class UserUpdate(UserBase):
    """Fields allowed to be updated by the user"""
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, min_length=1, max_length=120)
    first_name: str | None = Field(default=None, min_length=1, max_length=120)
    last_name: str | None = Field(default=None, min_length=1, max_length=120)


class UserProfile(BaseModel):
    """User's OWN profile - what the user sees about themselves"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime
    updated_at: datetime


class UserAdmin(BaseModel):
    """Admin view - full access to all fields"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime
    updated_at: datetime
    # Admin-specific fields you might add later:
    # is_active: bool
    # is_admin: bool
    # last_login: datetime | None