<template>
    <div class="ma-content-block lg:flex justify-between p-4">
        <div class="lg:w-full w-full lg:ml-4 mt-5 lg:mt-0">
            <ma-crud :options="crudOptions" :columns="crudColumns" ref="crudRef">
                <template #create_datetime="{ record }">
                    {{ record.create_datetime ? record.create_datetime.split(".")[0].replace("T", " ") : "-" }}
                </template>
                <template #tableBeforeButtons>
                    <a-popconfirm
                        content="仅清理 30 天前的日志，保留期内日志不可删除。确定继续？"
                        @ok="handleDeleteLogButton"
                    >
                        <a-button type="primary" status="warning">
                            <template #icon> <icon-delete /> </template>删除30天前数据
                        </a-button>
                    </a-popconfirm>
                </template>
                <!-- 操作列 -->
                <template #operationCell="{ record }">
                    <a-button size="mini" type="primary" status="success" @click="handleSee(record)"
                        ><icon-eye
                    /></a-button>
                </template>
            </ma-crud>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue"
import logApi from "@/api/monitor/loginLog"
import { Message, Notification } from "@arco-design/web-vue"
const crudRef = ref({})
// 删除日志按钮事件处理函数（审计日志保护：仅可清理30天前数据，禁全清）
const handleDeleteLogButton = async () => {
    try {
        const res = await logApi.loginLogsDelete() // 不传 day，后端按 30 天保留期默认清理
        if (res?.success === false) {
            Message.error(res.message || "清理被拒绝")
            return
        }
        Message.success(res?.message || "清理成功")
    } catch {
        // 清理被拒绝时接口层已提示，这里保留列表状态
    } finally {
        crudRef.value.refresh?.()
    }
}
// 点击操作：查看【思路打开编辑窗口】
const handleSee = (record) => {
    crudRef.value.editAction(record)
    // 设置表单标题
    crudRef.value.crudFormRef.actionTitle = "详情"
}
// 设置api
async function editClick() {
    Notification.error("该详情只能查看")
}
const crudOptions = ref({
    api: logApi.getLoginLogs,
    edit: { api: editClick, text: "查看操作日志信息", show: false },
    showIndex: false,
    pageLayout: "fixed",
    tablePagination: false,
    operationColumn: true,
    operationColumnAlign: "center",
    bordered: { wrapper: true, cell: true },
    isDbClickEdit: false,
    formOption: {
        viewType: "drawer",
        width: 600
    },
    afterDelete(response) {
        crudRef.value.tableRef.selectAll(false)
    }
})
const crudColumns = ref([
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
])

defineOptions({
    name: "loginLog"
})
</script>

<style lang="less" scoped></style>
