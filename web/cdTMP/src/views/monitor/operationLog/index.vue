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
                        ><template #icon> <icon-delete /> </template>删除7天前数据</a-button
                    >
                    <a-button type="primary" status="danger" @click="handleDeleteAllLogButton"
                        ><template #icon> <icon-delete /> </template>删除全部日志</a-button
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
// 删除日志按钮事件处理函数
const handleDeleteLogButton = async () => {
    const res = await operationApi.deleteOperationLogs() // 参数：{day:4}保留4天内的日志
    Message.success(res.message)
}
const handleDeleteAllLogButton = async () => {
    const res = await operationApi.deleteOperationLogs({ day: 0 }) // 0表示删除全部日志
    crudRef.value.refresh()
    Message.success(res.message)
}

defineOptions({
    name: "operationLog"
})
</script>

<style lang="less" scoped></style>
