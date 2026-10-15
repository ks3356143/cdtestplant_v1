import { defineComponent, ref } from "vue"
import { TreeNodeData } from "@arco-design/web-vue"
import { useTreeDataStore } from "@/store"
import testDemandAPI from "@/api/project/testDemand"
import useOptions from "./useOptions"
import subFormHooks from "@/views/project/projPublicHooks/subFormHooks"
import useBeforeCancel from "@/views/project/projPublicHooks/useBeforeCancel"
import { cloneDeep } from "lodash-es"

const DemandSubForm = defineComponent({
    name: "DemandSubFormForm",
    setup(_, { expose }) {
        // hook variable
        const treeDataStore = useTreeDataStore()
        const { title, formData, formRef, modalOptions, project_id, visible } = subFormHooks(
            testDemandAPI.update,
            treeDataStore.updateTestDemandTreeData,
            "80%"
        )
        // hooks
        const { options, columnOptions } = useOptions(formRef) // **option里面变化**
        // 双击打开回调
        const open = async (nodeData: TreeNodeData) => {
            // 请求数据
            try {
                const key = nodeData.key as string
                // 设置表单名称
                title.value = nodeData.title!
                const res = await testDemandAPI.getTestDemandOne({ project_id, key }) // **API变化**
                // 得到数据时候将beforeFormContent搞定
                beforeFormContent.value = cloneDeep(res.data.testContent)
                // 更新表单
                formData.value = res.data // **属性变化**
                formData.value.round = key.split("-")[0]
                formData.value.dut = key.split("-")[1]
                formData.value.designDemand = key.split("-")[2]
                visible.value = true
            } catch (e) {
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
            <a-modal {...modalOptions} v-model:visible={visible.value} on-before-cancel={handleBeforeCancel} width='86%' unmount-on-close>
                {{
                    title: () => <span>[测试项]-{title.value}</span>,
                    default: () => (
                        <ma-form
                            ref={formRef}
                            v-model={formData.value}
                            options={options.value}
                            columns={columnOptions.value}
                        >
                            {{
                                "inputPrepend-ident": () => <span>XQ_XX_</span>
                            }}
                        </ma-form>
                    )
                }}
            </a-modal>
        )
    }
})

export default DemandSubForm
// 组件类型导出
type DemandSubFormOrigin = InstanceType<typeof DemandSubForm>
export interface DemandSubFormInstance extends DemandSubFormOrigin {
    open(nodeData: TreeNodeData): void
}
