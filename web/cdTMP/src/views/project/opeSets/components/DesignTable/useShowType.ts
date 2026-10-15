import { ref } from "vue"
import commonApi from "@/api/common"

export default function useShowType(dictCode: string) {
    const codeDict = ref<any>([])
    ;(function () {
        commonApi.getDict(dictCode).then((res: any) => {
            codeDict.value = res
        })
    })()
    const showType = (record: any) => {
        let len = codeDict.value.data.length
        for (let i = 0; i < len; i++) {
            if (codeDict.value.data[i].key === record[dictCode]) {
                let item = codeDict.value.data[i]
                return item.title
            }
        }
    }
    return showType
}
