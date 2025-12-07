"""
Stock API - POST-only架构

股票管理API - 使用POST-only + Service + Converter + Builder模式
"""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.schemas.common import Response
from app.services.stock import (
    StockQueryService,
    StockDetailService,
    StockSearchService,
)


router = APIRouter(prefix="/stock", tags=["股票管理"])


# ========================================
# Request Schemas
# ========================================

class StockQueryRequest(BaseModel):
    """股票查询请求"""
    market: Optional[str] = Field(None, description="市场类型筛选（A-share/HK/US）")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class StockDetailRequest(BaseModel):
    """股票详情请求"""
    symbol: str = Field(..., description="股票代码")


class StockSearchRequest(BaseModel):
    """股票搜索请求"""
    keyword: str = Field(..., description="搜索关键词（股票代码或名称）")
    market: Optional[str] = Field(None, description="市场类型筛选（A-share/HK/US）")
    limit: int = Field(20, ge=1, le=100, description="最大返回数量")


# ========================================
# API Endpoints
# ========================================

@router.post("/query")
async def query_stocks(
    request: StockQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    查询股票列表

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/stock/query
    对应页面: pages/stock/list.vue - 股票列表页
    接口功能: 查询股票列表，支持市场类型筛选，支持分页

    注意：此接口为公开接口，不需要身份验证

    ========================================
    请求参数
    ========================================
    {
        "market": "A-share",                // 市场类型筛选（可选）A-share/HK/US
        "page": 1,                          // 页码（默认1）
        "page_size": 20                     // 每页数量（默认20）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "items": [
                {
                    "stock_id": 1,
                    "symbol": "600519",
                    "name": "贵州茅台",
                    "market": "A-share",
                    "industry": "白酒",
                    "current_price": 1800.50,
                    "change_percent": 2.5,
                    "volume": 12345678.0,
                    "market_cap": 2260000000000.0,
                    "pe_ratio": 35.6,
                    "updated_at": "2025-01-17T15:00:00"
                }
            ],
            "total": 5000,
            "page": 1,
            "page_size": 20,
            "total_pages": 250
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求（无需身份验证）
    2. 调用 StockQueryService.execute()
       2.1 调用 StockRepository.query_all() 查询股票列表
       2.2 调用 StockQueryConverter.convert() 转换为业务数据
       2.3 调用 StockQueryBuilder.build_response() 构建分页响应
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 此接口为公开接口，无需登录

    2. 筛选规则：
       - market: 筛选指定市场的股票（A-share/HK/US）
       - 如不提供market，返回所有市场股票

    3. 数据来源：
       - 股票数据由系统定期从第三方API更新
       - 价格数据实时性取决于更新频率

    4. 分页规则：
       - 默认页码1，每页20条
       - 最大每页100条
       - 按更新时间倒序

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1003: 数据验证失败（ValidationError）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/stock/list.vue
    const queryStocks = async (filters) => {
      const response = await api.post('/api/v1/stock/query', {
        market: filters.market,
        page: filters.page,
        page_size: 20
      });

      if (response.data.code === 0) {
        stocks.value = response.data.data.items;
        pagination.value = {
          total: response.data.data.total,
          page: response.data.data.page,
          pageSize: response.data.data.page_size,
          totalPages: response.data.data.total_pages
        };
      }
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = StockQueryService()
    data = await service.execute(
        db=db,
        market=request.market,
        page=request.page,
        page_size=request.page_size
    )
    return Response.success(data)


@router.post("/detail")
async def get_stock_detail(
    request: StockDetailRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    查询股票详情

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/stock/detail
    对应页面: pages/stock/detail.vue - 股票详情页
    接口功能: 查询单个股票的详细信息，包含价格、交易量、基本面等完整数据

    注意：此接口为公开接口，不需要身份验证

    ========================================
    请求参数
    ========================================
    {
        "symbol": "600519"                  // 股票代码（必需）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "stock_id": 1,
            "symbol": "600519",
            "name": "贵州茅台",
            "market": "A-share",
            "industry": "白酒",
            "sector": "食品饮料",
            "company_name": "贵州茅台酒股份有限公司",
            "description": "主营业务为茅台酒及系列酒的生产与销售...",
            // 价格信息
            "current_price": 1800.50,
            "change_percent": 2.5,
            "day_high": 1820.00,
            "day_low": 1780.00,
            "open_price": 1785.00,
            "close_price": 1756.40,
            // 交易量信息
            "volume": 12345678.0,
            "turnover": 22000000000.0,
            // 基本面信息
            "market_cap": 2260000000000.0,
            "pe_ratio": 35.6,
            "pb_ratio": 12.8,
            "dividend_yield": 1.2,
            // 时间戳
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2025-01-17T15:00:00"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求（无需身份验证）
    2. 调用 StockDetailService.execute()
       2.1 调用 StockRepository.get_by_symbol() 查询股票
       2.2 如股票不存在，抛出ResourceNotFound异常
       2.3 调用 StockDetailConverter.convert() 转换为详情数据
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 此接口为公开接口，无需登录

    2. 数据完整性：
       - 返回股票所有可用信息
       - 价格数据可能为空（停牌、未开盘等）
       - 基本面数据定期更新

    3. 数据来源：
       - 实时价格来自第三方行情API
       - 基本面数据来自定期同步

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1002: 股票不存在（ResourceNotFound）
    - 1003: 数据验证失败（ValidationError）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/stock/detail.vue
    const getStockDetail = async (symbol) => {
      const response = await api.post('/api/v1/stock/detail', {
        symbol: symbol
      });

      if (response.data.code === 0) {
        stock.value = response.data.data;
      } else if (response.data.code === 1002) {
        showError('股票不存在');
      }
    };
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = StockDetailService()
    data = await service.execute(
        db=db,
        symbol=request.symbol
    )
    return Response.success(data)


@router.post("/search")
async def search_stocks(
    request: StockSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    搜索股票

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/stock/search
    对应页面:
    - pages/trade/create.vue - 创建交易时搜索股票
    - pages/stock/search.vue - 股票搜索页
    接口功能: 根据关键词搜索股票（支持股票代码或名称模糊匹配）

    注意：此接口为公开接口，不需要身份验证

    ========================================
    请求参数
    ========================================
    {
        "keyword": "茅台",                  // 搜索关键词（必需）代码或名称
        "market": "A-share",                // 市场类型筛选（可选）
        "limit": 20                         // 最大返回数量（默认20）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "items": [
                {
                    "stock_id": 1,
                    "symbol": "600519",
                    "name": "贵州茅台",
                    "market": "A-share",
                    "industry": "白酒",
                    "current_price": 1800.50,
                    "change_percent": 2.5
                },
                {
                    "stock_id": 25,
                    "symbol": "000858",
                    "name": "五粮液",
                    "market": "A-share",
                    "industry": "白酒",
                    "current_price": 185.20,
                    "change_percent": 1.8
                }
            ],
            "total": 2,
            "keyword": "茅台"
        }
    }

    ========================================
    执行流程（时序）
    ========================================
    1. API接收请求（无需身份验证）
    2. 调用 StockSearchService.execute()
       2.1 调用 StockSearchConverter.validate() 验证参数
           - 关键词不能为空
           - 关键词长度不超过100
           - 返回数量在1-100之间
       2.2 调用 StockRepository.search() 搜索股票
           - 匹配股票代码（前缀匹配）
           - 匹配股票名称（模糊匹配）
       2.3 调用 StockSearchConverter.convert() 转换为搜索结果
       2.4 调用 StockSearchBuilder.build_response() 构建响应
    3. 返回统一响应格式

    ========================================
    业务规则
    ========================================
    1. 权限规则：
       - 此接口为公开接口，无需登录

    2. 搜索规则：
       - 支持股票代码前缀匹配（600 → 600519, 600036, ...）
       - 支持股票名称模糊匹配（茅台 → 贵州茅台, 茅台酒, ...）
       - 同时搜索代码和名称，合并结果
       - 优先返回代码精确匹配的结果

    3. 筛选规则：
       - market: 可选筛选市场类型
       - limit: 限制返回数量（1-100）

    4. 返回规则：
       - 返回简化的股票信息（不含完整基本面）
       - 按相关度排序
       - 最多返回limit条记录

    ========================================
    错误码
    ========================================
    - 0: 成功
    - 1003: 数据验证失败（ValidationError）
    - 1000: 服务器内部错误

    ========================================
    前端调用示例
    ========================================
    ```javascript
    // pages/trade/create.vue - 创建交易时搜索股票
    const searchStocks = async (keyword) => {
      if (!keyword || keyword.length < 1) return;

      const response = await api.post('/api/v1/stock/search', {
        keyword: keyword,
        market: selectedMarket.value,
        limit: 10
      });

      if (response.data.code === 0) {
        searchResults.value = response.data.data.items;
      }
    };

    // 防抖搜索
    const debouncedSearch = debounce(searchStocks, 300);
    ```

    ========================================
    修改记录
    ========================================
    2025-01-17: 重构为POST-only架构，使用Service+Converter+Builder模式
    """
    service = StockSearchService()
    data = await service.execute(
        db=db,
        keyword=request.keyword,
        market=request.market,
        limit=request.limit
    )
    return Response.success(data)
