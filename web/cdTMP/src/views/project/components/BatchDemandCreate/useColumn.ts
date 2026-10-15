import { TableColumnData } from "@arco-design/web-vue"

import { ref } from "vue"

export default function () {
    const demandColumns = ref<TableColumnData[]>([
        {
            title: "序号",
            align: "center",
            dataIndex: "xuhao",
            slotName: "xuhao",
            width: 50
        },
        {
            title: "设计需求",
            dataIndex: "parent_key",
            align: "center",
            slotName: "parent_key",
            width: 300
        },
        {
            title: "标识(必填)",
            dataIndex: "ident",
            align: "center",
            slotName: "ident",
            width: 150
        },
        {
            title: "名称(必填)",
            dataIndex: "name",
            align: "center",
            slotName: "name",
            width: 250
        },
        {
            title: "优先级",
            dataIndex: "priority",
            align: "center",
            slotName: "priority",
            width: 120
        },
        {
            title: "充分性描述(必填)",
            dataIndex: "adequacy",
            align: "center",
            slotName: "adequacy",
            width: 300
        },
        {
            title: "测试手段",
            dataIndex: "testMethod",
            align: "center",
            slotName: "testMethod",
            width: 220
        },
        {
            title: "测试类型",
            dataIndex: "testType",
            align: "center",
            slotName: "testType",
            width: 200
        },
        {
            title: "测试项描述",
            dataIndex: "testDesciption",
            align: "center",
            slotName: "testDesciption",
            width: 350
        },
        {
            title: "测试子项(必填)",
            dataIndex: "testContent",
            align: "center",
            slotName: "testContent"
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

    return { demandColumns }
}
