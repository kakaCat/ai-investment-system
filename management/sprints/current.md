# Sprint 002 - 前端AI功能对接

> **周期**: 2025-12-09 ~ 2025-12-15
> **目标**: 完成前端AI功能对接，让用户能够使用AI分析功能

---

## 📊 进度统计

- **总任务数**: 8
- **已完成**: 6 (75%)
- **进行中**: 0 (0%)
- **待开始**: 2 (25%)

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

| ID | 任务 | 状态 | 负责人 | 估算 | 备注 |
|----|------|------|--------|------|------|
| FE-011 | AI分析结果展示组件 | ✅ 已完成 | Frontend | 2天 | 单股分析结果卡片 |
| FE-012 | AI对话界面 | ✅ 已完成 | Frontend | 2天 | 聊天式交互 |
| FE-013 | 批量分析进度组件 | ✅ 已完成 | Frontend | 1天 | 进度条+结果列表 |
| FE-014 | 每日复盘展示页面 | ✅ 已完成 | Frontend | 1天 | 市场总结展示 |
| FE-015 | AI功能集成到股票详情页 | ✅ 已完成 | Frontend | 1天 | 添加"AI分析"按钮 |
| FE-016 | AI对话页面路由 | ✅ 已完成 | Frontend | 0.5天 | /ai-chat 路由 |

---

## 测试任务

| ID | 任务 | 状态 | 负责人 | 估算 | 备注 |
|----|------|------|--------|------|------|
| QA-006 | AI功能UI测试 | ⏳ 待开始 | QA | 1天 | Playwright测试 |
| QA-007 | AI响应时间测试 | ⏳ 待开始 | QA | 0.5天 | 性能测试 |

---

## 📋 详细任务说明

### FE-011: AI分析结果展示组件

**目标**: 创建美观的AI分析结果展示组件

**文件位置**: `frontend/src/components/AIAnalysisResult.vue` (已存在，需完善)

**需求**:
- 展示综合评分（饼图或仪表盘）
- 展示基本面、技术面、估值分数
- 展示AI投资建议（文字）
- 展示置信度
- 数据来源标签（Tushare/AkShare）

**API调用**:
```typescript
// frontend/src/api/ai.ts (已存在)
import { getSingleAnalysis } from '@/api/ai'

const result = await getSingleAnalysis({
  symbol: "600519",
  stock_name: "贵州茅台",
  dimensions: ["fundamental", "technical", "valuation"]
})
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
- ECharts图表展示评分（雷达图或仪表盘）
- Loading状态处理（骨架屏，30秒超时）
- 错误处理和重试机制

---

### FE-012: AI对话界面

**目标**: 实现聊天式AI投资顾问界面

**文件位置**: `frontend/src/components/AIChat.vue` (已存在，需完善)

**需求**:
- 消息列表（用户消息 + AI回复）
- 输入框和发送按钮
- 打字机效果（可选）
- 清空对话按钮
- 支持Markdown渲染

**API调用**:
```typescript
// frontend/src/api/ai.ts
import { chatWithAI } from '@/api/ai'

const result = await chatWithAI({
  message: "如何看待茅台的投资价值？",
  context: []  // 历史对话上下文（可选）
})
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
- 消息滚动到底部
- Markdown渲染AI回复（可用markdown-it）
- 保存对话历史到LocalStorage

---

### FE-013: 批量分析进度组件

**目标**: 展示批量股票分析的进度和结果

**文件位置**: `frontend/src/components/BatchAnalysisProgress.vue` (新建)

**需求**:
- 进度条（已完成/总数）
- 实时更新分析结果列表
- 点击查看单个股票详细分析
- 支持筛选和排序

**API调用**:
```typescript
import { getBatchAnalysis } from '@/api/ai'

const result = await getBatchAnalysis({
  symbols: ["600519", "000858", "600600"],
  dimensions: ["fundamental", "technical"]
})
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
- 表格展示结果，支持排序（按评分）
- 进度条动画效果

---

### FE-014: 每日复盘展示页面

**目标**: 展示AI生成的每日市场复盘

**文件位置**: `frontend/src/views/review/DailyReview.vue` (已存在，需完善)

**需求**:
- 市场总结（文字）
- 关键事件列表
- 板块表现
- 明日关注点
- 日期选择器

**API调用**:
```typescript
import { getDailyReview } from '@/api/ai'

const result = await getDailyReview({
  date: "2025-12-08"
})
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
- 日期选择器（Element Plus DatePicker）
- Markdown渲染市场总结
- 卡片式布局
- 支持分享和导出

---

### FE-015: AI功能集成到股票详情页

**目标**: 在股票详情页添加AI分析入口

**文件位置**: `frontend/src/views/stocks/StockDetail.vue` (已存在)

**需求**:
- 添加"AI分析"按钮
- 点击按钮触发分析
- 在对话框中展示分析结果
- 支持重新分析

