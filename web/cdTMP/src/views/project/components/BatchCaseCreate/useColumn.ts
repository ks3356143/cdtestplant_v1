import { TableColumnData } from "@arco-design/web-vue"

import { ref } from "vue"

export default function () {
    const caseColumns = ref<TableColumnData[]>([
        {
            title: "序号",
            align: "center",
            dataIndex: "xuhao",
            slotName: "xuhao",
            width: 50
        },
        {
            title: "所属测试项(必填)",
            dataIndex: "parent_key",
            align: "center",
            slotName: "parent_key",
            width: 300
        },
        {
            title: "名称(必填)",
            dataIndex: "name",
            align: "center",
            slotName: "name",
            width: 250
        },
        {
            title: "用例初始化",
            dataIndex: "initialization",
            align: "center",
            slotName: "initialization",
            width: 300
        },
        {
            title: "前提和约束",
            dataIndex: "premise",
            align: "center",
            slotName: "premise",
            width: 350
        },
        {
            title: "用例综述",
            dataIndex: "summarize",
            align: "center",
            slotName: "summarize",
            width: 450
        },
        {
            title: "测试步骤-快捷步骤录入字符串(必填)",
            dataIndex: "test_step",
            align: "center",
            slotName: "test_step"
        },
        {
            title: "时序图",
            dataIndex: "sequence",
            align: "center",
            slotName: "sequence",
            width: 500
        },
        {
            title: "操作",
            dataIndex: "caozuo",
            align: "center",
            slotName: "caozuo",
            width: 250,
            fixed: "right"
        }
    ])

    return { caseColumns }
}
