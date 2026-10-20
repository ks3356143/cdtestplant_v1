import { ref } from "vue"

/**
 * 远程数据获取 hook：传入默认值与请求函数，返回数据、加载态、错误与刷新方法
 * 说明：错误提示由 axios 拦截器统一弹出，这里只维护 error 状态，避免未捕获的 Promise
 */
const useFetchData = (defaultValue = {}, fetchDataFunc) => {
    const data = ref(defaultValue)
    const isLoading = ref(false)
    const error = ref(null)

    async function fetchData() {
        isLoading.value = true
        error.value = null
        try {
            const res = await fetchDataFunc()
            data.value = res?.data ?? defaultValue
            return data.value
        } catch (e) {
            error.value = e
            return data.value
        } finally {
            isLoading.value = false
        }
    }

    fetchData()
    return {
        data,
        isLoading,
        error,
        fetchData
    }
}
export default useFetchData
