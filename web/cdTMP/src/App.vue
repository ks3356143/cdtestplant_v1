<template>
    <a-config-provider>
        <router-view />
    </a-config-provider>
</template>
<script setup lang="ts">
import { onUnmounted } from "vue"
import { Modal } from "@arco-design/web-vue"
const storageEvent = function (e: StorageEvent) {
    if (e.key === "token") {
        Modal.warning({
            title: "警告消息",
            content: "登录用户在其他窗口发生改变，正在刷新浏览器",
            onOk: () => {
                location.reload()
            }
        })
    }
}

window.addEventListener("storage", storageEvent)
onUnmounted(() => {
    window.removeEventListener("storage", storageEvent)
})
</script>

<style scoped></style>
