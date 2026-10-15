/**
 * 该hook为了各个页面双击弹窗SubForm进行公共代码提取
 */
import { ref, inject } from "vue"
import { useRoute } from "vue-router"
import MaForm from "@/components/ma-form/index.vue"
import { Message } from "@arco-design/web-vue"

export default function (updateApiFunc: Function, updateTreeFunc: Function, width = "40%") {
    const route = useRoute()
    const project_id = route.query.id // 只能拿ID其他是null
    const rightViewRef = inject("rightViewRef")
    // has returns
    const visible = ref(false)
    const formRef = ref<InstanceType<typeof MaForm> | null>(null)
    const formData = ref<any>({})
    // 标题
    const title = ref("")
    // 异步确认按钮点击
    const handleBeforeOk = async () => {
        const isValidated = await formRef.value!.validateForm()
        if (isValidated) {
            // 失败
            return false
        } else {
            // 成功 **变化**
            try {
                const res = await updateApiFunc(formData.value.id, { project_id, ...formData.value })
                updateTreeFunc(res.data, project_id) // 刷新树节点信息
                !(rightViewRef as any).value.refresh()
                Message.success("修改成功")
            } catch (e) {
                return false
            }
        }
    }
    const modalOptions = {
        width,
        draggable: true,
        "unmount-on-close": true,
        "ok-text": "保存",
        "cancel-text": "关闭",
        "on-before-ok": handleBeforeOk
    }
    return { title, formData, formRef, modalOptions, project_id, visible }
}
