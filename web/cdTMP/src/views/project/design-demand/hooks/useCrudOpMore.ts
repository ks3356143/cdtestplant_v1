import MaCrud from "@/components/ma-crud/index.vue"
import { type Ref, ref, getCurrentInstance } from "vue"
import testDemandApi from "@/api/project/testDemand"
import { useRoute } from "vue-router"
import { useTreeDataStore } from "@/store"
import { cloneDeep, isEqual } from "lodash-es"
// types
interface ITestContent {
    subName: string
    subDesc: string
}
/**
 * 测试项表格的Crud-options
 */
export default function (crudRef: Ref<InstanceType<typeof MaCrud>>) {
    // global
    const treeDataStore = useTreeDataStore()
    const route = useRoute() as any
    //  variable
    const roundNumber = (route.query.key as string)!.split("-")[0]
    const dutNumber = (route.query.key as string)!.split("-")[1]
    const designDemandNumber = (route.query.key as string)!.split("-")[2]
    // refs
    const projectId = ref(route.query.id)
    // 处理弹窗关闭事件:处理用户数据是否保留
    const app = getCurrentInstance()!.appContext.config.globalProperties
    let beforeFormContent: ITestContent[] | undefined = undefined
    const handleBeforeCancel = () => {
        if (!beforeFormContent) {
            return
        }
        const iuEqualValue = isEqual(crudRef.value.getFormData().testContent, beforeFormContent)
        !iuEqualValue &&
            app.$modal.confirm({
                title: "测试项步骤内容你已改动，是否保留您编写的测试项/测试用例步骤数据？",
                content: "",
                okText: "保留",
                cancelText: "恢复原数据",
                simple: true,
                onOk: () => null,
                onCancel: () => {
                    crudRef.value.refresh()
                }
            })
    }
    const crudOptions = ref({
        api: testDemandApi.getTestDemandList,
        add: { show: true, api: testDemandApi.save, text: "新增测试项" },
        edit: { show: true, api: testDemandApi.update, text: "修改测试项" },
        delete: { show: true, api: testDemandApi.delete },
        beforeOpenAdd: function () {
            // 1.新增则将form的content数据变为undifined以便判断
            beforeFormContent = undefined
            // 2.设置标识
            let key_split = (route.query.key as string)!.split("-")
            let round_key = key_split[0]
            let dut_key = key_split[1]
            let design_key = key_split[2]
            let td = treeDataStore.treeData
            crudRef.value.crudFormRef.actionTitle = `${route.query.ident} > ${td[round_key].title} > ${td[round_key].children[dut_key].title} > ${td[round_key].children[dut_key].children[design_key].title} > 测试项-`
            return true
        },
        beforeOpenEdit: function (record: any) {
            // 1.储存打开前form的content数据到ref中，以便后续比较
            beforeFormContent = cloneDeep(record.testContent)
            // 2.处理标识
            let key_split = (route.query.key as string)!.split("-")
            let round_key = key_split[0]
            let dut_key = key_split[1]
            let design_key = key_split[2]
            let td = treeDataStore.treeData
            crudRef.value.crudFormRef.actionTitle = `${route.query.ident} > ${td[round_key].title} > ${td[round_key].children[dut_key].title} > ${td[round_key].children[dut_key].children[design_key].title} >测试项[${record.name}]-`
            return true
        },
        afterAdd: (res: any) => {
            let id = projectId.value
            treeDataStore.updateTestDemandTreeData(res.data, id)
        },
        afterEdit: (res: any) => {
            let id = projectId.value
            treeDataStore.updateTestDemandTreeData(res.data, id)
        },
        afterDelete: (_: any, record: any) => {
            let id = projectId.value
            if (!record) {
                record = { key: route.query.key + "-X" }
            }
            treeDataStore.updateTestDemandTreeData(record, id)
            // 清空选择
            crudRef.value.tableRef.selectAll(false)
        },
        parameters: {
            projectId: route.query.id,
            round: roundNumber,
            dut: dutNumber,
            designDemand: designDemandNumber
        },
        showIndex: false,
        rowSelection: { showCheckedAll: true },
        searchColNumber: 3,
        tablePagination: false,
        operationColumnWidth: 200,
        operationColumn: true,
        draggable: false,
        operationColumnAlign: "center",
        formOption: {
            width: "86%",
            layout: [
                {
                    formType: "grid",
                    cols: [
                        { span: 12, formList: [{ dataIndex: "ident" }] },
                        { span: 12, formList: [{ dataIndex: "name" }] }
                    ]
                },
                {
                    formType: "grid",
                    cols: [{ span: 24, formList: [{ dataIndex: "priority" }] }]
                },
                {
                    formType: "grid",
                    cols: [
                        { span: 12, formList: [{ dataIndex: "testType" }] },
                        { span: 12, formList: [{ dataIndex: "testMethod" }] }
                    ]
                }
            ]
        }
    })
    return { projectId, crudOptions, handleBeforeCancel }
}
