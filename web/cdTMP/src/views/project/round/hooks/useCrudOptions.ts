import MaCrud from "@/components/ma-crud/index.vue"
import { type Ref, ref } from "vue"
import dutApi from "@/api/project/dut"
import { useRoute } from "vue-router"
import { useTreeDataStore } from "@/store"
/**
 * Dut被测件的crud选项
 */
export default function (crudRef: Ref<InstanceType<typeof MaCrud>>) {
    // globals
    const route = useRoute()
    const projectId = ref(route.query.id)
    const treeDataStore = useTreeDataStore()
    const roundNumber = (route.query.key as any).split("-")[0]
    // refs
    const crudOptions = {
        api: dutApi.getDutList,
        add: { show: true, api: dutApi.save, text: "新增被测件" },
        edit: { show: true, api: dutApi.update, text: "编辑被测件" },
        delete: { show: true, api: dutApi.delete },
        // 处理添加后函数
        beforeOpenAdd: function () {
            let round_str = parseInt(route.query.key as any) + 1
            crudRef.value.crudFormRef.actionTitle = `${route.query.ident}>第${round_str}轮>被测件-`
            return true
        },
        beforeOpenEdit: function (record) {
            let round_str = parseInt(route.query.key as any) + 1
            crudRef.value.crudFormRef.actionTitle = `${route.query.ident}>第${round_str}轮>被测件[${record.name}]-`
            return true
        },
        afterAdd: (res) => {
            let id = projectId.value
            treeDataStore.updateDutTreeData(res.data, id)
        },
        afterEdit: (res) => {
            let id = projectId.value
            treeDataStore.updateDutTreeData(res.data, id)
        },
        afterDelete: (res, record) => {
            let id = projectId.value
            if (!record) {
                record = { key: route.query.key + "-X" }
            }
            treeDataStore.updateDutTreeData(record, id)
            // 清空行选择器
            crudRef.value.tableRef.selectAll(false)
        },

        // 新增、编辑、删除均携带下面
        parameters: {
            projectId: route.query.id,
            round: roundNumber
        },
        operationWidth: 500,
        showIndex: false,
        rowSelection: { showCheckedAll: true },
        searchColNumber: 3,
        tablePagination: false,
        operationColumnWidth: 200, // 操作列宽度
        operationColumn: true,
        operationColumnAlign: "center",
        formOption: {
            viewType: "drawer",
            width: 600,
            mask: false
        }
    }
    return crudOptions
}
