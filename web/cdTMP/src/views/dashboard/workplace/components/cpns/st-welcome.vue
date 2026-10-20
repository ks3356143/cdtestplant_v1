<template>
    <div class="flex justify-between">
        <div class="ma-content-block rounded-xs flex justify-between w-full p-3 bg-color">
            <div class="pl-0 flex">
                <a-avatar :size="64" class="welcome-avatar hidden lg:inline-block">
                    <img src="@/assets/avatar/zhu.jpg" />
                </a-avatar>
                <div class="pl-3 mt-2">
                    <div class="content-block-title">{{ userStore.name }}，好久不见，欢迎回来！</div>
                    <div class="leading-5 mt-2 flex items-center">
                        <a-tag color="arcoblue" bordered class="mr-2">好用的测试工具集</a-tag>
                        欢迎使用测试管理平台 ⭐长期更新。
                    </div>
                </div>
            </div>
            <div class="datetime ml-5 hidden md:block">
                <h2 class="text-3xl text-center">{{ time }}</h2>
                <p class="text-base">{{ day }}</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue"
import { useUserStore } from "@/store"
import dayjs from "dayjs"
const userStore = useUserStore()
const time = ref(null)
const day = ref(null)
const showTime = () => {
    time.value = dayjs().format("HH:mm:ss")
    day.value = dayjs().format("YYYY年MM月DD日")
}
let timer = null
onMounted(() => {
    showTime()
    timer = setInterval(() => showTime(), 1000)
})
onUnmounted(() => {
    clearInterval(timer)
})
</script>

<style lang="less" scoped>
.welcome-avatar {
    border-radius: 0 !important;
    border: 1px solid var(--app-line, #e4e7eb);
    overflow: hidden;
}

.datetime {
    position: relative;
    background: var(--app-sidebar, #0f172a);
    color: #fff;
    width: 176px;
    text-align: center;
    border-radius: 0;
    padding: 8px 12px;
    border-top: 3px solid rgb(var(--primary-6));
}

.datetime h2 {
    font-variant-numeric: tabular-nums;
    letter-spacing: 0.06em;
}

.datetime p {
    color: var(--app-sidebar-text, #c7d0dd);
    font-size: 12px;
}
.bg-color {
    background: var(--color-bg-2);
}
</style>
