import { post } from './request'

/**
 * 查询事件列表
 */
export const queryEvents = (params: {
  symbol?: string
  category?: string
  is_read?: boolean
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}) => {
  return post('/event/query', params)
}

/**
 * 获取事件详情
 */
export const getEventDetail = (params: { event_id: number }) => {
  return post('/event/detail', params)
}

/**
 * 创建事件
 */
export const createEvent = (params: {
  symbol: string
  stock_name: string
  category: string
  subcategory: string
  title: string
  content: string
  event_date: string
  source?: string
  source_url?: string
  impact_level?: number
  impact_analysis?: string
  tags?: string[]
}) => {
  return post('/event/create', params)
}

/**
 * 更新事件
 */
export const updateEvent = (params: {
  event_id: number
  title?: string
  content?: string
  impact_level?: number
  impact_analysis?: string
  tags?: string[]
}) => {
  return post('/event/update', params)
}

/**
 * 标记事件已读
 */
export const markEventRead = (params: {
  event_id: number
  is_read?: boolean
}) => {
  return post('/event/mark-read', params)
}
