import { onMounted, Ref, ref, shallowRef } from "vue"
import { useRoute } from "vue-router"

/**
 * 该hook传入异步请求数据函数，返回isFetching和请求函数
 * 该hook还处理分页数据和请求
 */
export default function useFetchData(fetchFn: Function, columns: Ref<any>) {
    // 分页参数
    const page = ref(1)
    const pageSize = ref(10)
    // 搜索参数
    const searchParams = ref({})
    for (const item of columns.value) {
        searchParams.value[item.dataIndex] = ""
    }
    // 表格数据和isLoading数据
    const route = useRoute()
    const projectId = route.query.id ?? ""
    const round = route.query.key ?? ""
    const tableData = shallowRef([]) // 表格数据（整表替换、无需深层响应式）
    const total = ref(0)
    const isFetching = ref(false)
    // 请求序号：快速翻页/搜索时丢弃过期响应，避免旧数据覆盖新数据
    let requestSeq = 0
    const fetchData = async (isSearch: boolean = false) => {
        if (isSearch) {
            page.value = 1
        }
        const seq = ++requestSeq
        isFetching.value = true
        try {
            const res = await fetchFn({
                projectId,
                round,
                page: page.value, // 不要忘记value
                pageSize: pageSize.value, // 不要忘记value
                ...searchParams.value
            })
            if (seq !== requestSeq) return
            tableData.value = res?.data?.items ?? []
            total.value = res?.data?.pageInfo?.total ?? 0
        } catch {
            // 错误提示由 axios 拦截器统一处理，这里保留现有表格数据
        } finally {
            if (seq === requestSeq) {
                isFetching.value = false
            }
        }
    }
    // 首次加载时触发一次
    onMounted(() => {
        fetchData()
    })
    // 定义a-table的分页改变函数
    const pageChange = (current: number) => {
        page.value = current
        fetchData()
    }
    const pageSizeChange = (size: number) => {
        pageSize.value = size
        fetchData()
    }
    return { tableData, isFetching, fetchData, total, pageChange, pageSizeChange, searchParams }
}
