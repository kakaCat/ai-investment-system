<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  symbol: string
  stockName: string
}

const props = defineProps<Props>()

// 评价数据
const rating = ref(4)
const bullishReasons = ref<string[]>([
  '新能源汽车龙头，市占率35%稳居第一',
  '技术研发投入大，产品竞争力强',
  '垂直整合供应链，成本控制优秀'
])
const bearishReasons = ref<string[]>([
  '估值偏高，PE 45倍',
  '行业竞争加剧，价格战风险'
])
const holdingLogic = ref(`长期看好新能源汽车行业，比亚迪作为龙头企业具有核心竞争力：

1. **技术优势**：刀片电池技术领先，续航和安全性兼具
2. **市场地位**：国内市占率第一，品牌认可度高
3. **成本控制**：垂直整合供应链，降本增效明显
4. **政策支持**：新能源政策持续利好

风险点主要在估值较高，需要等待合适价位加仓。`)

const targetPrice = ref<number | null>(280)
const stopLossPrice = ref<number | null>(180)
const strategyNotes = ref('等待回调至220-230区间加仓，长期持有目标280')

// 新增输入框
const newBullishReason = ref('')
const newBearishReason = ref('')

// 操作日志
const reviewLogs = ref([
  {
    id: 1,
    date: '2025-11-15 14:30',
    type: 'rating_changed',
    description: '评分从 3星 调整为 4星',
    note: '看好公司长期发展'
  },
  {
    id: 2,
    date: '2025-11-10 09:20',
    type: 'target_price_updated',
    description: '目标价从 ¥260 调整为 ¥280',
    note: '上调盈利预期'
  },
  {
    id: 3,
    date: '2025-11-05 16:45',
    type: 'created',
    description: '创建股票评价',
    note: '初始评分 3星'
  }
])

// 星级评分
const setRating = (value: number) => {
  rating.value = value
  ElMessage.success(`已更新评分为 ${value} 星`)
}

// 添加看好原因
const addBullishReason = () => {
  const reason = newBullishReason.value.trim()
  if (!reason) {
    ElMessage.warning('请输入看好原因')
    return
  }
  bullishReasons.value.push(reason)
  newBullishReason.value = ''
  ElMessage.success('已添加看好原因')
}

// 删除看好原因
const removeBullishReason = (index: number) => {
  bullishReasons.value.splice(index, 1)
  ElMessage.success('已删除')
}

// 添加风险原因
const addBearishReason = () => {
  const reason = newBearishReason.value.trim()
  if (!reason) {
    ElMessage.warning('请输入风险原因')
    return
  }
  bearishReasons.value.push(reason)
  newBearishReason.value = ''
  ElMessage.success('已添加风险原因')
}

// 删除风险原因
const removeBearishReason = (index: number) => {
  bearishReasons.value.splice(index, 1)
  ElMessage.success('已删除')
}

// 保存评价
const saveReview = () => {
  // TODO: 调用API保存评价
  console.log('保存评价', {
    symbol: props.symbol,
    rating: rating.value,
    bullishReasons: bullishReasons.value,
    bearishReasons: bearishReasons.value,
    holdingLogic: holdingLogic.value,
    targetPrice: targetPrice.value,
    stopLossPrice: stopLossPrice.value,
    strategyNotes: strategyNotes.value
  })
  ElMessage.success('评价已保存')
}

// 获取日志类型标签
const getLogTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    created: '创建评价',
    rating_changed: '评分变更',
    bullish_reasons_updated: '看好原因更新',
    bearish_reasons_updated: '风险原因更新',
    holding_logic_updated: '持有逻辑更新',
    target_price_updated: '目标价更新',
    stop_loss_price_updated: '止损价更新'
  }
  return labels[type] || type
}

// 获取日志类型颜色
const getLogTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    created: 'blue',
    rating_changed: 'orange',
    bullish_reasons_updated: 'green',
    bearish_reasons_updated: 'red',
    holding_logic_updated: 'purple',
    target_price_updated: 'yellow',
    stop_loss_price_updated: 'red'
  }
  return colors[type] || 'gray'
}

onMounted(() => {
  // TODO: 加载用户评价数据
})
</script>

