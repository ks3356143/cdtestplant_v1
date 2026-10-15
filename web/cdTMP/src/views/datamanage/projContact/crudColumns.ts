export const columnsOptions = [
    { title: "ID", dataIndex: "id", addDisplay: false, editDisplay: false, width: 50, hide: true },
    { title: "公司编号", align: "center", dataIndex: "key", search: true, width: 70, formType: "input-number" },
    {
        title: "名称",
        align: "center",
        dataIndex: "name",
        search: true,
        commonRules: [{ required: true, message: "名称必填" }]
    },
    {
        title: "简称",
        align: "center",
        dataIndex: "refer_name",
        width: 200,
        search: true,
        commonRules: [{ required: true, message: "简称必填" }]
    },
    {
        title: "法人",
        align: "center",
        dataIndex: "entrust_person",
        search: true,
        width: 90,
        commonRules: [{ required: true, message: "法人必填" }]
    },
    {
        title: "地址",
        align: "center",
        dataIndex: "addr",
        search: true,
        commonRules: [{ required: true, message: "公司地址必填" }]
    }
]
