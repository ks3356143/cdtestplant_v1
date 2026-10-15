<template>
    <!-- 组件：该组件显示一个正方体，可粘贴图片内容进去并展示，并生成base64到数据里面 -->
    <div class="image-input-container flex flex-col gap-1">
        <div class="image-input-handle flex items-center justify-center" @paste="handlePaste">
            <!-- 加载状态 -->
            <div v-if="isLoading">
                <a-spin :size="32" />
            </div>
            <!-- 正常显示状态 -->
            <template v-else-if="imgData">
                <img :src="imgData" alt="粘贴的图片" class="preview-image img-container" />
            </template>

            <template v-else>
                <div class="placeholder">此处Ctrl+V粘贴图片</div>
            </template>
        </div>
        <!-- 题注：fontnote -->
        <a-input v-model="fontnote" class="max-w-100" placeholder="请输入题注"></a-input>
    </div>
</template>

<script setup lang="ts">
import { Message } from "@arco-design/web-vue"
import { nextTick, ref, onMounted, onBeforeUnmount } from "vue"

const imgData = defineModel<string>()
const fontnote = defineModel<string>("fontnote")
const isLoading = ref(false)

// 全局粘贴处理函数
const onGlobalPaste = (e: ClipboardEvent) => {
    // 可以增加判断：只有当前组件所在的 modal 打开时才处理（通过 props 传入 visible 状态或使用 provide/inject）
    // 简单起见，这里假设始终需要处理（父组件控制显示隐藏）
    handlePaste(e)
}

// 处理粘贴逻辑（复用之前的修复版）
const handlePaste = (e: ClipboardEvent) => {
    e.preventDefault()
    const clipboardData = e.clipboardData
    if (!clipboardData) return

    const items = clipboardData.items
    let imageItem: DataTransferItem | null = null

    for (let i = 0; i < items.length; i++) {
        const item = items[i]
        if (item.kind === "file" && item.type.startsWith("image/")) {
            imageItem = item
            break
        }
    }

    if (!imageItem) {
        Message.error("请粘贴图片，无法粘贴文字或其他内容")
        return
    }

    const file = imageItem.getAsFile()
    if (!file) {
        Message.error("读取图片失败，请重新粘贴")
        return
    }

    if (file.size > 50 * 1024 * 1024) {
        Message.error("要求图片不超过50M")
        return
    }

    isLoading.value = true
    const reader = new FileReader()
    reader.onload = (e) => {
        imgData.value = e.target!.result as string
        nextTick(() => {
            isLoading.value = false
        })
    }
    reader.onerror = () => {
        Message.error("图片加载失败，请重试")
        isLoading.value = false
    }
    reader.readAsDataURL(file)
}

// 挂载全局监听
onMounted(() => {
    document.addEventListener("paste", onGlobalPaste)
})

onBeforeUnmount(() => {
    document.removeEventListener("paste", onGlobalPaste)
})
</script>

<style scoped lang="less">
.image-input-handle {
    width: 200px;
    height: 180px;
    border: 1px solid #eee;
    cursor: alias;

    .img-container {
        width: 100%;
        height: 100%;
    }
}

.preview-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}
</style>
