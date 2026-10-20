import { Ref, ref } from "vue"
import { Message } from "@arco-design/web-vue"

export default function useDelete(api: Function, resetApi: Function, selecteds: Ref<any[]>) {
    // 删除中状态：防止重复点击，也让按钮显示 loading
    const isDeleting = ref(false)
    const deletesMultipleAction = async () => {
        if (!selecteds.value || selecteds.value.length === 0) {
            Message.error("至少选择一条数据")
            return
        }
        if (isDeleting.value) return
        isDeleting.value = true
        try {
            const response = await api({ ids: selecteds.value })
            if (response?.success) {
                Message.success(response.message || "删除成功！")
                selecteds.value = []
                await resetApi()
            }
        } catch {
            // 失败提示由 axios 拦截器统一处理，保留选中项便于重试
        } finally {
            isDeleting.value = false
        }
    }
    return { deletesMultipleAction, isDeleting }
}
