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
            //
            switch (selectedValue.value) {
                case fragmentName.NotSelect:
                    columnsService.get("name").setAttr("addDefaultValue", "")
                    columnsService.get("content").setAttr("addDefaultValue", "")
                    break
                case fragmentName.TestObject:
                    columnsService.get("name").setAttr("addDefaultValue", fragmentName.TestObject)
                    columnsService.get("content").setAttr("addDefaultValue", TestObjectHTML)
                    break
                case fragmentName.StaticEnv:
                    columnsService.get("name").setAttr("addDefaultValue", fragmentName.StaticEnv)
                    columnsService.get("content").setAttr("addDefaultValue", StaticEnvHTML)
                    break
                case fragmentName.StaticSoft:
                    columnsService.get("name").setAttr("addDefaultValue", fragmentName.StaticSoft)
                    columnsService.get("content").setAttr("addDefaultValue", StaticSoftHTML)
                    break
                case fragmentName.StaticHard:
                    columnsService.get("name").setAttr("addDefaultValue", fragmentName.StaticHard)
                    columnsService.get("content").setAttr("addDefaultValue", StaticHardHTML)
                    break
                case fragmentName.DynamicEnv:
                    columnsService.get("name").setAttr("addDefaultValue", fragmentName.DynamicEnv)
                    columnsService.get("content").setAttr("addDefaultValue", DynamicEnvHTML)
                    break
                case fragmentName.DynamicSoft:
                    columnsService.get("name").setAttr("addDefaultValue", fragmentName.DynamicSoft)
                    columnsService.get("content").setAttr("addDefaultValue", DynamicSoftHTML)
                    break
                case fragmentName.DynamicHard:
                    columnsService.get("name").setAttr("addDefaultValue", fragmentName.DynamicHard)
                    columnsService.get("content").setAttr("addDefaultValue", DynamicHardHTML)
                    break
                case fragmentName.TestData:
                    columnsService.get("name").setAttr("addDefaultValue", fragmentName.TestData)
                    columnsService.get("content").setAttr("addDefaultValue", TestDataHTML)
                    break
                case fragmentName.EnvDiff:
                    columnsService.get("name").setAttr("addDefaultValue", fragmentName.EnvDiff)
                    columnsService.get("content").setAttr("addDefaultValue", EnvDiffHTML)
                    break
                case fragmentName.TestLevelAndType:
                    columnsService.get("name").setAttr("addDefaultValue", fragmentName.TestLevelAndType)
                    columnsService.get("content").setAttr("addDefaultValue", TestLevelAndTypeHTML)
                    break
                case fragmentName.TestStrategy:
                    columnsService.get("name").setAttr("addDefaultValue", fragmentName.TestStrategy)
                    columnsService.get("content").setAttr("addDefaultValue", TestStrategyHTML)
                    break
                default:
                    break
            }
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
