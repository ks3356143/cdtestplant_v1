<template>
    <log-page :api="logApi.getOperations" :columns="crudColumns" :delete-api="logApi.operationsDelete" show-detail />
</template>

<script setup>
import logApi from "@/api/monitor/operations"
import LogPage from "@/views/monitor/components/LogPage.vue"

const crudColumns = [
    { title: "ID", dataIndex: "id", addDisplay: false, editDisplay: false, width: 50, hide: true },
    { title: "操作用户", dataIndex: "request_username", search: true, align: "center" },
    { title: "请求方式", dataIndex: "request_method", align: "center" },
    { title: "IP", dataIndex: "request_ip", align: "center" },
    { title: "浏览器", dataIndex: "request_browser", align: "center" },
    { title: "响应状态码", dataIndex: "response_code", align: "center" },
    { title: "操作系统", dataIndex: "request_os", align: "center" },
    {
        title: "创建时间",
        dataIndex: "create_datetime",
        align: "center",
        width: 150,
        addDisplay: false,
        editDisplay: false
    },
    { title: "请求地址", dataIndex: "request_path", hide: true },
    { title: "请求参数", dataIndex: "request_body", hide: true, formType: "textarea" },
    { title: "返回信息", dataIndex: "json_result", hide: true, formType: "textarea" }
]

defineOptions({
    name: "operations"
})
</script>

<style lang="less" scoped></style>
