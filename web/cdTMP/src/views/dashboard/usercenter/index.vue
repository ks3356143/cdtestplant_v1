<template>
    <div class="block">
        <div class="user-header rounded-xs text-center">
            <div class="pt-6 mx-auto avatar-box top-box">
                {{ userStore.name }}
            </div>
            <div>
                <a-tag size="large" class="mt-3 rounded-full" color="#de53ff"> 账号：{{ userStore.username }} </a-tag>
            </div>
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
import MaUpload from "@cps/ma-upload/index.vue"
import userInfomation from "./components/userInfo.vue"
import editpassword from "./components/editpassword.vue"
import { useUserStore } from "@/store"
import logApi from "@/api/system/log"
import useFetchData from "@/hooks/fetchData"
const { loadingData, isDataLoading } = useFetchData([], logApi.getLoginLog)
const userStore = useUserStore()
const loginLogList = computed(() => {
    return loadingData.value.map((item) => {
        item.create_datetime = item.create_datetime.split(".")[0].replace("T", " ")
        return item
    })
})
// 操作日志不用hook
const isLoading = ref(true)
const data = ref([])
logApi.getOperationLog().then((res) => {
    data.value = res.data
    isLoading.value = false
})

const operationLogList = computed(() => {
    return data.value.map((item) => {
        item.create_datetime = item.create_datetime.split(".")[0].replace("T", " ")
        return item
    })
})

// 组件命名
defineOptions({
    name: "usercenter"
})
</script>

<style scoped>
.avatar-box {
    width: 130px;
}
.user-header {
    width: 100%;
    height: 150px;
    background: url("@/assets/userBanner.jpg") no-repeat;
    background-size: cover;
}
.nostatus {
    color: red;
}
.top-box {
    font-size: 2rem;
}
:deep(.arco-form-item) {
    margin-bottom: 20px; /* 覆盖默认样式 */
}
</style>
