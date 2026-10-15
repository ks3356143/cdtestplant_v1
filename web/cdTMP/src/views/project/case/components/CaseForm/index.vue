<template>
    <a-modal
        v-model:visible="visible"
        width="80%"
        draggable
        :okLoading="okLoading"
        unmount-on-close
        :title="form.name ? form.name : '请填写用例名称'"
        :on-before-ok="handleOkBefore"
    >
        <a-spin :loading="loading" class="w-full h-full">
            <ma-form :columns="columnsOptions" v-model="form" :options="options" ref="maFormRef"></ma-form>
        </a-spin>
    </a-modal>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue"
import { type ICaseFormInData } from "../types"
import caseApi from "@/api/project/case"
import { Message } from "@arco-design/web-vue"

const visible = ref(false) // 显示和隐藏
const loading = ref(false) // 整个modal的加载状态-根据请求case而定
const okLoading = ref(false) // 提交按钮的loading状态
const form = ref<any>({}) // 表单数据
const maFormRef = ref<any>(null)

// 定义事件
const emit = defineEmits(["caseUpdate"])

// event：点击modal的确定修改按钮
const handleOkBefore = async () => {
    // 验证表单
    const validateRes = await maFormRef.value.validateForm()
    if (validateRes) {
        // 验证不通过
        return false
    } else {
        // 验证通过
        okLoading.value = true
        try {
            await caseApi.update(form.value.id, form.value)
            okLoading.value = false
            Message.success("修改用例成功")
            emit("caseUpdate", form.value)
            return true
        } catch (err) {
            okLoading.value = false
            return false
        }
    }
}

// 暴露组件方法
const open = async (formData: ICaseFormInData): Promise<void> => {
    visible.value = true
    loading.value = true
    const res = await caseApi.getCaseList({ id: formData.id })
    form.value = res.data.items[0]
    loading.value = false
}

// options
const options = ref({
    showButtons: false
})

// columns
const columnsOptions = reactive([
    {
        formType: "grid",
        cols: [
            { span: 12, formList: [{ title: "用例标识", dataIndex: "ident", disabled: true }] },
            {
                span: 12,
                formList: [{ title: "用例名称", dataIndex: "name", rules: [{ required: true, message: "名称是必填" }] }]
            }
        ]
    },
    {
        formType: "card",
        customClass: ["ml-5", "mb-3", "py-0", "px-0"],
        title: "人员信息",
        formList: [
            {
                formType: "grid",
                cols: [
                    { span: 8, formList: [{ title: "设计人员", dataIndex: "designPerson" }] },
                    { span: 8, formList: [{ title: "执行人员", dataIndex: "testPerson" }] },
                    { span: 8, formList: [{ title: "审核人员", dataIndex: "monitorPerson" }] }
                ]
            }
        ]
    },
    {
        formType: "grid",
        cols: [{ span: 24, formList: [{ title: "用例综述", dataIndex: "summarize" }] }]
    },
    {
        formType: "grid",
        cols: [{ span: 24, formList: [{ title: "用例初始化", dataIndex: "initialization" }] }]
    },
    {
        formType: "grid",
        cols: [
            { span: 12, formList: [{ title: "前提与约束", dataIndex: "premise" }] },
            { span: 12, formList: [{ title: "执行时间", dataIndex: "exe_time", formType: "date" }] }
        ]
    },
    {
        title: "测试步骤",
        dataIndex: "testStep",
        formType: "children-form",
        formList: [
            {
                title: "操作",
                dataIndex: "operation",
                formType: "editor",
                height: 180
            },
            {
                title: "预期",
                placeholder: "请输入预期结果",
                dataIndex: "expect"
            },
            {
                title: "结果",
                dataIndex: "result",
                formType: "editor",
                height: 180
            },
            {
                title: "是否通过",
                dataIndex: "passed",
                formType: "radio",
                dict: { name: "passType", props: { label: "title", value: "key" } },
                rules: [{ required: true, message: "是否通过必填" }]
            }
        ]
    }
])

defineExpose({
    open
})
</script>

<style scoped></style>
