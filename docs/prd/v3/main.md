# PRD v3.2 - AI 驱动的个人投资管理系统

> **版本**: v3.2
> **状态**: 设计完成，待实施
> **最后更新**: 2025-01-17
> **完整版本**: 见 [archive/main-v3.2-full.md](archive/main-v3.2-full.md)
> **更新**: v3.2 新增AI决策流程系统（section 2.11）

---

## 文档说明

为便于维护和查阅，PRD v3.1 已按金字塔原则拆分为6个专题文档，统一存放在 [sections/](sections/) 目录。

## 📑 文档导航

### [01 - 背景与目标](sections/01-overview.md)
产品背景、核心目标、用户画像

**关键内容**:
- 产品定位：事件驱动 + AI 赋能的投资管理工具
- 核心优势：多账户管理、AI 分析、事件追踪
- 目标用户：个人投资者、多账户管理者

---

### [02 - 核心功能需求](sections/02-core-features.md)
基础功能模块设计（2.1-2.8, 2.10-2.11章节）

**包含模块**:
- 2.1 用户与认证
- 2.2 账户管理
- 2.3 股票信息库
- 2.4 持仓管理
- 2.5 交易记录
- 2.6 AI 策略生成
- 2.7 策略记录与复盘
- 2.8 价格管理
- 2.10 数据可视化
- 2.11 AI决策流程系统 ⭐ (v3.2 新增)

**功能亮点**:
- ✅ 多账户支持（A股/港股/美股）
- ✅ AI 策略生成与复盘
- ✅ 精确的盈亏计算
- ✨ AI决策流程（每日分析、推荐、复盘、用户评价）

---

### [03 - 事件分析系统](sections/03-event-system.md) ⭐
v3.1 核心特性，事件驱动分析体系（2.9章节）

**核心设计**:
- **4大类16子类事件**：政策/公司/市场/行业
- **AI 影响分析**：单事件分析、批量综合分析
- **事件时间线**：股票级、账户级、全局事件视图
- **智能提醒**：Critical 立即推送、High 当日汇总
- **持仓影响矩阵**：事件与持仓的关联分析

**技术要点**:
- 定时任务：每小时事件收集、异步 AI 分析
- 性能优化：按月分区、GIN 索引、Redis 缓存
- 成本控制：批量分析、高优先级详细分析

---

### [04 - 场景用例与流程](sections/04-use-cases.md)
用户故事、流程图、时序图、状态机

**包含内容**:
- 3.1 用户故事（账户管理、持仓分析、AI 策略）
- 3.2 核心流程图
- 3.3 关键时序图（AI 分析、事件处理）
- 3.4 状态机图（策略生命周期、事件状态）
- 3.5 数据流图

**典型流程**:
- 用户添加账户 → 导入持仓 → 触发 AI 分析 → 查看建议
- 事件收集 → AI 影响分析 → 推送提醒 → 用户决策

---

### [05 - 数据库与 API 设计](sections/05-database-api.md)
技术实现细节

**数据库设计**:
- **11张核心表**：users, accounts, holdings, trade_records, ai_strategies, company_events, event_analysis 等
- **设计原则**：虚拟外键、幂等性、JSONB 灵活性、软删除
- **索引策略**：account_id + symbol + time 复合索引
- **盈亏计算**：未实现盈亏（holdings）+ 已实现盈亏（trade_records）

**API 设计**:
- 4.1 用户认证 API
- 4.2 账户管理 API
- 4.3 持仓管理 API
- 4.4 交易记录 API
- 4.5 AI 策略 API
- 4.6 价格管理 API
- 4.7 事件管理 API（v3.1 新增）
- 4.8 事件分析 API（v3.1 新增）
- 4.9 关注列表 API
- 4.10 策略评估 API
- 4.11 AI Token 管理 API
- 4.12 公司信息 API

---

### [06 - 实施计划与风险](sections/06-implementation.md)
技术架构、开发计划、成功指标

**技术栈**:
- 后端：FastAPI + Python 3.11+ + SQLAlchemy 2.0
- 前端：Vue 3 + TypeScript + TailwindCSS
- 数据库：PostgreSQL 15+
- AI：DeepSeek API（deepseek-chat）
- 数据源：Tushare / AkShare

**开发里程碑**（12周）:
- Phase 1: 基础框架（2周）
- Phase 2: 账户与持仓（2周）
- Phase 3: 交易与关注（1周）
- Phase 4: AI 集成（2周）
- Phase 5: 策略与复盘（2周）
- Phase 6: 可视化与优化（2周）
- Phase 7: 测试与上线（1周）
- **Phase 8: 事件系统增强**（2周，建议延后）

**成功指标**:
- MVP 阶段：100+ 注册用户，20+ 日活
- 产品成熟期：500+ 注册用户，100+ 月活，60%+ AI 准确率

---

## 🎯 快速查阅

| 需求 | 推荐章节 |
|------|---------|
| 了解产品定位 | [01-overview.md](sections/01-overview.md) |
| 查看功能清单 | [02-core-features.md](sections/02-core-features.md) |
| AI决策流程系统 | [02-core-features.md#2.11](sections/02-core-features.md) ⭐ NEW |
| 事件系统设计 | [03-event-system.md](sections/03-event-system.md) ⭐ |
| 查看业务流程 | [04-use-cases.md](sections/04-use-cases.md) |
| 数据库表结构 | [05-database-api.md](sections/05-database-api.md) |
| 开发排期计划 | [06-implementation.md](sections/06-implementation.md) |

---

## 📐 配套文档

- **原型设计**: [docs/design/ui/wireframes/](../design/ui/wireframes/)
- **数据库详细设计**: [docs/design/database/schema-v1.md](../design/database/schema-v1.md)
- **事件系统详细设计**: [docs/design/features/events/](../design/features/events/)
- **技术架构**: [docs/design/architecture/tech-stack.md](../design/architecture/tech-stack.md)

---

## 📝 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|---------|
| v3.1 | 2025-01-15 | 文档拆分到 sections/ 目录，符合文档管理规范 |
| v3.1 | 2025-01-14 | 新增事件分析系统（2.9章节） |
| v3.0 | 2025-01-10 | 完整 PRD 初版 |
| v2.0 | 2024-12-XX | 量化 Agent 方向（已废弃） |
| v1.0 | 2024-11-XX | 最初版本 |

---

**维护者**: Claude Code
**仓库**: /Users/mac/Documents/ai/stock
**联系方式**: 见项目 CLAUDE.md
