import { ref, type Ref } from "vue"
import dictApi from "@/api/system/dict"
/**
 * 定义crud的ref以及其
 */
export default function useCrudRef(currentRow: Ref<{ id: number | string; name: string }>) {
    const crudRef = ref()
    // crud选项
    const crudOptions = ref({
        autoRequest: false,
        api: dictApi.getDictItemAll,
        showIndex: false,
        rowSelection: { showCheckedAll: true },
        operationColumn: true,
        operationWidth: 160,
        operationColumnAlign: "center",
        beforeAdd: (form: any) => {
            form.id = currentRow.value?.id
            return true
        },
        add: { show: true, api: dictApi.saveDictItem },
        edit: { show: true, api: dictApi.updateDictItemData },
        delete: { show: true, api: dictApi.realDeleteItem },
        afterDelete() {
            crudRef.value.tableRef.selectAll(false)
        }
    })

    // crudColumns
    const columns = ref([
        { title: "ID", dataIndex: "id", addDisplay: false, editDisplay: false, width: 50, hide: true },
        {
            title: "字典标签",
            align: "center",
            dataIndex: "title",
            search: true,
            width: 150,
            commonRules: [{ required: true, message: "字典标签必填" }]
        },
        {
            title: "字段缩写",
            dataIndex: "show_title",
            align: "center",
            search: true
        },
        {
            title: "字典键值",
            align: "center",
            dataIndex: "key",
            addDisplay: false,
            editDisplay: false,
            search: true,
            commonRules: [{ required: true, message: "字典键值必填" }]
        },
        {
            title: "排序",
            align: "center",
            dataIndex: "sort",
            formType: "input-number",
            addDefaultValue: 1,
            width: 150,
            min: 0,
            max: 1000
        },
        {
            title: "状态",
            align: "center",
            dataIndex: "status",
            search: true,
            addDefaultValue: "1",
            formType: "radio",
            dict: { name: "data_status", props: { label: "title", value: "key" } },
            width: 70
        },
        {
            title: "备注",
            align: "center",
            dataIndex: "remark",
            hide: true,
            formType: "textarea"
        },
        {
            title: "更新时间",
            align: "center",
            dataIndex: "update_datetime",
            addDisplay: false,
            editDisplay: false,
            search: true,
            formType: "range",
            width: 110
        },
        {
            title: "文档名称",
            dataIndex: "doc_name",
            align: "center",
            search: false,
            placeholder: "不是标准则不填"
        },
        {
            title: "发布日期",
            dataIndex: "publish_date",
            align: "center",
            search: false,
            placeholder: "不是标准则不填，该文档发布日期",
            formType: "date"
        },
        {
            title: "标准来源",
            dataIndex: "source",
            align: "center",
            search: false,
            placeholder: "不是标准则不填，文档发布机构"
        }
    ])

    return {
        crudRef,
        crudOptions,
        columns
    }
}
