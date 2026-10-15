import { defineComponent } from "vue"
import { TreeNodeData } from "@arco-design/web-vue"
import { useTreeDataStore } from "@/store"
import designDemandAPI from "@/api/project/designDemand"
import useOptions from "./useOptions"
import subFormHooks from "@/views/project/projPublicHooks/subFormHooks"

const DesignSubForm = defineComponent({
    name: "DesignSubForm",
    setup(_, { expose }) {
        // hook variable
        const treeDataStore = useTreeDataStore()
        const { title, formData, formRef, modalOptions, project_id, visible } = subFormHooks(
            designDemandAPI.update,
            treeDataStore.updateDesignDemandTreeData,
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
                const res = await designDemandAPI.getDesignDemandOne({ project_id, key }) // **API变化**
                // 更新表单
                formData.value = res.data // **属性变化**
                formData.value.round = key.split("-")[0]
                formData.value.dut = key.split("-")[1]
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
                    title: () => <span>[设计需求]-{title.value}</span>,
                    default: () => (
                        <ma-form ref={formRef} v-model={formData.value} options={options.value} columns={columnOptions.value}>
                            {{
                                "inputPrepend-ident": () => <span>SJ-XX-</span>
                            }}
                        </ma-form>
                    )
                }}
            </a-modal>
        )
    }
})

export default DesignSubForm
// 组件类型导出
type DesignSubFormOrigin = InstanceType<typeof DesignSubForm>
export interface DesignSubFormInstance extends DesignSubFormOrigin {
    open(nodeData: TreeNodeData): void
}
