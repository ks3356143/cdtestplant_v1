<template>
    <div class="form-container">
        <a-modal v-model:visible="visible" width="70%" unmount-on-close ok-text="更新" :on-before-ok="handleBeforeOk">
            <template #title>设计需求-{{ modalTitle }}</template>
            <ma-form v-model="form" ref="formRef" :columns="columnOptions" :options="options">
                <template #inputPrepend-ident> SJ_XX </template>
            </ma-form>
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import useOptions from "@/views/project/dut/DesignSubForm/useOptions"
import designApi from "@/api/project/designDemand"
import { useRoute } from "vue-router"
import { Message } from "@arco-design/web-vue"

// route
const route = useRoute()

// refs
const formRef = ref(null)

// emits
const emit = defineEmits(["refresh"])

// columns/options
const { options, columnOptions } = useOptions(formRef)

// modal-visible
const visible = ref(false)

// form-data
const form = ref({})

// 暴露给外部open函数
const modalTitle = ref("")
const open = async (rowData: any) => {
    // 请求数据
    try {
        // 设置表单名称
        modalTitle.value = rowData.title
        const res = await designApi.getDesignOneById(rowData.id)
        // 更新表单
        form.value = res.data
        visible.value = true
    } catch (e) {
        visible.value = false
    }
}
// 异步确认按钮点击
const handleBeforeOk = async () => {
    const isValidated = await (formRef.value as any).validateForm()
    if (isValidated) {
        // 失败
        return false
    } else {
        // 成功 **变化**
        const round = (form.value as any).key.split("-")[0]
        const dut_key = (form.value as any).key.split("-")[1]
        await designApi.update((form.value as any).id, {
            project_id: route.query.id,
            round,
            ...form.value,
            dut: dut_key
        })
        // 刷新table
        emit("refresh")
        Message.success("修改成功")
    }
}
// out use
defineExpose({ open })
</script>

<style lang="less" scoped></style>
