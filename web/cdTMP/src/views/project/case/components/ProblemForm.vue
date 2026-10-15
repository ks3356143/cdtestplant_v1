<template>
    <div class="problem-form-caintainer">
        <a-modal
            v-model:visible="visible"
            :on-before-ok="handleBeforeOk"
            ok-text="修改"
            cancel-text="关闭"
            width="950px"
            draggable
            unmount-on-close
        >
            <template #title>{{ props.title }}</template>
            <ma-form v-model="form" :columns="columnsOptions" :options="options" ref="crudForm" />
        </a-modal>
    </div>
</template>

<script setup lang="ts">
// 本组件是在：测试项页面 -> 显示用例关联的问题单
import { ref, reactive } from "vue"
import { IProps } from "./problemFormTypes"
import { useRoute } from "vue-router"
import problemApi from "@/api/project/problem"
import { Message } from "@arco-design/web-vue"
const visible = ref<boolean>(false)
const route = useRoute()
const props = defineProps<IProps>()
const handleBeforeOk = async () => {
    const validateRes = await crudForm.value.validateForm()
    if (validateRes) {
        return false
    }
    const res = await problemApi.update(form.value.id, { ...form.value, projectId: route.query.id })
    if (res.success) {
        Message.success("更新问题单成功")
    }
}
// 初始化ma-form
const crudForm = ref<any>()
const form = ref<any>({})
const options = ref({
    showButtons: false,
    labelAlign: "center"
})
const columnsOptions = reactive([
    {
        formType: "grid-tailwind",
        customClass: [],
        colNumber: 2,
        cols: [
            {
                formList: [
                    {
                        title: "问题名称",
                        dataIndex: "name",
                        rules: [{ required: true, message: "名称是必填" }]
                    },
                    {
                        title: "缺陷状态",
                        dataIndex: "status",
                        formType: "radio",
                        rules: [{ required: true, message: "缺陷状态必填" }],
                        dict: {
                            name: "problemStatu",
                            translation: true,
                            props: { label: "title", value: "key" }
                        }
                    },
                    {
                        title: "缺陷等级",
                        dataIndex: "grade",
                        formType: "radio",
                        rules: [{ required: true, message: "缺陷等级必填" }],
                        dict: {
                            name: "problemGrade",
                            translation: true,
                            props: { label: "title", value: "key" }
                        }
                    }
                ]
            },
            {
                formList: [
                    {
                        title: "问题标识",
                        dataIndex: "ident",
                        disabled: true
                    },
                    {
                        title: "闭环方式",
                        dataIndex: "closeMethod",
                        formType: "checkbox",
                        dict: {
                            name: "closeMethod",
                            translation: true,
                            props: { label: "title", value: "key" }
                        }
                    },
                    {
                        title: "缺陷类型",
                        dataIndex: "type",
                        rules: [{ required: true, message: "缺陷类型必填" }],
                        formType: "radio",
                        dict: {
                            name: "problemType",
                            translation: true,
                            props: { label: "title", value: "key" }
                        }
                    }
                ]
            }
        ]
    },
    {
        title: "测试人员填写",
        formType: "divider"
    },
    {
        title: "问题描述",
        dataIndex: "operation",
        formType: "editor"
    },
    {
        title: "问题影响",
        dataIndex: "result",
        formType: "textarea"
    },
    {
        title: "研制方回复",
        formType: "divider"
    },
    {
        title: "原因分析",
        dataIndex: "analysis",
        formType: "textarea"
    },
    {
        title: "影响域分析",
        dataIndex: "effect_scope",
        formType: "textarea"
    },
    {
        title: "改正措施",
        dataIndex: "solve",
        formType: "textarea"
    },
    {
        title: "回归填写",
        formType: "divider"
    },
    {
        title: "回归结果",
        dataIndex: "verify_result",
        formType: "editor"
    },
    {
        title: "人员信息",
        formType: "divider"
    },
    {
        formType: "grid-tailwind",
        customClass: [],
        colNumber: 2,
        cols: [
            {
                formList: [
                    {
                        title: "测试人员",
                        dataIndex: "postPerson",
                        formType: "select",
                        rules: [{ required: true, message: "测试人员必填" }],
                        dict: {
                            url: "system/user/list",
                            translation: true,
                            params: { project_id: route.query.id },
                            props: { label: "name", value: "name" }
                        }
                    },
                    {
                        title: "开发人员",
                        dataIndex: "designerPerson",
                        formType: "input",
                    },
                    {
                        title: "回归人员",
                        dataIndex: "verifyPerson",
                        formType: "select",
                        dict: {
                            url: "system/user/list",
                            translation: true,
                            params: { project_id: route.query.id },
                            props: { label: "name", value: "name" }
                        }
                    }
                ]
            },
            {
                formList: [
                    {
                        title: "测试日期",
                        dataIndex: "postDate",
                        formType: "date"
                    },
                    {
                        title: "开发方日期",
                        dataIndex: "designDate",
                        formType: "date"
                    },
                    {
                        title: "回归日期",
                        dataIndex: "verifyDate",
                        formType: "date"
                    }
                ]
            }
        ]
    }
])

// 暴露属性和方法
const open = (problem: object) => {
    visible.value = true
    // 打开时初始化表单
    form.value = problem
}
defineExpose({ open })
</script>

<style lang="less" scoped></style>
