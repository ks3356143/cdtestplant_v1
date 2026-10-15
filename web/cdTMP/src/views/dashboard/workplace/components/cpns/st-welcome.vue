<template>
    <div class="flex justify-between">
        <div class="ma-content-block rounded-xs flex justify-between w-full p-3 bg-color">
            <div class="pl-0 flex">
                <a-avatar :size="75" class="hidden lg:inline-block">
                    <img src="@/assets/avatar/zhu.jpg" />
                </a-avatar>
                <div class="pl-3 mt-2">
                    <div class="content-block-title">{{ userStore.name }}，好久不见，欢迎回来！</div>
                    <div class="leading-5 mt-2 flex items-center">
                        <a-tag color="red" bordered class="mr-2">好用的测试工具集</a-tag>
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
import { ref, onMounted } from "vue"
import { useUserStore } from "@/store"
import dayjs from "dayjs"
const userStore = useUserStore()
const time = ref(null)
const day = ref(null)
const showTime = () => {
    time.value = dayjs().format("HH:mm:ss")
    day.value = dayjs().format("YYYY年MM月DD日")
}
onMounted(() => {
    showTime()
    setInterval(() => showTime(), 1000)
})
</script>

<style lang="less" scoped>
.datetime {
    background: rgb(var(--primary-6));
    color: #fff;
    width: 160px;
    text-align: center;
    border-radius: 2px;
    padding: 5px 10px;
}
.bg-color {
    background: var(--color-bg-2);
}
</style>
