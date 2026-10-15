<template>
    <div v-if="visible" class="global-loading">
        <div class="spinner"></div>
        <div v-if="text" class="loading-text">{{ text }}</div>
    </div>
</template>

<script setup lang="ts">
import { ref } from "vue"

const visible = ref(false)
const text = ref("加载中...")
const show = (loadingText = "加载中...") => {
    text.value = loadingText
    visible.value = true
}

const hide = () => {
    visible.value = false
}

// 暴露方法供外部调用
defineExpose({ show, hide })
</script>

<style scoped>
.global-loading {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: rgba(255, 255, 255, 0.8);
    z-index: 9999;
}

.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-left-color: rgb(var(--blue-6));
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}

.loading-text {
    margin-top: 10px;
    color: rgb(var(--blue-6));
    user-select: none;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}
</style>