**实现要点**:
```vue
<template>
  <div class="stock-detail">
    <!-- 现有内容 -->

    <!-- 新增AI分析按钮 -->
    <el-button type="primary" @click="showAIAnalysis">
      <el-icon><MagicStick /></el-icon>
      AI分析
    </el-button>

    <!-- AI分析对话框 -->
    <el-dialog v-model="aiDialogVisible" title="AI分析结果" width="70%">
      <AIAnalysisResult :symbol="stockSymbol" :stock-name="stockName" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import AIAnalysisResult from '@/components/AIAnalysisResult.vue'

const aiDialogVisible = ref(false)
const showAIAnalysis = () => {
  aiDialogVisible.value = true
}
</script>
```

---

### FE-016: AI对话页面路由

**目标**: 添加AI对话独立页面路由

**文件位置**: `frontend/src/router/index.ts`

**实现**:
```typescript
// 添加路由
{
  path: '/ai-chat',
  name: 'AIChat',
  component: () => import('@/views/ai/AIChat.vue'),
  meta: {
    title: 'AI投资顾问',
    requiresAuth: true
  }
}
```

**菜单集成**:
在`frontend/src/layouts/MainLayout.vue`中添加菜单项：
```vue
<el-menu-item index="/ai-chat">
  <el-icon><ChatDotRound /></el-icon>
  <span>AI顾问</span>
</el-menu-item>
```

---

## 🚨 风险和依赖

| 风险 | 级别 | 影响 | 应对措施 |
|------|------|------|---------|
| AI响应时间长（30秒） | 中 | 用户体验 | 添加Loading动画、进度提示 |
| 网络不稳定导致超时 | 中 | 功能失败 | 错误重试机制、友好错误提示 |
| ECharts集成复杂 | 低 | 开发困难 | 使用vue-echarts简化集成 |

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
- [ ] 通过UI自动化测试（QA-006）
- [ ] 代码符合前端架构规范

### 文档验收
- [ ] 前端组件文档完成
- [ ] API集成文档更新
- [ ] 用户使用手册更新

---

## 📝 开发指南

### 快速开始

1. **启动开发环境**
   ```bash
   ./scripts/dev.sh
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/sprint-002-ai-integration
   ```

3. **安装依赖（如需要）**
   ```bash
   cd frontend
   npm install vue-echarts echarts markdown-it
   ```

### 开发流程

1. **阅读相关文档**
   - [前端架构约束](../../frontend/ARCHITECTURE.md)
   - [AI API文档](../../docs/design/api/ai-api.md)
   - [后端AI验证报告](../../docs/AI-VERIFICATION-REPORT.md)

2. **查看已有代码**
   - `frontend/src/api/ai.ts` - AI API调用函数
   - `frontend/src/components/AIAnalysisResult.vue` - 分析结果组件框架
   - `frontend/src/components/AIChat.vue` - 对话组件框架

3. **开发组件**
   - 使用Composition API
   - TypeScript类型定义
   - 错误处理和Loading状态
   - Element Plus组件

4. **测试**
   ```bash
   npm run lint    # 代码检查
   npm run build   # 构建测试
   ```

5. **提交代码**
   ```bash
   git add .
   git commit -m "feat(ai): 完成AI分析结果展示组件"
   git push origin feature/sprint-002-ai-integration
   ```

### 代码规范

**组件文件结构**:
```vue
<template>
  <!-- HTML结构 -->
</template>

<script setup lang="ts">
// 导入
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAPI } from '@/api/module'

// 类型定义
interface Props {
  prop1: string
}

// Props
const props = defineProps<Props>()

// 响应式数据
const loading = ref(false)
const data = ref([])

// 方法
const fetchData = async () => {
  try {
    loading.value = true
    const result = await getAPI()
    data.value = result.data
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
// 样式
</style>
```

### 常见问题

**Q: ECharts图表不显示？**
A: 确保容器有明确的宽高，使用`v-loading`可能影响渲染

**Q: API调用超时？**
A: AI分析需要30秒，设置合理的timeout和Loading提示

**Q: Markdown渲染不生效？**
A: 使用markdown-it库，注意XSS防护

---

## 📚 参考资源

### 技术文档
- [Vue 3文档](https://vuejs.org/)
- [Element Plus文档](https://element-plus.org/)
- [ECharts文档](https://echarts.apache.org/)
- [vue-echarts文档](https://github.com/ecomfe/vue-echarts)
- [markdown-it文档](https://github.com/markdown-it/markdown-it)

### 项目文档
- [前端架构约束](../../frontend/ARCHITECTURE.md)
- [PRD v3.1](../../docs/prd/v3/main.md)
- [AI功能设计](../../docs/design/features/ai/)

### 示例代码
- Element Plus官方示例
- ECharts在线编辑器
- Vue 3 Composition API示例

---

**最后更新**: 2025-12-08
**Sprint状态**: ⏳ 待开始
**预计开始**: 2025-12-09
**预计完成**: 2025-12-15
