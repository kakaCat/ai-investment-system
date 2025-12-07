# Sprint 002 - 前端AI功能对接

> **周期**: 2025-11-20 ~ 2025-11-27
> **目标**: 完成前端AI功能对接，让用户能够使用AI分析功能

---

## 📊 进度统计

- **总任务数**: 8
- **已完成**: 0 (0%)
- **进行中**: 0 (0%)
- **待开始**: 8 (100%)

---

## 🎯 Sprint目标

### 核心目标
让用户能够在前端界面中：
1. ✅ 查看AI单股分析结果
2. ✅ 与AI对话交流投资问题
3. ✅ 查看批量分析进度和结果
4. ✅ 查看每日市场复盘

### 依赖项
- ✅ 后端AI功能已完成（Sprint 001扩展）
- ✅ 数据源集成已完成（Sprint 001扩展）
- ✅ 基础前端页面已完成（Sprint 001）

---

## 前端任务

| ID | 任务 | 状态 | 估算 | 负责人 | 备注 |
|----|------|------|------|--------|------|
| FE-011 | AI分析结果展示组件 | ⏳ 待开始 | 2天 | Frontend | 单股分析结果卡片 |
| FE-012 | AI对话界面 | ⏳ 待开始 | 2天 | Frontend | 聊天式交互 |
| FE-013 | 批量分析进度组件 | ⏳ 待开始 | 1天 | Frontend | 进度条+结果列表 |
| FE-014 | 每日复盘展示页面 | ⏳ 待开始 | 1天 | Frontend | 市场总结展示 |
| FE-015 | AI功能集成到股票详情页 | ⏳ 待开始 | 1天 | Frontend | 添加"AI分析"按钮 |
| FE-016 | AI对话页面路由 | ⏳ 待开始 | 0.5天 | Frontend | /ai-chat 路由 |

---

## 测试任务

| ID | 任务 | 状态 | 估算 | 负责人 | 备注 |
|----|------|------|------|--------|------|
| QA-006 | AI功能UI测试 | ⏳ 待开始 | 1天 | QA | Playwright测试 |
| QA-007 | AI响应时间测试 | ⏳ 待开始 | 0.5天 | QA | 性能测试 |

---

## 可选任务（如时间充足）

| ID | 任务 | 状态 | 估算 | 备注 |
|----|------|------|------|------|
| OPT-001 | AI分析历史记录 | - | 1天 | 保存和查看历史分析 |
| OPT-002 | AI分析加载优化 | - | 0.5天 | 骨架屏、进度提示 |

---

## 📋 详细任务说明

### FE-011: AI分析结果展示组件

**目标**: 创建美观的AI分析结果展示组件

**需求**:
- 展示综合评分（饼图或仪表盘）
- 展示基本面、技术面、估值分数
- 展示AI投资建议（文字）
- 展示置信度
- 数据来源标签（Tushare/AkShare）

**API调用**:
```typescript
POST /api/v1/ai/single-analysis
{
  "symbol": "600519",
  "stock_name": "贵州茅台",
  "dimensions": ["fundamental", "technical", "valuation"]
}
```

**响应格式**:
```json
{
  "ai_score": {
    "overall_score": 85,
    "fundamental_score": 90,
    "technical_score": 82,
    "valuation_score": 78
  },
  "ai_suggestion": "建议买入，目标价1800元",
  "confidence_level": 85,
  "data_source": "tushare"
}
```

**技术要点**:
- 使用Element Plus的Card、Progress组件
- ECharts图表展示评分
- Loading状态处理（30秒AI推理时间）

---

### FE-012: AI对话界面

**目标**: 实现聊天式AI投资顾问界面

**需求**:
- 消息列表（用户消息 + AI回复）
- 输入框和发送按钮
- 打字机效果（可选）
- 清空对话按钮

**API调用**:
```typescript
POST /api/v1/ai/chat
{
  "message": "如何看待茅台的投资价值？",
  "context": []  // 历史对话上下文（可选）
}
```

**响应格式**:
```json
{
  "reply": "基于当前数据分析...",
  "conversation_id": "uuid"
}
```

**技术要点**:
- 使用Element Plus的Timeline或自定义消息气泡
- WebSocket长连接（可选，后续优化）
- Markdown渲染AI回复

---

### FE-013: 批量分析进度组件

**目标**: 展示批量股票分析的进度和结果

**需求**:
- 进度条（已完成/总数）
- 实时更新分析结果列表
- 点击查看单个股票详细分析

**API调用**:
```typescript
POST /api/v1/ai/batch-analysis
{
  "symbols": ["600519", "000858", "600600"],
  "dimensions": ["fundamental", "technical"]
}
```

**响应格式**:
```json
{
  "results": [
    {"symbol": "600519", "ai_score": {...}, "status": "completed"},
    {"symbol": "000858", "ai_score": {...}, "status": "completed"},
    {"symbol": "600600", "status": "analyzing"}
  ],
  "progress": {"completed": 2, "total": 3}
}
```

**技术要点**:
- 轮询或WebSocket实时更新进度
- 表格展示结果，支持排序

---

### FE-014: 每日复盘展示页面

**目标**: 展示AI生成的每日市场复盘

**需求**:
- 市场总结（文字）
- 关键事件列表
- 板块表现
- 明日关注点

**API调用**:
```typescript
POST /api/v1/ai/daily-review
{
  "date": "2025-11-20"
}
```

**响应格式**:
```json
{
  "market_summary": "今日A股...",
  "key_events": ["事件1", "事件2"],
  "sector_performance": {...},
  "tomorrow_focus": "关注..."
}
```

**技术要点**:
- 日期选择器
- Markdown渲染市场总结
- 卡片式布局

---

## 🚨 风险和依赖

| 风险 | 级别 | 影响 | 应对措施 |
|------|------|------|---------|
| AI响应时间长（30秒） | 中 | 用户体验 | 添加Loading动画、进度提示 |
| 网络不稳定导致超时 | 中 | 功能失败 | 错误重试机制、友好错误提示 |
| 前端团队资源不足 | 低 | 进度延期 | 优先核心功能（FE-011, FE-012） |

---

## ✅ 完成标准

### 功能验收
- [ ] 用户能在股票详情页点击"AI分析"查看结果
- [ ] AI分析结果包含评分、建议、置信度
- [ ] AI对话页面能正常发送消息并收到回复
- [ ] 批量分析能显示进度和结果列表
- [ ] 每日复盘页面能展示市场总结

### 技术验收
- [ ] 所有API调用正确，错误处理完善
- [ ] Loading状态友好（骨架屏或进度条）
- [ ] 响应式布局，移动端可用
- [ ] 通过UI自动化测试
- [ ] 代码符合前端架构规范

### 文档验收
- [ ] 前端组件文档完成
- [ ] API集成文档更新
- [ ] 用户使用手册更新

---

## 📝 备注

### 技术栈
- Vue 3 Composition API
- TypeScript
- Element Plus
- ECharts (图表)
- Axios (API调用)

### 参考文档
- [后端AI API文档](../../docs/guides/ai-setup.md)
- [AI验证报告](../../docs/AI-VERIFICATION-REPORT.md)
- [前端架构约束](../../frontend/ARCHITECTURE.md)

---

**创建时间**: 2025-11-20
**Sprint状态**: ⏳ 待开始
**预计开始**: 2025-11-20
**预计完成**: 2025-11-27
