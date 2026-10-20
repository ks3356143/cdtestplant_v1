<template>
    <log-page :api="operationApi.getOperationsLogs" :columns="crudColumns" :delete-api="operationApi.deleteOperationLogs" />
</template>

<script setup>
import operationApi from "@/api/monitor/operationLog"
import LogPage from "@/views/monitor/components/LogPage.vue"

const crudColumns = [
    { title: "ID", dataIndex: "id", addDisplay: false, editDisplay: false, width: 50, hide: true },
    { title: "用户", dataIndex: "user", search: true, align: "center" },
    { title: "操作对象", dataIndex: "operate_obj", align: "center" },
    { title: "操作内容", dataIndex: "operate_des", align: "center" },
    { title: "时间", dataIndex: "create_datetime", align: "center", search: true, formType: "range" }
]

defineOptions({
    name: "operationLog"
})
</script>

<style lang="less" scoped></style>
