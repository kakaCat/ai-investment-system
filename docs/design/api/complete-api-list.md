# 完整API接口列表

> 基于所有前端页面和组件生成的完整API清单

**版本**: v1.0
**最后更新**: 2025-11-20
**覆盖范围**: 全部12个页面 + 17个对话框组件 + v3.2新功能

---

## 📑 目录

- [1. 认证与用户](#1-认证与用户)
- [2. 账户管理](#2-账户管理)
- [3. 持仓管理](#3-持仓管理)
- [4. 交易记录](#4-交易记录)
- [5. 股票数据](#5-股票数据)
- [6. 事件管理](#6-事件管理)
- [7. AI分析](#7-ai分析)
- [8. 用户评价 (v3.2)](#8-用户评价-v32)
- [9. 每日复盘 (v3.2)](#9-每日复盘-v32)
- [10. AI对话 (v3.2)](#10-ai对话-v32)
- [11. 系统设置](#11-系统设置)
- [12. 数据导出](#12-数据导出)
- [附录: 完整接口索引](#附录-完整接口索引)

---

> 迁移说明：本文件已统一为 POST-only 架构与模块/动作路径规范。
> 所有历史 `GET/PUT/DELETE` 接口均迁移为 `POST /api/v1/{module}/{action}`；
> 具体映射与优先级请参考最新索引文档：`docs/design/api/api-index.md`。

## 1. 认证与用户

### 页面/组件
- `Login.vue`

### 接口列表

#### 1.1 用户登录
```
POST /api/v1/auth/login
```

**请求体**:
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "user_id": 1,
      "username": "user@example.com",
      "nickname": "投资者",
      "avatar": "https://..."
    },
    "expires_at": "2025-01-24T14:30:00Z"
  }
}
```

#### 1.2 用户注册
```
POST /api/v1/auth/register
```

#### 1.3 退出登录
```
POST /api/v1/auth/logout
```

#### 1.4 刷新Token
```
POST /api/v1/auth/refresh
```

#### 1.5 获取当前用户信息
```
GET /api/v1/auth/me
```

---

## 2. 账户管理

### 页面/组件
- `AccountList.vue` - 账户列表页
- `AccountDetail.vue` - 账户详情页
- `Dashboard.vue` - 仪表盘（账户汇总）
- `AddAccountDialog.vue` - 添加账户对话框
- `AccountFormDialog.vue` - 账户表单对话框
- `DepositDialog.vue` - 充值/提现对话框
- `TransferDialog.vue` - 转账对话框

### 接口列表

#### 2.1 获取账户列表
```
GET /api/v1/accounts
```

**Query参数**:
- `user_id` (number): 用户ID
- `market` (string, optional): 市场类型 "A股" | "港股" | "美股"
- `status` (string, optional): 账户状态 "active" | "frozen"

**响应**:
```json
{
  "code": 200,
  "data": {
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
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

#### 2.2 获取账户详情
```
GET /api/v1/accounts/{account_id}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "account_id": 1,
    "account_name": "华泰证券-A股",
    "account_number": "12345678",
    "market": "A股",
    "broker": "华泰证券",
    "total_value": 350000,
    "available_cash": 120000,
    "invested_value": 230000,
    "frozen_cash": 5000,
    "today_profit": 1200,
    "today_profit_rate": 0.34,
    "total_profit": 15000,
    "total_profit_rate": 4.28,
    "holdings_count": 8,
    "watchlist_count": 15,
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2025-01-17T14:30:00Z"
  }
}
```

#### 2.3 创建账户
```
POST /api/v1/accounts
```

**请求体**:
```json
{
  "user_id": 1,
  "account_name": "华泰证券-A股",
  "account_number": "12345678",
  "market": "A股",
  "broker": "华泰证券",
  "initial_cash": 100000
}
```

#### 2.4 更新账户
```
PUT /api/v1/accounts/{account_id}
```

#### 2.5 删除账户
```
DELETE /api/v1/accounts/{account_id}
```

#### 2.6 充值
```
POST /api/v1/accounts/{account_id}/deposit
```

**请求体**:
```json
{
  "amount": 50000,
  "note": "追加资金"
}
```

#### 2.7 提现
```
POST /api/v1/accounts/{account_id}/withdraw
```

**请求体**:
```json
{
  "amount": 20000,
  "note": "提取部分资金"
}
```

#### 2.8 转账（账户间）
```
POST /api/v1/accounts/transfer
```

**请求体**:
```json
{
  "from_account_id": 1,
  "to_account_id": 2,
  "amount": 10000,
  "note": "资金调拨"
}
```

#### 2.9 获取账户资金流水
```
GET /api/v1/accounts/{account_id}/cashflow
```

**Query参数**:
- `start_date` (string, optional): 开始日期
- `end_date` (string, optional): 结束日期
- `type` (string, optional): "deposit" | "withdraw" | "transfer" | "trade"
- `limit` (number): 返回条数，默认50
- `offset` (number): 偏移量

---

## 3. 持仓管理

### 页面/组件
- `HoldingsList.vue` - 持仓列表页
- `Dashboard.vue` - 仪表盘（持仓汇总）
- `StockDetail.vue` - 股票详情页（持仓信息）
- `AddHoldingDialog.vue` - 添加持仓对话框
- `HoldingAdjustDialog.vue` - 调整持仓对话框
- `AddToWatchlistDialog.vue` - 添加关注对话框
- `HoldingTable.vue` - 持仓表格组件
- `WatchlistTable.vue` - 关注列表组件

### 接口列表

#### 3.1 获取持仓列表
```
GET /api/v1/holdings
```

**Query参数**:
- `user_id` (number): 用户ID
- `account_id` (number, optional): 账户ID
- `market` (string, optional): 市场
- `sort_by` (string, optional): "profit_rate" | "market_value" | "symbol"
- `order` (string, optional): "asc" | "desc"

**响应**:
```json
{
  "code": 200,
  "data": {
    "total": 8,
    "total_market_value": 230000,
    "total_profit": 15000,
    "total_profit_rate": 6.98,
    "holdings": [
      {
        "holding_id": 1,
        "account_id": 1,
        "symbol": "600600",
        "name": "青岛啤酒",
        "market": "A股",
        "quantity": 1600,
        "available_quantity": 1600,
        "frozen_quantity": 0,
        "avg_cost": 78.40,
        "current_price": 62.50,
        "market_value": 100000,
        "profit_loss": -25440,
        "profit_loss_rate": -20.3,
        "today_profit": -3200,
        "today_profit_rate": -4.87,
        "position_ratio": 43.5,
        "first_buy_date": "2024-08-15",
        "last_updated": "2025-01-17T15:00:00Z"
      }
    ]
  }
}
```

#### 3.2 获取单个持仓详情
```
GET /api/v1/holdings/{holding_id}
```

#### 3.3 添加持仓
```
POST /api/v1/holdings
```

**请求体**:
```json
{
  "user_id": 1,
  "account_id": 1,
  "symbol": "600519",
  "name": "贵州茅台",
  "quantity": 100,
  "avg_cost": 1680.00,
  "first_buy_date": "2025-01-17"
}
```

#### 3.4 调整持仓（手动修正）
```
PUT /api/v1/holdings/{holding_id}
```

**请求体**:
```json
{
  "quantity": 1500,
  "avg_cost": 75.20,
  "note": "成本价修正"
}
```

#### 3.5 删除持仓
```
DELETE /api/v1/holdings/{holding_id}
```

#### 3.6 获取关注列表
```
GET /api/v1/watchlist
```

**Query参数**:
- `user_id` (number): 用户ID
- `account_id` (number, optional): 账户ID

**响应**:
```json
{
  "code": 200,
  "data": {
    "total": 15,
    "watchlist": [
      {
        "id": 1,
        "user_id": 1,
        "account_id": 1,
        "symbol": "601398",
        "name": "工商银行",
        "market": "A股",
        "current_price": 5.82,
        "change_rate": 0.50,
        "watch_reason": "估值低，股息率高",
        "target_price": 6.50,
        "alert_on_target_price": true,
        "alert_on_news": false,
        "priority": 2,
        "added_at": "2025-01-10T10:00:00Z"
      }
    ]
  }
}
```

#### 3.7 添加关注
```
POST /api/v1/watchlist
```

**请求体**:
```json
{
  "user_id": 1,
  "account_id": 1,
  "symbol": "AAPL",
  "name": "Apple",
  "watch_reason": "科技龙头，长期看好",
  "target_price": 200.00,
  "alert_on_target_price": true,
  "priority": 1
}
```

#### 3.8 更新关注
```
PUT /api/v1/watchlist/{watchlist_id}
```

#### 3.9 删除关注
```
DELETE /api/v1/watchlist/{watchlist_id}
```

---

## 4. 交易记录

### 页面/组件
- `TradesList.vue` - 交易记录页
- `Dashboard.vue` - 仪表盘（快捷记录交易入口）
- `RecordTradeDialog.vue` - 记录交易对话框
- `ImportTradesDialog.vue` - 导入交易对话框

### 接口列表

#### 4.1 获取交易记录列表
```
GET /api/v1/trades
```

**Query参数**:
- `user_id` (number): 用户ID
- `account_id` (number, optional): 账户ID
- `symbol` (string, optional): 股票代码
- `trade_type` (string, optional): "buy" | "sell"
- `start_date` (string, optional): 开始日期
- `end_date` (string, optional): 结束日期
- `limit` (number): 返回条数，默认50
- `offset` (number): 偏移量

**响应**:
```json
{
  "code": 200,
  "data": {
    "total": 127,
    "summary": {
      "total_buy_amount": 350000,
      "total_sell_amount": 180000,
      "total_commission": 1250,
      "net_investment": 171250
    },
    "trades": [
      {
        "trade_id": 1,
        "account_id": 1,
        "symbol": "600600",
        "name": "青岛啤酒",
        "trade_type": "buy",
        "quantity": 500,
        "price": 78.40,
        "total_amount": 39200,
        "commission": 19.60,
        "tax": 0,
        "net_amount": 39219.60,
        "trade_date": "2024-08-15",
        "settle_date": "2024-08-16",
        "note": "首次建仓",
        "created_at": "2024-08-15T14:30:00Z"
      }
    ]
  }
}
```

#### 4.2 获取单条交易详情
```
GET /api/v1/trades/{trade_id}
```

#### 4.3 记录交易
```
POST /api/v1/trades
```

**请求体**:
```json
{
  "user_id": 1,
  "account_id": 1,
  "symbol": "600600",
  "name": "青岛啤酒",
  "trade_type": "buy",
  "quantity": 500,
  "price": 78.40,
  "commission": 19.60,
  "tax": 0,
  "trade_date": "2024-08-15",
  "note": "首次建仓"
}
```

**响应**:
```json
{
  "code": 201,
  "message": "交易记录已创建，持仓已更新",
  "data": {
    "trade_id": 1,
    "holding_updated": true,
    "new_avg_cost": 78.40,
    "new_quantity": 500
  }
}
```

#### 4.4 批量导入交易
```
POST /api/v1/trades/import
```

**请求体**:
```json
{
  "user_id": 1,
  "account_id": 1,
  "source": "broker_export",
  "trades": [
    {
      "symbol": "600600",
      "name": "青岛啤酒",
      "trade_type": "buy",
      "quantity": 500,
      "price": 78.40,
      "trade_date": "2024-08-15"
    }
  ]
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "total_imported": 127,
    "success": 125,
    "failed": 2,
    "duplicates": 0,
    "errors": [
      {
        "row": 5,
        "reason": "股票代码不存在"
      }
    ]
  }
}
```

#### 4.5 更新交易记录
```
PUT /api/v1/trades/{trade_id}
```

#### 4.6 删除交易记录
```
DELETE /api/v1/trades/{trade_id}
```

**注意**: 删除交易会重新计算持仓成本

---

## 5. 股票数据

### 页面/组件
- `StockDetail.vue` - 股票详情页
- `StockSearchDialog.vue` - 股票搜索对话框
- `StockCard.vue` - 股票卡片组件
- `KLineChart.vue` - K线图组件
- `Dashboard.vue` - 仪表盘（涨跌榜）

### 接口列表

#### 5.1 搜索股票
```
GET /api/v1/stocks/search
```

**Query参数**:
- `q` (string): 搜索关键词（代码或名称）
- `market` (string, optional): "A股" | "港股" | "美股"
- `limit` (number): 返回条数，默认20

**响应**:
```json
{
  "code": 200,
  "data": [
    {
      "symbol": "600600",
      "name": "青岛啤酒",
      "market": "A股",
      "industry": "消费",
      "sector": "啤酒",
      "current_price": 62.50,
      "change_rate": -4.87
    }
  ]
}
```

#### 5.2 获取股票实时行情
```
GET /api/v1/stocks/{symbol}/quote
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "symbol": "600600",
    "name": "青岛啤酒",
    "market": "A股",
    "current_price": 62.50,
    "change_amount": -3.20,
    "change_rate": -4.87,
    "open": 63.20,
    "high": 64.50,
    "low": 61.80,
    "prev_close": 65.70,
    "volume": 2300000,
    "turnover": 145000000,
    "turnover_rate": 1.23,
    "pe_ratio": 25.6,
    "pb_ratio": 3.8,
    "market_value": 15600000000,
    "update_time": "2025-01-17T15:00:00Z"
  }
}
```

#### 5.3 获取K线数据
```
GET /api/v1/stocks/{symbol}/kline
```

**Query参数**:
- `period` (string): "1min" | "5min" | "15min" | "30min" | "60min" | "daily" | "weekly" | "monthly"
- `start_date` (string, optional): 开始日期
- `end_date` (string, optional): 结束日期
- `limit` (number, optional): 返回条数，默认250

**响应**:
```json
{
  "code": 200,
  "data": {
    "symbol": "600600",
    "period": "daily",
    "klines": [
      {
        "date": "2025-01-17",
        "open": 63.20,
        "high": 64.50,
        "low": 61.80,
        "close": 62.50,
        "volume": 2300000,
        "turnover": 145000000
      }
    ]
  }
}
```

#### 5.4 获取公司基本信息
```
GET /api/v1/stocks/{symbol}/profile
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "symbol": "600600",
    "name": "青岛啤酒",
    "full_name": "青岛啤酒股份有限公司",
    "market": "A股",
    "industry": "消费",
    "sector": "啤酒",
    "list_date": "1993-08-27",
    "description": "青岛啤酒股份有限公司是国内最大的啤酒生产企业之一...",
    "website": "https://www.tsingtao.com.cn",
    "address": "山东省青岛市"
  }
}
```

#### 5.5 获取财务数据
```
GET /api/v1/stocks/{symbol}/financials
```

**Query参数**:
- `type` (string): "income" | "balance" | "cashflow"
- `period` (string): "quarterly" | "annual"
- `limit` (number): 返回期数，默认8

#### 5.6 获取涨跌榜
```
GET /api/v1/stocks/ranking
```

**Query参数**:
- `market` (string): "A股" | "港股" | "美股"
- `type` (string): "gainers" | "losers"
- `limit` (number): 返回条数，默认10

**响应**:
```json
{
  "code": 200,
  "data": {
    "type": "gainers",
    "market": "A股",
    "update_time": "2025-01-17T15:00:00Z",
    "stocks": [
      {
        "symbol": "002594",
        "name": "比亚迪",
        "current_price": 248.20,
        "change_rate": 2.30,
        "volume": 15000000,
        "is_holding": true
      }
    ]
  }
}
```

---

## 6. 事件管理

### 页面/组件
- `EventsList.vue` - 事件列表页
- `EventDetail.vue` - 事件详情页
- `EventFormDialog.vue` - 事件表单对话框
- `EventTimeline.vue` - 事件时间线组件
- `Dashboard.vue` - 仪表盘（事件提醒）
- `StockDetail.vue` - 股票详情页（相关事件）

### 接口列表

#### 6.1 获取事件列表
```
GET /api/v1/events
```

**Query参数**:
- `user_id` (number): 用户ID
- `category` (string, optional): "policy" | "company" | "market" | "industry"
- `subcategory` (string, optional): 具体子类型
- `level` (string, optional): "critical" | "high" | "medium" | "low"
- `symbol` (string, optional): 关联股票代码
- `start_date` (string, optional): 开始日期
- `end_date` (string, optional): 结束日期
- `is_read` (boolean, optional): 是否已读
- `limit` (number): 返回条数，默认50
- `offset` (number): 偏移量

**响应**:
```json
{
  "code": 200,
  "data": {
    "total": 45,
    "unread_count": 12,
    "events": [
      {
        "event_id": 1,
        "category": "policy",
        "subcategory": "monetary_policy",
        "level": "high",
        "title": "美联储加息25个基点",
        "description": "美联储宣布加息25个基点，符合市场预期...",
        "source": "美联储官网",
        "source_url": "https://...",
        "event_date": "2025-01-17",
        "affected_symbols": ["00700", "09988"],
        "ai_analysis": {
          "impact_direction": "negative",
          "impact_score": 75,
          "affected_holdings": 2,
          "expected_change": "-2% ~ -5%",
          "confidence": 0.82,
          "summary": "加息对科技股形成压力，建议减仓观望"
        },
        "is_read": false,
        "created_at": "2025-01-17T10:00:00Z"
      }
    ]
  }
}
```

#### 6.2 获取事件详情
```
GET /api/v1/events/{event_id}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "event_id": 1,
    "category": "policy",
    "subcategory": "monetary_policy",
    "level": "high",
    "title": "美联储加息25个基点",
    "description": "美联储宣布加息25个基点...",
    "full_content": "详细内容...",
    "source": "美联储官网",
    "source_url": "https://...",
    "event_date": "2025-01-17",
    "affected_symbols": ["00700", "09988"],
    "ai_analysis": {
      "impact_direction": "negative",
      "impact_score": 75,
      "short_term_impact": "利空",
      "mid_term_impact": "中性",
      "long_term_impact": "利好",
      "affected_holdings": [
        {
          "symbol": "00700",
          "name": "腾讯控股",
          "holding_quantity": 1000,
          "expected_change": "-2.5%",
          "suggested_action": "减仓"
        }
      ],
      "summary": "加息对科技股形成压力...",
      "confidence": 0.82,
      "analyzed_at": "2025-01-17T10:05:00Z"
    },
    "user_notes": "已减仓500股腾讯",
    "is_read": true,
    "created_at": "2025-01-17T10:00:00Z",
    "updated_at": "2025-01-17T14:00:00Z"
  }
}
```

#### 6.3 创建事件
```
POST /api/v1/events
```

**请求体**:
```json
{
  "user_id": 1,
  "category": "company",
  "subcategory": "earnings",
  "level": "medium",
  "title": "比亚迪Q4财报超预期",
  "description": "营收同比增长35%，净利润增长40%",
  "source": "比亚迪官网",
  "source_url": "https://...",
  "event_date": "2025-01-17",
  "affected_symbols": ["002594"],
  "trigger_ai_analysis": true
}
```

#### 6.4 更新事件
```
PUT /api/v1/events/{event_id}
```

#### 6.5 删除事件
```
DELETE /api/v1/events/{event_id}
```

#### 6.6 标记事件为已读
```
POST /api/v1/events/{event_id}/read
```

#### 6.7 批量标记已读
```
POST /api/v1/events/batch-read
```

**请求体**:
```json
{
  "event_ids": [1, 2, 3, 4, 5]
}
```

#### 6.8 获取事件统计
```
GET /api/v1/events/stats
```

**Query参数**:
- `user_id` (number): 用户ID
- `period` (string): "today" | "week" | "month"

**响应**:
```json
{
  "code": 200,
  "data": {
    "total_events": 45,
    "unread_count": 12,
    "by_category": {
      "policy": 8,
      "company": 22,
      "market": 10,
      "industry": 5
    },
    "by_level": {
      "critical": 2,
      "high": 15,
      "medium": 20,
      "low": 8
    },
    "affected_holdings": 5
  }
}
```

---

## 7. AI分析

### 页面/组件
- `AnalysisHub.vue` - AI分析中心
- `SingleStockAnalysisDialog.vue` - 单股分析对话框
- `PortfolioAnalysisDialog.vue` - 持仓分析对话框
- `StrategyGenerationDialog.vue` - 策略生成对话框
- `AnalysisReportDialog.vue` - 分析报告对话框
- `AIActionList.vue` - AI建议列表组件
- `AIActionCard.vue` - AI建议卡片组件
- `Dashboard.vue` - 仪表盘（AI操作建议）
- `StockDetail.vue` - 股票详情页（AI分析）

### 接口列表

#### 7.1 单股AI分析
```
POST /api/v1/ai/analysis/stock
```

**请求体**:
```json
{
  "user_id": 1,
  "symbol": "600600",
  "analysis_type": "comprehensive",
  "options": {
    "include_fundamentals": true,
    "include_technicals": true,
    "include_valuation": true,
    "include_events": true,
    "include_strategy": true
  }
}
```

**响应** (异步):
```json
{
  "code": 202,
  "data": {
    "task_id": "analysis_abc123",
    "status": "processing",
    "estimated_time": 15
  }
}
```

#### 7.2 持仓AI分析
```
POST /api/v1/ai/analysis/portfolio
```

**请求体**:
```json
{
  "user_id": 1,
  "account_id": 1,
  "analysis_type": "comprehensive",
  "options": {
    "include_risk_assessment": true,
    "include_correlation": true,
    "include_rebalancing": true,
    "include_optimization": true
  }
}
```

#### 7.3 策略生成
```
POST /api/v1/ai/strategy
```

**请求体**:
```json
{
  "user_id": 1,
  "account_id": 1,
  "strategy_type": "rebalancing",
  "constraints": {
    "max_position_ratio": 20,
    "min_cash_ratio": 20,
    "allowed_symbols": ["600600", "002594"],
    "risk_level": "moderate"
  }
}
```

#### 7.4 获取AI分析结果
```
GET /api/v1/ai/analysis/{task_id}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "task_id": "analysis_abc123",
    "status": "completed",
    "analysis_type": "stock",
    "symbol": "600600",
    "result": {
      "overall_score": 7.2,
      "recommendation": "hold",
      "fundamentals": {
        "score": 7.5,
        "pe_ratio": 25.6,
        "roe": 12.5,
        "revenue_growth": 5.2,
        "profit_margin": 8.3,
        "summary": "基本面良好，盈利稳定"
      },
      "technicals": {
        "score": 6.8,
        "trend": "downtrend",
        "support_levels": [60, 58],
        "resistance_levels": [65, 68],
        "indicators": {
          "ma5": 63.20,
          "ma20": 66.30,
          "rsi": 42,
          "macd": "bearish"
        },
        "summary": "技术面偏弱，等待企稳"
      },
      "valuation": {
        "score": 7.3,
        "fair_value": 70.00,
        "current_price": 62.50,
        "upside": 12.0,
        "summary": "估值合理偏低，有安全边际"
      },
      "strategy": {
        "action": "hold",
        "target_price": 70.00,
        "stop_loss": 55.00,
        "position_suggestion": "保持当前仓位，等待回调至60元可加仓",
        "risk_level": "medium"
      }
    },
    "tokens_used": 2500,
    "cost": 0.35,
    "analyzed_at": "2025-01-17T14:35:00Z"
  }
}
```

#### 7.5 获取AI操作建议列表
```
GET /api/v1/ai/suggestions
```

**Query参数**:
- `user_id` (number): 用户ID
- `account_id` (number, optional): 账户ID
- `priority` (string, optional): "urgent" | "today" | "week"
- `action` (string, optional): "buy" | "sell" | "hold" | "watch"

**响应**:
```json
{
  "code": 200,
  "data": {
    "total": 8,
    "suggestions": [
      {
        "suggestion_id": 1,
        "priority": "urgent",
        "stock": {
          "symbol": "600600",
          "name": "青岛啤酒"
        },
        "action": "sell",
        "current_price": 62.50,
        "holding": {
          "quantity": 1600,
          "profit_loss_rate": -20.3
        },
        "reason": "Q3财报不及预期，成本上升，销量疲软",
        "suggestion": "止损减仓500股，降低风险敞口",
        "target_price": 60.00,
        "confidence": 0.78,
        "generated_at": "2025-01-17T09:00:00Z"
      }
    ]
  }
}
```

---

## 8. 用户评价 (v3.2)

### 页面/组件
- `StockReview.vue` - 股票评价组件
- `StockDetail.vue` - 股票详情页（我的评价标签）

### 接口列表

#### 8.1 获取股票评价
```
GET /api/v1/reviews/{symbol}
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 1.1

#### 8.2 创建/更新股票评价
```
POST /api/v1/reviews/{symbol}
PUT /api/v1/reviews/{symbol}
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 1.2

#### 8.3 获取评价日志
```
GET /api/v1/reviews/{symbol}/logs
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 1.3

---

## 9. 每日复盘 (v3.2)

### 页面/组件
- `DailyReview.vue` - 每日复盘页
- `DailyAIAnalysis.vue` - 每日AI分析组件
- `Dashboard.vue` - 仪表盘（集成AI分析模块）

### 接口列表

#### 9.1 获取可分析股票列表
```
GET /api/v1/ai/daily-analysis/stocks
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 2.1

#### 9.2 批量AI分析
```
POST /api/v1/ai/daily-analysis
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 2.2

#### 9.3 查询分析进度
```
GET /api/v1/ai/daily-analysis/{task_id}/progress
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 2.3

#### 9.4 获取分析结果
```
GET /api/v1/ai/daily-analysis/{task_id}/results
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 2.4

#### 9.5 获取每日复盘报告
```
GET /api/v1/ai/daily-review
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 3.1

#### 9.6 生成每日复盘报告
```
POST /api/v1/ai/daily-review
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 3.2

#### 9.7 获取历史复盘列表
```
GET /api/v1/ai/daily-review/history
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 3.3

---

## 10. AI对话 (v3.2)

### 页面/组件
- `AIChat.vue` - AI对话组件

### 接口列表

#### 10.1 创建对话会话
```
POST /api/v1/ai/chat/sessions
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 4.1

#### 10.2 发送消息
```
POST /api/v1/ai/chat/sessions/{session_id}/messages
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 4.2

#### 10.3 获取会话历史
```
GET /api/v1/ai/chat/sessions/{session_id}/messages
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 4.3

#### 10.4 删除会话
```
DELETE /api/v1/ai/chat/sessions/{session_id}
```

详见 [v3.2-api-list.md](./v3.2-api-list.md) Section 4.4

---

## 11. 系统设置

### 页面/组件
- `SettingsPage.vue` - 系统设置页
- `ApiKeyConfigDialog.vue` - API密钥配置对话框

### 接口列表

#### 11.1 获取用户设置
```
GET /api/v1/settings
```

**Query参数**:
- `user_id` (number): 用户ID

**响应**:
```json
{
  "code": 200,
  "data": {
    "user_id": 1,
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
}
```

#### 11.2 更新用户设置
```
PUT /api/v1/settings
```

**请求体**:
```json
{
  "user_id": 1,
  "preferences": {
    "theme": "dark"
  },
  "notifications": {
    "push_enabled": true
  }
}
```

#### 11.3 配置AI API密钥
```
POST /api/v1/settings/ai-api-key
```

**请求体**:
```json
{
  "user_id": 1,
  "provider": "deepseek",
  "api_key": "sk-1234567890abcdef",
  "model": "deepseek-chat"
}
```

#### 11.4 测试API密钥
```
POST /api/v1/settings/ai-api-key/test
```

**请求体**:
```json
{
  "provider": "deepseek",
  "api_key": "sk-1234567890abcdef"
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "valid": true,
    "model": "deepseek-chat",
    "remaining_quota": 1000000
  }
}
```

---

## 12. 数据导出

### 页面/组件
- `ExportDialog.vue` - 导出对话框
- `TradesList.vue` - 交易记录导出
- `HoldingsList.vue` - 持仓数据导出
- `EventsList.vue` - 事件数据导出

### 接口列表

#### 12.1 导出交易记录
```
POST /api/v1/export/trades
```

**请求体**:
```json
{
  "user_id": 1,
  "account_id": 1,
  "format": "xlsx",
  "start_date": "2024-01-01",
  "end_date": "2025-01-17",
  "include_summary": true
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "download_url": "https://.../exports/trades_20250117.xlsx",
    "expires_at": "2025-01-18T14:30:00Z",
    "file_size": 52480
  }
}
```

#### 12.2 导出持仓数据
```
POST /api/v1/export/holdings
```

#### 12.3 导出事件数据
```
POST /api/v1/export/events
```

#### 12.4 导出分析报告
```
POST /api/v1/export/analysis-report
```

**请求体**:
```json
{
  "user_id": 1,
  "report_type": "portfolio",
  "format": "pdf",
  "include_charts": true
}
```

---

## 附录: 完整接口索引

### 按模块分类

| 模块 | 接口数量 | 详情 |
|------|---------|------|
| 认证与用户 | 5 | [Section 1](#1-认证与用户) |
| 账户管理 | 9 | [Section 2](#2-账户管理) |
| 持仓管理 | 9 | [Section 3](#3-持仓管理) |
| 交易记录 | 6 | [Section 4](#4-交易记录) |
| 股票数据 | 6 | [Section 5](#5-股票数据) |
| 事件管理 | 8 | [Section 6](#6-事件管理) |
| AI分析 | 5 | [Section 7](#7-ai分析) |
| 用户评价 (v3.2) | 3 | [Section 8](#8-用户评价-v32) |
| 每日复盘 (v3.2) | 7 | [Section 9](#9-每日复盘-v32) |
| AI对话 (v3.2) | 4 | [Section 10](#10-ai对话-v32) |
| 系统设置 | 4 | [Section 11](#11-系统设置) |
| 数据导出 | 4 | [Section 12](#12-数据导出) |
| **总计** | **70个** | - |

### 接口优先级

#### P0 - 核心功能（必须实现）

**用户体验核心路径**

1. `POST /api/v1/auth/login` - 登录
2. `GET /api/v1/accounts` - 获取账户列表
3. `GET /api/v1/holdings` - 获取持仓列表
4. `GET /api/v1/trades` - 获取交易记录
5. `POST /api/v1/trades` - 记录交易
6. `GET /api/v1/stocks/{symbol}/quote` - 获取股票行情
7. `GET /api/v1/events` - 获取事件列表
8. `GET /api/v1/reviews/{symbol}` - 获取股票评价
9. `POST /api/v1/reviews/{symbol}` - 保存股票评价
10. `POST /api/v1/ai/daily-analysis` - 批量AI分析
11. `GET /api/v1/ai/daily-analysis/{task_id}/results` - 获取分析结果

**预计工作量**: 7-10天

#### P1 - 重要功能（第二批）

**提升用户体验**

12. `GET /api/v1/accounts/{account_id}` - 账户详情
13. `POST /api/v1/accounts` - 创建账户
14. `POST /api/v1/accounts/{account_id}/deposit` - 充值
15. `GET /api/v1/stocks/search` - 搜索股票
16. `GET /api/v1/stocks/{symbol}/kline` - K线数据
17. `GET /api/v1/events/{event_id}` - 事件详情
18. `POST /api/v1/events` - 创建事件
19. `POST /api/v1/ai/analysis/stock` - 单股AI分析
20. `GET /api/v1/ai/suggestions` - AI操作建议
21. `GET /api/v1/ai/daily-review` - 每日复盘
22. `POST /api/v1/ai/chat/sessions` - 创建AI对话
23. `GET /api/v1/settings` - 获取用户设置

**预计工作量**: 5-7天

#### P2 - 辅助功能（第三批）

**锦上添花**

24. `GET /api/v1/watchlist` - 关注列表
25. `POST /api/v1/trades/import` - 批量导入交易
26. `GET /api/v1/stocks/{symbol}/financials` - 财务数据
27. `GET /api/v1/events/stats` - 事件统计
28. `POST /api/v1/ai/analysis/portfolio` - 持仓分析
29. `GET /api/v1/reviews/{symbol}/logs` - 评价日志
30. `POST /api/v1/export/trades` - 导出交易

**预计工作量**: 3-5天

---

## 技术规范

### 认证方式
```http
Authorization: Bearer {jwt_token}
```

### 统一响应格式

**成功**:
```json
{
  "code": 200,
  "message": "Success",
  "data": { ... }
}
```

**错误**:
```json
{
  "code": 400,
  "message": "Invalid request",
  "error": {
    "type": "ValidationError",
    "details": [...]
  }
}
```

### 常见错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 202 | 已接受（异步任务） |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |
| 503 | 服务暂时不可用 |

### 分页规范

使用 `limit` 和 `offset` 参数：

```
GET /api/v1/trades?limit=50&offset=100
```

响应包含总数：
```json
{
  "total": 1250,
  "data": [...]
}
```

### 日期时间格式

- 日期: `YYYY-MM-DD`
- 时间: ISO 8601 `YYYY-MM-DDTHH:mm:ssZ`

### 速率限制

| 接口类型 | 限制 |
|---------|------|
| AI接口 | 100次/小时/用户 |
| 数据查询 | 1000次/小时/用户 |
| 数据写入 | 500次/小时/用户 |

---

## 相关文档

- [v3.2 API详细文档](./v3.2-api-list.md)
- [v3.2 API简洁清单](./v3.2-api-summary.md)
- [数据库设计](../database/schema-v1.md)
- [PRD v3](../../prd/v3/main.md)
- [HTML原型](../ui/html-prototypes/README.md)

---

**文档版本**: v1.0
**维护者**: AI Investment System Team
**最后审核**: 2025-01-17
