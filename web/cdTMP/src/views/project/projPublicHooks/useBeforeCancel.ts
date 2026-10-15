import { isEqual } from "lodash-es"
import { getCurrentInstance } from "vue"

/**
 * 该hook为测试项子项和测试用例步骤设计，当其改变时候弹窗通知用户
 */
export default function useBeforeCancel(formData: any, beforeFormContent: any, visible: any) {
    const app = getCurrentInstance()!.appContext.config.globalProperties
    const handleBeforeCancel = () => {
        if (!beforeFormContent.value) {
            return true
        }
        const content = formData.value.testContent || formData.value.testStep
        const iuEqualValue = isEqual(content, beforeFormContent.value)
        !iuEqualValue &&
            app.$modal.confirm({
                title: "测试项步骤内容你已改动，是否保留您编写的测试项/测试用例步骤数据？",
                content: "",
                okText: "返回重新编辑",
                cancelText: "取消",
                simple: true,
                onOk: () => {
                    visible.value = true
                },
                onCancel: () => {}
            })
        return true
    }
    return {
        handleBeforeCancel
    }
}
