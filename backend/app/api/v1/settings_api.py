"""
Settings API - POST-only架构

用户设置API - 使用POST-only + Service + Converter + Builder模式
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import Response
from app.services.settings import SettingsService


router = APIRouter(prefix="/settings", tags=["用户设置"])


# ========================================
# Request Schemas
# ========================================


class SettingsUpdateRequest(BaseModel):
    """设置更新请求"""

    preferences: Optional[Dict[str, Any]] = Field(None, description="偏好设置")
    notifications: Optional[Dict[str, Any]] = Field(None, description="通知设置")
    risk_settings: Optional[Dict[str, Any]] = Field(None, description="风险设置")
    ai_settings: Optional[Dict[str, Any]] = Field(None, description="AI设置")


class AIKeyConfigRequest(BaseModel):
    """AI密钥配置请求"""

    provider: str = Field(..., description="AI提供商：deepseek/openai")
    api_key: str = Field(..., description="API密钥")
    model: str = Field(..., description="模型名称")


class AIKeyTestRequest(BaseModel):
    """AI密钥测试请求"""

    provider: str = Field(..., description="AI提供商")
    api_key: str = Field(..., description="API密钥")


# ========================================
# API Endpoints
# ========================================


@router.post("/get")
async def get_settings(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    获取用户设置

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/settings/get
    对应页面: pages/settings/index.vue - 设置页
    接口功能: 获取用户的所有配置项

    ========================================
    请求参数
    ========================================
    无

    ========================================
    响应数据
    ========================================
    {
        "user_id": 1001,
        "preferences": {
            "theme": "light",
            "language": "zh-CN",
            "timezone": "Asia/Shanghai",
            "currency": "CNY"
        },
        "notifications": {
            "email_enabled": true,
            "push_enabled": false,
            "event_alerts": true,
            "ai_suggestions": true,
            "price_alerts": true
        },
        "risk_settings": {
            "risk_level": "moderate",
            "max_position_ratio": 20,
            "min_cash_ratio": 20,
            "stop_loss_ratio": -15
        },
        "ai_settings": {
            "api_provider": "deepseek",
            "api_key": "sk-***",
            "model": "deepseek-chat",
            "auto_analysis": true,
            "analysis_frequency": "daily"
        }
    }

    ========================================
    前端调用示例
    ========================================
    const settings = await post('/settings/get', {})
    """
    service = SettingsService()
    result = await service.get_settings(db, current_user.user_id)
    return Response.success(data=result)


@router.post("/update")
async def update_settings(
    request: SettingsUpdateRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    更新用户设置

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/settings/update
    对应页面: pages/settings/index.vue - 设置表单
    接口功能: 更新用户配置项（支持部分更新）

    ========================================
    请求参数
    ========================================
    {
        "preferences": {
            "theme": "dark"
        },
        "notifications": {
            "email_enabled": false
        }
    }

    ========================================
    响应数据
    ========================================
    {
        "message": "设置已更新",
        "updated_fields": ["preferences", "notifications"]
    }

    ========================================
    业务规则
    ========================================
    1. 支持部分更新，只更新提供的字段
    2. 未提供的字段保持原值不变

    ========================================
    前端调用示例
    ========================================
    await post('/settings/update', {
        preferences: { theme: 'dark' }
    })
    """
    service = SettingsService()

    # 过滤掉None值的字段
    settings_data = {k: v for k, v in request.dict().items() if v is not None}

    result = await service.update_settings(db, current_user.user_id, settings_data)
    return Response.success(data=result)


@router.post("/ai-key/config")
async def config_ai_key(
    request: AIKeyConfigRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    配置AI API密钥

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/settings/ai-key/config
    对应页面: pages/settings/ai.vue - AI配置页
    接口功能: 保存用户的AI API配置（需要加密存储）

    ========================================
    请求参数
    ========================================
    {
        "provider": "deepseek",
        "api_key": "sk-xxxxxxxxxxxxx",
        "model": "deepseek-chat"
    }

    ========================================
    响应数据
    ========================================
    {
        "provider": "deepseek",
        "model": "deepseek-chat",
        "masked_key": "sk-xxxxx***"
    }

    ========================================
    业务规则
    ========================================
    1. API密钥需要加密存储
    2. 返回时只显示前几位和掩码

    ========================================
    前端调用示例
    ========================================
    await post('/settings/ai-key/config', {
        provider: 'deepseek',
        api_key: 'sk-xxx',
        model: 'deepseek-chat'
    })
    """
    # TODO: 加密存储API密钥
    masked_key = f"{request.api_key[:8]}***" if len(request.api_key) > 8 else "***"

    return Response.success(
        data={"provider": request.provider, "model": request.model, "masked_key": masked_key}, message="API密钥已配置"
    )


@router.post("/ai-key/test")
async def test_ai_key(
    request: AIKeyTestRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    测试AI API密钥

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/settings/ai-key/test
    对应页面: pages/settings/ai.vue - 密钥测试按钮
    接口功能: 验证API密钥是否有效

    ========================================
    请求参数
    ========================================
    {
        "provider": "deepseek",
        "api_key": "sk-xxxxxxxxxxxxx"
    }

    ========================================
    响应数据
    ========================================
    {
        "valid": true,
        "model": "deepseek-chat",
        "remaining_quota": 1000000
    }

    ========================================
    业务规则
    ========================================
    1. 调用对应AI服务的验证接口
    2. 返回密钥有效性和剩余配额

    ========================================
    前端调用示例
    ========================================
    const result = await post('/settings/ai-key/test', {
        provider: 'deepseek',
        api_key: 'sk-xxx'
    })
    """
    # TODO: 实际调用AI API测试
    return Response.success(data={"valid": True, "model": "deepseek-chat", "remaining_quota": 1000000})
