# API接口快速索引

> 所有70个API接口的快速查询表

**最后更新**: 2025-11-20

> 统一规范：所有接口采用 POST 方法，路径格式为 `POST /api/v1/{module}/{action}`

---

## 📊 接口总览

| 模块 | 接口数 | 优先级分布 | 文档链接 |
|------|-------|-----------|---------|
| 认证与用户 | 5 | P0: 1, P1: 2, P2: 2 | [详情](#认证与用户-5个) |
| 账户管理 | 9 | P0: 1, P1: 3, P2: 5 | [详情](#账户管理-9个) |
| 持仓管理 | 9 | P0: 1, P1: 2, P2: 6 | [详情](#持仓管理-9个) |
| 交易记录 | 6 | P0: 2, P1: 1, P2: 3 | [详情](#交易记录-6个) |
| 股票数据 | 6 | P0: 1, P1: 2, P2: 3 | [详情](#股票数据-6个) |
| 事件管理 | 8 | P0: 1, P1: 2, P2: 5 | [详情](#事件管理-8个) |
| AI分析 | 5 | P1: 2, P2: 3 | [详情](#ai分析-5个) |
| 用户评价 (v3.2) | 3 | P0: 2, P2: 1 | [详情](#用户评价-v32-3个) |
| 每日复盘 (v3.2) | 7 | P0: 3, P1: 2, P2: 2 | [详情](#每日复盘-v32-7个) |
| AI对话 (v3.2) | 4 | P1: 2, P2: 2 | [详情](#ai对话-v32-4个) |
| 系统设置 | 4 | P1: 1, P2: 3 | [详情](#系统设置-4个) |
| 数据导出 | 4 | P2: 4 | [详情](#数据导出-4个) |
| **总计** | **70** | P0: 11, P1: 19, P2: 40 | - |

---

## 认证与用户 (5个)

| # | 方法 | 路径 | 说明 | 优先级 |
|---|------|------|------|--------|
| 1 | POST | `/api/v1/auth/login` | 用户登录 | P0 |
| 2 | POST | `/api/v1/auth/register` | 用户注册 | P1 |
| 3 | POST | `/api/v1/auth/logout` | 退出登录 | P1 |
| 4 | POST | `/api/v1/auth/refresh` | 刷新Token | P2 |
| 5 | POST | `/api/v1/auth/me` | 获取当前用户信息 | P2 |

**对应页面**: `Login.vue`

---

## 账户管理 (9个)

| # | 方法 | 路径 | 说明 | 优先级 |
|---|------|------|------|--------|
| 6 | POST | `/api/v1/account/query` | 获取账户列表 | P0 |
| 7 | POST | `/api/v1/account/detail` | 获取账户详情 | P1 |
| 8 | POST | `/api/v1/account/create` | 创建账户 | P1 |
| 9 | POST | `/api/v1/account/update` | 更新账户 | P2 |
| 10 | POST | `/api/v1/account/delete` | 删除账户 | P2 |
| 11 | POST | `/api/v1/account/deposit` | 充值 | P1 |
| 12 | POST | `/api/v1/account/withdraw` | 提现 | P2 |
| 13 | POST | `/api/v1/account/transfer` | 转账（账户间） | P2 |
| 14 | POST | `/api/v1/account/cashflow` | 获取资金流水 | P2 |

**对应页面**: `AccountList.vue`, `AccountDetail.vue`, `Dashboard.vue`
**对应组件**: `AddAccountDialog.vue`, `DepositDialog.vue`, `TransferDialog.vue`, `AccountFormDialog.vue`

---

## 持仓管理 (9个)

| # | 方法 | 路径 | 说明 | 优先级 |
|---|------|------|------|--------|
| 15 | POST | `/api/v1/holding/query` | 获取持仓列表 | P0 |
| 16 | POST | `/api/v1/holding/detail` | 获取持仓详情 | P1 |
| 17 | POST | `/api/v1/holding/create` | 添加持仓 | P1 |
| 18 | POST | `/api/v1/holding/update` | 调整持仓 | P2 |
| 19 | POST | `/api/v1/holding/delete` | 删除持仓 | P2 |
| 20 | POST | `/api/v1/watchlist/query` | 获取关注列表 | P2 |
| 21 | POST | `/api/v1/watchlist/create` | 添加关注 | P2 |
| 22 | POST | `/api/v1/watchlist/update` | 更新关注 | P2 |
| 23 | POST | `/api/v1/watchlist/delete` | 删除关注 | P2 |

**对应页面**: `HoldingsList.vue`, `Dashboard.vue`, `StockDetail.vue`
**对应组件**: `AddHoldingDialog.vue`, `HoldingAdjustDialog.vue`, `AddToWatchlistDialog.vue`, `HoldingTable.vue`, `WatchlistTable.vue`

---

## 交易记录 (6个)

| # | 方法 | 路径 | 说明 | 优先级 |
|---|------|------|------|--------|
| 24 | POST | `/api/v1/trade/query` | 获取交易记录列表 | P0 |
| 25 | POST | `/api/v1/trade/detail` | 获取交易详情 | P2 |
| 26 | POST | `/api/v1/trade/create` | 记录交易 | P0 |
| 27 | POST | `/api/v1/trade/import` | 批量导入交易 | P2 |
| 28 | POST | `/api/v1/trade/update` | 更新交易记录 | P2 |
| 29 | POST | `/api/v1/trade/delete` | 删除交易记录 | P2 |

**对应页面**: `TradesList.vue`, `Dashboard.vue`
**对应组件**: `RecordTradeDialog.vue`, `ImportTradesDialog.vue`

---

## 股票数据 (6个)

| # | 方法 | 路径 | 说明 | 优先级 |
|---|------|------|------|--------|
| 30 | POST | `/api/v1/stock/search` | 搜索股票 | P1 |
| 31 | POST | `/api/v1/stock/quote` | 获取实时行情 | P0 |
| 32 | POST | `/api/v1/stock/kline` | 获取K线数据 | P1 |
| 33 | POST | `/api/v1/stock/profile` | 获取公司信息 | P2 |
| 34 | POST | `/api/v1/stock/financials` | 获取财务数据 | P2 |
| 35 | POST | `/api/v1/stock/ranking` | 获取涨跌榜 | P2 |

**对应页面**: `StockDetail.vue`, `Dashboard.vue`
**对应组件**: `StockSearchDialog.vue`, `StockCard.vue`, `KLineChart.vue`

---

## 事件管理 (8个)

| # | 方法 | 路径 | 说明 | 优先级 |
|---|------|------|------|--------|
| 36 | POST | `/api/v1/event/query` | 获取事件列表 | P0 |
| 37 | POST | `/api/v1/event/detail` | 获取事件详情 | P1 |
| 38 | POST | `/api/v1/event/create` | 创建事件 | P1 |
| 39 | POST | `/api/v1/event/update` | 更新事件 | P2 |
| 40 | POST | `/api/v1/event/delete` | 删除事件 | P2 |
| 41 | POST | `/api/v1/event/read` | 标记已读 | P2 |
| 42 | POST | `/api/v1/event/batch-read` | 批量标记已读 | P2 |
| 43 | POST | `/api/v1/event/stats` | 获取事件统计 | P2 |

**对应页面**: `EventsList.vue`, `EventDetail.vue`, `Dashboard.vue`, `StockDetail.vue`
**对应组件**: `EventFormDialog.vue`, `EventTimeline.vue`

---

## AI分析 (5个)

| # | 方法 | 路径 | 说明 | 优先级 |
|---|------|------|------|--------|
| 44 | POST | `/api/v1/ai/single-analysis` | 单股AI分析 | P1 |
| 45 | POST | `/api/v1/ai/daily-analysis/create` | 批量AI分析任务 | P0 |
| 46 | POST | `/api/v1/ai/daily-analysis/results` | 获取批量分析结果 | P0 |
| 47 | POST | `/api/v1/ai/suggestions` | 获取AI操作建议 | P1 |
| 48 | POST | `/api/v1/ai/strategy` | 策略生成 | P2 |

**对应页面**: `AnalysisHub.vue`, `Dashboard.vue`, `StockDetail.vue`
**对应组件**: `SingleStockAnalysisDialog.vue`, `PortfolioAnalysisDialog.vue`, `StrategyGenerationDialog.vue`, `AnalysisReportDialog.vue`, `AIActionList.vue`, `AIActionCard.vue`

---

## 用户评价 (v3.2) (3个)

| # | 方法 | 路径 | 说明 | 优先级 |
|---|------|------|------|--------|
| 49 | POST | `/api/v1/review/get` | 获取股票评价 | P0 |
| 50 | POST | `/api/v1/review/save` | 创建/更新评价 | P0 |
| 51 | POST | `/api/v1/review/logs` | 获取评价日志 | P2 |

**对应页面**: `StockDetail.vue`
**对应组件**: `StockReview.vue`

---

## 每日复盘 (v3.2) (7个)

| # | 方法 | 路径 | 说明 | 优先级 |
|---|------|------|------|--------|
| 52 | POST | `/api/v1/ai/review/stocks` | 获取可分析股票 | P2 |
| 53 | POST | `/api/v1/ai/daily-analysis/create` | 提交批量分析任务 | P0 |
| 54 | POST | `/api/v1/ai/daily-analysis/results` | 查询分析结果 | P0 |
| 55 | POST | `/api/v1/ai/review/get` | 获取每日复盘 | P1 |
| 56 | POST | `/api/v1/ai/review/generate` | 生成每日复盘 | P1 |
| 57 | POST | `/api/v1/ai/review/history` | 获取历史复盘 | P2 |

**对应页面**: `DailyReview.vue`, `Dashboard.vue`
**对应组件**: `DailyAIAnalysis.vue`

---

## AI对话 (v3.2) (4个)

| # | 方法 | 路径 | 说明 | 优先级 |
|---|------|------|------|--------|
| 59 | POST | `/api/v1/ai/chat` | 简化AI对话 | P1 |
| 60 | POST | `/api/v1/ai/chat/session/create` | 创建对话会话 | P1 |
| 61 | POST | `/api/v1/ai/chat/message/send` | 发送消息 | P1 |
| 62 | POST | `/api/v1/ai/chat/history` | 获取会话历史 | P2 |
| 63 | POST | `/api/v1/ai/chat/session/delete` | 删除会话 | P2 |

**对应组件**: `AIChat.vue`

---

## 系统设置 (4个)

| # | 方法 | 路径 | 说明 | 优先级 |
|---|------|------|------|--------|
| 63 | POST | `/api/v1/settings/query` | 获取用户设置 | P1 |
| 64 | POST | `/api/v1/settings/update` | 更新用户设置 | P2 |
| 65 | POST | `/api/v1/settings/ai-api-key` | 配置AI密钥 | P2 |
| 66 | POST | `/api/v1/settings/ai-api-key/test` | 测试API密钥 | P2 |

**对应页面**: `SettingsPage.vue`
**对应组件**: `ApiKeyConfigDialog.vue`

---

## 数据导出 (4个)

| # | 方法 | 路径 | 说明 | 优先级 |
|---|------|------|------|--------|
| 67 | POST | `/api/v1/export/trades` | 导出交易记录 | P2 |
| 68 | POST | `/api/v1/export/holdings` | 导出持仓数据 | P2 |
| 69 | POST | `/api/v1/export/events` | 导出事件数据 | P2 |
| 70 | POST | `/api/v1/export/analysis-report` | 导出分析报告 | P2 |

**对应组件**: `ExportDialog.vue`

---

## 按优先级分类

### P0 - 核心功能 (11个)

**必须先实现，否则前端无法工作**

1. `POST /api/v1/auth/login` - 登录
2. `POST /api/v1/account/query` - 账户列表
3. `POST /api/v1/holding/query` - 持仓列表
4. `POST /api/v1/trade/query` - 交易记录
5. `POST /api/v1/trade/create` - 记录交易
6. `POST /api/v1/stock/quote` - 股票行情
7. `POST /api/v1/event/query` - 事件列表
8. `POST /api/v1/review/get` - 获取评价
9. `POST /api/v1/review/save` - 保存评价
10. `POST /api/v1/ai/daily-analysis/create` - 批量分析
11. `POST /api/v1/ai/daily-analysis/results` - 分析结果

**工作量评估**: 7-10天

---

### P1 - 重要功能 (19个)

**第二批实现，提升用户体验**

12-30: 详见各模块详细列表

**工作量评估**: 5-7天

---

### P2 - 辅助功能 (40个)

**第三批实现，锦上添花**

31-70: 详见各模块详细列表

**工作量评估**: 3-5天

---

## 按页面查找接口

### Dashboard.vue (仪表盘)
- 账户汇总: #6
- 持仓汇总: #15
- AI操作建议: #48
- 事件提醒: #36
- 涨跌榜: #35
- AI分析模块: #53, #54, #55

### AccountList.vue (账户列表)
- 账户列表: #6
- 创建账户: #8

### AccountDetail.vue (账户详情)
- 账户详情: #7
- 充值/提现: #11, #12
- 资金流水: #14

### HoldingsList.vue (持仓管理)
- 持仓列表: #15
- 添加持仓: #17
- 调整持仓: #18

### TradesList.vue (交易记录)
- 交易列表: #24
- 记录交易: #26
- 批量导入: #27

### StockDetail.vue (股票详情)
- 股票行情: #31
- K线数据: #32
- 公司信息: #33
- 相关事件: #36
- 我的评价: #49, #50, #51
- AI分析: #44

### EventsList.vue (事件中心)
- 事件列表: #36
- 创建事件: #38
- 事件统计: #43

### EventDetail.vue (事件详情)
- 事件详情: #37
- 标记已读: #41

### AnalysisHub.vue (AI分析中心)
- 单股分析: #44
- 持仓分析: #45
- 策略生成: #46
- AI建议: #48

### DailyReview.vue (每日复盘)
- 获取复盘: #56
- 生成复盘: #57
- 历史复盘: #58

### SettingsPage.vue (系统设置)
- 用户设置: #63, #64
- AI密钥: #65, #66

---

## 快速开发指南

### 第一周（P0接口）
1. 认证系统 (#1)
2. 账户基础 (#6)
3. 持仓查询 (#15)
4. 交易记录 (#24, #26)
5. 股票行情 (#31)
6. 事件查询 (#36)
7. 用户评价 (#49, #50)
8. AI分析 (#53, #55)

### 第二周（P1接口）
9. 账户管理完善 (#7, #8, #11)
10. 股票数据完善 (#30, #32)
11. 事件管理完善 (#37, #38)
12. AI分析完善 (#44, #47, #48)
13. 每日复盘 (#56, #57)
14. AI对话 (#59, #60)
15. 系统设置 (#63)

### 第三周（P2接口）
16. 其余辅助功能

---

## 相关文档

- [完整API文档](./complete-api-list.md) - 所有接口的详细定义
- [v3.2 API文档](./v3.2-api-list.md) - v3.2新增接口详细说明
- [v3.2 API简洁清单](./v3.2-api-summary.md) - v3.2接口快速查询
- [数据库设计](../database/schema-v1.md) - 数据表结构
- [PRD v3](../../prd/v3/main.md) - 产品需求文档

---

**文档版本**: v1.0
**最后更新**: 2025-01-17
