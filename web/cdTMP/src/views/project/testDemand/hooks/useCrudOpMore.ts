import { ref, getCurrentInstance, type Ref } from "vue"
import MaCrud from "@/components/ma-crud/index.vue"
import { useRoute } from "vue-router"
import caseApi from "@/api/project/case"
import { useTreeDataStore } from "@/store"
import { isEqual, cloneDeep } from "lodash-es"
/**
 * 用例的Crud Init
 */
export default function (crudRef: Ref<InstanceType<typeof MaCrud>>) {
    // globals
    const route = useRoute() as any
    const projectId = ref(route.query.id)
    const treeDataStore = useTreeDataStore()
    // 刷新/直链时 key 可能缺失，统一兜底，避免 setup 阶段抛错整页白屏
    const keyParts = String(route.query.key ?? "").split("-")
    const roundNumber = keyParts[0]
    const dutNumber = keyParts[1]
    const designDemandNumber = keyParts[2]
    const testDemandNumber = keyParts[3]
    // 按树节点下标取标题；树未加载到该层级时返回占位符，避免 undefined.title
    const nodeTitle = (path: string[], fallback = "-") => {
        let node: any = treeDataStore.treeData
        for (const idx of path) {
            node = node?.[Number(idx)]
            if (!node) return fallback
        }
        return node.title ?? fallback
    }
    // 辅助
    const app = getCurrentInstance()!.appContext.config.globalProperties
    let beforeFormStep = undefined
    // 注意只保留测试步骤!!!
    const handleBeforeCancel = () => {
        if (!beforeFormStep) {
            return
        }
        const iuEqualValue = isEqual(crudRef.value.getFormData().testStep, beforeFormStep)
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
    // refs
    const crudOptions = ref({
        api: caseApi.getCaseList,
        add: { show: true, api: caseApi.save, text: "新增用例" },
        edit: { show: true, api: caseApi.update, text: "修改用例" },
        delete: { show: true, api: caseApi.delete },
        operationColumnAlign: "center",
        isDbClickEdit: true, // 关闭双击编辑
        // 处理新增删除后树状图显示
        beforeOpenAdd: function () {
            // 1.新增则将form的content数据变为undifined以便判断
            beforeFormStep = undefined
            // 2.标识处理
            let round_key = keyParts[0]
            let dut_key = keyParts[1]
            let design_key = keyParts[2]
            let test_key = keyParts[3]
            crudRef.value.crudFormRef.actionTitle = `${route.query.ident ?? ""} >
            ${nodeTitle([round_key])} > ${nodeTitle([round_key, dut_key])} >
            ${nodeTitle([round_key, dut_key, design_key])} >
            ${nodeTitle([round_key, dut_key, design_key, test_key])} > 用例-`
            return true
        },
        beforeOpenEdit: function (record) {
            // 1.储存打开前form的content数据到ref中，以便后续比较
            beforeFormStep = cloneDeep(record.testStep)
            // 2.标识处理
            let round_key = keyParts[0]
            let dut_key = keyParts[1]
            let design_key = keyParts[2]
            let test_key = keyParts[3]
            crudRef.value.crudFormRef.actionTitle = `${route.query.ident ?? ""} >
            ${nodeTitle([round_key])} > ${nodeTitle([round_key, dut_key])} >
            ${nodeTitle([round_key, dut_key, design_key])} >
            ${nodeTitle([round_key, dut_key, design_key, test_key])}
            >用例[${record.name}]-`
            return true
        },
        afterAdd: (res) => {
            let id = projectId.value
            treeDataStore.updateCaseTreeData(res.data, id)
        },
        afterEdit: (res) => {
            let id = projectId.value
            treeDataStore.updateCaseTreeData(res.data, id)
        },
        afterDelete: (res, record) => {
            let id = projectId.value
            if (!record) {
                record = { key: String(route.query.key ?? "") + "-X" }
            }
            treeDataStore.updateCaseTreeData(record, id)
            // 被删除还是在选择里面
            crudRef.value.tableRef?.selectAll(false)
        },
        parameters: {
            projectId: route.query.id,
            round: roundNumber,
            dut: dutNumber,
            designDemand: designDemandNumber,
            testDemand: testDemandNumber
        },
        showIndex: false,
        rowSelection: { showCheckedAll: true },
        searchColNumber: 3,
        tablePagination: false,
        draggable: false,
        operationColumnWidth: 180,
        operationColumn: true,
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
                    formType: "card",
                    customClass: ["ml-5", "mb-3", "py-0", "px-0"],
                    title: "人员信息",
                    formList: [
                        {
                            formType: "grid",
                            cols: [
                                { span: 8, formList: [{ dataIndex: "designPerson" }] },
                                { span: 8, formList: [{ dataIndex: "testPerson" }] },
                                { span: 8, formList: [{ dataIndex: "monitorPerson" }] }
                            ]
                        }
                    ]
                },
                {
                    formType: "grid",
                    cols: [{ span: 24, formList: [{ dataIndex: "summarize" }] }]
                },
                {
                    formType: "grid",
                    cols: [{ span: 24, formList: [{ dataIndex: "initialization" }] }]
                },
                {
                    formType: "grid",
                    cols: [
                        { span: 12, formList: [{ dataIndex: "premise" }] },
                        { span: 12, formList: [{ dataIndex: "exe_time" }] }
                    ]
                }
            ]
        }
    })
    return { handleBeforeCancel, crudOptions }
}
