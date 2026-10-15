import { ref } from "vue"
import dictApi from "@/api/system/dict"
import { Message } from "@arco-design/web-vue"
/**
 * dict主页面展示配置以及ref定义
 */
export default function useDictCrud() {
    // refs
    const crudRef = ref()
    // 事件函数
    const changeStatus = async (status: string, id: number) => {
        // 点击切换status
        try {
            const response = await dictApi.changeStatus({ id, status })
            if (response.success) {
                Message.success(response.message)
            }
        } catch (err) {
            return
        }
    }
    // crud定义
    const crudOptions = ref({
        api: dictApi.getDictIndex,
        showIndex: false,
        operationColumnAlign: "center",
        rowSelection: { showCheckedAll: true },
        searchColNumber: 4,
        tablePagination: false,
        operationColumn: true,
        afterDelete() {
            crudRef.value.tableRef.selectAll(false)
        }
    })
    const crudColumns = ref([
        { title: "ID", dataIndex: "id", addDisplay: false, editDisplay: false, width: 50, hide: true },
        {
            title: "字典备注",
            dataIndex: "remark",
            search: true,
            width: 220,
            align: "center",
            commonRules: [{ required: true, message: "字典备注必填" }]
        },
        {
            title: "字典标识",
            dataIndex: "code",
            search: true,
            width: 260,
            align: "center",
            commonRules: [{ required: true, message: "字典标识必填" }]
        },
        {
            title: "状态",
            dataIndex: "status",
            search: true,
            hide: true,
            formType: "radio",
            align: "center",
            dict: { name: "data_status", props: { label: "title", value: "key" } },
            addDefaultValue: "1",
            width: 180
        },
        {
            title: "字典名称",
            dataIndex: "name",
            hide: true,
            formType: "textarea",
            align: "center"
        },
        {
            title: "更新时间",
            dataIndex: "update_datetime",
            addDisplay: false,
            editDisplay: false,
            align: "center",
            search: true,
            formType: "range",
            width: 180
        }
    ])
    return {
        crudRef,
        changeStatus,
        crudOptions,
        crudColumns
    }
}
