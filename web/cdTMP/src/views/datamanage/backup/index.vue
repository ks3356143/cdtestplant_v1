<template>
  <div>
    <a-card :bordered="false">
      <template #title>
        <icon-storage style="color: rgb(var(--primary-6))" />
        备份现状
      </template>
      <a-alert type="info" style="margin-bottom: 16px">
        用户可有选择地备份重要信息（按项目范围），信息丢失或破坏后按备份精准恢复；
        增量备份只带走上次备份之后新增/变更的数据，可由计划任务定时执行
        （GB/T 28452-2012 第三级 7.1.9 备份与故障恢复）。
      </a-alert>
      <a-descriptions :column="descColumns" bordered size="medium">
        <a-descriptions-item label="备份总数">{{ summary.total }}</a-descriptions-item>
        <a-descriptions-item label="全量/增量">{{ summary.full }}/{{ summary.incremental }}</a-descriptions-item>
        <a-descriptions-item label="累计数据条数">{{ summary.total_records }}</a-descriptions-item>
        <a-descriptions-item label="纳入备份业务表">{{ summary.model_count }} 张</a-descriptions-item>
        <a-descriptions-item label="最近备份时间">{{ formatTime(summary.latest_time) }}</a-descriptions-item>
      </a-descriptions>
    </a-card>

    <a-card :bordered="false" style="margin-top: 16px">
      <template #title>
        <icon-cloud style="color: rgb(var(--primary-6))" />
        备份记录
      </template>
      <a-space style="margin-bottom: 12px">
        <a-button type="primary" @click="openCreate">
          <template #icon><icon-plus /></template>
          新建备份
        </a-button>
        <a-button type="outline" :loading="creating" @click="quickIncremental">
          <template #icon><icon-play-arrow /></template>
          立即执行增量备份
        </a-button>
        <a-button @click="loadAll">刷新</a-button>
      </a-space>

      <a-table
        :columns="columns"
        :data="rows"
        :loading="loading"
        :pagination="{ pageSize: 10 }"
        :scroll="{ x: 1360 }"
        row-key="id"
      >
        <template #kind="{ record }">
          <a-tag :color="record.kind === 'full' ? 'arcoblue' : 'green'">{{ record.kind_label }}</a-tag>
        </template>
        <template #digest="{ record }">
          <a-tooltip :content="record.digest">
            <a-typography-text code>{{ String(record.digest).slice(0, 16) }}…</a-typography-text>
          </a-tooltip>
        </template>
        <template #state="{ record }">
          <a-tag v-if="record.status === 'success' && record.file_exists" color="green">完好</a-tag>
          <a-tag v-else color="red">{{ record.file_exists ? "异常" : "文件缺失" }}</a-tag>
        </template>
        <template #creator="{ record }">
          {{ record.creator_name || "定时任务" }}
        </template>
        <template #time="{ record }">
          {{ formatTime(record.create_datetime) }}
        </template>
        <template #operations="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="doRestore(record)">恢复</a-button>
            <a-button type="text" size="small" @click="doDownload(record)">下载</a-button>
            <a-popconfirm content="确认删除该备份及其文件？" @ok="doDelete(record)">
              <a-button type="text" size="small" status="danger">删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table>
    </a-card>

    <a-modal v-model:visible="createVisible" title="新建备份" :ok-loading="creating" @ok="doCreate" @cancel="closeCreate">
      <a-form :model="form" layout="vertical">
        <a-form-item label="备份名称">
          <a-input v-model="form.name" placeholder="留空自动生成，如 20261019_140000 全量备份" allow-clear />
        </a-form-item>
        <a-form-item label="备份类型" required>
          <a-radio-group v-model="form.kind">
            <a-radio value="full">全量备份</a-radio>
            <a-radio value="incremental">增量备份（只带上次备份后的新增/变更）</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="备份范围">
          <a-select v-model="form.project_id" placeholder="全部业务数据（仅系统管理员可选）" allow-clear>
            <a-option v-for="p in projects" :key="p.id" :value="p.id">{{ p.ident }} - {{ p.name }}</a-option>
          </a-select>
        </a-form-item>
        <a-typography-text type="secondary">
          备份内容为业务数据表（项目/轮次/被测件/设计需求/测试项/用例/问题单等）的 JSON 导出，
          含 SHA-256 摘要便于事后核对；抗抵赖证据与完整性标签不纳入备份。
        </a-typography-text>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue"
