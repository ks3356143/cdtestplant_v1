import { Ref } from "vue"
import { Message } from "@arco-design/web-vue"

export default function useDelete(api: Function, resetApi: Function, selecteds: Ref<any[]>) {
    const deletesMultipleAction = async () => {
        if (selecteds.value && selecteds.value.length > 0) {
            let data = {}
            const response = await api(Object.assign({ ids: selecteds.value }, data))
            response.success && Message.success(response.message || `删除成功！`)
            selecteds.value = []
            await resetApi()
        } else {
            Message.error("至少选择一条数据")
        }
    }
    return { deletesMultipleAction }
}
