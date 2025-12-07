<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Stock } from '@/types/stock'

interface Props {
  stock: Stock
  mode?: 'card' | 'compact' // 显示模式：卡片模式或紧凑模式
  showActions?: boolean // 是否显示操作按钮
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'card',
  showActions: true
})

const emit = defineEmits<{
  watch: [stock: Stock] // 添加到关注
  analyze: [stock: Stock] // AI分析
  trade: [stock: Stock] // 记录交易
}>()

const router = useRouter()

// 涨跌状态
const priceStatus = computed(() => {
  if (props.stock.change_rate > 0) return 'up'
  if (props.stock.change_rate < 0) return 'down'
  return 'neutral'
})

// 涨跌颜色类
const priceClass = computed(() => {
  return {
    up: 'text-red-600',
    down: 'text-green-600',
    neutral: 'text-gray-600'
  }[priceStatus.value]
})

// 背景颜色类
const bgClass = computed(() => {
  return {
    up: 'bg-red-50',
    down: 'bg-green-50',
    neutral: 'bg-gray-50'
  }[priceStatus.value]
})

// 查看详情
const viewDetail = () => {
  router.push({
    name: 'StockDetail',
    params: { symbol: props.stock.symbol }
  })
}

// 添加到关注
const handleWatch = () => {
  emit('watch', props.stock)
}

// AI分析
const handleAnalyze = () => {
  emit('analyze', props.stock)
}

// 记录交易
const handleTrade = () => {
  emit('trade', props.stock)
}
</script>

<template>
  <!-- 卡片模式 -->
  <div
    v-if="mode === 'card'"
    class="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
    :class="bgClass"
    @click="viewDetail"
  >
    <!-- 头部：股票代码和名称 -->
    <div class="flex items-start justify-between mb-3">
      <div>
        <div class="text-lg font-bold text-gray-900">{{ stock.name }}</div>
        <div class="text-sm text-gray-500">{{ stock.symbol }}</div>
      </div>
      <div class="text-xs px-2 py-1 bg-white rounded-md border">
        {{ stock.market }}
      </div>
    </div>

    <!-- 价格信息 -->
    <div class="mb-3">
      <div class="text-2xl font-bold" :class="priceClass">
        ¥{{ stock.current_price.toFixed(2) }}
      </div>
      <div class="text-sm mt-1" :class="priceClass">
        {{ stock.change_amount >= 0 ? '+' : '' }}{{ stock.change_amount.toFixed(2) }}
        <span class="ml-2">
          {{ stock.change_rate >= 0 ? '+' : '' }}{{ stock.change_rate.toFixed(2) }}%
        </span>
      </div>
    </div>

    <!-- 其他信息 -->
    <div v-if="stock.volume || stock.market_cap" class="text-xs text-gray-600 space-y-1">
      <div v-if="stock.volume">成交量: {{ stock.volume.toLocaleString() }}</div>
      <div v-if="stock.market_cap">
        市值: {{ (stock.market_cap / 100000000).toFixed(2) }}亿
      </div>
    </div>

    <!-- 操作按钮 -->
    <div v-if="showActions" class="mt-4 flex gap-2" @click.stop>
      <el-button size="small" @click="handleWatch">
        <el-icon><Star /></el-icon>
        关注
      </el-button>
      <el-button size="small" @click="handleAnalyze">
        <el-icon><TrendCharts /></el-icon>
        分析
      </el-button>
      <el-button size="small" @click="handleTrade">
        <el-icon><Sell /></el-icon>
        交易
      </el-button>
    </div>
  </div>

  <!-- 紧凑模式 -->
  <div
    v-else
    class="flex items-center justify-between p-3 border-b hover:bg-gray-50 cursor-pointer"
    @click="viewDetail"
  >
    <!-- 左侧：股票信息 -->
    <div class="flex-1">
      <div class="flex items-center gap-2">
        <span class="font-semibold text-gray-900">{{ stock.name }}</span>
        <span class="text-sm text-gray-500">{{ stock.symbol }}</span>
        <span class="text-xs px-1.5 py-0.5 bg-gray-100 rounded">{{ stock.market }}</span>
      </div>
    </div>

    <!-- 中间：价格 -->
    <div class="text-right mr-6">
      <div class="font-semibold" :class="priceClass">
        ¥{{ stock.current_price.toFixed(2) }}
      </div>
    </div>

    <!-- 右侧：涨跌幅 -->
    <div class="text-right min-w-[100px]">
      <div class="text-sm font-medium" :class="priceClass">
        {{ stock.change_amount >= 0 ? '+' : '' }}{{ stock.change_amount.toFixed(2) }}
      </div>
      <div class="text-xs" :class="priceClass">
        {{ stock.change_rate >= 0 ? '+' : '' }}{{ stock.change_rate.toFixed(2) }}%
      </div>
    </div>

    <!-- 操作按钮（紧凑模式） -->
    <div v-if="showActions" class="ml-4 flex gap-1" @click.stop>
      <el-button link size="small" @click="handleWatch">关注</el-button>
      <el-button link size="small" @click="handleAnalyze">分析</el-button>
    </div>
  </div>
</template>

<style scoped>
.profit-text {
  @apply text-red-600;
}

.loss-text {
  @apply text-green-600;
}
</style>
