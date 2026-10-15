<template>
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
</template>

<script setup>
import { onMounted, reactive, ref } from "vue"
import { Message } from "@arco-design/web-vue"
import policyApi from "@/api/system/policy"

const saving = ref(false)
const form = reactive({
  login_max_attempts: 5,
  login_window_minutes: 15,
  login_lock_minutes: 30
})

const loadPolicy = async () => {
  const res = await policyApi.getPolicy()
  Object.assign(form, res.data)
}

const savePolicy = async () => {
  saving.value = true
  try {
    await policyApi.updatePolicy(form)
    Message.success("策略已保存并实时生效")
  } finally {
    saving.value = false
  }
}

onMounted(loadPolicy)
</script>
