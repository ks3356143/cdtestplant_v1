import { ref } from "vue"

export default function () {
    const columns = ref([
        {
            title: "名称",
            dataIndex: "name",
            slotName: "name",
            align: "left",
            hide: false,
            width: 250,
            fixed: ""
        },
        {
            title: "问题标识",
            dataIndex: "ident",
            slotName: "ident",
            align: "center",
            hide: false,
            width: 150,
            fixed: ""
        },
        {
            title: "缺陷状态",
            dataIndex: "problemStatu",
            slotName: "problemStatu",
            align: "center",
            hide: false,
            width: 100,
            fixed: "",
            formType: "select",
            dict: true
        },
        {
            title: "缺陷等级",
            dataIndex: "problemGrade",
            slotName: "problemGrade",
            align: "center",
            hide: false,
            width: 100,
            fixed: "",
            formType: "select",
            dict: true
        },
        {
            title: "问题描述",
            dataIndex: "operation",
            slotName: "operation",
            align: "left",
            hide: false,
            isHyperText: true,
            fixed: ""
        }
    ])

    return { columns }
}
