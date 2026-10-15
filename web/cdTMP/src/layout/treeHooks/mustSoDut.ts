import { Message, Notification } from "@arco-design/web-vue"
import { useTreeDataStore } from "@/store"
import dutApi from "@/api/project/dut"
import { useRouter } from "vue-router"
import { ref, onMounted } from "vue"
import type { Ref } from "vue"
import MaFormModal from "@/components/ma-form-modal/index.vue"

// 源代码弹窗ma-form的列定义
// 源代码so_dut的弹窗
const soDutColumn = ref([
    {
        title: "轮次key",
        dataIndex: "round_key",
        placeholder: "非用户填写",
        disabled: true,
        rules: [{ required: true, message: "非用户填写，但必填" }]
    },
    {
        title: "代码版本",
        dataIndex: "version",
        placeholder: "请输入代码版本，注意不要带V",
        rules: [{ required: true, message: "代码版本必填" }],
        openPrepend: true
    },
    {
        title: "用户标识",
        dataIndex: "userRef",
        placeholder: "请输入用户标识",
        help: "客户使用的标识",
        rules: [{ required: true, message: "用户标识为客户的标识，必填，可随意填写后面再修改" }]
    },
    {
        title: "单位",
        dataIndex: "unit",
        placeholder: "请选择单位名称",
        formType: "select",
        dict: { url: "system/contact/index", props: { label: "name", value: "name" }, translation: true },
        rules: [{ required: true, message: "单位必选" }]
    },
    {
        title: "总行数",
        dataIndex: "total_lines",
        formType: "input-number",
        rules: [{ required: true, message: "总行数必填" }],
        min: 0
    },
    {
        title: "有效行数",
        dataIndex: "effective_lines",
        formType: "input-number",
        rules: [{ required: true, message: "有效行数必填" }],
        min: 0
    },
    {
        title: "注释行数",
        dataIndex: "comment_lines",
        formType: "input-number",
        rules: [{ required: true, message: "注释行数必填" }],
        min: 0
    }
])

/**判断必须包含源代码被测件的弹窗，用户提交/取消逻辑 */
export default function useMustSoDut(projectId: Ref<string>) {
    // global
    const treeDataStore = useTreeDataStore()
    const router = useRouter()
    // refs
    const soDutFormRef = ref<InstanceType<typeof MaFormModal>>() // 源代码强制弹窗ref
    const soDutModalTitle = ref("强制添加第一轮源代码信息")
    // lifecycles
    onMounted(async () => {
        await treeDataStore.initTreeData(projectId.value)
        // 依次找轮次里面是否有源代码被测件，如果没有则强制弹窗让用户创建
        handleSoDutExistsForceModal()
    })
    const handleSoDutExistsForceModal = async () => {
        /// 主动后端请求
        const res = await dutApi.getSoExists({ id: projectId.value })
        res.data.round_list.forEach((item) => {
            if (!item.isExists) {
                Message.warning(`识别到您未添加第${parseInt(item.key) + 1}轮源代码的信息，请填写信息自动创建`)
                soDutModalTitle.value = `强制添加第${parseInt(item.key) + 1}轮源代码的信息`
                soDutFormRef.value!.open({ round_key: item.key })
                return
            }
        })
    }
    // events
    /**
     * 提交源代码被测件
     */
    const handleSoDutSubmit = async (data: object) => {
        // 只有一个参数就是被提交的数据，然后返回false阻止弹窗消失
        const input_data = { ...data, project_id: projectId.value }
        const res = await dutApi.createR1SoDut(input_data)
        if (res.code == 200) {
            treeDataStore.updateDutTreeData(res.data, projectId.value)
            Message.success("添加源代码被测件成功，并自动创建第一轮的文档审查、静态分析、代码审查测试项和用例")
            setTimeout(() => {
                location.reload()
            }, 500)
            return
        }
        return false
    }
    /**
     * 用户点击源代码被测件取消按钮 -> 返回项目管理页面
     */
    const handleSoDutCancel = () => {
        Notification.error("必须按要求添加源代码信息，返回项目列表页面!")
        router.replace({ name: "projmanage" })
    }
    return {
        soDutFormRef,
        soDutModalTitle,
        handleSoDutExistsForceModal,
        handleSoDutSubmit,
        handleSoDutCancel,
        soDutColumn
    }
}
