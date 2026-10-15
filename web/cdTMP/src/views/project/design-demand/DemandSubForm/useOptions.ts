import { ref, computed } from "vue"
import tool from "@/utils/tool"
import useColumn from "../hooks/useColumns"

// demand在这里设置不同ma-form选项
export default function useOptions(formRef: any) {
    const options = ref({
        showButtons: false,
        labelAlign: "center"
    })
    const crudColumns = useColumn(formRef)
    const columnOptions = computed(() => {
        const transformColumns = tool.renameKeyInArray(crudColumns.value, "commonRules", "rules")
        // 针对测试项的布局优化
        // 取出所有字段
        const identColumn = transformColumns.find((item: any) => item.dataIndex === "ident")
        const nameColumn = transformColumns.find((item: any) => item.dataIndex === "name")
        const priorityColumn = transformColumns.find((item: any) => item.dataIndex === "priority")
        const testTypeColumn = transformColumns.find((item: any) => item.dataIndex === "testType")
        const testMethodColumn = transformColumns.find((item: any) => item.dataIndex === "testMethod")
        // 组装表单布局
        const identAndNameColumn = {
            formType: "grid",
            cols: [
                { span: 12, formList: [identColumn] },
                { span: 12, formList: [nameColumn] }
            ]
        }
        const priorityColumnNew = {
            formType: "grid",
            cols: [{ span: 24, formList: [priorityColumn] }]
        }
        const testTypeAndMethodColumn = {
            formType: "grid",
            cols: [
                { span: 12, formList: [testTypeColumn] },
                { span: 12, formList: [testMethodColumn] }
            ]
        }
        // 取除原数组里面的内容
        const newColumnsArray = transformColumns.filter(
            (it: any) =>
                it.dataIndex !== "ident" &&
                it.dataIndex !== "name" &&
                it.dataIndex !== "priority" &&
                it.dataIndex !== "testType" &&
                it.dataIndex !== "testMethod"
        )
        newColumnsArray.unshift(identAndNameColumn, priorityColumnNew, testTypeAndMethodColumn)
        return newColumnsArray
    })
    return { options, columnOptions }
}
