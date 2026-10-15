import { ref, computed } from "vue"
import tool from "@/utils/tool"
import useColumn from "../hooks/useColumns"

// 设置不同ma-form选项
export default function useOptions(formRef?: any) {
    const options = ref({
        showButtons: false,
        labelAlign: "center"
    })
    const crudColumns = useColumn()
    const columnOptions = computed(() => {
        return tool.renameKeyInArray(crudColumns.value, "commonRules", "rules")
    })
    return { options, columnOptions }
}
