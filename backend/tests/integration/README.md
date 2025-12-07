# 集成测试

> API端点和服务集成测试

---

## 🚧 状态

**当前状态**: 待开发

**预计完成**: Phase 2 - 核心功能开发阶段

---

## 🎯 测试范围（规划）

### 1. API端点测试

- **账户管理API** - 创建、查询、更新、删除
- **持仓管理API** - 查询、统计、历史
- **交易记录API** - 记录、导入、查询
- **事件管理API** - 创建、更新、查询、AI评估
- **AI分析API** - 单股分析、组合分析、策略生成
- **认证API** - 登录、注册、token刷新

### 2. 数据库集成测试

- **事务完整性** - 确保数据一致性
- **并发处理** - 多用户并发操作
- **数据隔离** - 用户数据隔离验证
- **软删除** - deleted_at标记验证

### 3. 第三方服务集成

- **DeepSeek API** - AI分析调用
- **Tushare API** - 股票数据获取
- **AkShare API** - 备用数据源

---

## 📝 测试框架

**计划使用**:
- `pytest` - 测试框架
- `httpx` - 异步HTTP客户端
- `pytest-asyncio` - 异步测试支持
- `faker` - 测试数据生成

---

## 🔗 相关文档

- [API设计文档](../../docs/design/api/)
- [数据库Schema](../../docs/design/database/schema-v1.md)
- [后端架构](../../docs/design/architecture/backend-architecture.md)

---

**最后更新**: 2025-11-19
