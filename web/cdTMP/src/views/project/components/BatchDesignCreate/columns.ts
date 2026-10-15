import { TableColumnData } from "@arco-design/web-vue"

export const designColumn: TableColumnData[] = [
    {
        title: "序号",
        align: "center",
        dataIndex: "xuhao",
        slotName: "xuhao",
        width: 80
    },
    {
        title: "标识",
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
        width: 200
    },
    {
        title: "章节号(必填)",
        dataIndex: "chapter",
        align: "center",
        slotName: "chapter",
        width: 150
    },
    {
        title: "类型(必填)",
        dataIndex: "demandType",
        align: "center",
        slotName: "demandType",
        width: 200
    },
    {
        title: "需求描述",
        dataIndex: "description",
        align: "center",
        slotName: "description",
    },
    {
        title: "操作",
        fixed: "right", // 固定右侧
        dataIndex: "caozuo",
        align: "center",
        slotName: "caozuo",
        width: 100
    }
]
