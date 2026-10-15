<template>
  <div>
    <a-card :bordered="false" class="policy-card">
      <template #title>
        <icon-lock style="color: rgb(var(--primary-6))" />
        登录失败锁定策略
      </template>
      <a-alert type="info" style="margin-bottom: 16px">
        本策略由系统安全员配置：连续登录失败达到阈值后锁定账号，防止暴力破解（GB/T 28452-2012 第三级 7.1.1）。
      </a-alert>
      <a-form :model="form" layout="vertical" style="max-width: 520px">
        <a-form-item label="登录失败最大尝试次数" required>
          <a-input-number v-model="form.login_max_attempts" :min="1" :max="100" mode="button" style="width: 200px" />
        </a-form-item>
        <a-form-item label="失败统计时间窗口（分钟）" required>
          <a-input-number v-model="form.login_window_minutes" :min="1" :max="1440" mode="button" style="width: 200px" />
        </a-form-item>
        <a-form-item label="账号锁定时长（分钟）" required>
          <a-input-number v-model="form.login_lock_minutes" :min="1" :max="1440" mode="button" style="width: 200px" />
        </a-form-item>
        <a-form-item>
          <a-space>
            <a-button type="primary" :loading="saving" @click="savePolicy">保存策略</a-button>
            <a-button @click="loadPolicy">重置</a-button>
            <a-button @click="loadPolicy">刷新</a-button>
          </a-space>
        </a-form-item>
        <a-form-item label="策略说明" disabled>
          <a-typography-text type="secondary">
            锁定策略在登录接口实时生效：窗口内失败达次数→锁定账号指定时长，并记录登录日志与告警。
          </a-typography-text>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card :bordered="false" class="policy-card" style="margin-top: 16px">
      <template #title>
        <icon-safe style="color: rgb(var(--primary-6))" />
        敏感标记管理（用户密级许可）
      </template>
      <a-alert type="info" style="margin-bottom: 16px">
        标记由系统安全员统一配置，管理员与普通用户无权修改（GB/T 28452-2012 第三级 7.1.4/7.1.5 强制访问控制）。
        用户仅能访问密级不高于本人许可的项目数据；调整后立即生效。
      </a-alert>
      <a-table :data="users" :loading="usersLoading" :pagination="false" size="medium">
        <template #columns>
          <a-table-column title="用户名" data-index="username" :width="160"></a-table-column>
          <a-table-column title="姓名" data-index="name" :width="160"></a-table-column>
          <a-table-column title="角色" :width="140">
            <template #cell="{ record }">{{ roleLabel(record.role) }}</template>
          </a-table-column>
          <a-table-column title="密级许可" :width="220">
            <template #cell="{ record }">
              <a-select v-model="record.clearance" size="small" style="width: 180px"
                        :disabled="record.username === 'superAdmin'">
                <a-option v-for="(label, key) in secretLevels" :key="key" :value="key">{{ label }}</a-option>
              </a-select>
            </template>
          </a-table-column>
          <a-table-column title="操作" :width="110">
            <template #cell="{ record }">
              <a-button size="mini" type="outline" :disabled="record.username === 'superAdmin'"
                        :loading="savingId === record.id" @click="saveClearance(record)">保存</a-button>
            </template>
          </a-table-column>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { Message } from "@arco-design/web-vue"
import policyApi from "@/api/system/policy"

// 登录失败锁定策略
const saving = ref(false)
const form = ref({
  login_max_attempts: 5,
  login_window_minutes: 15,
  login_lock_minutes: 30
})

const loadPolicy = async () => {
  const res = await policyApi.getPolicy()
  form.value = { ...form.value, ...res.data }
}

const savePolicy = async () => {
  saving.value = true
  try {
    await policyApi.updatePolicy(form.value)
    Message.success("策略已保存并实时生效")
  } finally {
    saving.value = false
  }
}

// 敏感标记管理
const users = ref([])
const usersLoading = ref(false)
const savingId = ref(null)
// 密级字典（与后端 secret 字典 key 一致）
const secretLevels = { 1: "公开", 2: "内部", 3: "秘密★5年", 4: "机密★10年", 5: "绝密★20年" }
const roleMap = { admin: "系统管理员", secadmin: "系统安全员", auditadmin: "系统审计员", user: "普通用户" }
const roleLabel = (role) => roleMap[role] || "普通用户"

const loadUsers = async () => {
  usersLoading.value = true
  try {
    const res = await policyApi.getClearanceList()
    users.value = res.data || []
  } finally {
    usersLoading.value = false
  }
}

const saveClearance = async (record) => {
  savingId.value = record.id
  try {
    await policyApi.updateClearance(record.id, { clearance: String(record.clearance) })
    Message.success(`${record.name} 密级许可已更新`)
  } finally {
    savingId.value = null
  }
}

onMounted(() => {
  loadPolicy()
  loadUsers()
})
</script>
