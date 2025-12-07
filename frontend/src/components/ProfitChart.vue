<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import type { EChartsOption } from 'echarts'

/**
 * 盈亏数据点
 */
export interface ProfitDataPoint {
  date: string // 日期
  profit: number // 累计盈亏
  profit_rate: number // 盈亏率 (%)
}

interface Props {
  data: ProfitDataPoint[] // 盈亏数据
  title?: string // 图表标题
  height?: string // 图表高度
  showRate?: boolean // 是否显示盈亏率曲线
}

const props = withDefaults(defineProps<Props>(), {
  title: '盈亏曲线',
  height: '400px',
  showRate: true
})

// ECharts 配置
const option = computed<EChartsOption>(() => {
  const dates = props.data.map(item => item.date)
  const profits = props.data.map(item => item.profit)
  const profitRates = props.data.map(item => item.profit_rate)

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
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: (params: any) => {
        if (!params || !params.length) return ''

        const date = params[0].axisValue
        let html = `<div style="font-weight: bold; margin-bottom: 5px;">${date}</div>`

        params.forEach((param: any) => {
          const value = param.value
          const color = param.color

          if (param.seriesName === '累计盈亏') {
            html += `
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: ${color};"></span>
                <span>${param.seriesName}:</span>
                <span style="font-weight: bold; color: ${value >= 0 ? '#ef4444' : '#22c55e'};">
                  ${value >= 0 ? '+' : ''}¥${value.toLocaleString()}
                </span>
              </div>
            `
          } else {
            html += `
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: ${color};"></span>
                <span>${param.seriesName}:</span>
                <span style="font-weight: bold; color: ${value >= 0 ? '#ef4444' : '#22c55e'};">
                  ${value >= 0 ? '+' : ''}${value.toFixed(2)}%
                </span>
              </div>
            `
          }
        })

        return html
      }
    },
    legend: {
      data: props.showRate ? ['累计盈亏', '盈亏率'] : ['累计盈亏'],
      top: 30
    },
    grid: {
      left: '10%',
      right: '10%',
      top: 80,
      bottom: 80,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: props.showRate
      ? [
          {
            type: 'value',
            name: '累计盈亏 (¥)',
            position: 'left',
            axisLabel: {
              formatter: (value: number) => {
                return value >= 0 ? `+${value}` : value.toString()
              }
            },
            splitLine: {
              show: true,
              lineStyle: {
                type: 'dashed'
              }
            }
          },
          {
            type: 'value',
            name: '盈亏率 (%)',
            position: 'right',
            axisLabel: {
              formatter: (value: number) => {
                return value >= 0 ? `+${value}%` : `${value}%`
              }
            }
          }
        ]
      : {
          type: 'value',
          name: '累计盈亏 (¥)',
          axisLabel: {
            formatter: (value: number) => {
              return value >= 0 ? `+${value}` : value.toString()
            }
          },
          splitLine: {
            show: true,
            lineStyle: {
              type: 'dashed'
            }
          }
        },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        start: 0,
        end: 100,
        bottom: 20
      }
    ],
    series: props.showRate
      ? [
          {
            name: '累计盈亏',
            type: 'line',
            data: profits,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            itemStyle: {
              color: '#3b82f6'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
                  { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
                ]
              }
            },
            markLine: {
              data: [{ type: 'average', name: '平均值' }],
              label: {
                formatter: (params: any) => `平均: ¥${params.value.toLocaleString()}`
              }
            }
          },
          {
            name: '盈亏率',
            type: 'line',
            yAxisIndex: 1,
            data: profitRates,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            itemStyle: {
              color: '#f59e0b'
            },
            lineStyle: {
              type: 'dashed'
            }
          }
        ]
      : [
          {
            name: '累计盈亏',
            type: 'line',
            data: profits,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            itemStyle: {
              color: '#3b82f6'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
                  { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
                ]
              }
            },
            markLine: {
              data: [{ type: 'average', name: '平均值' }],
              label: {
                formatter: (params: any) => `平均: ¥${params.value.toLocaleString()}`
              }
            }
          }
        ]
  }
})
</script>

<template>
  <div class="profit-chart">
    <v-chart :option="option" :style="{ height: height }" autoresize />
  </div>
</template>

<style scoped>
.profit-chart {
  width: 100%;
}
</style>
