import { ref } from "vue"
import { useRoute } from "vue-router"
import tool from "@/utils/tool"

export default function (crudOrFormRef: any, problemFormRef?: any) {
    const title = ref("问题单表单")
    const route = useRoute()
    // 固定是否为FPGA
    const isFPGA = !tool.checkForCpuOrFPGA(route.query.plant_type)
    const crudColumns = ref([
        {
            title: "ID",
            width: 60,
            align: "center",
            hide: true,
            dataIndex: "id",
            fixed: "left",
            display: false
        },
        {
            title: "用例标识",
            dataIndex: "ident",
            sortable: { sortDirections: ["ascend"] },
            width: 180,
            align: "center",
            addDisabled: true,
            disabled: true,
            addDefaultValue: "用例标识自动生成，结构为YL_IO_XXXX_001",
            editDefaultValue: "用例标识自动生成，结构为YL_IO_XXXX_001",
            editDisabled: true,
            search: true,
            searchPlaceholder:"仅搜索标识字母，不要搜索YL、SU、-、001等字样",
            validateTrigger: "blur-sm"
        },
        {
            title: "名称",
            dataIndex: "name",
            align: "center",
            search: true,
            commonRules: [{ required: true, message: "名称是必填" }],
            validateTrigger: "blur-sm"
        },
        {
            title: "是否通过",
            align: "center",
            display: false,
            addDisplay: false,
            editDisplay: false,
            customRender: ({ record }) => {
                let passCount = 0
                let failCount = 0
                let stepCount = record.testStep.length
                record.testStep.forEach((item) => {
                    if (item.passed === "1") {
                        passCount++
                    } else if (item.passed === "2") {
                        failCount++
                    }
                })
                if (failCount > 0) {
                    return (
                        <a-tag bordered color="red">
                            未通过
                        </a-tag>
                    )
                } else {
                    if (passCount === stepCount) {
                        return (
                            <a-tag bordered color="green">
                                已通过
                            </a-tag>
                        )
                    } else {
                        return (
                            <a-tag bordered color="orange">
                                包含未执行
                            </a-tag>
                        )
                    }
                }
            }
        },
        {
            title: "设计人员",
            width: 80,
            dataIndex: "designPerson",
            align: "center",
            hide: true,
            search: true,
            formType: "select",
            dict: {
                url: "system/user/list",
                params: { project_id: route.query.id },
                translation: true,
                props: { label: "name", value: "name" }
            }
        },
        {
            title: "执行人员",
            dataIndex: "testPerson",
            width: 120,
            align: "center",
            search: true,
            formType: "select",
            dict: {
                url: "system/user/list",
                params: { project_id: route.query.id },
                translation: true,
                props: { label: "name", value: "name" }
            }
        },
        {
            title: "审核人员",
            dataIndex: "monitorPerson",
            width: 80,
            align: "center",
            hide: true,
            formType: "select",
            dict: {
                url: "system/user/list",
                params: { project_id: route.query.id },
                translation: true,
                props: { label: "name", value: "name" }
            }
        },
        {
            title: "用例综述",
            align: "center",
            dataIndex: "summarize",
            hide: true,
            search: true,
            addDefaultValue: ""
        },
        {
            title: "用例初始化",
            dataIndex: "initialization",
            hide: true,
            addDefaultValue: "软件正常启动，正常登录进软件"
        },
        {
            title: "前提和约束",
            dataIndex: "premise",
            hide: true,
            addDefaultValue: "软件正常启动，各界面显示工作正常"
        },
        {
            title: "执行时间",
            align: "center",
            dataIndex: "exe_time",
            formType: "date",
            customRender: ({ record }) => {
                // 如果不存在exe_time则显示为“没有设置”
                return record.exe_time ? record.exe_time : <a-tag color="red">未填写</a-tag>
            }
        },
        {
            title: "时序图(cpu不填写此字段)",
            hide: true,
            dataIndex: "timing_diagram",
            addDefaultValue: "",
            formType: "editor",
            display: !isFPGA,
            editDisplay: !isFPGA,
            addDisplay: !isFPGA
        },
        {
            title: "测试步骤",
            dataIndex: "testStep",
            hide: true,
            addDefaultValue: [
                {
                    operation: "",
                    expect: "",
                    result: "",
                    passed: "3"
                }
            ],
            formType: "children-form",
            type: "table", // 注意这里可能改样式"group"/"table"
            formList: [
                {
                    title: "操作",
                    dataIndex: "operation",
                    formType: "editor",
                    height: 180,
                    width: 360
                },
                {
                    title: "预期",
                    placeholder: "请输入预期结果",
                    dataIndex: "expect",
                    formType: "textarea",
                    width: 160
                },
                {
                    title: "结果",
                    dataIndex: "result",
                    formType: "editor",
                    height: 400
                },
                {
                    title: "是否通过",
                    dataIndex: "passed",
                    formType: "radio",
                    dict: { name: "passType", props: { label: "title", value: "key" } },
                    commonRules: [{ required: true, message: "是否通过必填" }],
                    width: 128
                }
            ]
        },
        {
            title: "关联问题",
            dataIndex: "problem",
            width: 150,
            addDisplay: false,
            editDisplay: false,
            align: "center",
            display: false,
            customRender: ({ record }) => {
                if (record.problem) {
                    return (
                        <a-link
                            onClick={() => {
                                title.value = `PT_${route.query.ident}_${record.problem.ident.padStart(3, 0)}`
                                problemFormRef.value.open(record.problem)
                            }}
                        >{`PT_${route.query.ident}_${record.problem.ident.padStart(3, 0)}`}</a-link>
                    )
                } else {
                    return "无问题单"
                }
            }
        }
    ])
    return crudColumns
}
