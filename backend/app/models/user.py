"""
User Model
"""

from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """User table"""

    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(100), comment="昵称")
    email = Column(String(100), unique=True, index=True, comment="邮箱")
    phone = Column(String(20), comment="手机号")
    avatar_url = Column(String(500), comment="头像URL")

    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否删除")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )
    deleted_at = Column(TIMESTAMP(timezone=True), comment="删除时间")
    last_login_at = Column(TIMESTAMP(timezone=True), comment="最后登录时间")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"
