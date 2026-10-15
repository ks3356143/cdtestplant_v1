<template>
    <div class="upload-input-container">
        <a-upload
            accept=".zip"
            tip="只支持C/C++，不支持FPGA代码，上传后会自行录入圈复杂度等信息"
            :limit="1"
            :action="`/api/dut_upload/upload_file?dut_id=${form.id}`"
            @success="uploadSuccessHandle"
            @error="handleError"
        ></a-upload>
    </div>
</template>

<script setup lang="ts">
import { Message } from "@arco-design/web-vue"
import { inject } from "vue"

// 表单数据
const form: any = inject("formModel")
// 组件props
const props = defineProps({
    component: Object, // 组件配置信息
    customField: { type: String, default: undefined } // 自定义字段名称，用于子表单
})
// 上传成功后回调-即时给前端反馈
const uploadSuccessHandle = (FileItem: any) => {
    form.value.comment_lines = FileItem.response.data.comment_lines
    form.value.effective_lines = FileItem.response.data.effective_lines
    form.value.total_lines = FileItem.response.data.total_lines
    Message.success("解析代码成功，圈复杂度、模块大小等均已录入")
}
// 上传失败
const handleError = () => {
    Message.error("处理失败，请检查是否是C/C++代码，且zip文件")
}

defineOptions({
    name: "UploadInput"
})
</script>

<style lang="less" scoped></style>
