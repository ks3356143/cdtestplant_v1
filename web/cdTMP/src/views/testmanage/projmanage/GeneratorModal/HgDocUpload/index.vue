<template>
    <div class="hg-doc-upload-container">
        <div v-if="roundNum === 0">
            <a-alert type="warning">暂无回归测试轮次信息</a-alert>
        </div>
        <a-tabs v-else :default-active-key="1" type="line">
            <a-tab-pane v-for="n in roundNum" :key="n" :title="`第${n + 1}轮${documentType}`">
                <a-upload
                    :action="`/api/documentUpload/file?id=${projectId}&documentType=${documentType}&round_num=${n + 1}`"
                    :limit="1"
                    accept=".docx, application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    @error="uploadErrorHandle"
                    @before-upload="confirmUploadHandle"
                >
                    <template #upload-button>
                        <a-button type="primary"><icon-upload />点击上传</a-button>
                    </template>
                </a-upload>
            </a-tab-pane>
        </a-tabs>
    </div>
</template>

<script setup lang="ts">
/* 该组件是回归测试说明、回归测试记录上传逻辑组件 */
import { onMounted, ref } from "vue"
import otherApi from "@/api/generate/other"
import { Message, Modal } from "@arco-design/web-vue"

// props
const { projectId, documentType } = defineProps<{ projectId: number | null; documentType: string }>()

// 组件加载时候就请求后端，有几个轮次
onMounted(async () => {
    try {
        if (!projectId) return
        const {
            data: { count }
        } = await otherApi.getHgRoundNumber({ id: projectId })
        // count为非第一轮其他轮次数量
        roundNum.value = count
    } catch (err) {
        roundNum.value = 0
    }
})

// ref - 定义非第一轮轮次数量
const roundNum = ref(0)

// 上传失败的事件 - 报错内容由后端定义（message字段）
const uploadErrorHandle = (fielItem: any) => {
    const res = JSON.parse(fielItem.response)
    if (res.message) {
        Message.error(res.message)
    }
}
// 上传弹窗事件
const confirmUploadHandle = (file: any) => {
    return new Promise((resolve, reject) => {
        Modal.confirm({
            title: "请确认您上传的文件是带有文档片段的docx文档",
            content: `${file.name}`,
            onOk: () => resolve(true),
            onCancel: () => reject("cancel")
        })
    })
}

defineOptions({
    name: "HgDocUpload"
})
</script>

<style lang="less" scoped></style>
