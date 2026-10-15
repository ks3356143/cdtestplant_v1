export const columnsOptions = [
    { title: "ID", dataIndex: "id", addDisplay: false, editDisplay: false, width: 50, hide: true },
    {
        title: "缩略语",
        align: "center",
        width: 200,
        dataIndex: "title",
        search: true,
        commonRules: [{ required: true, message: "缩略语必填" }]
    },
    {
        title: "全称",
        align: "center",
        dataIndex: "des",
        search: true,
        ellipsis: true,
        commonRules: [{ required: true, message: "全称和描述必填" }]
    }
]
