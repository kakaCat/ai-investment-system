<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type {
  EventDetail,
  Event,
  ImpactLevel
} from '@/types/event'
import {
  EVENT_CATEGORY_LABELS,
  EVENT_SUBTYPE_LABELS,
  IMPACT_LEVEL_LABELS,
  IMPACT_LEVEL_COLORS
} from '@/types/event'

const route = useRoute()
const router = useRouter()

const eventId = computed(() => route.params.id as string)
const loading = ref(false)
const eventDetail = ref<EventDetail | null>(null)
const userNotes = ref('')
const isEditingNotes = ref(false)

// 获取事件详情
const fetchEventDetail = async () => {
  loading.value = true
  try {
    // Mock 数据
    await new Promise(resolve => setTimeout(resolve, 500))

    eventDetail.value = {
      event_id: parseInt(eventId.value),
      title: '央行宣布降准0.5个百分点',
      category: 'policy',
      subtype: 'monetary_policy',
      description: '中国人民银行宣布全面降准0.5个百分点，释放长期流动性约1万亿元',
      event_date: '2025-01-15',
      created_at: '2025-01-15T10:00:00Z',
      source_url: 'https://www.example.com/news/123',
      content: `
# 央行宣布降准0.5个百分点

中国人民银行1月15日宣布，决定于2025年1月20日下调金融机构存款准备金率0.5个百分点（不含已执行5%存款准备金率的金融机构）。

## 政策背景

本次降准是为了保持银行体系流动性合理充裕，引导金融机构加大对实体经济的支持力度。

## 预计影响

- 释放长期流动性约1万亿元
- 降低银行资金成本约150亿元/年
- 有利于支持实体经济发展

## 市场反应

消息公布后，A股三大指数集体上涨，银行、地产板块领涨。
      `,
      timeline: [
        {
          date: '2025-01-15 10:00',
          title: '央行发布公告',
          description: '中国人民银行官网发布降准公告'
        },
        {
          date: '2025-01-15 10:30',
          title: '市场反应',
          description: 'A股三大指数快速拉升，银行板块涨幅超过3%'
        },
        {
          date: '2025-01-15 14:00',
          title: '专家解读',
          description: '多位经济学家发表评论，认为此次降准有利于稳增长'
        },
        {
          date: '2025-01-15 16:00',
          title: '收盘总结',
          description: '沪指涨1.8%，创业板涨2.3%，两市成交额突破万亿'
        }
      ],
      ai_impact: {
        short_term: 4,
        mid_term: 3,
        long_term: 2,
        confidence: 0.85,
        reasoning:
          '短期内对市场情绪有显著提振作用，银行、地产等资金敏感行业受益明显。中期来看，流动性改善有助于支持经济复苏。长期影响相对有限，需配合其他政策措施。'
      },
      related_stocks: ['600036', '000001', '601398'],
      related_events: [
        {
          event_id: 2,
          title: '上次降准（2024年9月）',
          category: 'policy',
          subtype: 'monetary_policy',
          description: '央行上一次降准0.25个百分点',
          event_date: '2024-09-15',
          created_at: '2024-09-15T10:00:00Z'
        }
      ],
      user_notes: userNotes.value
    }

    userNotes.value = eventDetail.value.user_notes || ''
  } catch (error) {
    ElMessage.error('获取事件详情失败')
  } finally {
    loading.value = false
  }
}

// 保存备注
const saveNotes = () => {
  ElMessage.success('备注已保存')
  isEditingNotes.value = false
  if (eventDetail.value) {
    eventDetail.value.user_notes = userNotes.value
  }
}

// 查看股票详情
const viewStock = (symbol: string) => {
  router.push({
    name: 'StockDetail',
    params: { symbol }
  })
}

// 查看相关事件
const viewEvent = (eventId: number) => {
  router.push({
    name: 'EventDetail',
    params: { id: eventId }
  })
}

// 返回
const goBack = () => {
  router.back()
}

// 获取影响级别颜色
const getImpactColor = (level: ImpactLevel) => {
  return IMPACT_LEVEL_COLORS[level]
}

// 格式化置信度
const formatConfidence = (confidence: number) => {
  return (confidence * 100).toFixed(0) + '%'
}

onMounted(() => {
  fetchEventDetail()
})
</script>

