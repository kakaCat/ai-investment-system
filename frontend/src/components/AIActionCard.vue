<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

interface AIAction {
  priority: 'urgent' | 'today' | 'week'
  stock: {
    symbol: string
    name: string
  }
  action: 'buy' | 'sell' | 'hold' | 'watch'
  current_price: number
  holding?: {
    quantity: number
    profit_loss_rate: number
  }
  reason: string
  suggestion: string
  target_price?: number
  confidence: number
}

const props = defineProps<{
  action: AIAction
}>()

const router = useRouter()

// 操作类型映射
const actionConfig = computed(() => {
  const configs = {
    buy: { label: '买入建仓', color: 'text-red-600 bg-red-50', icon: '📈' },
    sell: { label: '卖出减仓', color: 'text-green-600 bg-green-50', icon: '📉' },
    hold: { label: '持有观望', color: 'text-blue-600 bg-blue-50', icon: '💎' },
    watch: { label: '关注等待', color: 'text-yellow-600 bg-yellow-50', icon: '👀' }
  }
  return configs[props.action.action]
})

// 查看股票详情
const viewStock = () => {
  router.push(`/stocks/detail/${props.action.stock.symbol}`)
}

// 记录交易
const recordTrade = () => {
  // 跳转到交易记录页并带上股票信息
  router.push({
    path: '/trades/list',
    query: {
      symbol: props.action.stock.symbol,
      action: props.action.action
    }
  })
}

// 稍后提醒
const setReminder = () => {
  // TODO: 实现提醒功能
  console.log('设置提醒')
}
</script>

<template>
  <div class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all bg-white">
    <!-- 头部：股票信息 + 操作类型 -->
    <div class="flex items-start justify-between mb-3">
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-1">
          <span class="text-lg font-bold text-gray-900">
            {{ action.stock.name }}
          </span>
          <span class="text-sm text-gray-500">({{ action.stock.symbol }})</span>
          <span :class="['px-2 py-1 text-xs font-semibold rounded', actionConfig.color]">
            {{ actionConfig.icon }} {{ actionConfig.label }}
          </span>
        </div>

        <!-- 持仓信息（如果有） -->
        <div class="flex items-center gap-4 text-sm">
          <span class="text-gray-600">
            当前价: <span class="font-semibold text-gray-900">¥{{ action.current_price.toFixed(2) }}</span>
          </span>
          <span v-if="action.holding" class="text-gray-600">
            持仓: {{ action.holding.quantity }}股
          </span>
          <span
            v-if="action.holding"
            :class="action.holding.profit_loss_rate >= 0 ? 'text-red-600' : 'text-green-600'"
            class="font-semibold"
          >
            {{ action.holding.profit_loss_rate >= 0 ? '+' : '' }}{{ action.holding.profit_loss_rate.toFixed(2) }}%
          </span>
        </div>
      </div>

      <!-- 置信度 -->
      <div class="text-right">
        <div class="text-xs text-gray-500 mb-1">AI置信度</div>
        <div class="text-lg font-bold text-blue-600">{{ action.confidence }}%</div>
      </div>
    </div>

    <!-- 原因 -->
    <div class="mb-2">
      <span class="text-xs font-semibold text-gray-700">• 原因: </span>
      <span class="text-sm text-gray-600">{{ action.reason }}</span>
    </div>

    <!-- 建议 -->
    <div class="mb-2">
      <span class="text-xs font-semibold text-gray-700">• 建议: </span>
      <span class="text-sm text-gray-800">{{ action.suggestion }}</span>
    </div>

    <!-- 目标价 -->
    <div v-if="action.target_price" class="mb-3">
      <span class="text-xs font-semibold text-gray-700">• 目标价: </span>
      <span class="text-sm font-semibold text-blue-600">¥{{ action.target_price.toFixed(2) }}</span>
      <span class="text-xs text-gray-500 ml-2">
        {{ action.action === 'buy' || action.action === 'watch' ? '等待回调至此价位' : '建议止盈价位' }}
      </span>
    </div>

    <!-- 操作按钮 -->
    <div class="flex gap-2 pt-3 border-t border-gray-100">
      <button
        v-if="action.action === 'sell' || action.action === 'buy'"
        class="flex-1 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition"
        @click="recordTrade"
      >
        {{ action.action === 'buy' ? '立即记录买入' : '立即记录卖出' }}
      </button>
      <button
        class="flex-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
        @click="viewStock"
      >
        查看详情
      </button>
      <button
        class="px-3 py-2 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        @click="setReminder"
      >
        稍后提醒
      </button>
    </div>
  </div>
</template>
