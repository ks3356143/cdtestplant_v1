<template>
  <div>
    <a-card :bordered="false">
      <template #title>
        <icon-safe style="color: rgb(var(--primary-6))" />
        系统安全性检测分析
      </template>
      <a-alert type="info" style="margin-bottom: 16px">
        按操作系统 / 数据库 / 网络 / 应用系统 / 硬件五类被测对象逐项检测并给出整改建议；
        应用层之外的对象如实标注承担方（GB/T 28452-2012 第三级 7.1.10 引用 GB/T 20271-2006 6.3.2.2）。
      </a-alert>

      <a-space style="margin-bottom: 16px">
        <a-button type="primary" :loading="loading" @click="runCheck">
          <template #icon><icon-search /></template>
          执行检测
        </a-button>
        <a-typography-text type="secondary" v-if="checkedAt">本次检测时间：{{ checkedAt }}</a-typography-text>
      </a-space>

      <a-row :gutter="16" style="margin-bottom: 8px">
        <a-col v-for="stat in statCards" :key="stat.key" :span="6">
          <a-card :bordered="false" class="stat-card">
            <a-typography-text type="secondary">{{ stat.title }}</a-typography-text>
            <div class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</div>
          </a-card>
        </a-col>
      </a-row>
      <a-space wrap style="margin: 12px 0">
        <a-tag v-for="c in summary.categories" :key="c.name" color="arcoblue">
          {{ c.name }}：{{ c.total }} 项{{ c.risk ? `（风险 ${c.risk}）` : "" }}{{ c.na ? `（不适用 ${c.na}）` : "" }}
        </a-tag>
      </a-space>

      <a-table :data="items" :loading="loading" :pagination="false" size="medium" row-key="name">
        <template #columns>
          <a-table-column title="被测对象" data-index="category" :width="110"></a-table-column>
          <a-table-column title="检测项" data-index="name" :width="180"></a-table-column>
          <a-table-column title="检测方式" data-index="method" :width="220"></a-table-column>
          <a-table-column title="结论" :width="100">
            <template #cell="{ record }">
              <a-tag :color="statusColor(record.status)">{{ record.status_label }}</a-tag>
            </template>
          </a-table-column>
          <a-table-column title="检测结论" data-index="detail" ellipsis></a-table-column>
          <a-table-column title="整改建议" data-index="advice" ellipsis></a-table-column>
        </template>
      </a-table>
    </a-card>

    <a-card :bordered="false" style="margin-top: 16px">
      <template #title>
        <icon-check-circle style="color: rgb(var(--primary-6))" />
        依据检测结论已落地的改进
      </template>
      <a-alert type="success" style="margin-bottom: 16px">
        检测发现的问题已在本级安全性要求范围内整改，形成"检测分析 → 改进"闭环；确需由外部承担的，如实标注承担方。
      </a-alert>
      <a-table :data="improvements" :pagination="false" size="medium">
        <template #columns>
          <a-table-column title="改进项" data-index="item" :width="180"></a-table-column>
          <a-table-column title="检测发现" data-index="finding" ellipsis></a-table-column>
          <a-table-column title="整改措施" data-index="action" ellipsis></a-table-column>
          <a-table-column title="完成日期" data-index="date" :width="120"></a-table-column>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue"
import { Message } from "@arco-design/web-vue"
import selfCheckApi from "@/api/system/selfcheck"

const loading = ref(false)
const items = ref([])
const improvements = ref([])
const checkedAt = ref("")
const summary = reactive({ total: 0, passed: 0, risk: 0, notice: 0, na: 0, categories: [] })

const statCards = computed(() => [
  { key: "total", title: "检测项总数", value: summary.total, color: "#165DFF" },
  { key: "passed", title: "通过", value: summary.passed, color: "#00B42A" },
  { key: "risk", title: "风险", value: summary.risk, color: "#F53F3F" },
  { key: "na", title: "不适用 / 提示", value: `${summary.na} / ${summary.notice}`, color: "#86909C" }
])

const statusColor = (status) =>
  ({ pass: "green", risk: "red", notice: "orange", na: "gray" })[status] || "gray"

const runCheck = async () => {
  loading.value = true
  try {
    const res = await selfCheckApi.runSelfCheck()
    const data = res?.data || res || {}
    items.value = data.items || []
    improvements.value = data.improvements || []
    Object.assign(summary, data.summary || {})
    checkedAt.value = data.checked_at ? String(data.checked_at).replace("T", " ").slice(0, 19) : ""
    if (summary.risk > 0) {
      Message.warning(`检测完成：发现 ${summary.risk} 项风险，请按建议整改`)
    } else {
      Message.success("检测完成：未发现风险项")
    }
  } finally {
    loading.value = false
  }
}

onMounted(runCheck)
</script>

<style scoped>
.stat-card {
  background: var(--color-fill-1);
}
.stat-value {
  font-size: 24px;
  font-weight: 600;
  line-height: 32px;
}
</style>

<script>
export default { name: "selfcheck" }
</script>
