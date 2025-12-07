<script setup lang="ts">
import { computed } from 'vue'
import AIActionCard from './AIActionCard.vue'

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
  actions: AIAction[]
}>()

// 按优先级分组
const groupedActions = computed(() => {
  return {
    urgent: props.actions.filter(a => a.priority === 'urgent'),
    today: props.actions.filter(a => a.priority === 'today'),
    week: props.actions.filter(a => a.priority === 'week')
  }
})

// 本周关注文字
const weekSummary = computed(() => {
  const weekActions = groupedActions.value.week
  if (weekActions.length === 0) return []

  return weekActions.map(action => {
    let text = ''
    if (action.action === 'hold') {
      text = `保持${action.stock.name}持仓，${action.reason}`
    } else if (action.action === 'watch') {
      text = `关注${action.stock.name}，${action.reason}`
    }
    return text
  }).filter(t => t)
})
</script>

<template>
  <div class="space-y-6">
    <!-- 紧急操作 -->
    <div v-if="groupedActions.urgent.length > 0">
      <div class="flex items-center gap-2 mb-3">
        <span class="text-2xl">🔴</span>
        <h3 class="text-lg font-bold text-gray-900">紧急操作</h3>
        <span class="text-sm text-gray-500">（建议今日执行）</span>
      </div>
      <div class="space-y-3">
        <ai-action-card
          v-for="(action, index) in groupedActions.urgent"
          :key="`urgent-${index}`"
          :action="action"
        />
      </div>
    </div>

    <!-- 今日建议 -->
    <div v-if="groupedActions.today.length > 0">
      <div class="flex items-center gap-2 mb-3">
        <span class="text-2xl">🟡</span>
        <h3 class="text-lg font-bold text-gray-900">今日建议</h3>
        <span class="text-sm text-gray-500">（关注并择机操作）</span>
      </div>
      <div class="space-y-3">
        <ai-action-card
          v-for="(action, index) in groupedActions.today"
          :key="`today-${index}`"
          :action="action"
        />
      </div>
    </div>

    <!-- 本周关注 -->
    <div v-if="weekSummary.length > 0">
      <div class="flex items-center gap-2 mb-3">
        <span class="text-2xl">🟢</span>
        <h3 class="text-lg font-bold text-gray-900">本周关注</h3>
        <span class="text-sm text-gray-500">（中长期策略）</span>
      </div>
      <div class="bg-green-50 border border-green-200 rounded-lg p-4">
        <ul class="space-y-2">
          <li v-for="(summary, index) in weekSummary" :key="`week-${index}`" class="flex items-start gap-2">
            <span class="text-green-600 mt-0.5">•</span>
            <span class="text-sm text-gray-700">{{ summary }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="actions.length === 0" class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
      <div class="text-5xl mb-3">🤖</div>
      <div class="text-gray-600 mb-2">暂无AI操作建议</div>
      <div class="text-sm text-gray-500">系统会根据市场变化和持仓情况自动生成建议</div>
    </div>
  </div>
</template>
