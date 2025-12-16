<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { BatchAnalysisItem } from '@/api/ai'

interface Props {
  modelValue: boolean
  results: BatchAnalysisItem[]
  progress: {
    completed: number
    total: number
    percentage: number
  }
  isAnalyzing?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'view-detail', item: BatchAnalysisItem): void
  (e: 'retry', symbol: string): void
}

const props = withDefaults(defineProps<Props>(), {
  isAnalyzing: false
})

const emit = defineEmits<Emits>()

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const sortedResults = computed(() => {
  return [...props.results].sort((a, b) => {
    // 优先显示失败的
    if (a.status === 'failed' && b.status !== 'failed') return -1
    if (a.status !== 'failed' && b.status === 'failed') return 1

    // 其次按评分降序
    const scoreA = a.ai_score?.overall_score || 0
    const scoreB = b.ai_score?.overall_score || 0
    return scoreB - scoreA
  })
})

// 统计信息
const stats = computed(() => {
  const completed = props.results.filter(r => r.status === 'completed').length
  const failed = props.results.filter(r => r.status === 'failed').length
  const analyzing = props.results.filter(r => r.status === 'analyzing').length

  return { completed, failed, analyzing }
})

// 获取状态标签类型
const getStatusType = (status: string): 'success' | 'danger' | 'warning' | 'info' => {
  const typeMap: Record<string, 'success' | 'danger' | 'warning' | 'info'> = {
    completed: 'success',
    failed: 'danger',
    analyzing: 'info'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string): string => {
  const textMap: Record<string, string> = {
    completed: '已完成',
    failed: '失败',
    analyzing: '分析中'
  }
  return textMap[status] || status
}

// 获取评分颜色
const getScoreColor = (score: number): string => {
  if (score >= 80) return '#67C23A'
  if (score >= 60) return '#409EFF'
  if (score >= 40) return '#E6A23C'
  return '#F56C6C'
}

// 查看详情
const viewDetail = (item: BatchAnalysisItem) => {
  if (item.status === 'completed') {
    emit('view-detail', item)
  }
}

// 重试失败项
const retryItem = (symbol: string) => {
  emit('retry', symbol)
}

// 导出结果
const exportResults = () => {
  const completedResults = props.results.filter(r => r.status === 'completed')
  if (completedResults.length === 0) {
    ElMessage.warning('暂无可导出的结果')
    return
  }

  const csv = [
    ['股票代码', '股票名称', '综合评分', 'AI建议', '置信度', '状态'].join(','),
    ...completedResults.map(r => [
      r.symbol,
      r.stock_name,
      r.ai_score?.overall_score || 0,
      `"${r.ai_suggestion.replace(/"/g, '""')}"`,
      r.confidence_level,
      getStatusText(r.status)
    ].join(','))
  ].join('\n')

  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `batch-analysis-${new Date().toISOString().slice(0, 10)}.csv`
  link.click()

  ElMessage.success('导出成功')
}
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="📊 批量分析进度"
    width="900px"
    :close-on-click-modal="false"
  >
    <div class="batch-analysis-progress">
      <!-- 进度统计 -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-3">
          <div class="text-sm text-gray-600">
            分析进度: {{ progress.completed }} / {{ progress.total }}
          </div>
          <div class="text-lg font-semibold" :class="isAnalyzing ? 'text-blue-600' : 'text-green-600'">
            {{ progress.percentage }}%
          </div>
        </div>

        <el-progress
          :percentage="progress.percentage"
          :status="isAnalyzing ? undefined : 'success'"
          :stroke-width="24"
        >
          <span class="text-xs">{{ progress.completed }}/{{ progress.total }}</span>
        </el-progress>

        <!-- 统计卡片 -->
        <div class="grid grid-cols-3 gap-3 mt-4">
          <div class="bg-green-50 border border-green-200 rounded-lg p-3">
            <div class="text-xs text-green-600 mb-1">已完成</div>
            <div class="text-2xl font-bold text-green-700">{{ stats.completed }}</div>
          </div>
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div class="text-xs text-blue-600 mb-1">分析中</div>
            <div class="text-2xl font-bold text-blue-700">{{ stats.analyzing }}</div>
          </div>
          <div class="bg-red-50 border border-red-200 rounded-lg p-3">
            <div class="text-xs text-red-600 mb-1">失败</div>
            <div class="text-2xl font-bold text-red-700">{{ stats.failed }}</div>
          </div>
        </div>
      </div>

      <!-- 结果列表 -->
      <div class="results-section">
        <div class="flex items-center justify-between mb-3">
          <h4 class="font-semibold">分析结果</h4>
          <el-button
            size="small"
            :disabled="stats.completed === 0"
            @click="exportResults"
          >
            导出CSV
          </el-button>
        </div>

        <div v-if="sortedResults.length === 0" class="text-center py-12 text-gray-400">
          暂无分析结果
        </div>

        <div v-else class="space-y-2 max-h-96 overflow-y-auto">
          <div
            v-for="item in sortedResults"
            :key="item.symbol"
            class="result-item border rounded-lg p-4 hover:shadow-md transition-shadow"
            :class="{
              'bg-white': item.status === 'completed',
              'bg-gray-50': item.status === 'analyzing',
              'bg-red-50 border-red-200': item.status === 'failed',
              'cursor-pointer': item.status === 'completed'
            }"
            @click="viewDetail(item)"
          >
            <div class="flex items-center justify-between">
              <!-- 左侧信息 -->
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <div class="font-semibold text-lg">
                    {{ item.stock_name }}
                  </div>
                  <div class="text-sm text-gray-500">
                    {{ item.symbol }}
                  </div>
                  <el-tag :type="getStatusType(item.status)" size="small">
                    {{ getStatusText(item.status) }}
                  </el-tag>
                </div>

                <!-- 已完成：显示评分和建议 -->
                <div v-if="item.status === 'completed'" class="space-y-1">
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-gray-600">综合评分:</span>
                    <div
                      class="text-lg font-bold"
                      :style="{ color: getScoreColor(item.ai_score.overall_score) }"
                    >
                      {{ item.ai_score.overall_score }}
                    </div>
                    <span class="text-xs text-gray-500">/100</span>

                    <span class="text-xs text-gray-600 ml-4">置信度:</span>
                    <span class="text-sm font-semibold">{{ item.confidence_level }}%</span>
                  </div>

                  <div class="text-sm text-gray-700 line-clamp-2">
                    {{ item.ai_suggestion }}
                  </div>
                </div>

                <!-- 分析中 -->
                <div v-else-if="item.status === 'analyzing'" class="text-sm text-blue-600">
                  <el-icon class="is-loading mr-1">
                    <Loading />
                  </el-icon>
                  正在分析中...
                </div>

                <!-- 失败 -->
                <div v-else-if="item.status === 'failed'" class="text-sm">
                  <div class="text-red-600 mb-2">
                    {{ item.error || '分析失败，请重试' }}
                  </div>
                  <el-button
                    size="small"
                    type="danger"
                    plain
                    @click.stop="retryItem(item.symbol)"
                  >
                    重试
                  </el-button>
                </div>
              </div>

              <!-- 右侧操作 -->
              <div v-if="item.status === 'completed'" class="ml-4">
                <el-icon :size="20" class="text-gray-400">
                  <ArrowRight />
                </el-icon>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部提示 -->
      <div v-if="isAnalyzing" class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
        <el-icon class="mr-1">
          <InfoFilled />
        </el-icon>
        分析进行中，请稍候。每只股票大约需要3-5秒。
      </div>
    </div>

    <template #footer>
      <el-button @click="dialogVisible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.result-item {
  transition: all 0.3s;
}

.result-item:hover {
  transform: translateX(4px);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
