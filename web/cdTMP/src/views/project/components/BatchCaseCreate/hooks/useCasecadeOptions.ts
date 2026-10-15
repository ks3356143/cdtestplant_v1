import demandApi from "@/api/project/testDemand"
import { Message } from "@arco-design/web-vue"
import { computed, ref } from "vue"
import { useRoute } from "vue-router"

interface OriginHouType {
    label: string
    value: number
    children: {
        label: string
        value: number
        key: string
    }[]
}

export default function () {
    const route = useRoute()
    const casecadeLoading = ref(false)
    const originOptions = ref<OriginHouType[]>([])
    const casecadeOptions = computed(() => {
        return originOptions.value.map(({ children, ...rest }) => ({
            children: children.map(({ label, key }) => ({
                isLeaf: true,
                label,
                value: key
            })),
            ...rest
        }))
    })
    // 初始化时候直接获取数据
    const fetchOptionsData = async () => {
        casecadeLoading.value = true
        try {
            // 获取轮次key
            const rawKey = Array.isArray(route.query.key) ? route.query.key[0] : route.query.key
            const round_key = rawKey?.split("-")[0]
            const res = await demandApi.getRelatedTestDemand({
                id: route.query.id,
                round: round_key
            })
            originOptions.value = res.data
        } catch (e) {
            console.log(e)
            Message.error("级联数据获取失败，请重新打开此页面!")
        } finally {
            casecadeLoading.value = false
        }
    }
    return { fetchOptionsData, casecadeOptions }
}
