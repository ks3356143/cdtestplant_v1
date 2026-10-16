<template>
    <div class="ma-content-block lg:flex justify-between p-4">
        <div class="lg:w-full w-full lg:ml-4 mt-5 lg:mt-0">
            <!-- crud组件 -->
            <ma-crud :options="crudOptions" :columns="crudColumns" ref="crudRef">
                <template #create_datetime="{ record }">
                    {{ record.create_datetime.split(".")[0].replace("T", " ") }}
                </template>
                <template #tableBeforeButtons>
                    <a-button type="primary" status="warning" @click="handleDeleteLogButton"
                        ><template #icon> <icon-delete /> </template>删除30天前数据</a-button
                    >
                </template>
            </ma-crud>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import operationApi from "@/api/monitor/operationLog"
import { Message } from "@arco-design/web-vue"

const crudRef = ref()
const crudOptions = reactive({
    api: operationApi.getOperationsLogs,
    showIndex: false,
    pageLayout: "fixed",
    tablePagination: false,
    bordered: { wrapper: true, cell: true },
    afterDelete(response) {
        crudRef.value.tableRef.selectAll(false)
    }
})
const crudColumns = reactive([
    { title: "ID", dataIndex: "id", addDisplay: false, editDisplay: false, width: 50, hide: true },
    { title: "用户", dataIndex: "user", search: true, align: "center" },
    { title: "操作对象", dataIndex: "operate_obj", align: "center" },
    { title: "操作内容", dataIndex: "operate_des", align: "center" },
    { title: "时间", dataIndex: "create_datetime", align: "center", search: true, formType: "range" }
])
// 删除日志按钮事件处理函数（审计日志保护：仅可清理30天前数据，禁全清）
const handleDeleteLogButton = async () => {
    const res = await operationApi.deleteOperationLogs({ day: 30 }) // 只能清理保留期外的日志
    if (res.data || res.message) Message.success(res.message || "清理成功")
    else Message.error("清理被拒绝")
    crudRef.value.refresh()
}

defineOptions({
    name: "operationLog"
})
</script>

<style lang="less" scoped></style>
