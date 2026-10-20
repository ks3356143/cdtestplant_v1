<template>
    <div class="ma-content-block lg:flex justify-between p-4">
        <div class="lg:w-full w-full lg:ml-4 mt-5 lg:mt-0">
            <ma-crud :options="crudOptions" :columns="columns" ref="crudRef">
                <template #create_datetime="{ record }">
                    {{ formatTime(record.create_datetime) }}
                </template>
                <template #tableBeforeButtons>
                    <a-popconfirm v-if="deleteApi" :content="deleteTip" @ok="handleDeleteLogButton">
                        <a-button type="primary" status="warning">
                            <template #icon> <icon-delete /> </template>删除30天前数据
                        </a-button>
                    </a-popconfirm>
                </template>
                <template #operationCell="{ record }">
                    <a-button v-if="showDetail" size="mini" type="primary" status="success" @click="handleSee(record)">
                        <icon-eye />
                    </a-button>
                </template>
            </ma-crud>
        </div>
    </div>
</template>

<script setup>
import { reactive, ref } from "vue"
import { Message, Notification } from "@arco-design/web-vue"

/**
 * 日志监控三页（登录日志 / 接口操作日志 / 数据操作日志）的公共页面骨架：
 * 差异只有数据源、列定义、是否可查看详情与清理接口。
 */
const props = defineProps({
    api: { type: Function, required: true },
    columns: { type: Array, required: true },
    deleteApi: { type: Function, default: null },
    deleteTip: { type: String, default: "仅清理 30 天前的日志，保留期内日志不可删除。确定继续？" },
    showDetail: { type: Boolean, default: false }
})

const crudRef = ref({})

// 日志时间统一格式化：容忍空值，避免 null.split 崩溃
const formatTime = (value) => (value ? String(value).split(".")[0].replace("T", " ") : "-")

const crudOptions = reactive({
    api: props.api,
    // 详情只读：编辑动作固定提示，不允许真正落库
    edit: { api: () => Notification.error("该详情只能查看"), text: "查看日志信息", show: false },
    showIndex: false,
    pageLayout: "fixed",
    tablePagination: false,
    operationColumn: props.showDetail,
    operationColumnAlign: "center",
    operationColumnWidth: 80,
    bordered: { wrapper: true, cell: true },
    isDbClickEdit: false,
    formOption: {
        viewType: "drawer",
        width: 600
    },
    afterDelete() {
        crudRef.value.tableRef?.selectAll(false)
    }
})

// 点击操作：打开只读详情抽屉
const handleSee = (record) => {
    crudRef.value.editAction(record)
    crudRef.value.crudFormRef.actionTitle = "详情"
}

// 删除日志（审计日志保护：仅可清理 30 天前数据，禁全清）
const handleDeleteLogButton = async () => {
    if (!props.deleteApi) return
    try {
        const res = await props.deleteApi() // 不传 day，后端按 30 天保留期默认清理
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

defineExpose({ crudRef })
</script>

<style lang="less" scoped></style>
