import type { Ref } from "vue"
import { cloneDeep } from "lodash-es"

export default function useDataOperation(datas: Ref<any[]>) {
    const newRow = {
        id: Date.now().toString(),
        change_type: "",
        change_des: "",
        effect_cases: []
    }
    const handleChange = (_data: any) => {
        datas.value = _data
    }
    const addRow = (rowIndex: number) => {
        const insertIndex = rowIndex === -1 ? datas.value!.length : rowIndex + 1
        const rowToAdd = {
            ...cloneDeep(newRow),
            id: `row_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
        }
        datas.value!.splice(insertIndex, 0, rowToAdd)
    }
    const deleteRow = (rowIndex: number) => {
        if (rowIndex < 0 || rowIndex >= datas.value!.length) return
        datas.value!.splice(rowIndex, 1)
    }
    return { handleChange, addRow, deleteRow }
}
