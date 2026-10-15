import { computed, defineComponent, PropType, ref } from "vue"
import type { BatchFormData } from "./types"
import { designColumn } from "./columns"
import commonApi from "@/api/common"
import { FormInstance, Message } from "@arco-design/web-vue"
import { useRoute } from "vue-router"
import designApi from "@/api/project/designDemand"
import { useTreeDataStore } from "@/store"

// props.type类型
type CreateType = "design" | "demand" | "case"

// 常量
const typeTitle = {
    design: "设计需求",
    demand: "测试项",
    case: "用例"
}

const BatchCreate = defineComponent({
    name: "BatchCreate",
    emits: ["batchCreateFinish"],
    props: {
        type: {
            type: String as PropType<CreateType>,
            default: "design"
        }
    },
    setup({ type }, { expose, emit }) {
        const visible = ref(false)
        const route = useRoute()
        const treeDataStore = useTreeDataStore()

        // 表单的引用
        const formRef = ref<FormInstance>()

        // 请求需求类型-预备数据
        const xqType = ref<any>([])
        ;(function () {
            commonApi.getDict("demandType").then((res: any) => {
                xqType.value = res.data
            })
        })()
        const xqTypeOptions = computed(() => {
            return xqType.value.map(({ key, title }) => ({
                label: title,
                value: key
            }))
        })

        // 初始化数据-默认有一行空数据
        const newData = {
            ident: "",
            name: "",
            chapter: "",
            demandType: "1",
            description: ""
        }

        const formData = ref<BatchFormData[]>([{ ...newData }])

        // 定义表单的验证规则
        const validationRules = {
            ident: [],
            name: [{ required: true, message: "需求名称不能为空" }],
            chapter: [{ required: true, message: "可为'/',不能为空" }],
            demandType: [{ required: true, message: "需求类型不能为空" }],
            description: []
        }

        const open = () => {
            visible.value = true
        }

        // data数据操作
        const handleNewLine = () => {
            formData.value.push({ ...newData })
        }

        const handleDeleteAll = () => {
            formData.value = [{ ...newData }]
        }

        const handleDeletePoint = (idx: number) => {
            formData.value.splice(idx, 1)
        }

        // 提交操作-可阻止关闭模态框
        const handleSubmit = async () => {
            // 配置提交变量
            const projectId = route.query.id
            const key = route.query.key
            // 修改符合后端要求的数据要求content和title
            const data = formData.value.map(({ name, description, ...rest }) => ({
                title: name,
                content: description,
                ...rest
            }))
            const validation = await formRef.value?.validate()
            if (validation === undefined) {
                // 验证成功
                try {
                    const res = await designApi.multiSave({ projectId, key, data })
                    handleDeleteAll()
                    treeDataStore.updateDesignDemandTreeData(res.data, projectId)
                    emit("batchCreateFinish")
                    Message.success("批量新增成功!")
                    return true
                } catch (e) {
                    return false
                }
            }
            return false
        }

        expose({ open })

        return () => (
            <div class="batch-create-container">
                <a-modal
                    fullscreen
                    unmount-on-close
                    v-model:visible={visible.value}
                    title={"批量新增" + typeTitle[type]}
                    ok-text="批量新增"
                    on-before-ok={handleSubmit}
                >
                    <a-space>
                        <a-button type="primary" style={{ marginBottom: "10px" }} onClick={handleNewLine}>
                            {{
                                icon: () => <icon-plus />,
                                default: () => "新增一行"
                            }}
                        </a-button>
                        <a-popconfirm content="您确定要重置?" onOk={handleDeleteAll}>
                            <a-button type="primary" status="warning" style={{ marginBottom: "10px" }}>
                                重置
                            </a-button>
                        </a-popconfirm>
                    </a-space>
                    <a-form ref={formRef} model={formData.value} layout="vertical">
                        <a-table
                            data={formData.value}
                            columns={designColumn}
                            pagination={false}
                            hoverable={false}
                            scroll={{ x: 1500 }}
                            bordered={{ wrapper: true, cell: true }}
                            v-slots={{
                                xuhao: ({ rowIndex }) => rowIndex + 1,
                                ident: ({ rowIndex }) => (
                                    <a-form-item help="例如SJGL" field={`${rowIndex}.ident`} rules={validationRules.ident} hide-label>
                                        <a-input allow-clear v-model={formData.value[rowIndex].ident} placeholder="无须写前缀" />
                                    </a-form-item>
                                ),
                                name: ({ rowIndex }) => (
                                    <a-form-item help="章节名称" field={`${rowIndex}.name`} rules={validationRules.name} hide-label>
                                        <a-input allow-clear v-model={formData.value[rowIndex].name} placeholder="请填写需求名称" />
                                    </a-form-item>
                                ),
                                chapter: ({ rowIndex }) => (
                                    <a-form-item help="可填写'/'为章节号" field={`${rowIndex}.chapter`} rules={validationRules.chapter} hide-label>
                                        <a-input allow-clear v-model={formData.value[rowIndex].chapter} placeholder="请填写章节号" />
                                    </a-form-item>
                                ),
                                demandType: ({ rowIndex }) => (
                                    <a-form-item help="接口需补充内容" field={`${rowIndex}.demandType`} rules={validationRules.demandType} hide-label>
                                        <a-select v-model={formData.value[rowIndex].demandType} options={xqTypeOptions.value} />
                                    </a-form-item>
                                ),
                                description: ({ rowIndex }) => (
                                    <a-form-item field={`${rowIndex}.description`} rules={validationRules.description} hide-label>
                                        <ma-editor v-model={formData.value[rowIndex].description} style="width: 100%" id={"description" + rowIndex}></ma-editor>
                                    </a-form-item>
                                ),
                                caozuo: ({ rowIndex }) => (
                                    <div>
                                        <a-popover title="新增">
                                            <a-button type="text" onClick={handleNewLine}>
                                                {{
                                                    icon: () => <icon-plus />
                                                }}
                                            </a-button>
                                        </a-popover>
                                        <a-popover title="删除">
                                            <a-button type="text" status="danger" onClick={() => handleDeletePoint(rowIndex)}>
                                                {{
                                                    icon: () => <icon-delete />
                                                }}
                                            </a-button>
                                        </a-popover>
                                    </div>
                                )
                            }}
                        ></a-table>
                    </a-form>
                </a-modal>
            </div>
        )
    }
})

export default BatchCreate
