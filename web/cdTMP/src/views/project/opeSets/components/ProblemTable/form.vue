<template>
    <div class="problem-form-container">
        <a-modal
            width="60%"
            draggable
            unmount-on-close
            ok-text="确认修改"
            cancel-text="关闭"
            v-model:visible="visible"
            title="修改问题单"
            :on-before-ok="handleSubmit"
        >
            <ma-form v-model="formData" :columns="columns" :options="options" ref="formRef">
                <template #form-ident> PT_{{ route.query.ident }}_{{ formData["ident"] }} </template>
            </ma-form>
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import useFormColumns from "./formHooks/useFormColumns"
import { ref } from "vue"
import MaForm from "@/components/ma-form/index.vue"
import problemApi from "@/api/project/problem"
import { useRoute } from "vue-router"
import { Message } from "@arco-design/web-vue"

const visible = ref(false)
const formRef = ref<InstanceType<typeof MaForm> | null>(null)
const route = useRoute()

// form数据
const project_id = route.query.id
const formData = ref<any>({})

const emit = defineEmits(["updateProblem"])

// modal提交按钮
const handleSubmit = async () => {
    const isValidated = await formRef.value!.validateForm()
    if (isValidated) {
        return false
    }
    try {
        await problemApi.update(formData.value.id, { project_id, ...formData.value })
        emit("updateProblem")
        Message.success("修改成功")
        formData.value = {} // 清除已有数据，防止卡顿
    } catch {
        return false
    }
}

// options
const options = ref({
    showButtons: false,
    labelAlign: "center"
})

// columns
const { columns } = useFormColumns()

const open = (record: any) => {
    visible.value = true
    formData.value = record
}

defineExpose({ open })
</script>

<style scoped></style>
