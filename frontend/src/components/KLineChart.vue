<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import VChart from 'vue-echarts'
import type { KLineData, KLineDataPoint } from '@/types/stock'
import type { EChartsOption } from 'echarts'

interface Props {
  data: KLineData // K线数据
  height?: string // 图表高度
  showVolume?: boolean // 是否显示成交量
  showMA?: boolean // 是否显示均线
}

const props = withDefaults(defineProps<Props>(), {
  height: '500px',
  showVolume: true,
  showMA: true
})

const chartRef = ref()

// 计算均线数据
const calculateMA = (data: KLineDataPoint[], dayCount: number) => {
  const result: (number | string)[] = []
  for (let i = 0; i < data.length; i++) {
    if (i < dayCount - 1) {
      result.push('-')
      continue
    }
    let sum = 0
    for (let j = 0; j < dayCount; j++) {
      sum += data[i - j].close
    }
    result.push(+(sum / dayCount).toFixed(2))
  }
  return result
}

// ECharts 配置项
const option = computed<EChartsOption>(() => {
  const klineData = props.data.data || []

  // 准备数据
  const dates = klineData.map(item => item.timestamp)
  const values = klineData.map(item => [item.open, item.close, item.low, item.high])
  const volumes = klineData.map(item => item.volume)

  // 计算均线
  const ma5 = props.showMA ? calculateMA(klineData, 5) : []
  const ma10 = props.showMA ? calculateMA(klineData, 10) : []
  const ma20 = props.showMA ? calculateMA(klineData, 20) : []
  const ma60 = props.showMA ? calculateMA(klineData, 60) : []

  const series: any[] = [
    {
      name: 'K线',
      type: 'candlestick',
      data: values,
      itemStyle: {
        color: '#ef4444', // 上涨颜色（红色）
        color0: '#22c55e', // 下跌颜色（绿色）
        borderColor: '#ef4444',
        borderColor0: '#22c55e'
      }
    }
  ]

  // 添加均线
  if (props.showMA) {
    series.push(
      {
        name: 'MA5',
        type: 'line',
        data: ma5,
        smooth: true,
        lineStyle: { opacity: 0.8, width: 1 },
        showSymbol: false
      },
      {
        name: 'MA10',
        type: 'line',
        data: ma10,
        smooth: true,
        lineStyle: { opacity: 0.8, width: 1 },
        showSymbol: false
      },
      {
        name: 'MA20',
        type: 'line',
        data: ma20,
        smooth: true,
        lineStyle: { opacity: 0.8, width: 1 },
        showSymbol: false
      },
      {
        name: 'MA60',
        type: 'line',
        data: ma60,
        smooth: true,
        lineStyle: { opacity: 0.8, width: 1 },
        showSymbol: false
      }
    )
  }

  // 添加成交量
  if (props.showVolume) {
    series.push({
      name: '成交量',
      type: 'bar',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: volumes,
      itemStyle: {
        color: (params: any) => {
          const dataIndex = params.dataIndex
          if (dataIndex === 0) return '#ef4444'
          const current = klineData[dataIndex]
          const prev = klineData[dataIndex - 1]
          return current.close >= prev.close ? '#ef4444' : '#22c55e'
        }
      }
    })
  }

  return {
    title: {
      text: `${props.data.name} (${props.data.symbol})`,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    legend: {
      top: 30,
      data: ['K线', 'MA5', 'MA10', 'MA20', 'MA60']
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: (params: any) => {
        const param = params[0]
        if (!param) return ''

        const dataIndex = param.dataIndex
        const kline = klineData[dataIndex]

        let html = `<div style="font-size: 12px;">
          <div style="font-weight: bold; margin-bottom: 5px;">${kline.timestamp}</div>
          <div>开盘: ${kline.open.toFixed(2)}</div>
          <div>收盘: ${kline.close.toFixed(2)}</div>
          <div>最高: ${kline.high.toFixed(2)}</div>
          <div>最低: ${kline.low.toFixed(2)}</div>
          <div>成交量: ${kline.volume.toLocaleString()}</div>
        `

        // 显示均线数据
        if (props.showMA) {
          html += `<div style="margin-top: 5px;">
            <div style="color: #6366f1;">MA5: ${ma5[dataIndex]}</div>
            <div style="color: #f59e0b;">MA10: ${ma10[dataIndex]}</div>
            <div style="color: #ec4899;">MA20: ${ma20[dataIndex]}</div>
            <div style="color: #8b5cf6;">MA60: ${ma60[dataIndex]}</div>
          </div>`
        }

        html += '</div>'
        return html
      }
    },
    grid: props.showVolume
      ? [
          {
            left: '10%',
            right: '8%',
            top: 80,
            height: '50%'
          },
          {
            left: '10%',
            right: '8%',
            top: '70%',
            height: '15%'
          }
        ]
      : [
          {
            left: '10%',
            right: '8%',
            top: 80,
            bottom: 60
          }
        ],
    xAxis: props.showVolume
      ? [
          {
            type: 'category',
            data: dates,
            boundaryGap: false,
            axisLine: { onZero: false },
            splitLine: { show: false },
            axisLabel: { show: false }
          },
          {
            type: 'category',
            gridIndex: 1,
            data: dates,
            boundaryGap: false,
            axisLine: { onZero: false },
            axisTick: { show: false },
            splitLine: { show: false }
          }
        ]
      : {
          type: 'category',
          data: dates,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false }
        },
    yAxis: props.showVolume
      ? [
          {
            scale: true,
            splitArea: {
              show: true
            }
          },
          {
            scale: true,
            gridIndex: 1,
            splitNumber: 2,
            axisLabel: { show: false },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { show: false }
          }
        ]
      : {
          scale: true,
          splitArea: {
            show: true
          }
        },
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: props.showVolume ? [0, 1] : [0],
        start: 70,
        end: 100
      },
      {
        show: true,
        xAxisIndex: props.showVolume ? [0, 1] : [0],
        type: 'slider',
        top: '90%',
        start: 70,
        end: 100
      }
    ],
    series
  }
})

// 响应式调整
const handleResize = () => {
  chartRef.value?.resize()
}

// 监听窗口大小变化
if (typeof window !== 'undefined') {
  window.addEventListener('resize', handleResize)
}

// 组件卸载时移除事件监听
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', handleResize)
  }
})
</script>

<template>
  <div class="kline-chart">
    <v-chart ref="chartRef" :option="option" :style="{ height: height }" autoresize />
  </div>
</template>

<style scoped>
.kline-chart {
  width: 100%;
}
</style>
