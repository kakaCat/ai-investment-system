"""
Dependency Injection Functions
"""

import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    Get current authenticated user from JWT token

    In development mode (ENVIRONMENT=development), accepts 'dev-token'
    and automatically creates/returns a test user.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Check if token is provided
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Development mode: accept dev-token
    environment = os.getenv("ENVIRONMENT", "production")
    if environment == "development" and token == "dev-token":
        # Get or create dev user
        stmt = select(User).where(User.email == "dev@example.com")
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            # Create dev user
            user = User(
                email="dev@example.com",
                username="dev_user",
                password_hash="dev_password",  # Not used in dev mode
                is_active=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        return user

    # Production mode: validate JWT token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Get user from database
    try:
        stmt = select(User).where(User.user_id == int(user_id))
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise credentials_exception

        return user
    except Exception:
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (additional check for is_active)

    Args:
        current_user: Current user from get_current_user

    Returns:
        User: Active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="用户已被禁用")
    return current_user
