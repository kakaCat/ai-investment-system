"""
Authentication Service
"""
from typing import Optional
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import Token, UserResponse
from app.core.security import verify_password, create_access_token
from app.core.config import settings


class AuthService:
    """Authentication service"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, username: str, password: str) -> Token:
        """
        Authenticate user with username and password

        Args:
            username: Username
            password: Plain text password

        Returns:
            Token: JWT token with user info

        Raises:
            HTTPException: If authentication fails
        """
        # Get user from database
        stmt = select(User).where(
            User.username == username,
            User.is_active == True,
            User.is_deleted == False
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.user_id), "username": user.username},
            expires_delta=access_token_expires
        )

        # Prepare user response
        user_response = UserResponse(
            user_id=user.user_id,
            username=user.username,
            nickname=user.nickname
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )

    async def get_current_user(self, user_id: int) -> Optional[User]:
        """
        Get current user by user_id

        Args:
            user_id: User ID from JWT token

        Returns:
            Optional[User]: User object if found

        Raises:
            HTTPException: If user not found or inactive
        """
        stmt = select(User).where(
            User.user_id == user_id,
            User.is_active == True,
            User.is_deleted == False
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user
