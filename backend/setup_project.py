"""
Backend Project Setup Script
一键生成后端项目所有必要文件
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 需要创建的空__init__.py文件列表
INIT_FILES = [
    "app/__init__.py",
    "app/api/__init__.py",
    "app/core/__init__.py",
    "app/models/__init__.py",
    "app/schemas/__init__.py",
    "app/services/__init__.py",
    "app/utils/__init__.py",
    "tests/__init__.py",
]

# API路由模块模板
API_ROUTER_TEMPLATE = """\"\"\"
API v1 Router
\"\"\"
from fastapi import APIRouter
from app.api.v1 import auth, accounts, holdings, trades, stocks, events, reviews

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
api_router.include_router(holdings.router, prefix="/holdings", tags=["Holdings"])
api_router.include_router(trades.router, prefix="/trades", tags=["Trades"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews (v3.2)"])
"""

# Auth API模板 (P0核心)
AUTH_API_TEMPLATE = """\"\"\"
Authentication API
\"\"\"
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import Token, UserResponse
# from app.services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    \"\"\"用户登录 (P0核心接口)\"\"\"
    # TODO: 实现认证逻辑
    # auth_service = AuthService(db)
    # return await auth_service.authenticate(form_data.username, form_data.password)

    # Mock response
    return {
        "access_token": "mock_token",
        "token_type": "bearer",
        "user": {
            "user_id": 1,
            "username": form_data.username,
            "nickname": "测试用户"
        }
    }


@router.post("/register", response_model=UserResponse)
async def register(db: AsyncSession = Depends(get_db)):
    \"\"\"用户注册 (P1功能)\"\"\"
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/logout")
async def logout():
    \"\"\"退出登录 (P1功能)\"\"\"
    return {"message": "Logged out successfully"}
"""

# Accounts API模板 (P0核心)
ACCOUNTS_API_TEMPLATE = """\"\"\"
Accounts API
\"\"\"
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.account import AccountResponse, AccountListResponse

router = APIRouter()


@router.get("", response_model=AccountListResponse)
async def get_accounts(
    user_id: int = Query(..., description="用户ID"),
    market: str = Query(None, description="市场类型"),
    db: AsyncSession = Depends(get_db)
):
    \"\"\"获取账户列表 (P0核心接口)\"\"\"
    # TODO: 实现业务逻辑
    # account_service = AccountService(db)
    # return await account_service.get_accounts(user_id, market)

    # Mock response
    return {
        "total": 3,
        "accounts": [
            {
                "account_id": 1,
                "account_name": "华泰证券-A股",
                "account_number": "12345678",
                "market": "A股",
                "broker": "华泰证券",
                "total_value": 350000,
                "available_cash": 120000,
                "invested_value": 230000,
                "today_profit": 1200,
                "today_profit_rate": 0.34,
                "total_profit": 15000,
                "total_profit_rate": 4.28,
                "status": "active"
            }
        ]
    }
"""

# Holdings API模板
HOLDINGS_API_TEMPLATE = """\"\"\"
Holdings API
\"\"\"
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.holding import HoldingListResponse

router = APIRouter()


@router.get("", response_model=HoldingListResponse)
async def get_holdings(
    user_id: int = Query(...),
    account_id: int = Query(None),
    db: AsyncSession = Depends(get_db)
):
    \"\"\"获取持仓列表 (P0核心接口)\"\"\"
    # Mock response
    return {
        "total": 0,
        "total_market_value": 0,
        "total_profit": 0,
        "total_profit_rate": 0,
        "holdings": []
    }
"""

# Trades API模板
TRADES_API_TEMPLATE = """\"\"\"
Trades API
\"\"\"
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.trade import TradeListResponse, TradeCreate, TradeResponse

router = APIRouter()


@router.get("", response_model=TradeListResponse)
async def get_trades(
    user_id: int = Query(...),
    account_id: int = Query(None),
    db: AsyncSession = Depends(get_db)
):
    \"\"\"获取交易记录列表 (P0核心接口)\"\"\"
    return {"total": 0, "trades": []}


@router.post("", response_model=TradeResponse, status_code=201)
async def create_trade(
    trade: TradeCreate,
    db: AsyncSession = Depends(get_db)
):
    \"\"\"记录交易 (P0核心接口)\"\"\"
    return {
        "code": 201,
        "message": "交易记录已创建",
        "data": {"trade_id": 1}
    }
"""

# Stocks API模板
STOCKS_API_TEMPLATE = """\"\"\"
Stocks API
\"\"\"
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.stock import StockQuote

router = APIRouter()


@router.get("/{symbol}/quote", response_model=StockQuote)
async def get_stock_quote(
    symbol: str = Path(...),
    db: AsyncSession = Depends(get_db)
):
    \"\"\"获取股票实时行情 (P0核心接口)\"\"\"
    # Mock response
    return {
        "symbol": symbol,
        "name": "测试股票",
        "market": "A股",
        "current_price": 100.00,
        "change_amount": 2.50,
        "change_rate": 2.56
    }
"""

# Events API模板
EVENTS_API_TEMPLATE = """\"\"\"
Events API
\"\"\"
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.event import EventListResponse

router = APIRouter()


@router.get("", response_model=EventListResponse)
async def get_events(
    user_id: int = Query(...),
    category: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    \"\"\"获取事件列表 (P0核心接口)\"\"\"
    return {"total": 0, "unread_count": 0, "events": []}
"""

# Reviews API模板 (v3.2)
REVIEWS_API_TEMPLATE = """\"\"\"
Stock Reviews API (v3.2)
\"\"\"
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.review import ReviewResponse, ReviewCreate

router = APIRouter()


@router.get("/{symbol}", response_model=ReviewResponse)
async def get_review(
    symbol: str = Path(...),
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    \"\"\"获取股票评价 (P0核心接口)\"\"\"
    return {
        "review_id": 1,
        "user_id": user_id,
        "symbol": symbol,
        "rating": 0,
        "bullish_reasons": [],
        "bearish_reasons": [],
        "holding_logic": "",
        "target_price": None,
        "stop_loss_price": None
    }


@router.post("/{symbol}", response_model=ReviewResponse, status_code=201)
async def create_or_update_review(
    symbol: str = Path(...),
    review: ReviewCreate = Body(...),
    db: AsyncSession = Depends(get_db)
):
    \"\"\"创建/更新股票评价 (P0核心接口)\"\"\"
    return {"code": 200, "message": "评价已保存"}
"""


def create_file(filepath: str, content: str):
    """创建文件"""
    file_path = BASE_DIR / filepath
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Created: {filepath}")


def main():
    """主函数"""
    print("🚀 Setting up backend project...")
    print()

    # 创建__init__.py文件
    print("📝 Creating __init__.py files...")
    for init_file in INIT_FILES:
        create_file(init_file, '"""Init module"""\\n')
    print()

    # 创建API路由
    print("📡 Creating API routers...")
    create_file("app/api/v1/__init__.py", API_ROUTER_TEMPLATE)
    create_file("app/api/v1/auth.py", AUTH_API_TEMPLATE)
    create_file("app/api/v1/accounts.py", ACCOUNTS_API_TEMPLATE)
    create_file("app/api/v1/holdings.py", HOLDINGS_API_TEMPLATE)
    create_file("app/api/v1/trades.py", TRADES_API_TEMPLATE)
    create_file("app/api/v1/stocks.py", STOCKS_API_TEMPLATE)
    create_file("app/api/v1/events.py", EVENTS_API_TEMPLATE)
    create_file("app/api/v1/reviews.py", REVIEWS_API_TEMPLATE)
    print()

    # 创建.gitignore
    print("📦 Creating .gitignore...")
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/
*.log

# Database
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db
"""
    create_file(".gitignore", gitignore_content)
    print()

    print("✨ Project setup completed!")
    print()
    print("📋 Next steps:")
    print("1. cp .env.example .env")
    print("2. Edit .env with your actual configuration")
    print("3. pip install -r requirements.txt")
    print("4. alembic upgrade head")
    print("5. python -m app.main")


if __name__ == "__main__":
    main()
