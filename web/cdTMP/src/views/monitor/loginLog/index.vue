<template>
    <log-page :api="logApi.getLoginLogs" :columns="crudColumns" :delete-api="logApi.loginLogsDelete" show-detail />
</template>

<script setup>
import logApi from "@/api/monitor/loginLog"
import LogPage from "@/views/monitor/components/LogPage.vue"

const crudColumns = [
    { title: "ID", dataIndex: "id", addDisplay: false, editDisplay: false, width: 50, hide: true },
    { title: "登录用户", dataIndex: "username", search: true, align: "center" },
    { title: "IP", dataIndex: "ip", align: "center" },
    { title: "客户端信息", width: 215, dataIndex: "agent", align: "center" },
    { title: "操作系统", dataIndex: "os", align: "center" },
    { title: "浏览器", width: 110, dataIndex: "browser", align: "center" },
    {
        title: "创建时间",
        dataIndex: "create_datetime",
        align: "center",
        width: 150,
        addDisplay: false,
        editDisplay: false
    }
]

defineOptions({
    name: "loginLog"
})
</script>

<style lang="less" scoped></style>
