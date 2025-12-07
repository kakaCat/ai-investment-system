import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { accountApi } from '@/api/account'
import type { Account, AccountDetail } from '@/types/account'

export const useAccountStore = defineStore('account', () => {
  // 状态
  const accounts = ref<Account[]>([])
  const currentAccount = ref<AccountDetail | null>(null)
  const loading = ref(false)

  // 计算属性
  const activeAccounts = computed(() => accounts.value.filter((a) => a.status === 'active'))

  const totalAccounts = computed(() => accounts.value.length)

  // 方法
  const fetchAccounts = async () => {
    loading.value = true
    try {
      const res = await accountApi.query({
        page: 1,
        page_size: 100,
        status: 'active'
      })
      accounts.value = res.data.list
    } finally {
      loading.value = false
    }
  }

  const fetchAccountDetail = async (accountId: number) => {
    loading.value = true
    try {
      const res = await accountApi.detail({ account_id: accountId })
      currentAccount.value = res.data
    } finally {
      loading.value = false
    }
  }

  const createAccount = async (params: { account_name: string; account_type: string }) => {
    const res = await accountApi.create(params)
    await fetchAccounts() // 刷新列表
    return res
  }

  const deleteAccount = async (accountId: number) => {
    await accountApi.delete({ account_id: accountId })
    await fetchAccounts() // 刷新列表
  }

  return {
    // 状态
    accounts,
    currentAccount,
    loading,

    // 计算属性
    activeAccounts,
    totalAccounts,

    // 方法
    fetchAccounts,
    fetchAccountDetail,
    createAccount,
    deleteAccount
  }
})
