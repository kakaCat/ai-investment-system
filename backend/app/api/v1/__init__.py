"""
API v1 Router - 重构后（POST-only架构）

所有API使用POST-only + Service + Converter + Builder模式
"""

from fastapi import APIRouter
from app.api.v1 import (
    auth,
    account_api,
    trade_api,
    stock_api,
    holding_api,
    event_api,
    ai_api,
    review_api,
    settings_api,
    export_api,
    strategy_api,
)

api_router = APIRouter()

# ========================================
# 路由注册（POST-only架构）
# ========================================

# 认证
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 账户管理
api_router.include_router(account_api.router, tags=["账户管理"])

# 交易管理
api_router.include_router(trade_api.router, tags=["交易管理"])

# 股票管理
api_router.include_router(stock_api.router, tags=["股票管理"])

# 持仓管理
api_router.include_router(holding_api.router, tags=["持仓管理"])

# 事件管理
api_router.include_router(event_api.router, tags=["事件管理"])

# AI分析
api_router.include_router(ai_api.router, tags=["AI分析"])

# 股票评价
api_router.include_router(review_api.router, tags=["股票评价"])

# 用户设置
api_router.include_router(settings_api.router, tags=["用户设置"])

# 数据导出
api_router.include_router(export_api.router, tags=["数据导出"])

# 操作策略管理
api_router.include_router(strategy_api.router, tags=["操作策略管理"])
