import designApi from "@/api/project/designDemand"
import { Message } from "@arco-design/web-vue"
import { computed, ref } from "vue"
import { useRoute } from "vue-router"

// 定义后端返回的级联数据，注意修改后端也要修改此处
interface OriginOptionsType {
    label: string
    value: number
    children: {
        label: string
        value: number
        children: {
            label: string
            value: number
            key: string // 这里要放options的value里面
        }[]
    }[]
}

export default function () {
    const route = useRoute()
    const casecadeLoading = ref(false)
    const originOptions = ref<OriginOptionsType[]>([])
    const casecadeOptions = computed(() => {
        return originOptions.value.map(({ children, ...rest }) => ({
            children: children.map(({ children, ...rest2 }) => ({
                children: children.map(({ label, key }) => ({
                    label,
                    value: key,
                    isLeaf: true
                })),
                ...rest2
            })),
            ...rest
        }))
    })
    // 初始化是直接获取数据
    const fetchOptionsData = async () => {
        casecadeLoading.value = true
        try {
            const res = await designApi.getRelatedCasDesign({ id: route.query.id })
            originOptions.value = res.data
        } catch (e) {
            Message.error("级联数据获取失败，请重新打开此页面!")
        } finally {
            casecadeLoading.value = false
        }
    }
    return { fetchOptionsData, casecadeOptions }
}
