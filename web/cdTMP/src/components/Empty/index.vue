<template>
    <div class="empty-container">
        <icon-empty :size="60" />
        <p>{{ text }}</p>
    </div>
</template>

<script setup lang="ts">
// 标准vue3.5+的默认值写法、结构写法、ts类型写法
const { text = "暂无数据" } = defineProps<{ text?: string }>()
</script>

<style lang="less" scoped>
.empty-container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    color: #aaa;
    p {
        margin-top: 6px;
        user-select: none;
    }
}
</style>
