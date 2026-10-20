import { ref, onMounted, onUnmounted } from "vue"

/**
 * 远程数据获取 hook：传入默认值与请求函数，返回数据、加载态、错误与刷新方法
 * 说明：
 * 1. 错误提示由 axios 拦截器统一弹出，这里只维护 error 状态；
 * 2. 用请求序号避免旧请求回包覆盖新数据；
 * 3. 组件卸载后不再写状态，避免 keep-alive 场景下的竞态。
 */
const useFetchData = (defaultValue = {}, fetchDataFunc) => {
    const data = ref(defaultValue)
    // 初始即为加载态：首帧不能把空数据交给消费组件（如看板 TimeLine）
    const isLoading = ref(true)
    const error = ref(null)
    let requestSeq = 0
    let alive = true

    async function fetchData() {
        const currentSeq = ++requestSeq
        isLoading.value = true
        error.value = null
        try {
            const res = await fetchDataFunc()
            if (!alive || currentSeq !== requestSeq) return data.value
            data.value = res?.data ?? defaultValue
            return data.value
        } catch (e) {
            if (alive && currentSeq === requestSeq) error.value = e
            return data.value
        } finally {
            if (alive && currentSeq === requestSeq) isLoading.value = false
        }
    }

    onMounted(() => {
        fetchData()
    })
    onUnmounted(() => {
        alive = false
        // 使在途请求的回包失效
        requestSeq += 1
    })

    return {
        data,
        isLoading,
        error,
        fetchData
    }
}
export default useFetchData
