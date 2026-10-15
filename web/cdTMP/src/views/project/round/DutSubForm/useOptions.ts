import { ref, computed } from "vue"
import tool from "@/utils/tool"
import useColumn from "../hooks/useColumn"

export default function useOptions(formRef: any) {
    const options = ref({
        showButtons: false,
        labelAlign: "center"
    })
    const crudColumns = useColumn(formRef)
    const columnOptions = computed(() => {
        return tool.renameKeyInArray(crudColumns.value, "commonRules", "rules")
    })
    return { options, columnOptions }
}
