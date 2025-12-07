"""
Authentication API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import Token, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录 (P0核心接口)

    使用用户名和密码进行认证，返回JWT访问令牌
    """
    auth_service = AuthService(db)
    return await auth_service.authenticate(form_data.username, form_data.password)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    username: str = Body(..., min_length=3, max_length=50),
    password: str = Body(..., min_length=6),
    nickname: str = Body(None, max_length=100),
    email: str = Body(None),
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册 (P1功能)

    创建新用户账号
    """
    from sqlalchemy import select
    from app.models.user import User
    from app.core.security import get_password_hash

    # Check if username already exists
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # Create new user
    new_user = User(
        username=username,
        password_hash=get_password_hash(password),
        nickname=nickname or username,
        email=email
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse(
        user_id=new_user.user_id,
        username=new_user.username,
        nickname=new_user.nickname
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """
    刷新Token (P1功能)

    使用refresh token获取新的access token
    """
    # TODO: 实现refresh token验证逻辑
    # 当前简化实现，直接返回新token
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/logout")
async def logout():
    """
    退出登录 (P1功能)

    客户端应删除本地token
    """
    return {"message": "Logged out successfully"}
