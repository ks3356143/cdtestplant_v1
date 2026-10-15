import { defineComponent, ref } from "vue"
import { Message, TreeNodeData } from "@arco-design/web-vue"
import { useTreeDataStore } from "@/store"
import caseApi from "@/api/project/case"
import useOptions from "./useOptions"
import subFormHooks from "@/views/project/projPublicHooks/subFormHooks"
import useBeforeCancel from "@/views/project/projPublicHooks/useBeforeCancel"
import { cloneDeep } from "lodash-es"

const CaseSubForm = defineComponent({
    name: "CaseSubFrom",
    setup(_, { expose }) {
        // hook variable
        const treeDataStore = useTreeDataStore()
        const { title, formData, formRef, modalOptions, project_id, visible } = subFormHooks(caseApi.update, treeDataStore.updateCaseTreeData, "80%")
        // hooks
        const { options, columnOptions } = useOptions(formRef) // **option里面变化**
        // 双击打开回调
        const open = async (nodeData: TreeNodeData) => {
            // 请求数据
            try {
                const key = nodeData.key as string
                // 设置表单名称
                title.value = nodeData.title!
                // 注意这里因为case接口原因，这里需要projectId!
                const res = await caseApi.getCaseOne({ projectId: project_id, key }) // **API变化**
                // 得到数据时候将beforeFormContent搞定
                beforeFormContent.value = cloneDeep(res.data.testStep)
                // 更新表单
                formData.value = res.data // **属性变化**
                formData.value.round = key.split("-")[0]
                formData.value.dut = key.split("-")[1]
                formData.value.designDemand = key.split("-")[2]
                formData.value.testDemand = key.split("-")[3]
                visible.value = true
            } catch (e) {
                Message.error("数据未获取到，请联系开发者")
                visible.value = false
            }
        }
        // out use
        expose({ open })

        // hook-判断是否更变内容关闭-只用于测试项和测试用例
        const beforeFormContent = ref<any>(undefined)
        const { handleBeforeCancel } = useBeforeCancel(formData, beforeFormContent, visible)

        // Dom
        return () => (
            // 注意v-model:visible是不能放在对象解构的
            <a-modal {...modalOptions} v-model:visible={visible.value} on-before-cancel={handleBeforeCancel} width="86%" unmount-on-close>
                {{
                    title: () => <span>[测试用例]-{title.value}</span>,
                    default: () => <ma-form ref={formRef} v-model={formData.value} options={options.value} columns={columnOptions.value}></ma-form>
                }}
            </a-modal>
        )
    }
})

export default CaseSubForm
// 组件类型导出
type CaseSubFormOrigin = InstanceType<typeof CaseSubForm>
export interface CaseSubFormInstance extends CaseSubFormOrigin {
    open(nodeData: TreeNodeData): void
}
