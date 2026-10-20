<template>
    <div class="block">
        <div class="user-header">
            <div class="user-identity">
                <div class="user-avatar">{{ (userStore.name || userStore.username || "U").slice(0, 1) }}</div>
                <div class="user-meta">
                    <div class="user-name">{{ userStore.name || userStore.username }}</div>
                    <div class="user-account">账号：{{ userStore.username }}</div>
                </div>
            </div>
            <div class="user-header-note">个人资料 · 账号安全 · 登录日志</div>
        </div>
        <div class="block lg:flex lg:justify-between">
            <div class="ma-content-block w-full lg:w-6/12 mt-3 p-4">
                <a-tabs default-active-key="info" :animation="true">
                    <a-tab-pane key="info" title="个人资料">
                        <user-infomation />
                    </a-tab-pane>
                    <a-tab-pane key="safe" title="安全设置">
                        <editpassword />
                    </a-tab-pane>
                </a-tabs>
            </div>
            <div class="ma-content-block w-full lg:w-6/12 mt-3 p-4 ml-0 lg:ml-3">
                <a-tabs default-active-key="login-log" :animation="true">
                    <a-tab-pane key="login-log" title="登录日志" v-loading="isDataLoading">
                        <a-timeline class="pl-5 mt-3" v-if="loginLogList.length">
                            <a-timeline-item :label="`IP地址：${item.ip}，操作系统：${item.os}`" v-for="(item, idx) in loginLogList" :key="idx">
                                您于 {{ item.create_datetime }} 登录系统，浏览器：{{ item.browser }}
                            </a-timeline-item>
                        </a-timeline>
                    </a-tab-pane>
                    <a-tab-pane key="operation-log" title="操作日志" v-loading="isLoading">
                        <a-timeline class="pl-5 mt-3">
                            <a-timeline-item
                                :label="`IP地址：${item.request_ip}，方式：${item.request_method}，系统：${item.request_os}，浏览器：${item.request_browser}`"
                                v-for="(item, idx) in operationLogList"
                                :key="idx"
                            >
                                您于 {{ item.create_datetime }} 请求了 {{ item.request_path }}，<span
                                    :class="{ nostatus: item.response_code === '200' ? false : true }"
                                    >状态码：{{ item.response_code }}</span
                                >
                            </a-timeline-item>
                        </a-timeline>
                    </a-tab-pane>
                </a-tabs>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed, ref } from "vue"
import userInfomation from "./components/userInfo.vue"
import editpassword from "./components/editpassword.vue"
import { useUserStore } from "@/store"
import logApi from "@/api/system/log"
import useFetchData from "@/hooks/fetchData"
const { data: loadingData, isLoading: isDataLoading } = useFetchData([], logApi.getLoginLog)
// 后端时间字段可能为空，统一做空值兜底
const formatTime = (value) => (value ? String(value).split(".")[0].replace("T", " ") : "-")
const userStore = useUserStore()
const loginLogList = computed(() => {
    return loadingData.value.map((item) => ({
        ...item,
        create_datetime: formatTime(item.create_datetime)
    }))
})
// 操作日志不用hook
const isLoading = ref(true)
const data = ref([])
logApi.getOperationLog()
    .then((res) => {
        data.value = res.data
    })
    .catch(() => {})
    .finally(() => {
        isLoading.value = false
    })

const operationLogList = computed(() => {
    return data.value.map((item) => ({
        ...item,
        create_datetime: formatTime(item.create_datetime)
    }))
})

// 组件命名
defineOptions({
    name: "usercenter"
})
</script>

<style scoped>
/* 用户中心头部：墨黑底 + 青绿竖线 + 工程网格，与全站直角风格一致 */
.user-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    height: 136px;
    padding: 0 32px;
    color: #ffffff;
    background-color: #0f172a;
    background-image:
        linear-gradient(to right, rgba(148, 163, 184, 0.09) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(148, 163, 184, 0.09) 1px, transparent 1px);
    background-size: 36px 36px;
    border-left: 4px solid rgb(var(--primary-6));
}

.user-identity {
    display: flex;
    align-items: center;
    gap: 18px;
    min-width: 0;
}

.user-avatar {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 72px;
    height: 72px;
    background-color: rgb(var(--primary-6));
    color: #ffffff;
    font-size: 30px;
    font-weight: 700;
    flex-shrink: 0;
}

.user-name {
    color: #ffffff;
    font-size: 24px;
    font-weight: 600;
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.user-account {
    margin-top: 6px;
    color: #9aa7b8;
    font-size: 13px;
    letter-spacing: 0.02em;
}

.user-header-note {
    color: #94a3b8;
    font-size: 12px;
    letter-spacing: 0.08em;
    white-space: nowrap;
}

.nostatus {
    color: red;
}

:deep(.arco-form-item) {
    margin-bottom: 20px; /* 覆盖默认样式 */
}

@media (max-width: 768px) {
    .user-header {
        height: 112px;
        padding: 0 18px;
    }

    .user-header-note {
        display: none;
    }

    .user-avatar {
        width: 56px;
        height: 56px;
        font-size: 24px;
    }

    .user-name {
        font-size: 19px;
    }
}
</style>
