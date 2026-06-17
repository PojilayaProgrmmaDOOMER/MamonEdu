from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True
        
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    avatar_url: str | None = None
    bio: str | None = None

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    username: str | None = None
    avatar_url: str | None = None
    bio: str | None = None