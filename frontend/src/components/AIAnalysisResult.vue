<script setup lang="ts">
import { computed } from 'vue'
import { getScoreLevel, getConfidenceLevel } from '@/api/ai'
import type { SingleAnalysisResponse } from '@/api/ai'

interface Props {
  analysis: SingleAnalysisResponse | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

// 计算评分等级
const overallLevel = computed(() => {
  if (!props.analysis) return null
  return getScoreLevel(props.analysis.ai_score.overall_score)
})

const confidenceInfo = computed(() => {
  if (!props.analysis) return null
  return getConfidenceLevel(props.analysis.confidence_level)
})

// 维度评分
const dimensionScores = computed(() => {
  if (!props.analysis) return []

  const scores = []
  const aiScore = props.analysis.ai_score

  if (aiScore.fundamental_score !== undefined) {
    scores.push({
      name: '基本面',
      score: aiScore.fundamental_score,
      level: getScoreLevel(aiScore.fundamental_score)
    })
  }

  if (aiScore.technical_score !== undefined) {
    scores.push({
      name: '技术面',
      score: aiScore.technical_score,
      level: getScoreLevel(aiScore.technical_score)
    })
  }

  if (aiScore.valuation_score !== undefined) {
    scores.push({
      name: '估值',
      score: aiScore.valuation_score,
      level: getScoreLevel(aiScore.valuation_score)
    })
  }

  return scores
})

// 数据来源标签
const dataSourceLabel = computed(() => {
  if (!props.analysis?.data_source) return null

  const sourceMap: Record<string, { label: string; color: string }> = {
    tushare: { label: 'Tushare专业数据', color: 'success' },
    akshare: { label: 'AkShare数据', color: 'primary' },
    mock: { label: 'Mock数据', color: 'warning' }
  }

  return sourceMap[props.analysis.data_source] || { label: '未知来源', color: 'info' }
})

// 格式化时间
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}
</script>

<template>
  <div class="ai-analysis-result">
    <!-- Loading状态 -->
    <div v-if="loading" class="text-center py-12">
      <el-icon :size="40" class="is-loading text-blue-500">
        <Loading />
      </el-icon>
      <div class="mt-4 text-gray-600">AI正在分析中，预计需要30秒...</div>
      <div class="mt-2 text-sm text-gray-400">正在获取真实股票数据并进行深度分析</div>
    </div>

    <!-- 无数据 -->
    <div v-else-if="!analysis" class="text-center py-12 text-gray-400">
      <el-icon :size="40">
        <DocumentDelete />
      </el-icon>
      <div class="mt-4">暂无分析结果</div>
    </div>

    <!-- 分析结果 -->
    <div v-else class="space-y-4">
      <!-- 头部信息 -->
      <div class="flex items-center justify-between pb-4 border-b">
        <div>
          <h3 class="text-lg font-semibold">
            {{ analysis.stock_name }} ({{ analysis.symbol }})
          </h3>
          <div class="text-sm text-gray-500 mt-1">
            分析时间: {{ formatDate(analysis.created_at) }}
          </div>
        </div>
        <el-tag v-if="dataSourceLabel" :type="dataSourceLabel.color" size="small">
          {{ dataSourceLabel.label }}
        </el-tag>
      </div>

      <!-- 综合评分 -->
      <el-card shadow="never">
        <template #header>
          <div class="flex items-center justify-between">
            <span class="font-semibold">🎯 综合评分</span>
            <el-tag v-if="overallLevel" :type="overallLevel.color" size="small">
              {{ overallLevel.label }}
            </el-tag>
          </div>
        </template>

        <div class="text-center py-4">
          <div
            class="text-6xl font-bold mb-2"
            :style="{ color: overallLevel?.color || '#409EFF' }"
          >
            {{ analysis.ai_score.overall_score }}
          </div>
          <div class="text-gray-500">满分100分</div>

          <!-- 置信度 -->
          <div class="mt-4 flex items-center justify-center gap-2">
            <span class="text-sm text-gray-600">置信度:</span>
            <el-tag
              v-if="confidenceInfo"
              :type="confidenceInfo.color"
              size="small"
            >
              {{ analysis.confidence_level }}% ({{ confidenceInfo.label }})
            </el-tag>
          </div>
        </div>
      </el-card>

      <!-- 维度评分 -->
      <el-card v-if="dimensionScores.length > 0" shadow="never">
        <template #header>
          <span class="font-semibold">📊 分维度评分</span>
        </template>

        <div class="space-y-3">
          <div
            v-for="dim in dimensionScores"
            :key="dim.name"
            class="flex items-center gap-3"
          >
            <div class="w-20 text-sm font-medium">{{ dim.name }}</div>
            <el-progress
              :percentage="dim.score"
              :color="dim.level.color"
              :stroke-width="20"
              class="flex-1"
            >
              <span class="text-xs">{{ dim.score }}</span>
            </el-progress>
            <el-tag :type="dim.level.color" size="small">
              {{ dim.level.label }}
            </el-tag>
          </div>
        </div>
      </el-card>

      <!-- AI建议 -->
      <el-card shadow="never">
        <template #header>
          <span class="font-semibold">💡 AI投资建议</span>
        </template>

        <div class="whitespace-pre-wrap text-sm leading-relaxed">
          {{ analysis.ai_suggestion }}
        </div>
      </el-card>

      <!-- AI推理过程（如果有） -->
      <el-card v-if="analysis.ai_reasoning" shadow="never">
        <template #header>
          <div class="flex items-center justify-between">
            <span class="font-semibold">🤔 AI推理过程</span>
            <el-tag type="info" size="small">技术细节</el-tag>
          </div>
        </template>

        <div class="text-xs text-gray-600 whitespace-pre-wrap leading-relaxed bg-gray-50 p-3 rounded">
          {{ analysis.ai_reasoning }}
        </div>
      </el-card>

      <!-- 分析维度说明 -->
      <div class="text-xs text-gray-400 pt-2 border-t">
        <div>
          <span class="font-medium">分析维度:</span>
          {{ analysis.dimensions_analyzed.join(', ') }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-analysis-result {
  /* 自定义样式 */
}

/* Loading动画 */
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