import { Message } from "@arco-design/web-vue"
import backupApi from "@/api/system/backup"
import projectApi from "@/api/testmanage/project"
import tool from "@/utils/tool"

const loading = ref(false)
const creating = ref(false)
const createVisible = ref(false)
const rows = ref([])
const projects = ref([])
const summary = reactive({ total: 0, full: 0, incremental: 0, total_records: 0, latest_time: null, model_count: 0 })
const form = reactive({ name: "", kind: "full", project_id: undefined })
// 窄屏下 5 列会把标签挤成竖排，按断点降列
const descColumns = { xs: 1, sm: 2, md: 3, xl: 5 }

const columns = [
  { title: "备份名称", dataIndex: "name", ellipsis: true, width: 200 },
  { title: "类型", slotName: "kind", width: 100 },
  { title: "备份范围", dataIndex: "scope_label", ellipsis: true, width: 200 },
  { title: "数据条数", dataIndex: "record_count", width: 100 },
  { title: "文件大小", dataIndex: "size_text", width: 100 },
  { title: "SHA-256 摘要", slotName: "digest", width: 180 },
  { title: "状态", slotName: "state", width: 90 },
  { title: "创建人", slotName: "creator", width: 100 },
  { title: "创建时间", slotName: "time", width: 185 },
  { title: "操作", slotName: "operations", width: 190, fixed: "right" }
]

const loadAll = async () => {
  loading.value = true
  try {
    const [list, sum] = await Promise.all([backupApi.getList(), backupApi.getSummary()])
    rows.value = Array.isArray(list) ? list : list.data || []
    Object.assign(summary, sum?.data || sum || {})
  } finally {
    loading.value = false
  }
}

const loadProjects = async () => {
  try {
    const res = await projectApi.getPageList({ page: 1, pageSize: 200 })
    const data = res?.data ?? res
    projects.value = (data?.items ?? data) || []
  } catch (e) {
    projects.value = []
  }
}

// 后端返回 ISO 时间，去掉微秒与时区后缀，页面可读即可
const formatTime = (val) => (val ? String(val).replace("T", " ").slice(0, 19) : "—")

const openCreate = () => {  form.name = ""
  form.kind = "full"
  form.project_id = undefined
  createVisible.value = true
}

const closeCreate = () => {
  createVisible.value = false
}

const doCreate = async () => {
  creating.value = true
  try {
    const res = await backupApi.create({ ...form, project_id: form.project_id ?? null })
    Message.success(res.message || "备份完成")
    createVisible.value = false
    await loadAll()
  } finally {
    creating.value = false
  }
}

const quickIncremental = async () => {
  creating.value = true
  try {
    const res = await backupApi.create({ name: "", kind: "incremental", project_id: null })
    Message.success(res.message || "增量备份完成")
    await loadAll()
  } finally {
    creating.value = false
  }
}

const doRestore = async (record) => {
  try {
    const res = await backupApi.restore(record.id)
    if (res?.success === false || (res?.code && res.code !== 200)) {
      Message.error(res.message || "恢复失败")
      return
    }
    Message.success(res?.message || "恢复完成")
  } catch {
    // 摘要不一致/无权限等错误已由接口层提示
  } finally {
    await loadAll()
  }
}

const doDownload = async (record) => {
  try {
    const token = JSON.parse(localStorage.getItem("token") || "null")
    const resp = await fetch(`/api/system/backup/${record.id}/download`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!resp.ok) {
      let msg = "下载失败，备份文件可能已不存在"
      try {
        const body = await resp.json()
        msg = body?.message || msg
      } catch {
        // 非 JSON 错误响应，使用默认提示
      }
      Message.error(msg)
      return
    }
    tool.download(await resp.blob(), record.file_name)
  } catch {
    Message.error("下载失败，请检查网络后重试")
  }
}

const doDelete = async (record) => {
  try {
    const res = await backupApi.remove(record.id)
    if (res?.success === false) {
      Message.error(res.message || "删除失败")
      return
    }
    Message.success("删除成功")
  } catch {
    // 接口层已提示
  } finally {
    await loadAll()
  }
}

onMounted(() => {
  loadAll()
  loadProjects()
})
</script>

<script>
export default { name: "backup" }
</script>
