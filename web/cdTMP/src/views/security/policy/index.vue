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
            <a-button @click="resetPolicy">重置</a-button>
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

    <a-card :bordered="false" class="policy-card" style="margin-top: 16px">
      <template #title>
        <icon-lock style="color: rgb(var(--primary-6))" />
        数据保密性保护（落库加密 / 传输加密 / 剩余信息）
      </template>
      <a-alert type="info" style="margin-bottom: 16px">
        用户重要数据（电话、邮箱）落库前加密，数据库直查只见密文；网络传输走 TLS 密文；
        用户释放使用权后及时清除临时缓存与临时文件（GB/T 28452-2012 第三级 7.1.8）。
      </a-alert>

      <a-spin :loading="secrecyLoading" style="width: 100%">
        <a-divider orientation="left">① 存储保密性 —— 已加密字段</a-divider>
        <a-table :data="secrecy.encrypted_fields" :pagination="false" size="small">
          <template #columns>
            <a-table-column title="所属模型" data-index="model" :width="160"></a-table-column>
            <a-table-column title="字段" data-index="field" :width="160"></a-table-column>
            <a-table-column title="字段名" data-index="name" :width="160"></a-table-column>
            <a-table-column title="加密算法" data-index="algorithm"></a-table-column>
          </template>
        </a-table>
        <a-typography-text type="secondary" style="display: block; margin-top: 8px">
          密文前缀 enc:v1:，采用带完整性校验的对称加密；密钥由环境变量 FIELD_ENCRYPTION_KEY 提供。
          加密后无法 SQL 模糊匹配，按电话检索改用 SHA-256 盲索引做等值匹配。
        </a-typography-text>

        <a-divider orientation="left">② 传输保密性</a-divider>
        <a-descriptions :column="2" bordered size="medium">
          <a-descriptions-item label="是否已落实">
            <a-tag :color="secrecy.transport?.enabled ? 'green' : 'red'">
              {{ secrecy.transport?.enabled ? "已配置" : "未配置" }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="协议版本">{{ secrecy.transport?.protocol || "—" }}</a-descriptions-item>
          <a-descriptions-item label="配置文件">{{ secrecy.transport?.config_path || "—" }}</a-descriptions-item>
          <a-descriptions-item label="说明">{{ secrecy.transport?.detail }}</a-descriptions-item>
        </a-descriptions>

        <a-divider orientation="left">③ 剩余信息保护措施</a-divider>
        <a-table :data="secrecy.residue_measures" :pagination="false" size="small">
          <template #columns>
            <a-table-column title="措施" data-index="name" :width="240"></a-table-column>
            <a-table-column title="承担方" data-index="owner" :width="200">
              <template #cell="{ record }">
                <a-tag :color="record.owner.includes('操作系统') ? 'gray' : 'arcoblue'">{{ record.owner }}</a-tag>
              </template>
            </a-table-column>
            <a-table-column title="说明" data-index="detail"></a-table-column>
          </template>
        </a-table>

        <a-divider orientation="left">④ 临时文件清理（剩余信息）</a-divider>
        <a-space direction="vertical" fill>
          <a-space>
            <a-typography-text>
              当前临时文件：<b>{{ secrecy.temp_usage?.file_count ?? 0 }}</b> 个，
              合计 <b>{{ secrecy.temp_usage?.total_mb ?? 0 }}</b> MB
            </a-typography-text>
            <a-select v-model="purgeAge" size="small" style="width: 160px">
              <a-option :value="0">全部清理</a-option>
              <a-option :value="1">保留 1 小时</a-option>
              <a-option :value="24">保留 24 小时</a-option>
              <a-option :value="168">保留 7 天</a-option>
            </a-select>
            <a-button type="outline" size="small" :loading="purging" @click="doPurge">立即清理</a-button>
            <a-button size="small" @click="loadSecrecy">刷新现状</a-button>
          </a-space>
          <a-typography-text type="secondary">
            仅清理文档生成过程的中间产物目录（media/&lt;R号&gt;/temp、form_template/*/temporary）；
            输入模板与最终交付文档不在清理范围。
          </a-typography-text>
        </a-space>

        <a-divider orientation="left">⑤ 日志脱敏字段</a-divider>
        <a-space wrap>
          <a-tag v-for="key in secrecy.masked_log_keys" :key="key" color="orange">{{ key }}</a-tag>
        </a-space>
        <a-typography-text type="secondary" style="display: block; margin-top: 8px">
          上述字段写入接口操作日志前自动脱敏（口令全掩码、手机号保留前 3 后 4、邮箱保留首字符与域名）。
        </a-typography-text>
      </a-spin>
    </a-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { Message } from "@arco-design/web-vue"
import roleMap from "@/utils/roleMap"
import policyApi from "@/api/system/policy"
import dictApi from "@/api/system/dict"

// 登录失败锁定策略
const saving = ref(false)
const form = ref({
  login_max_attempts: 5,
  login_window_minutes: 15,
  login_lock_minutes: 30
})
// 服务端已保存的策略快照：「重置」回到这份值（撤销未保存的编辑），「刷新」重新拉取
const savedPolicy = ref({ ...form.value })

const loadPolicy = async () => {
  const res = await policyApi.getPolicy()
  form.value = { ...form.value, ...res.data }
  savedPolicy.value = { ...form.value }
}

const resetPolicy = () => {
  form.value = { ...form.value, ...savedPolicy.value }
  Message.info("已恢复为上次保存的策略")
}

const savePolicy = async () => {
  saving.value = true
  try {
    await policyApi.updatePolicy(form.value)
    savedPolicy.value = { ...form.value }
    Message.success("策略已保存并实时生效")
  } finally {
    saving.value = false
  }
}

// 敏感标记管理
const users = ref([])
const usersLoading = ref(false)
const savingId = ref(null)
// 密级字典来自后端 secret 字典，避免与后端定义重复维护
const secretLevels = ref({})
const loadSecretLevels = async () => {
  try {
    const res = await dictApi.getDictByCode({ code: "secret" })
    secretLevels.value = Object.fromEntries((res.data || []).map((item) => [item.key, item.title]))
  } catch {
    // 字典接口失败时保留空选项，由用户刷新重试
  }
}
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

// 数据保密性保护（7.1.8）
const secrecyLoading = ref(false)
const secrecy = ref({
  encrypted_fields: [],
  residue_measures: [],
  transport: {},
  temp_usage: {},
  masked_log_keys: []
})
const purgeAge = ref(24)
const purging = ref(false)

const loadSecrecy = async () => {
  secrecyLoading.value = true
  try {
    const res = await policyApi.getConfidentiality()
    secrecy.value = res.data || secrecy.value
  } finally {
    secrecyLoading.value = false
  }
}

const doPurge = async () => {
  purging.value = true
  try {
    const res = await policyApi.purgeResidue(purgeAge.value)
    Message.success(res.message || "清理完成")
    await loadSecrecy()
  } finally {
    purging.value = false
  }
}

onMounted(() => {
  loadPolicy()
  loadUsers()
  loadSecretLevels()
  loadSecrecy()
})
</script>
