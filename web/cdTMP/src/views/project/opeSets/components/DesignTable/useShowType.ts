import { ref } from "vue"
import commonApi from "@/api/common"

export default function useShowType(dictCode: string) {
    const codeDict = ref<any[]>([])
    commonApi
        .getDict(dictCode)
        .then((res: any) => {
            codeDict.value = res?.data ?? []
        })
        .catch(() => {
            // 字典未加载时保持空数组，渲染侧用原始 key 兜底
        })
    const showType = (record: any) => {
        const key = record?.[dictCode]
        const hit = codeDict.value.find((item: any) => item.key === key)
        return hit?.title ?? key ?? "-"
    }
    return showType
}
