import { defineComponent } from "vue"
import { TreeNodeData } from "@arco-design/web-vue"
import { useTreeDataStore } from "@/store"
import dutAPI from "@/api/project/dut"
import useOptions from "./useOptions"
import subFormHooks from "../../projPublicHooks/subFormHooks"

const DutSubForm = defineComponent({
    name: "DutSubForm",
    setup(_, { expose }) {
        // hook variable
        const treeDataStore = useTreeDataStore()
        const { title, formData, formRef, modalOptions, project_id, visible } = subFormHooks(
            dutAPI.update,
            treeDataStore.updateDutTreeData
        )
        // hooks
        const { options, columnOptions } = useOptions(formRef) // **变化**
        // 双击打开回调
        const open = async (nodeData: TreeNodeData) => {
            // 请求数据
            try {
                const key = nodeData.key
                // 设置表单名称
                title.value = nodeData.title!
                const res = await dutAPI.getDutOne({ project_id, key }) // **API变化**
                // 更新表单
                formData.value = res.data
                formData.value.round = key // **属性变化**
                visible.value = true
            } catch (e) {
                visible.value = false
            }
        }
        // out use
        expose({ open })

        // Dom
        return () => (
            // 注意v-model:visible是不能放在对象解构的
            <a-modal {...modalOptions} v-model:visible={visible.value} unmount-on-close>
                {{
                    title: () => <span >[被测件]-{title.value}</span>,
                    default: () => (
                        <ma-form
                            ref={formRef}
                            v-model={formData.value}
                            options={options.value}
                            columns={columnOptions.value}
                        >
                            {{
                                "inputPrepend-version": () => <span>V</span>
                            }}
                        </ma-form>
                    )
                }}
            </a-modal>
        )
    }
})

export default DutSubForm
// 组件类型导出
type DutSubFormOrigin = InstanceType<typeof DutSubForm>
export interface DutSubFormInstance extends DutSubFormOrigin {
    open(nodeData: TreeNodeData): void
}
