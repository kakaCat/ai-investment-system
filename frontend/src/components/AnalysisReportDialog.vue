<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Star, CopyDocument } from '@element-plus/icons-vue'

interface AnalysisReport {
  report_id: number
  report_type: 'single_stock' | 'portfolio' | 'strategy'
  title: string
  content: string // Markdown格式
  created_at: string
  token_used: number
  metadata?: {
    stock?: { symbol: string; name: string }
    accounts?: number[]
    [key: string]: any
  }
  is_favorite?: boolean
}

interface Props {
  visible: boolean
  report?: AnalysisReport
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  favorite: [reportId: number]
  export: [reportId: number, format: 'pdf' | 'md']
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// Mock markdown渲染（实际项目中应使用marked或markdown-it）
const renderedContent = computed(() => {
  if (!props.report) return ''

  // 简单的markdown渲染（仅用于演示）
  let html = props.report.content

  // 标题
  html = html.replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>')
  html = html.replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold mt-6 mb-3">$1</h2>')
  html = html.replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-8 mb-4">$1</h1>')

  // 粗体和斜体
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>')

  // 列表
  html = html.replace(/^\- (.*$)/gim, '<li class="ml-4">$1</li>')
  html = html.replace(/(<li.*<\/li>)/s, '<ul class="list-disc ml-4 my-2">$1</ul>')

  // 换行
  html = html.replace(/\n/g, '<br>')

  return html
})

// 报告类型标签
const reportTypeLabel = computed(() => {
  if (!props.report) return ''
  const labels = {
    single_stock: '单股分析',
    portfolio: '组合分析',
    strategy: '策略生成'
  }
  return labels[props.report.report_type]
})

// 收藏/取消收藏
const toggleFavorite = () => {
  if (!props.report) return
  emit('favorite', props.report.report_id)

  const action = props.report.is_favorite ? '已取消收藏' : '已收藏'
  ElMessage.success(action)
}

// 导出PDF
const exporting = ref(false)
const exportPDF = async () => {
  if (!props.report) return

  exporting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    emit('export', props.report.report_id, 'pdf')
    ElMessage.success('PDF导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 导出Markdown
const exportMarkdown = () => {
  if (!props.report) return
  emit('export', props.report.report_id, 'md')
  ElMessage.success('Markdown导出成功')
}

// 复制内容
const copyContent = async () => {
  if (!props.report) return

  try {
    await navigator.clipboard.writeText(props.report.content)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// Mock报告内容（如果没有提供）
const mockReport: AnalysisReport = {
  report_id: 1,
  report_type: 'single_stock',
  title: '贵州茅台 (600519) 投资分析报告',
  content: `# 贵州茅台 (600519) 投资分析报告

## 一、基本面分析

### 1.1 财务状况
贵州茅台作为白酒行业龙头，**财务状况极为稳健**。2024年三季报显示：
- 营业收入：1,234.56亿元，同比增长15.2%
- 净利润：567.89亿元，同比增长18.3%
- ROE：32.5%，处于行业领先水平
- 资产负债率：仅23.1%，现金流充沛

### 1.2 盈利能力
- 毛利率：91.2%（行业最高）
- 净利率：46.1%
- 每股收益：45.2元

## 二、技术面分析

### 2.1 趋势分析
- 当前价格：¥1,650.50
- 近期走势：震荡上行
- MA5/MA10形成金叉，技术面偏多

### 2.2 支撑与阻力
- 支撑位：¥1,600
- 阻力位：¥1,720

## 三、估值分析

### 3.1 估值指标
- PE（TTM）：35.2倍
- PB：12.8倍
- 相对行业估值：略高于平均水平

### 3.2 估值判断
当前估值处于合理区间，虽然PE较高，但考虑到公司的*品牌价值*和*盈利能力*，估值具有一定支撑。

## 四、投资建议

### 4.1 推荐评级
**买入持有**

### 4.2 理由
- 行业龙头地位稳固
- 品牌价值持续提升
- 财务状况优异
- 长期成长确定性高

### 4.3 风险提示
- 宏观经济波动风险
- 行业政策变化风险
- 市场竞争加剧风险

### 4.4 目标价位
- 6个月目标价：¥1,800
- 12个月目标价：¥2,000

## 五、总结

贵州茅台作为**白酒行业绝对龙头**，具有极强的护城河和定价权。建议长期价值投资者可逢低布局，短期波动不改长期向上趋势。

---
*本报告由AI生成，仅供参考，不构成投资建议*`,
  created_at: new Date().toISOString(),
  token_used: 3520,
  metadata: {
    stock: { symbol: '600519', name: '贵州茅台' }
  },
  is_favorite: false
}

const currentReport = computed(() => props.report || mockReport)
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="currentReport.title"
    width="900px"
    :close-on-click-modal="false"
    top="5vh"
  >
    <!-- 报告头部 -->
    <div class="mb-4 p-4 bg-gray-50 rounded">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-3">
          <el-tag :type="currentReport.report_type === 'single_stock' ? 'primary' : currentReport.report_type === 'portfolio' ? 'success' : 'warning'">
            {{ reportTypeLabel }}
          </el-tag>
          <span class="text-sm text-gray-600">
            生成时间: {{ new Date(currentReport.created_at).toLocaleString('zh-CN') }}
          </span>
        </div>
        <div class="flex items-center gap-2">
          <el-tag type="info" size="small">
            Token: {{ currentReport.token_used.toLocaleString() }}
          </el-tag>
          <el-button
            :icon="Star"
            :type="currentReport.is_favorite ? 'warning' : 'default'"
            size="small"
            @click="toggleFavorite"
          >
            {{ currentReport.is_favorite ? '已收藏' : '收藏' }}
          </el-button>
        </div>
      </div>

      <!-- 元数据 -->
      <div v-if="currentReport.metadata" class="flex items-center gap-4 text-sm text-gray-600">
        <div v-if="currentReport.metadata.stock">
          股票: {{ currentReport.metadata.stock.name }} ({{ currentReport.metadata.stock.symbol }})
        </div>
        <div v-if="currentReport.metadata.accounts">
          账户: {{ currentReport.metadata.accounts.length }} 个
        </div>
      </div>
    </div>

    <!-- 报告内容 -->
    <div class="report-content p-6 bg-white rounded border overflow-auto" style="max-height: 60vh">
      <!-- 使用v-html渲染Markdown（实际应使用专业的markdown渲染库） -->
      <div v-html="renderedContent" class="prose prose-sm max-w-none"></div>
    </div>

    <template #footer>
      <div class="flex justify-between">
        <div class="flex gap-2">
          <el-button :icon="CopyDocument" @click="copyContent">
            复制内容
          </el-button>
          <el-button @click="exportMarkdown">
            导出 Markdown
          </el-button>
        </div>
        <div class="flex gap-2">
          <el-button @click="dialogVisible = false">关闭</el-button>
          <el-button
            type="primary"
            :icon="Download"
            :loading="exporting"
            @click="exportPDF"
          >
            导出 PDF
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.report-content {
  line-height: 1.8;
}

.report-content :deep(h1) {
  @apply text-2xl font-bold mt-8 mb-4 pb-2 border-b;
}

.report-content :deep(h2) {
  @apply text-xl font-semibold mt-6 mb-3 text-gray-800;
}

.report-content :deep(h3) {
  @apply text-lg font-semibold mt-4 mb-2 text-gray-700;
}

.report-content :deep(strong) {
  @apply font-semibold text-gray-900;
}

.report-content :deep(em) {
  @apply italic text-gray-700;
}

.report-content :deep(ul) {
  @apply list-disc ml-6 my-3;
}

.report-content :deep(li) {
  @apply mb-1;
}

.report-content :deep(hr) {
  @apply my-6 border-gray-300;
}
</style>
