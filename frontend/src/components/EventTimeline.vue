<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Event, ImpactLevel } from '@/types/event'
import { EVENT_CATEGORY_LABELS, EVENT_SUBTYPE_LABELS, IMPACT_LEVEL_COLORS } from '@/types/event'

interface Props {
  events: Event[] // 事件列表
  loading?: boolean // 加载状态
  maxHeight?: string // 最大高度（超出滚动）
  showActions?: boolean // 是否显示操作按钮
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  maxHeight: '600px',
  showActions: true
})

const emit = defineEmits<{
  viewDetail: [event: Event] // 查看详情
}>()

const router = useRouter()

// 获取影响级别颜色
const getImpactColor = (level?: ImpactLevel) => {
  if (!level) return '#ccc'
  return IMPACT_LEVEL_COLORS[level]
}

// 查看详情
const viewDetail = (event: Event) => {
  if (props.showActions) {
    router.push({
      name: 'EventDetail',
      params: { id: event.event_id }
    })
  }
  emit('viewDetail', event)
}

// 获取时间线节点颜色（根据事件类别）
const getTimelineColor = (category: string) => {
  const colors: Record<string, string> = {
    policy: '#409eff',
    company: '#67c23a',
    market: '#e6a23c',
    industry: '#f56c6c'
  }
  return colors[category] || '#909399'
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}
</script>

<template>
  <div v-loading="loading" class="event-timeline">
    <div v-if="events.length === 0" class="py-8 text-center text-gray-400">
      <el-icon :size="48" class="mb-2"><Calendar /></el-icon>
      <div>暂无事件记录</div>
    </div>

    <div v-else :style="{ maxHeight: maxHeight }" class="overflow-y-auto">
      <el-timeline>
        <el-timeline-item
          v-for="event in events"
          :key="event.event_id"
          :timestamp="formatDate(event.event_date)"
          placement="top"
          :color="getTimelineColor(event.category)"
        >
          <div
            class="event-item cursor-pointer rounded-lg border bg-white p-4 transition-shadow hover:shadow-md"
            @click="viewDetail(event)"
          >
            <!-- 事件头部 -->
            <div class="mb-2 flex items-start justify-between">
              <div class="flex-1">
                <div class="mb-2 font-semibold text-gray-900">{{ event.title }}</div>
                <div class="flex flex-wrap items-center gap-2">
                  <el-tag size="small" :type="getCategoryType(event.category)">
                    {{ EVENT_CATEGORY_LABELS[event.category] }}
                  </el-tag>
                  <el-tag size="small">
                    {{ EVENT_SUBTYPE_LABELS[event.subtype] }}
                  </el-tag>
                </div>
              </div>

              <!-- AI影响评级 -->
              <div v-if="event.ai_impact" class="ml-4 text-right">
                <div class="text-xs text-gray-500">影响评级</div>
                <div
                  class="mt-1 font-bold"
                  :style="{ color: getImpactColor(event.ai_impact.short_term) }"
                >
                  {{ event.ai_impact.short_term }}/5
                </div>
              </div>
            </div>

            <!-- 事件描述 -->
            <div class="text-sm text-gray-600">{{ event.description }}</div>

            <!-- 关联股票 -->
            <div v-if="event.related_stocks?.length" class="mt-3 flex flex-wrap gap-2">
              <el-tag
                v-for="symbol in event.related_stocks"
                :key="symbol"
                size="small"
                effect="plain"
                @click.stop="viewStock(symbol)"
              >
                {{ symbol }}
              </el-tag>
            </div>

            <!-- 操作按钮 -->
            <div v-if="showActions" class="mt-3 flex gap-2">
              <el-button link size="small" type="primary" @click.stop="viewDetail(event)">
                查看详情
              </el-button>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  methods: {
    // 获取类别对应的Tag类型
    getCategoryType(category: string) {
      const types: Record<string, any> = {
        policy: 'primary',
        company: 'success',
        market: 'warning',
        industry: 'danger'
      }
      return types[category] || 'info'
    },
    // 查看股票（阻止冒泡）
    viewStock(symbol: string) {
      this.$router.push({
        name: 'StockDetail',
        params: { symbol }
      })
    }
  }
}
</script>

<style scoped>
.event-timeline {
  width: 100%;
}

.event-item {
  margin-left: -10px;
}

:deep(.el-timeline-item__timestamp) {
  font-weight: 500;
  color: #606266;
}
</style>
