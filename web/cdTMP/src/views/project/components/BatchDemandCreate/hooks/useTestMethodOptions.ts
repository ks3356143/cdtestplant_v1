import { computed, ref } from "vue"
import dictApi from "@/api/system/dict"
import { Message } from "@arco-design/web-vue"

export default function () {
    const loading = ref(false)
    const originOption = ref([])
    const testMethodOptions = computed(() => {
        return originOption.value.map(({ title, key }) => ({
            label: title,
            value: key
        }))
    })
    // 请求字典中测试手段数据
    const fetchDictData = async () => {
        try {
            const res = await dictApi.getDictByCode({ code: "testMethod" })
            originOption.value = res.data
            loading.value = true
        } catch (e) {
            Message.error("获取测试手段选项失败，请关闭后重新打开!")
        } finally {
            loading.value = false
        }
    }
    return { fetchDictData, loading, testMethodOptions }
}
