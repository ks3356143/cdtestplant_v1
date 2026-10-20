<template>
    <log-page :api="logApi.getLoginLogs" :columns="crudColumns" :delete-api="logApi.loginLogsDelete" show-detail />
</template>

<script setup>
import logApi from "@/api/monitor/loginLog"
import LogPage from "@/views/monitor/components/LogPage.vue"

const crudColumns = [
    { title: "ID", dataIndex: "id", addDisplay: false, editDisplay: false, width: 50, hide: true },
    { title: "登录用户", dataIndex: "username", search: true, align: "center", width: 120 },
    { title: "IP", dataIndex: "ip", align: "center", width: 120 },
    { title: "客户端信息", width: 280, dataIndex: "agent", align: "center" },
    { title: "操作系统", dataIndex: "os", align: "center", width: 120 },
    { title: "浏览器", width: 130, dataIndex: "browser", align: "center" },
    {
        title: "创建时间",
        dataIndex: "create_datetime",
        align: "center",
        width: 170,
        addDisplay: false,
        editDisplay: false
    }
]

defineOptions({
    name: "loginLog"
})
</script>

<style lang="less" scoped></style>
