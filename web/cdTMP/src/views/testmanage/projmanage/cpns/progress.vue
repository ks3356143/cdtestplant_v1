<template>
    <div class="progress">
        <a-modal
            draggable
            :visible="visible"
            hide-cancel
            unmount-on-close
            :mask-closable="false"
            :on-before-ok="handleClickConfirmButton"
            :on-before-cancel="handleClickConfirmButton"
        >
            <template #title>正在生成{{ text }}</template>
            <div><a-progress :percent="percent" size="large" :show-text="false" /></div>
        </a-modal>
    </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from "vue"
import { Notification } from "@arco-design/web-vue"
const emits = defineEmits(["clickConfirm"])
const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    isComplete: {
        type: Boolean,
        default: false
    },
    text: {
        type: String,
        default: "测评大纲"
    }
})
const percent = ref(0)
// 点击确定或关闭按钮判断是否完成，未完成则无法关闭进度条modal
const handleClickConfirmButton = async () => {
    if (props.isComplete) {
        emits("clickConfirm")
        return true
    }
    Notification.warning({
        title: "无法关闭",
        content: `生成${props.text}未完成，请等待生成完成后再关闭`
    })
    return false
}

// 使用requestAnimationFrame优化性能 - 放入下面进度条中
let animateFrame = null
const updateProgress = () => {
    if (percent.value <= 0.95) {
        percent.value += 0.00018
        animateFrame = requestAnimationFrame(updateProgress)
    }
}
const cancelAnimateFrame = () => {
    if (animateFrame) {
        cancelAnimationFrame(animateFrame)
        animateFrame = null
    }
}

// 打开modal后自动移动
watch(
    () => props.visible,
    (newVal, oldVal) => {
        if (newVal) {
            percent.value = 0
            animateFrame = requestAnimationFrame(updateProgress)
        } else {
            cancelAnimateFrame()
            percent.value = 0
        }
    }
)
// 监听是否完成大纲生成
watch(
    () => props.isComplete,
    (newVal, oldVal) => {
        if (newVal) {
            percent.value = 1
            cancelAnimateFrame()
        }
    }
)
onUnmounted(() => {
    // 进度条清零
    cancelAnimateFrame()
    percent.value = 0
})
</script>

<style lang="less" scoped></style>
