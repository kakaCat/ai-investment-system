# 架构设计

> 系统架构、技术选型和整体设计决策

---

## 文档索引

### [技术栈选型](tech-stack.md)
- 前端：Vue 3 + TypeScript + Vite
- 后端：FastAPI + Python 3.11+
- 数据库：PostgreSQL 15+ + SQLAlchemy 2.0
- AI：DeepSeek API
- 数据源：Tushare / AkShare

**关键决策**：
- 为什么选择 FastAPI 而不是 Flask/Django
- 为什么选择 DeepSeek 而不是 Claude/GPT-4
- 成本优化和技术风险对策

### [后端架构设计](backend-architecture.md) ⭐
- 分层设计：Controller → Service → Converter/Repository
- 目录结构：按业务模块组织
- 代码规范：完整的注释规范、命名规范
- 接口规范：POST-Only API、统一响应格式
- 业务逻辑：Converter 作为领域层，包含所有业务计算

**核心特点**：
- 一个接口一套业务（Service + Converter + Builder 在同一文件）
- Converter 静态类（所有业务逻辑集中在这里）
- 完整的接口注释（包含时序流程、业务规则、前端调用示例）

### [前端架构设计](frontend-architecture.md) ⭐
- 技术栈：Vue 3 + TypeScript + Vite + TailwindCSS + Pinia
- UI 组件库：Element Plus（企业级表格/表单组件强大）
- 图表库：ECharts（K 线图支持完善）
- 目录结构：按功能模块组织（views/components/api/stores）
- 路由设计：Vue Router 4 + 路由守卫
- 状态管理：Pinia（组合式 API 风格）
- API 调用：Axios 统一封装 + 模块化接口
- 样式方案：Tailwind CSS 优先

**核心特点**：
- TypeScript 类型安全
- 组合式 API（setup 语法糖）
- API 接口模块化（按业务分文件）
- 完整的代码规范和命名规范
- 不需要国际化和暗黑模式（专注核心功能）

---

## 待创建文档

- [ ] `api-design.md` - API 接口设计文档（完整接口列表）
- [ ] `data-flow.md` - 数据流向和处理流程
- [ ] `deployment.md` - 部署架构（Docker/K8s）
- [ ] `security.md` - 安全架构和认证方案

---

## 架构原则

1. **前后端分离**：Vue 前端 + FastAPI 后端
2. **多租户隔离**：用户级数据严格隔离
3. **异步优先**：充分利用 Python asyncio
4. **API 优先**：所有功能通过 RESTful API 暴露
5. **可扩展性**：模块化设计，易于添加新功能
