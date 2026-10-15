<template>
    <div>
        <a-dropdown
            @select="handleSelect"
            :popup-visible="fvisible"
            :popup-container="container"
            @popup-visible-change="change"
            position="bottom"
            alignPoint
            :style="{ display: 'block' }"
        >
            <div
                :style="{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: '300px',
                    backgroundColor: 'var(--color-fill-2)'
                }"
            ></div>
            <template #content>
                <a-dgroup title="执行操作">
                    <a-doption @click="handleProblemShow">
                        <template #icon>
                            <icon-list />
                        </template>
                        查看轮次下问题单
                    </a-doption>
                    <a-doption @click="handleRenjiTest">
                        <template #icon>
                            <icon-file />
                        </template>
                        点击生成人机交互界面测试
                    </a-doption>
                </a-dgroup>
            </template>
        </a-dropdown>
    </div>
</template>

<script setup>
const props = defineProps({
    fvisible: {
        type: Boolean,
        default() {
            return false
        }
    },
    container: {
        type: Object,
        default() {
            return false
        }
    }
})
const emits = defineEmits(["update:visible", "click-problem-show", "create-renji"])
// 点击查看问题单列表
const handleSelect = async (value) => {
    emits("update:visible") // 给父组件传递关闭弹窗
}
// 点击空白取消显示
const change = () => {
    emits("update:visible") // 给父组件传递关闭弹窗
}
// 点击给父组件发生事件
const handleProblemShow = () => {
    emits("click-problem-show")
}
// 点击生成人机交互界面测试
const handleRenjiTest = () => {
    emits("create-renji")
}
</script>

<style lang="less" scoped></style>
