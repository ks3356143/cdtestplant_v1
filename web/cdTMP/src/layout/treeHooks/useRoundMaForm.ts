import { Ref, ref } from "vue"
import { useRoute } from "vue-router"
import { useRouter } from "vue-router"
import roundApi from "@/api/project/round"
import { useTreeDataStore } from "@/store"
import dayjs from "dayjs"
import { Message } from "@arco-design/web-vue"
export default function useRoundMaForm(projectId: Ref<string>, handleSoDutExistsForceModal: Function) {
    // global
    const route = useRoute()
    const router = useRouter()
    const treeDataStore = useTreeDataStore()
    // refs
    const maFormModalRef = ref()
    const title = ref("")
    // MA-FORM表单配置
    const roundColumn = ref([
        {
            title: "基本信息",
            customClass: ["mb-2", "pb-0"],
            formType: "card",
            bodyStyle: { paddingBottom: 0 },
            formList: [
                {
                    formType: "grid",
                    cols: [
                        {
                            span: 12,
                            formList: [
                                { title: "轮次标识", dataIndex: "ident", disabled: true },
                                {
                                    title: "开始时间",
                                    dataIndex: "beginTime",
                                    formType: "date",
                                    placeholder: "请选择时间",
                                    extra: "尽量大于项目开始时间13天，生成文档才符合要求",
                                    rules: [
                                        { required: true, message: "开始时间必填" },
                                        {
                                            validator: (value, callback) => {
                                                const projectBegin = route.query.beginTime!
                                                value <= projectBegin
                                                    ? callback(
                                                          "不能早于项目开始时间，由于还有前期测试设计阶段，建议大于项目开始时间13天"
                                                      )
                                                    : null
                                            }
                                        }
                                    ]
                                },
                                {
                                    title: "动态地点",
                                    dataIndex: "location",
                                    placeholder: "请填入测试地点",
                                    extra: "该字段影响时间相关表格的地点",
                                    rules: [{ required: true, message: "测试地点是必填的" }]
                                }
                            ]
                        },
                        {
                            span: 12,
                            formList: [
                                { title: "名称", dataIndex: "name", rules: [{ required: true, message: "名称必填" }] },
                                {
                                    title: "结束时间",
                                    dataIndex: "endTime",
                                    formType: "date",
                                    placeholder: "请选择时间",
                                    extra: "该字段决定《测试记录》封面时间",
                                    rules: [
                                        { required: true, message: "结束时间必填" },
                                        {
                                            validator(value, errorCallback) {
                                                let start = maFormModalRef.value.form.beginTime
                                                value < start ? errorCallback("结束时间不能小于开始时间") : null
                                            }
                                        }
                                    ]
                                },
                                {
                                    title: "质量等级",
                                    dataIndex: "grade",
                                    formType: "select",
                                    dict: {
                                        data: [
                                            { label: "军级", value: "1" },
                                            { label: "商业级", value: "2" },
                                            { label: "宇航级", value: "3" },
                                            { label: "工业级", value: "4" }
                                        ]
                                    },
                                    placeholder: "请填入质量等级",
                                    addDefaultValue: "1",
                                    rules: [{ required: true, message: "质量等级必填" }]
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            formType: "card",
            title: "极端工况信息(FPGA)",
            customClass: ["mb-2", "pb-0"],
            bodyStyle: { paddingBottom: 0 },
            formList: [
                {
                    formType: "divider",
                    title: "最好工况",
                    orientation: "left",
                    margin: "20px"
                },
                {
                    formType: "grid",
                    cols: [
                        {
                            span: 12,
                            formList: [
                                { title: "电压", dataIndex: "best_condition_voltage", placeholder: "请填入电压" }
                            ]
                        },
                        {
                            span: 12,
                            formList: [{ title: "温度", dataIndex: "best_condition_tem", placeholder: "请填入温度" }]
                        }
                    ]
                },
                {
                    formType: "divider",
                    title: "典型工况",
                    orientation: "left",
                    margin: "20px"
                },
                {
                    formType: "grid",
                    cols: [
                        {
                            span: 12,
                            formList: [
                                { title: "电压", dataIndex: "typical_condition_voltage", placeholder: "请填入电压" }
                            ]
                        },
                        {
                            span: 12,
                            formList: [{ title: "温度", dataIndex: "typical_condition_tem", placeholder: "请填入温度" }]
                        }
                    ]
                },
                {
                    formType: "divider",
                    title: "最差工况",
                    orientation: "left",
                    margin: "20px"
                },
                {
                    formType: "grid",
                    cols: [
                        {
                            span: 12,
                            formList: [{ title: "电压", dataIndex: "low_condition_voltage", placeholder: "请填入电压" }]
                        },
                        {
                            span: 12,
                            formList: [{ title: "温度", dataIndex: "low_condition_tem", placeholder: "请填入温度" }]
                        }
                    ]
                }
            ]
        }
    ])
    // 表单的option
    const roundOption = ref({
        customClass: [""]
    })
    // events
    /// 点击新增轮次按钮
    const handleRoundAddClick = (nodeData) => {
        let create_number = treeDataStore.getRoundMiddleInfo()
        // 这里是文档写错了,调用form是里面组件绑定的数据
        maFormModalRef.value.form = {}
        // 这里如果删除中间轮次，那么新增信息应该从中间开始
        maFormModalRef.value.open({
            beginTime: dayjs().format("YYYY-MM-DD"),
            grade: "1",
            key: `${create_number}`,
            name: `第${create_number + 1}轮测试`,
            ident: `${route.query.ident}-R${create_number + 1}`,
            project: projectId.value
        })
        title.value = "新增轮次"
    }
    /// 点击编辑轮次按钮
    const handleRoundEditClick = async (nodeData) => {
        const data = await roundApi.getOneRoundInfo({
            projectId: projectId.value,
            round: nodeData.key
        })
        maFormModalRef.value.open(data.data)
        title.value = `编辑轮次:${data.data.name}`
    }
    /// 点击删除轮次按钮
    const handleRoundDelClick = async (value) => {
        try {
            await roundApi.delete(projectId.value, value)
            Message.success("删除成功！")
            treeDataStore.resetTreeData(projectId.value)
            router.replace({ name: "project", query: route.query })
        } catch {}
    }
    /// Ma-form-Modal的提交按钮 - 轮次新增/编辑逻辑
    const handleRoundSubmit = async (value) => {
        if (title.value.slice(0, 1) === "编") {
            try {
                await roundApi.update(value.id, value)
                Message.success("编辑成功！")
            } catch {
                Message.error("编辑失败！")
            }
        }
        if (title.value.slice(0, 1) === "新") {
            try {
                await roundApi.save(projectId.value, value)
                Message.success("新增成功！")
                treeDataStore.resetTreeData(projectId.value)
                // 调用判断函数，判断是否轮次有源代码dut
                handleSoDutExistsForceModal()
            } catch {
                Message.error("新增失败！")
            }
        }
    }
    return {
        maFormModalRef,
        title,
        roundColumn,
        roundOption,
        handleRoundAddClick,
        handleRoundEditClick,
        handleRoundDelClick,
        handleRoundSubmit
    }
}
