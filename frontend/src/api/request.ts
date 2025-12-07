import axios, { AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

/**
 * 统一响应格式
 */
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp: string
}

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data as ApiResponse

    // code !== 0 表示业务错误
    if (res.code !== 0) {
      ElMessage.error(res.message || '请求失败')

      // 401 未登录
      if (res.code === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/login')
      }

      return Promise.reject(new Error(res.message || 'Error'))
    }

    return res
  },
  (error) => {
    console.error('API Error:', error)

    // 处理HTTP 401状态码
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
      return Promise.reject(error)
    }

    // 处理其他HTTP错误
    const message = error.response?.data?.detail || error.message || '网络错误'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

/**
 * POST 请求封装
 */
export function post<T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<ApiResponse<T>> {
  return request.post(url, data, config)
}

export default request
