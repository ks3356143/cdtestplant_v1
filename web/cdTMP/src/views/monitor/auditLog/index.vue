<template>
    <div class="ma-content-block lg:flex justify-between p-4">
        <div class="lg:w-full w-full mt-5 lg:mt-0">
            <a-alert type="info" style="margin-bottom: 12px">
                统一安全审计（GB/T 28452-2012 第三级 7.1.6）：覆盖登录鉴别、标记与策略变更、账号管理、越权告警等核心安全事件，
                全程留痕、多维检索；审计日志受保护，仅能按保留期清理，无法被篡改或全清。
            </a-alert>

            <!-- 数据完整性核查（7.1.7） -->
            <a-card class="general-card" style="margin-bottom: 12px">
                <template #title>
                    <icon-safe style="color: rgb(var(--primary-6))" />
                    数据完整性核查（7.1.7）
                </template>
                <a-space style="margin-bottom: 8px" wrap>
                    <a-button type="primary" :loading="checking" @click="runIntegrityCheck">立即核查</a-button>
                    <span style="color: var(--color-text-3); font-size: 12px">
                        对项目/测试用例/执行结果/问题单的重要数据批量重算完整性标签，发现底层篡改即告警
                    </span>
                </a-space>
                <template v-if="lastCheck">
                    <a-alert :type="lastCheck.broken ? 'error' : 'success'" style="margin-bottom: 8px">
                        共核查 {{ lastCheck.total }} 条受保护数据：
                        <a-tag :color="lastCheck.broken ? 'red' : 'green'">
                            {{ lastCheck.broken ? `发现 ${lastCheck.broken} 条完整性破损` : '全部完好' }}
                        </a-tag>
                        <span style="font-size: 12px">{{ lastCheck.recovery_hint }}</span>
                    </a-alert>
                    <a-table v-if="lastCheck.broken" :data="brokenItems"
                             :pagination="false" size="small" :bordered="{ cell: true }">
                        <template #columns>
                            <a-table-column title="受保护数据" data-index="label" :width="180"></a-table-column>
                            <a-table-column title="标识" data-index="ident" :width="140"></a-table-column>
                            <a-table-column title="标签摘要" data-index="stored" :width="150"></a-table-column>
                            <a-table-column title="重算摘要" data-index="actual" :width="150"></a-table-column>
                            <a-table-column title="结论" :width="110">
                                <template #cell="{ record }">
                                    <a-tag color="red">完整性破损</a-tag>
                                </template>
                            </a-table-column>
                        </template>
                    </a-table>
                </template>
            </a-card>

            <!-- 筛选区 -->
            <a-card class="general-card" style="margin-bottom: 12px">
                <a-form :model="filters" layout="inline">
                    <a-form-item label="主体账号">
                        <a-input v-model="filters.username" placeholder="按账号检索" allow-clear style="width: 150px" />
                    </a-form-item>
                    <a-form-item label="事件类型">
                        <a-select v-model="filters.event_type" placeholder="全部" allow-clear style="width: 170px">
                            <a-option v-for="t in allTypes" :key="t" :value="t">{{ labelOf(t) }}</a-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="操作IP">
                        <a-input v-model="filters.ip" placeholder="按IP检索" allow-clear style="width: 130px" />
                    </a-form-item>
                    <a-form-item label="时间区间">
                        <a-range-picker v-model="timeRange" style="width: 240px" />
                    </a-form-item>
                    <a-form-item>
                        <a-space>
                            <a-button type="primary" @click="search">查询</a-button>
                            <a-button @click="reset">重置</a-button>
                            <a-checkbox v-model="filters.only_alerts">只看告警</a-checkbox>
                        </a-space>
                    </a-form-item>
                </a-form>

                <!-- 事件类型统计标签（点击快速筛选） -->
                <a-space style="margin-top: 10px" wrap>
                    <a-tag v-for="(c, t) in typeCounts" :key="t" :color="isAlert(t) ? 'red' : 'arcoblue'"
                           style="cursor: pointer" @click="filterByType(t)">
                        {{ labelOf(t) }} × {{ c }}
                    </a-tag>
                </a-space>
                <div style="margin-top: 8px; color: var(--color-text-3); font-size: 12px">
                    点击标签可按事件类型快速筛选；红色为安全告警类事件。
                </div>
            </a-card>

            <!-- 审计日志表 -->
            <a-card class="general-card">
                <a-table :data="rows" :loading="loading" :pagination="pagination" row-key="id"
                         :scroll="{ x: 1180 }"
                         @page-change="onPageChange" @page-size-change="onPageSizeChange"
                         :bordered="{ wrapper: true, cell: true }">
                    <template #columns>
                        <a-table-column title="ID" data-index="id" :width="70"></a-table-column>
                        <a-table-column title="时间" :width="180">
                            <template #cell="{ record }">
                                <span style="white-space: nowrap">{{ fmtTime(record.create_datetime) }}</span>
                            </template>
                        </a-table-column>
                        <a-table-column title="主体账号" data-index="username" :width="140"></a-table-column>
                        <a-table-column title="角色" :width="115">
                            <template #cell="{ record }">
                                <span style="white-space: nowrap">{{ roleLabel(record.role) }}</span>
                            </template>
                        </a-table-column>
                        <a-table-column title="事件类型" :width="130">
                            <template #cell="{ record }">
                                <a-tag :color="isAlert(record.event_type) ? 'red' : 'arcoblue'">
                                    {{ labelOf(record.event_type) }}
                                </a-tag>
                            </template>
                        </a-table-column>
                        <a-table-column title="事件内容">
                            <template #cell="{ record }">
                                <a-tooltip :content="record.detail">
                                    <span class="detail-cell">{{ record.detail }}</span>
                                </a-tooltip>
                            </template>
                        </a-table-column>
                        <a-table-column title="IP" data-index="ip" :width="115"></a-table-column>
                        <a-table-column title="结果" :width="85">
                            <template #cell="{ record }">
                                <a-tag :color="record.success ? 'green' : 'red'">
                                    {{ record.success ? '成功' : '失败' }}
                                </a-tag>
                            </template>
                        </a-table-column>
                    </template>
                </a-table>
            </a-card>
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue"
import roleMap from "@/utils/roleMap"
import auditLogApi from "@/api/monitor/auditLog"

