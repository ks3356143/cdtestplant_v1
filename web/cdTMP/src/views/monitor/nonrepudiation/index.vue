<template>
  <a-card :bordered="false">
    <a-form :model="filters" layout="inline" style="margin-bottom: 12px">
      <a-form-item label="业务标识">
        <a-input v-model="filters.business_ident" placeholder="问题单/用例 id" allow-clear style="width: 160px" />
      </a-form-item>
      <a-form-item label="业务类型">
        <a-select v-model="filters.business_type" placeholder="全部" allow-clear style="width: 140px">
          <a-option v-for="item in BUSINESS_TYPE_OPTIONS" :key="item.value" :value="item.value">
            {{ item.label }}
          </a-option>
        </a-select>
        <a-button style="margin-left: 8px" type="outline" @click="loadData">查询</a-button>
        <a-button style="margin-left: 8px" @click="resetFilters">重置</a-button>
      </a-form-item>
    </a-form>
    <a-alert type="info" style="margin-bottom: 12px">
      证据只进不改不删：自动记录主体身份、时间戳、数据摘要（SHA256），用于抗抵赖核验（GB/T 28452-2012 7.1.2）。
    </a-alert>
    <a-table
      :columns="columns"
      :data="rows"
      :loading="loading"
      :pagination="pagination"
      row-key="id"
    />
  </a-card>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue"
import evidenceApi from "@/api/monitor/nonrepudiation"

const loading = ref(false)
const rows = ref([])
// 避免每次渲染重建分页对象
const pagination = { pageSize: 10 }
const filters = reactive({ business_ident: "", business_type: undefined })
// 业务类型取值与后端 NonrepudiationEvidence.business_type 一致（problem/case）
const BUSINESS_TYPE_OPTIONS = [
  { value: "problem", label: "问题单" },
  { value: "case", label: "用例" }
]
const businessTypeLabel = (val) => BUSINESS_TYPE_OPTIONS.find((i) => i.value === val)?.label || val || "-"
// 数据摘要列太长，截断展示
const truncate = (val) => (val ? String(val).slice(0, 20) + "…" : "")

const columns = [
  { title: "证据类型", dataIndex: "evidence_type", width: 100 },
  { title: "主体账号", dataIndex: "actor_name", width: 110 },
  { title: "主体角色", dataIndex: "actor_role", width: 110 },
  { title: "行为类型", dataIndex: "action", width: 140 },
  {
    dataIndex: "business_type",
    title: "业务类型",
    width: 90,
    render: ({ record }) => businessTypeLabel(record.business_type)
  },
  { title: "业务标识", dataIndex: "business_ident", width: 90 },
  { title: "业务名称", dataIndex: "business_name", ellipsis: true, width: 160 },
  {
    title: "数据摘要(SHA256)",
    dataIndex: "data_digest",
    ellipsis: true,
    render: ({ record }) => truncate(record.data_digest)
  },
  { title: "操作IP", dataIndex: "operation_ip", width: 120 },
  { title: "证据生成时间", dataIndex: "create_datetime", width: 170 }
]

const loadData = async () => {
  loading.value = true
  try {
    const res = await evidenceApi.getEvidenceList({
      business_ident: filters.business_ident || undefined,
      business_type: filters.business_type || undefined
    })
    // 接口返回数组（ninja 原生列表响应）
    rows.value = Array.isArray(res) ? res : res.data || []
  } catch (e) {
    rows.value = []
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.business_ident = ""
  filters.business_type = undefined
  loadData()
}

onMounted(loadData)
</script>
