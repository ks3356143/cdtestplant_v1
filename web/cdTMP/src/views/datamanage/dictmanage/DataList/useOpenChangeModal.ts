import { ref, type Ref } from "vue"
import dictApi from "@/api/system/dict"
import { Message } from "@arco-design/web-vue"
import MaCrud from "@/components/ma-crud/index.vue"
/**
 * 1.打开该modal方法/改变状态/改变排序
 */
export default function useOpenChangeModal(crudRef: Ref<InstanceType<typeof MaCrud>>, currentRow: Ref<any>) {
    // refs
    const visible = ref(false)
    // 事件处理
    const changeSort = async (value: number, id: number): Promise<void> => {
        const response = await dictApi.numberOperation({ id, numberName: "sort", numberValue: value })
        response.success && Message.success(response.message)
        crudRef.value.refresh()
    }
    const changeStatus = async (status: number | string, id: number): Promise<void> => {
        const response = await dictApi.changeItemStatus({ id, status })
        if (response.success) {
            Message.success(response.message)
        }
    }
    // 定义该open方法并暴露给组件外部
    // 打开a-modal事件
    const open = (row: Ref<any>) => {
        currentRow.value = row
        // 调用固定方法请求数据
        crudRef.value.requestParams = { id: currentRow.value.id }
        crudRef.value.requestData()
        visible.value = true
        // 判断如果是行数据的code值为standard则不显示‘文档名称’‘发布来源’‘发布日期’,且表单也不显示
        // columnService可以动态设置表格列的属性!!!
        const columnService = crudRef.value.getColumnService()
        if (currentRow.value.code === "standard") {
            columnService.get("doc_name").setAttr("hide", false)
            columnService.get("publish_date").setAttr("hide", false)
            columnService.get("source").setAttr("hide", false)
            columnService.get("doc_name").setAttr("addDisplay", true)
            columnService.get("publish_date").setAttr("addDisplay", true)
            columnService.get("source").setAttr("addDisplay", true)
            columnService.get("doc_name").setAttr("editDisplay", true)
            columnService.get("publish_date").setAttr("editDisplay", true)
            columnService.get("source").setAttr("editDisplay", true)
        } else {
            columnService.get("doc_name").setAttr("hide", true)
            columnService.get("publish_date").setAttr("hide", true)
            columnService.get("source").setAttr("hide", true)
            columnService.get("doc_name").setAttr("addDisplay", false)
            columnService.get("publish_date").setAttr("addDisplay", false)
            columnService.get("source").setAttr("addDisplay", false)
            columnService.get("doc_name").setAttr("editDisplay", false)
            columnService.get("publish_date").setAttr("editDisplay", false)
            columnService.get("source").setAttr("editDisplay", false)
        }
    }

    return {
        visible,
        changeSort,
        changeStatus,
        open
    }
}
