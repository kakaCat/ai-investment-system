<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import type { EChartsOption } from 'echarts'

/**
 * 持仓分布数据项
 */
export interface DistributionItem {
  name: string // 名称（股票名称或分类名称）
  value: number // 市值
  percentage?: number // 占比 (%)
  symbol?: string // 股票代码（可选）
}

interface Props {
  data: DistributionItem[] // 分布数据
  title?: string // 图表标题
  type?: 'stock' | 'industry' | 'market' // 分布类型
  height?: string // 图表高度
  showPercentage?: boolean // 是否显示百分比
}

const props = withDefaults(defineProps<Props>(), {
  title: '持仓分布',
  type: 'stock',
  height: '400px',
  showPercentage: true
})

const emit = defineEmits<{
  itemClick: [item: DistributionItem] // 点击饼图项
}>()

// 计算百分比
const dataWithPercentage = computed(() => {
  const total = props.data.reduce((sum, item) => sum + item.value, 0)
  return props.data.map(item => ({
    ...item,
    percentage: total > 0 ? (item.value / total) * 100 : 0
  }))
})

// 颜色方案
const colorPalette = [
  '#5470c6',
  '#91cc75',
  '#fac858',
  '#ee6666',
  '#73c0de',
  '#3ba272',
  '#fc8452',
  '#9a60b4',
  '#ea7ccc',
  '#5D7092',
  '#E690D1',
  '#32C5E9',
  '#96BFFF',
  '#FFD93D',
  '#FF9F7F'
]

// ECharts 配置
const option = computed<EChartsOption>(() => {
  return {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const data = params.data
        return `
          <div style="font-weight: bold; margin-bottom: 5px;">${data.name}</div>
          <div>市值: ¥${data.value.toLocaleString()}</div>
          <div>占比: ${params.percent.toFixed(2)}%</div>
          ${data.symbol ? `<div style="margin-top: 3px; color: #999;">代码: ${data.symbol}</div>` : ''}
        `
      }
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'middle',
      itemGap: 12,
      formatter: (name: string) => {
        const item = dataWithPercentage.value.find(d => d.name === name)
        if (item && props.showPercentage) {
          return `${name}  ${item.percentage!.toFixed(1)}%`
        }
        return name
      },
      textStyle: {
        fontSize: 12
      }
    },
    series: [
      {
        name: props.title,
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            formatter: (params: any) => {
              return `${params.name}\n${params.percent.toFixed(1)}%`
            }
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        labelLine: {
          show: false
        },
        data: dataWithPercentage.value,
        color: colorPalette
      }
    ]
  }
})

// 处理点击事件
const handleChartClick = (params: any) => {
  if (params.componentType === 'series') {
    const item = dataWithPercentage.value.find(d => d.name === params.name)
    if (item) {
      emit('itemClick', item)
    }
  }
}
</script>

<template>
  <div class="portfolio-distribution">
    <!-- 统计摘要 -->
    <div v-if="data.length > 0" class="mb-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div class="rounded-lg bg-blue-50 p-3">
        <div class="text-sm text-gray-600">持仓数量</div>
        <div class="mt-1 text-xl font-bold text-blue-600">{{ data.length }}</div>
      </div>
      <div class="rounded-lg bg-green-50 p-3">
        <div class="text-sm text-gray-600">总市值</div>
        <div class="mt-1 text-xl font-bold text-green-600">
          ¥{{ data.reduce((sum, item) => sum + item.value, 0).toLocaleString() }}
        </div>
      </div>
      <div class="rounded-lg bg-orange-50 p-3">
        <div class="text-sm text-gray-600">最大持仓</div>
        <div class="mt-1 text-xl font-bold text-orange-600">
          {{ Math.max(...dataWithPercentage.map(d => d.percentage!)).toFixed(1) }}%
        </div>
      </div>
      <div class="rounded-lg bg-purple-50 p-3">
        <div class="text-sm text-gray-600">平均占比</div>
        <div class="mt-1 text-xl font-bold text-purple-600">
          {{ data.length > 0 ? (100 / data.length).toFixed(1) : 0 }}%
        </div>
      </div>
    </div>

    <!-- 饼图 -->
    <div v-if="data.length > 0">
      <v-chart
        :option="option"
        :style="{ height: height }"
        autoresize
        @click="handleChartClick"
      />
    </div>

    <!-- 空状态 -->
    <div v-else class="flex flex-col items-center justify-center py-12">
      <el-icon :size="48" class="mb-2 text-gray-300"><PieChart /></el-icon>
      <div class="text-gray-400">暂无持仓数据</div>
    </div>

    <!-- 详细列表 -->
    <div v-if="data.length > 0" class="mt-6">
      <div class="mb-3 font-semibold">详细数据</div>
      <div class="space-y-2">
        <div
          v-for="(item, index) in dataWithPercentage"
          :key="index"
          class="flex items-center justify-between rounded-lg border p-3 hover:bg-gray-50"
        >
          <div class="flex items-center gap-3">
            <div
              class="h-3 w-3 rounded-full"
              :style="{ backgroundColor: colorPalette[index % colorPalette.length] }"
            />
            <div>
              <div class="font-semibold">{{ item.name }}</div>
              <div v-if="item.symbol" class="text-sm text-gray-500">{{ item.symbol }}</div>
            </div>
          </div>
          <div class="text-right">
            <div class="font-semibold">¥{{ item.value.toLocaleString() }}</div>
            <div class="text-sm text-gray-500">{{ item.percentage!.toFixed(2) }}%</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.portfolio-distribution {
  width: 100%;
}
</style>
