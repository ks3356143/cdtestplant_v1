import { onMounted, Ref, ref } from "vue"
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
    const projectId = route.query.id
    const round = route.query.key
    const tableData = ref([]) // 表格数据
    const total = ref(0)
    const isFetching = ref(false)
    const fetchData = async (isSearch: boolean = false) => {
        if (isSearch) {
            page.value = 1
        }
        isFetching.value = true
        const res = await fetchFn({
            projectId,
            round,
            page: page.value, // 不要忘记value
            pageSize: pageSize.value, // 不要忘记value
            ...searchParams.value
        })
        tableData.value = res.data.items
        total.value = res.data.pageInfo.total
        isFetching.value = false
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