<template>
  <div v-loading="loading" class="event-detail p-6">
    <!-- 顶部导航 -->
    <div class="mb-6">
      <el-button @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>

    <div v-if="eventDetail" class="grid grid-cols-3 gap-6">
      <!-- 左侧主要内容 -->
      <div class="col-span-2 space-y-6">
        <!-- 事件基本信息 -->
        <div class="rounded-lg border bg-white p-6">
          <div class="mb-4 flex items-start justify-between">
            <div class="flex-1">
              <h1 class="mb-3 text-2xl font-bold">{{ eventDetail.title }}</h1>
              <div class="flex items-center gap-3 text-sm text-gray-600">
                <el-tag type="primary">{{ EVENT_CATEGORY_LABELS[eventDetail.category] }}</el-tag>
                <el-tag>{{ EVENT_SUBTYPE_LABELS[eventDetail.subtype] }}</el-tag>
                <span>{{ eventDetail.event_date }}</span>
              </div>
            </div>
          </div>

          <div class="mb-4 text-gray-700">
            {{ eventDetail.description }}
          </div>

          <div v-if="eventDetail.source_url" class="text-sm">
            <a
              :href="eventDetail.source_url"
              target="_blank"
              class="text-blue-600 hover:text-blue-800"
            >
              <el-icon><Link /></el-icon>
              查看新闻来源
            </a>
          </div>
        </div>

        <!-- 事件详细内容 -->
        <div class="rounded-lg border bg-white p-6">
          <h2 class="mb-4 text-lg font-semibold">事件详情</h2>
          <div class="prose max-w-none whitespace-pre-wrap text-gray-700">
            {{ eventDetail.content }}
          </div>
        </div>

        <!-- 事件时间线 -->
        <div class="rounded-lg border bg-white p-6">
          <h2 class="mb-4 text-lg font-semibold">事件时间线</h2>
          <el-timeline>
            <el-timeline-item
              v-for="(item, index) in eventDetail.timeline"
              :key="index"
              :timestamp="item.date"
              placement="top"
            >
              <div class="font-semibold">{{ item.title }}</div>
              <div class="mt-1 text-sm text-gray-600">{{ item.description }}</div>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- 相关事件 -->
        <div v-if="eventDetail.related_events?.length" class="rounded-lg border bg-white p-6">
          <h2 class="mb-4 text-lg font-semibold">相关事件</h2>
          <div class="space-y-3">
            <div
              v-for="event in eventDetail.related_events"
              :key="event.event_id"
              class="cursor-pointer rounded-lg border p-4 transition-shadow hover:shadow-md"
              @click="viewEvent(event.event_id)"
            >
              <div class="mb-2 flex items-center gap-2">
                <el-tag size="small" type="info">
                  {{ EVENT_CATEGORY_LABELS[event.category] }}
                </el-tag>
                <span class="text-sm text-gray-500">{{ event.event_date }}</span>
              </div>
              <div class="font-semibold">{{ event.title }}</div>
              <div class="mt-1 text-sm text-gray-600">{{ event.description }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧边栏 -->
      <div class="space-y-6">
        <!-- AI影响评估 -->
        <div v-if="eventDetail.ai_impact" class="rounded-lg border bg-white p-6">
          <h2 class="mb-4 text-lg font-semibold">AI影响评估</h2>

          <div class="mb-4 space-y-3">
            <div>
              <div class="mb-1 flex items-center justify-between text-sm">
                <span class="text-gray-600">短期影响 (1-3月)</span>
                <span class="font-semibold">
                  {{ IMPACT_LEVEL_LABELS[eventDetail.ai_impact.short_term] }}
                </span>
              </div>
              <el-progress
                :percentage="eventDetail.ai_impact.short_term * 20"
                :color="getImpactColor(eventDetail.ai_impact.short_term)"
                :show-text="false"
              />
            </div>

            <div>
              <div class="mb-1 flex items-center justify-between text-sm">
                <span class="text-gray-600">中期影响 (3-12月)</span>
                <span class="font-semibold">
                  {{ IMPACT_LEVEL_LABELS[eventDetail.ai_impact.mid_term] }}
                </span>
              </div>
              <el-progress
                :percentage="eventDetail.ai_impact.mid_term * 20"
                :color="getImpactColor(eventDetail.ai_impact.mid_term)"
                :show-text="false"
              />
            </div>

            <div>
              <div class="mb-1 flex items-center justify-between text-sm">
                <span class="text-gray-600">长期影响 (>12月)</span>
                <span class="font-semibold">
                  {{ IMPACT_LEVEL_LABELS[eventDetail.ai_impact.long_term] }}
                </span>
              </div>
              <el-progress
                :percentage="eventDetail.ai_impact.long_term * 20"
                :color="getImpactColor(eventDetail.ai_impact.long_term)"
                :show-text="false"
              />
            </div>
          </div>

          <div class="mb-4 border-t pt-4">
            <div class="mb-1 text-sm text-gray-600">置信度</div>
            <div class="text-2xl font-bold text-blue-600">
              {{ formatConfidence(eventDetail.ai_impact.confidence) }}
            </div>
          </div>

          <div v-if="eventDetail.ai_impact.reasoning" class="border-t pt-4">
            <div class="mb-2 text-sm font-semibold">分析理由</div>
            <div class="text-sm text-gray-600">
              {{ eventDetail.ai_impact.reasoning }}
            </div>
          </div>
        </div>

        <!-- 关联股票 -->
        <div v-if="eventDetail.related_stocks?.length" class="rounded-lg border bg-white p-6">
          <h2 class="mb-4 text-lg font-semibold">关联股票</h2>
          <div class="space-y-2">
            <div
              v-for="symbol in eventDetail.related_stocks"
              :key="symbol"
              class="cursor-pointer rounded-lg border p-3 transition-shadow hover:shadow-md"
              @click="viewStock(symbol)"
            >
              <div class="font-semibold">{{ symbol }}</div>
            </div>
          </div>
        </div>

        <!-- 用户备注 -->
        <div class="rounded-lg border bg-white p-6">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-semibold">我的备注</h2>
            <el-button
              v-if="!isEditingNotes"
              link
              type="primary"
              @click="isEditingNotes = true"
            >
              编辑
            </el-button>
          </div>

          <div v-if="!isEditingNotes">
            <div v-if="userNotes" class="text-sm text-gray-700">{{ userNotes }}</div>
            <div v-else class="text-sm text-gray-400">暂无备注</div>
          </div>

          <div v-else>
            <el-input
              v-model="userNotes"
              type="textarea"
              :rows="4"
              placeholder="输入备注内容..."
            />
            <div class="mt-2 flex gap-2">
              <el-button size="small" type="primary" @click="saveNotes">保存</el-button>
              <el-button size="small" @click="isEditingNotes = false">取消</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.event-detail {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.prose {
  line-height: 1.75;
}
</style>