<template>
  <div class="stock-review">
    <!-- 评分区域 -->
    <div class="mb-8">
      <h3 class="text-lg font-semibold mb-4 flex items-center">
        <span class="mr-2">⭐</span>
        我的评分
      </h3>
      <div class="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-6 border border-yellow-200">
        <div class="flex items-center justify-center gap-3 mb-3">
          <button
            v-for="star in 5"
            :key="star"
            @click="setRating(star)"
            class="text-5xl transition-all hover:scale-110 cursor-pointer"
            :class="star <= rating ? 'text-yellow-400' : 'text-gray-300'"
          >
            ★
          </button>
        </div>
        <div class="text-center text-gray-600 text-sm">
          当前评分: <span class="font-bold text-lg text-yellow-600">{{ rating }} 星</span>
          <span class="ml-2 text-xs text-gray-500">(点击星星修改评分)</span>
        </div>
      </div>
    </div>

    <!-- 看好原因 -->
    <div class="mb-8">
      <h3 class="text-lg font-semibold mb-4 flex items-center">
        <span class="mr-2">✅</span>
        看好原因
      </h3>
      <div class="space-y-2 mb-3">
        <div
          v-for="(reason, index) in bullishReasons"
          :key="index"
          class="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg group hover:shadow-md transition-shadow"
        >
          <span class="text-green-600 mt-1">✓</span>
          <div class="flex-1">
            <div class="text-sm text-gray-900">{{ reason }}</div>
          </div>
          <button
            @click="removeBullishReason(index)"
            class="text-red-500 hover:text-red-700 text-xs opacity-0 group-hover:opacity-100 transition-opacity"
          >
            删除
          </button>
        </div>
      </div>
      <div class="flex gap-2">
        <input
          v-model="newBullishReason"
          type="text"
          placeholder="添加看好原因..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
          @keyup.enter="addBullishReason"
        />
        <button
          @click="addBullishReason"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          ➕ 添加
        </button>
      </div>
    </div>

    <!-- 风险/不看好原因 -->
    <div class="mb-8">
      <h3 class="text-lg font-semibold mb-4 flex items-center">
        <span class="mr-2">⚠️</span>
        风险 / 不看好原因
      </h3>
      <div class="space-y-2 mb-3">
        <div
          v-for="(reason, index) in bearishReasons"
          :key="index"
          class="flex items-start gap-3 p-3 bg-red-50 border border-red-200 rounded-lg group hover:shadow-md transition-shadow"
        >
          <span class="text-red-600 mt-1">✗</span>
          <div class="flex-1">
            <div class="text-sm text-gray-900">{{ reason }}</div>
          </div>
          <button
            @click="removeBearishReason(index)"
            class="text-red-500 hover:text-red-700 text-xs opacity-0 group-hover:opacity-100 transition-opacity"
          >
            删除
          </button>
        </div>
      </div>
      <div class="flex gap-2">
        <input
          v-model="newBearishReason"
          type="text"
          placeholder="添加风险原因..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
          @keyup.enter="addBearishReason"
        />
        <button
          @click="addBearishReason"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          ➕ 添加
        </button>
      </div>
    </div>

    <!-- 持有逻辑 -->
    <div class="mb-8">
      <h3 class="text-lg font-semibold mb-4 flex items-center">
        <span class="mr-2">📝</span>
        持有逻辑 / 投资理由
      </h3>
      <textarea
        v-model="holdingLogic"
        rows="8"
        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
        placeholder="记录你的投资逻辑、持有理由、长期看法等..."
      ></textarea>
      <div class="text-xs text-gray-500 mt-2">
        💡 提示：可以使用 Markdown 格式，支持加粗、列表等
      </div>
    </div>

    <!-- 目标价与止损价 -->
    <div class="mb-8">
      <h3 class="text-lg font-semibold mb-4 flex items-center">
        <span class="mr-2">🎯</span>
        目标价与止损价
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
          <label class="block text-sm font-semibold text-green-800 mb-2">
            🎯 目标价 (元)
          </label>
          <input
            v-model.number="targetPrice"
            type="number"
            step="0.01"
            class="w-full px-4 py-2 border border-green-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="例如: 280.00"
          />
        </div>
        <div class="p-4 bg-red-50 border border-red-200 rounded-lg">
          <label class="block text-sm font-semibold text-red-800 mb-2">
            🛑 止损价 (元)
          </label>
          <input
            v-model.number="stopLossPrice"
            type="number"
            step="0.01"
            class="w-full px-4 py-2 border border-red-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
            placeholder="例如: 180.00"
          />
        </div>
      </div>
    </div>

    <!-- 操作策略备注 -->
    <div class="mb-8">
      <h3 class="text-lg font-semibold mb-4 flex items-center">
        <span class="mr-2">📋</span>
        操作策略备注
      </h3>
      <textarea
        v-model="strategyNotes"
        rows="3"
        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="记录你的操作计划、加仓减仓策略等..."
      ></textarea>
    </div>

    <!-- 操作日志 -->
    <div class="mb-8">
      <h3 class="text-lg font-semibold mb-4 flex items-center">
        <span class="mr-2">📜</span>
        操作日志
      </h3>
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="space-y-3">
          <div
            v-for="log in reviewLogs"
            :key="log.id"
            class="flex items-start gap-3 pb-3 border-b border-gray-200 last:border-b-0"
          >
            <div class="flex-shrink-0 mt-1">
              <el-tag :type="getLogTypeColor(log.type)" size="small">
                {{ getLogTypeLabel(log.type) }}
              </el-tag>
            </div>
            <div class="flex-1">
              <div class="text-sm text-gray-900 font-medium">{{ log.description }}</div>
              <div v-if="log.note" class="text-xs text-gray-500 mt-1">{{ log.note }}</div>
              <div class="text-xs text-gray-400 mt-1">{{ log.date }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
      <button
        @click="saveReview"
        class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
      >
        💾 保存评价
      </button>
    </div>
  </div>
</template>

<style scoped>
.stock-review {
  /* 可以添加自定义样式 */
}
</style>
