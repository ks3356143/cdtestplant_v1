import { computed, ref } from "vue"
import dictApi from "@/api/system/dict"
import { Message } from "@arco-design/web-vue"

export default function () {
    const loading = ref(false)
    const originOption = ref([])
    const gradeOptions = computed(() => {
        return Object.fromEntries(originOption.value.map(({ title, key }) => [key, title]))
    })
    // 请求问题单等级字典
    const fetchDictData = async () => {
        loading.value = true
        try {
            const res = await dictApi.getDictByCode({ code: "problemGrade" })
            originOption.value = res.data || []
        } catch (e) {
            Message.error("获取问题单等级字典失败，请刷新重试!")
        } finally {
            loading.value = false
        }
    }
    // 一个工具函数
    const changeGradeColor = (status: "1" | "2" | "3" | "4") => {
        const colorDict = {
            "1": "blue",
            "2": "orange",
            "3": "green",
            "4": "red"
        }
        return colorDict[status]
    }
    fetchDictData()
    return { fetchDictData, loading, gradeOptions, changeGradeColor }
}
