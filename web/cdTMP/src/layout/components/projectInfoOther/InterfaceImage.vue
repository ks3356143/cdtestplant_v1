<template>
    <div class="interface-image-container">
        <a-modal
            v-model:visible="visible"
            width="50%"
            draggable
            :on-before-ok="handleSyncOk"
            unmount-on-close
            ok-text="确认保存"
            cancel-text="关闭不保存"
            :maskClosable="false"
            @close="handleOnClose"
        >
            <template #title>软件接口图</template>
            <div class="flex justify-center items-center">
                <ImageInput v-model="imageUrl" v-model:fontnote="fontnote" />
            </div>
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { ref, getCurrentInstance } from "vue"
import ImageInput from "./projectModal/ImageInput/index.vue"
import { Message } from "@arco-design/web-vue"
import projectApi from "@/api/project/project"
import { useRoute } from "vue-router"

const { proxy } = getCurrentInstance() as any
const route = useRoute()
const visible = ref(false)

// props
const { reset } = defineProps<{
    reset: () => void
}>()

// 题注和图片数据
const fontnote = ref("")
const imageUrl = ref("")

const handleSyncOk = async () => {
    // 验证题注是否为空
    if (!fontnote.value?.trim() || !imageUrl.value?.trim()) {
        Message.error("请输入题注和粘贴图片")
        return false
    }
    // 提交数据
    try {
        await projectApi.postInterfaceImage(route.query.id, { fontnote: fontnote.value, content: imageUrl.value, type: "image" })
        Message.success("保存成功")
    } catch (e) {
        return false
    }
}

const handleOnClose = () => {
    // 用来清空数据
    fontnote.value = ""
    imageUrl.value = ""
    reset()
}

const open = async () => {
    proxy?.$loading?.show("数据加载中...")
    try {
        const { data } = await projectApi.getInterfaceImage(route.query.id)
        fontnote.value = data.fontnote || ""
        imageUrl.value = data.content || ""
        visible.value = true
    } catch (e) {
    } finally {
        proxy?.$loading?.hide()
    }
}

defineExpose({ open })
</script>

<style scoped></style>
