"""
User Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=6, description="密码")


class UserResponse(UserBase):
    """User response schema"""
    user_id: int = Field(..., description="用户ID")

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Token response"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[int] = None
    username: Optional[str] = None
