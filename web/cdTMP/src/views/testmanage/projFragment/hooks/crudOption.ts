import { useRoute } from "vue-router"
import { ref } from "vue"
import { FragApi } from "@/api/system/fragment"
import { IFragSearchCondition } from "@/api/system/types/fragmentTypes"
import {
    fragmentName,
    TestObjectHTML,
    StaticEnvHTML,
    StaticSoftHTML,
    StaticHardHTML,
    DynamicEnvHTML,
    DynamicSoftHTML,
    DynamicHardHTML,
    TestDataHTML,
    EnvDiffHTML,
    TestLevelAndTypeHTML
} from "@/views/testmanage/projFragment/constants"
import { TestStrategyHTML } from "@/views/testmanage/projFragment/constantsExtra"

// 片段名 → 预制内容模版（与 fragmentName 枚举一一对应）
const fragmentTemplateMap: Record<string, string> = {
    [fragmentName.TestObject]: TestObjectHTML,
    [fragmentName.StaticEnv]: StaticEnvHTML,
    [fragmentName.StaticSoft]: StaticSoftHTML,
    [fragmentName.StaticHard]: StaticHardHTML,
    [fragmentName.DynamicEnv]: DynamicEnvHTML,
    [fragmentName.DynamicSoft]: DynamicSoftHTML,
    [fragmentName.DynamicHard]: DynamicHardHTML,
    [fragmentName.TestData]: TestDataHTML,
    [fragmentName.EnvDiff]: EnvDiffHTML,
    [fragmentName.TestLevelAndType]: TestLevelAndTypeHTML,
    [fragmentName.TestStrategy]: TestStrategyHTML
}

const useCrudOption = () => {
    // global
    const route = useRoute()
    const crudRef = ref()
    // 5.下拉框v-model的值
    const selectedValue = ref<string>(fragmentName.NotSelect)
    // crud-options
    const crudOptions = ref<object>({
        api: FragApi.getFragList,
        add: { show: true, api: FragApi.add },
        edit: { show: true, api: FragApi.update },
        delete: { show: true, api: FragApi.delete },
        // 功能：预制文档片段数据
        beforeOpenAdd: () => {
            const columnsService = crudRef.value.getColumnService()
            // 根据所选片段预制「名称」与「内容」默认值
            const name = selectedValue.value === fragmentName.NotSelect ? "" : selectedValue.value
            const content = fragmentTemplateMap[selectedValue.value] ?? ""
            columnsService.get("name").setAttr("addDefaultValue", name)
            columnsService.get("content").setAttr("addDefaultValue", content)
            return true
        },
        // 新增需要项目id
        parameters: {
            projectId: route.params.projectId as string
        },
        beforeRequest: (params: IFragSearchCondition) => {
            // 添加项目id参数
            params.projectId = route.params.projectId as string
        },
        afterDelete(response: any) {
            crudRef.value.tableRef.selectAll(false)
        },
        operationColumn: true,
        operationColumnWidth: 180,
        operationColumnAlign: "center",
        bordered: { wrapper: true, cell: true },
        resizable: false, // 不允许调整列宽
        rowSelection: { showCheckedAll: true, checkStrictly: true },
        isDbClickEdit: false,
        searchColNumber: 2,
        formOption: {
            isFull: false,
            width: "80%",
            layout: [
                {
                    formType: "grid",
                    cols: [{ span: 6, formList: [{ dataIndex: "name" }] }]
                }
            ]
        }
    })
    const crudColumns = ref<any[]>([
        {
            title: "ID",
            align: "center",
            width: 50,
            hide: true,
            dataIndex: "id",
            commonRules: [{ required: true, message: "ID必填" }],
            validateTrigger: "blur-sm"
        },
        {
            title: "片段名称",
            align: "center",
            width: 180,
            dataIndex: "name",
            search: true,
            commonRules: [{ required: true, message: "片段名称必填" }],
            validateTrigger: "blur-sm"
        },
        {
            title: "替换片段",
            width: 100,
            align: "center",
            dataIndex: "is_main",
            addDisplay: false,
            editDisplay: false
        },
        {
            title: "内容",
            align: "center",
            dataIndex: "content",
            hide: true,
            formType: "editor",
            height: 550
        }
    ])

    return {
        crudRef,
        crudOptions,
        crudColumns,
        route,
        selectedValue
    }
}

export default useCrudOption
