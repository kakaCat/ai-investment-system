"""
Holding API - POST-only架构

持仓管理API - 使用POST-only + Service + Converter + Builder模式
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import Response
from app.services.holding import (
    HoldingQueryService,
    HoldingSyncService,
)


router = APIRouter(prefix="/holding", tags=["持仓管理"])


# ========================================
# Request Schemas
# ========================================


class HoldingQueryRequest(BaseModel):
    """持仓查询请求"""

    account_id: int | None = Field(None, description="账户ID（为空则查询所有账户持仓）")


class HoldingSyncRequest(BaseModel):
    """持仓同步请求"""

    account_id: int = Field(..., description="账户ID")


# ========================================
# API Endpoints
# ========================================


@router.post("/query")
async def query_holdings(
    request: HoldingQueryRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    查询账户持仓

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/holding/query
    对应页面: pages/account/detail.vue - 账户详情页（持仓列表）
    接口功能: 查询指定账户的所有持仓，包含成本、市值、盈亏等完整信息

    ========================================
    请求参数
    ========================================
    {
        "account_id": 1                     // 账户ID（必需）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "holdings": [
                {
                    "holding_id": 1,
                    "account_id": 1,
                    "symbol": "600519",
                    "stock_name": "贵州茅台",
                    "quantity": 100.0,
                    "average_cost": 1800.50,
                    "current_price": 1850.00,
                    "cost_basis": 180050.0,          // 成本总额
                    "market_value": 185000.0,        // 市值
                    "profit_loss": 4950.0,           // 盈亏
                    "profit_loss_percent": 2.75,     // 盈亏百分比
                    "updated_at": "2025-01-17T15:00:00"
                }
            ],
            "summary": {
                "total_holdings": 5,                 // 持仓数量
                "total_cost": 500000.0,              // 总成本
                "total_value": 520000.0,             // 总市值
                "total_profit_loss": 20000.0,        // 总盈亏
                "total_profit_loss_percent": 4.0     // 总盈亏百分比
            }
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求 → 验证JWT Token → 获取user_id
    2. 调用 HoldingQueryService.execute()
       2.1 调用 AccountRepository.get_by_id() 查询账户
       2.2 权限校验：检查account.user_id == user_id
       2.3 调用 HoldingRepository.query_by_account() 查询持仓列表
       2.4 调用 HoldingQueryConverter.convert() 转换数据并计算统计
           - 计算每个持仓的成本、市值、盈亏
           - 计算汇总统计（总成本、总市值、总盈亏）
       2.5 调用 HoldingQueryBuilder.build_response() 构建响应
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 只能查询当前登录用户的账户持仓
       - 如果账户不属于当前用户，返回1001错误

    2. 数据计算：
       - cost_basis = quantity × average_cost
       - market_value = quantity × current_price
       - profit_loss = market_value - cost_basis
       - profit_loss_percent = (profit_loss / cost_basis) × 100

    3. 价格来源：
       - current_price 来自持仓表（定期更新）
       - 如需实时价格，前端可调用股票详情API补充

    4. 汇总统计：
       - 计算所有持仓的总成本、总市值、总盈亏
       - total_profit_loss_percent = (total_profit_loss / total_cost) × 100

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1001: 无权访问（PermissionDenied）
    - 1002: 账户不存在（ResourceNotFound）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/account/detail.vue
    const queryHoldings = async (accountId) => {
      const response = await api.post('/api/v1/holding/query', {
        account_id: accountId
      });

      if (response.data.code === 0) {
        holdings.value = response.data.data.holdings;
        summary.value = response.data.data.summary;

        // 计算持仓占比
        holdings.value.forEach(h => {
          h.weight = (h.market_value / summary.value.total_value * 100).toFixed(2);
        });
      } else if (response.data.code === 1002) {
        showError('账户不存在');
      } else if (response.data.code === 1001) {
        showError('无权访问该账户');
      }
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = HoldingQueryService()
    data = await service.execute(db=db, user_id=current_user.user_id, account_id=request.account_id)
    return Response.success(data)


@router.post("/sync")
async def sync_holdings(
    request: HoldingSyncRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    同步账户持仓

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/holding/sync
    对应页面: pages/account/detail.vue - 账户详情页（同步按钮）
    接口功能: 根据账户的所有交易记录重新计算并更新持仓数据

    ========================================
    请求参数
    ========================================
    {
        "account_id": 1                     // 账户ID（必需）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "success": true,
            "updated_count": 5,              // 更新的持仓数量
            "total_holdings": 5,             // 总持仓数量
            "message": "成功同步 5 个持仓"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求 → 验证JWT Token → 获取user_id
    2. 调用 HoldingSyncService.execute()
       2.1 调用 AccountRepository.get_by_id() 查询账户
       2.2 权限校验：检查account.user_id == user_id
       2.3 调用 TradeRepository.query_by_account() 查询所有交易
       2.4 调用 HoldingSyncConverter.calculate_holdings() 计算持仓
           - 按股票代码分组
           - 遍历交易记录：
             买入：增加数量，更新平均成本
             卖出：减少数量，平均成本不变
           - 过滤掉数量为0的持仓
       2.5 调用 HoldingRepository.upsert() 更新每个持仓
       2.6 调用 HoldingSyncBuilder.build_response() 构建响应
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 只能同步当前登录用户的账户持仓
       - 如果账户不属于当前用户，返回1001错误

    2. 同步逻辑：
       - 从数据库读取该账户所有交易记录
       - 按时间顺序处理交易：
         买入：quantity += buy_quantity, avg_cost = (old_cost × old_qty + buy_cost × buy_qty) / new_qty
         卖出：quantity -= sell_quantity, avg_cost 保持不变
       - 数量为0的持仓不保存

    3. 触发时机：
       - 用户手动点击"同步持仓"按钮
       - 创建/修改/删除交易后自动触发
       - 定时任务定期同步

    4. 性能考虑：
       - 单次查询获取所有交易（限制10000条）
       - 内存中计算持仓
       - 批量更新数据库

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1001: 无权访问（PermissionDenied）
    - 1002: 账户不存在（ResourceNotFound）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/account/detail.vue
    const syncHoldings = async (accountId) => {
      loading.value = true;

      const response = await api.post('/api/v1/holding/sync', {
        account_id: accountId
      });

      loading.value = false;

      if (response.data.code === 0) {
        showSuccess(response.data.data.message);
        // 同步成功后刷新持仓列表
        await queryHoldings(accountId);
      } else if (response.data.code === 1002) {
        showError('账户不存在');
      } else if (response.data.code === 1001) {
        showError('无权访问该账户');
      }
    };

    // 创建交易后自动同步
    const afterTradeCreated = async (accountId) => {
      await syncHoldings(accountId);
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = HoldingSyncService()
    data = await service.execute(db=db, user_id=current_user.user_id, account_id=request.account_id)
    return Response.success(data)
