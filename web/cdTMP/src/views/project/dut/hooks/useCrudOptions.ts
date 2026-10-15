import MaCrud from "@/components/ma-crud/index.vue"
import { type Ref, ref } from "vue"
import designDemandApi from "@/api/project/designDemand"
import { useRoute } from "vue-router"
import { useTreeDataStore } from "@/store"
/**
 * Dut被测件的crud选项
 */
export default function (crudRef: Ref<InstanceType<typeof MaCrud>>) {
    // globals
    const route = useRoute() as any
    const projectId = ref(route.query.id)
    const treeDataStore = useTreeDataStore()
    const roundNumber = (route.query.key as any).split("-")[0]
    const dutNumber = (route.query.key as any).split("-")[1]
    // refs
    const crudOptions = ref({
        api: designDemandApi.getDesignDemandList,
        add: { show: true, api: designDemandApi.save, text: "新增设计需求" },
        edit: { show: true, api: designDemandApi.editDesignDemand, text: "编辑设计需求" },
        delete: { show: true, api: designDemandApi.delete },
        // 处理添加后函数
        beforeOpenAdd: function () {
            let key_split = route.query.key.split("-")
            let round_key = key_split[0]
            let dut_key = key_split[1]
            let td = treeDataStore.treeData
            crudRef.value.crudFormRef.actionTitle = `${route.query.ident} > ${(td[round_key] as any).title} > ${(td[round_key] as any).children[dut_key].title} > 设计需求-`
            return true
        },
        beforeOpenEdit: function (record) {
            let key_split = route.query.key.split("-")
            let round_key = key_split[0]
            let dut_key = key_split[1]
            let td = treeDataStore.treeData
            crudRef.value.crudFormRef.actionTitle = `${route.query.ident} > ${(td[round_key] as any).title} > ${(td[round_key] as any).children[dut_key].title} >设计需求[${record.name}]-`
            return true
        },
        afterAdd: (res: any) => {
            let id = projectId.value
            treeDataStore.updateDesignDemandTreeData(res.data, id)
        },
        afterEdit: (res: any) => {
            let id = projectId.value
            treeDataStore.updateDesignDemandTreeData(res.data, id)
        },
        afterDelete: (_: any, record: any) => {
            let id = projectId.value
            if (!record) {
                record = { key: route.query.key + "-X" }
            }
            treeDataStore.updateDesignDemandTreeData(record, id)
            // 删除后情况行选择器
            crudRef.value.tableRef.selectAll(false)
        },
        parameters: {
            projectId: route.query.id,
            round: roundNumber,
            dut: dutNumber
        },
        showIndex: false,
        rowSelection: { showCheckedAll: true },
        searchColNumber: 4,
        tablePagination: false,
        operationColumnWidth: 300,
        operationColumn: true,
        operationColumnAlign: "center",
        formOption: {
            width: 1200
        }
    })
    return crudOptions
}
