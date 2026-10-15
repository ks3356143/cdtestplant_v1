import { computed, ref } from "vue"
import dictApi from "@/api/system/dict"
import { Message } from "@arco-design/web-vue"

export default function () {
    const loading = ref(false)
    const originOption = ref([])
    const problemStatus = computed(() => {
        return Object.fromEntries(originOption.value.map(({ title, key }) => [key, title]))
    })

    // 请求字典中测试手段数据
    const fetchDictData = async () => {
        try {
            const res = await dictApi.getDictByCode({ code: "problemStatu" })
            originOption.value = res.data
            loading.value = true
        } catch (e) {
            Message.error("获取测试手段选项失败，请关闭后重新打开!")
        } finally {
            loading.value = false
        }
    }
    // 一个工具函数
    const changeColor = (status: "1" | "2" | "3" | "4") => {
        const colorDict = {
            "1": "green",
            "2": "red",
            "3": "magenta",
            "4": "arcoblue"
        }
        return colorDict[status]
    }

    // 在组件挂载请求dict
    fetchDictData()

    return { fetchDictData, loading, problemStatus, changeColor }
}
