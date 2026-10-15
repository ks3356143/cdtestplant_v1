import { ref, computed } from "vue"
import tool from "@/utils/tool"
import useColumn from "../hooks/useColumn"

// Case用例在这里设置不同ma-form选项
export default function useOptions(formRef: any) {
    const options = ref({
        showButtons: false,
        labelAlign: "center"
    })
    const crudColumns = useColumn(formRef)
    const columnOptions = computed(() => {
        // 处理表单布局
        const transformColumns = tool.renameKeyInArray(crudColumns.value, "commonRules", "rules")
        // 取出字段column对象
        const identColumn = transformColumns.find((item: any) => item.dataIndex === "ident")
        const nameColumn = transformColumns.find((item: any) => item.dataIndex === "name")
        const designPersonColumn = transformColumns.find((item: any) => item.dataIndex === "designPerson")
        const testPersonColumn = transformColumns.find((item: any) => item.dataIndex === "testPerson")
        const monitorPersonColumn = transformColumns.find((item: any) => item.dataIndex === "monitorPerson")
        const summarizeColumn = transformColumns.find((item: any) => item.dataIndex === "summarize")
        const initializationColumn = transformColumns.find((item: any) => item.dataIndex === "initialization")
        const premiseColumn = transformColumns.find((item: any) => item.dataIndex === "premise")
        const exe_timeColumn = transformColumns.find((item: any) => item.dataIndex === "exe_time")
        // 组装表单布局
        const identAndNameColumn = {
            formType: "grid",
            cols: [
                { span: 12, formList: [identColumn] },
                { span: 12, formList: [nameColumn] }
            ]
        }
        const cardColumn = {
            formType: "card",
            customClass: ["ml-5", "mb-3", "py-0", "px-0"],
            title: "人员信息",
            formList: [
                {
                    formType: "grid",
                    cols: [
                        { span: 8, formList: [designPersonColumn] },
                        { span: 8, formList: [testPersonColumn] },
                        { span: 8, formList: [monitorPersonColumn] }
                    ]
                }
            ]
        }
        const summarizeColumnNew = {
            formType: "grid",
            cols: [{ span: 24, formList: [summarizeColumn] }]
        }
        const initializationColumnNew = {
            formType: "grid",
            cols: [{ span: 24, formList: [initializationColumn] }]
        }
        const premiseAndExeColumn = {
            formType: "grid",
            cols: [
                { span: 12, formList: [premiseColumn] },
                { span: 12, formList: [exe_timeColumn] }
            ]
        }
        // 取除原数组里面的内容
        const newColumnsArray = transformColumns.filter(
            (it: any) =>
                it.dataIndex !== "ident" &&
                it.dataIndex !== "name" &&
                it.dataIndex !== "designPerson" &&
                it.dataIndex !== "testPerson" &&
                it.dataIndex !== "monitorPerson" &&
                it.dataIndex !== "summarize" &&
                it.dataIndex !== "initialization" &&
                it.dataIndex !== "premise" &&
                it.dataIndex !== "exe_time"
        )
        newColumnsArray.unshift(
            identAndNameColumn,
            cardColumn,
            summarizeColumnNew,
            initializationColumnNew,
            premiseAndExeColumn
        )
        return newColumnsArray
    })

    return { options, columnOptions }
}
