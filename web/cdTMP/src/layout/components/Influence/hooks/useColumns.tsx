import type { TableColumnData } from "@arco-design/web-vue/es/table/interface"

export default function useColumns() {
    const columns: TableColumnData[] = [
        {
            title: "序号",
            dataIndex: "index",
            width: 80,
            align: "center",
            slotName: "index"
        },
        {
            title: "更改类型",
            dataIndex: "change_type",
            width: 180,
            align: "center",
            slotName: "changeType"
        },
        {
            title: "更改内容描述",
            dataIndex: "change_des",
            align: "left",
            slotName: "changeDes"
        },
        {
            title: "影响域分析",
            dataIndex: "change_influ",
            align: "left",
            slotName: "changeInflu"
        },
        {
            title: "影响用例",
            dataIndex: "effect_cases",
            align: "center",
            slotName: "effectCases",
            width: 180
        },
        {
            title: "操作",
            dataIndex: "operator",
            align: "center",
            slotName: "operator",
            width: 80
        }
    ]
    return { columns }
}