// 事件类型清单（code/label/alert 由后端唯一提供：utils.audit.get_event_types）
const eventTypes = ref([])
// code → 事件类型对象，供 O(1) 查询（避免每个单元格 find 遍历）
const typeMap = computed(() => Object.fromEntries(eventTypes.value.map(e => [e.code, e])))
const labelOf = (t) => typeMap.value[t]?.label || t
const isAlert = (t) => typeMap.value[t]?.alert || false
const allTypes = computed(() => eventTypes.value.map(e => e.code))

// 筛选状态
const filters = reactive({
    username: "",
    event_type: "",
    ip: "",
    only_alerts: false
})
const timeRange = ref([])
const rows = ref([])
const loading = ref(false)
const pagination = ref({ total: 0, current: 1, pageSize: 10, showTotal: true })

// 角色中文标签（共享常量）
const roleLabel = (r) => roleMap[r] || "普通用户"
const fmtTime = (s) => (s ? String(s).replace(/T/, " ").split(".")[0] : "")

// 当前页事件类型统计
const typeCounts = computed(() => {
    const counts = {}
    for (const r of rows.value) counts[r.event_type] = (counts[r.event_type] || 0) + 1
    return counts
})

const doQuery = async () => {
    loading.value = true
    try {
        const params = {
            page: pagination.value.current,
            pageSize: pagination.value.pageSize,
            username: filters.username || undefined,
            event_type: filters.event_type || undefined,
            ip: filters.ip || undefined,
            only_alerts: filters.only_alerts || undefined,
            start_time: timeRange.value?.[0] || undefined,
            end_time: timeRange.value?.[1] || undefined
        }
        const res = await auditLogApi.getAuditLogs(params)
        rows.value = res.data?.items || []
        pagination.value.total = res.data?.pageInfo?.total || 0
    } finally {
        loading.value = false
    }
}

// 事件类型清单加载（后端唯一事实源：label/告警标记）
const loadEventTypes = async () => {
    const res = await auditLogApi.getAuditEventTypes()
    eventTypes.value = res.data || []
}

// 数据完整性核查（7.1.7）
const checking = ref(false)
const lastCheck = ref(null)
// 完整性破损条目（避免模板内联过滤重复计算）
const brokenItems = computed(() => (lastCheck.value?.items || []).filter(i => !i.intact))
const runIntegrityCheck = async () => {
    checking.value = true
    try {
        const res = await auditLogApi.integrityCheck()
        lastCheck.value = res.data
    } finally {
        checking.value = false
    }
}

onMounted(() => {
    loadEventTypes()
    doQuery()
})

const search = () => {
    pagination.value.current = 1
    doQuery()
}
const reset = () => {
    filters.username = ""
    filters.event_type = ""
    filters.ip = ""
    filters.only_alerts = false
    timeRange.value = []
    search()
}
const filterByType = (t) => {
    filters.event_type = t
    search()
}

const onPageChange = (p) => {
    pagination.value.current = p
    doQuery()
}
const onPageSizeChange = (s) => {
    pagination.value.pageSize = s
    doQuery()
}
</script>

<style scoped>
.detail-cell {
    display: inline-block;
    max-width: 360px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
</style>
