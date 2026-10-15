<template>
    <div class="description">
        <div v-if="isProblemData">
            <a-empty></a-empty>
        </div>
        <div v-else>
            <a-alert title="提示">对平台有什么意见如修改操作和修改格式都可以提出</a-alert>
            <a-tabs v-model:active-key="activeTab" class="atabs">
                <a-tab-pane title="基本信息" key="basic_detail">
                    <a-row :gutter="24" class="flex items-center ml-0 pl-0">
                        <a-col :xs="12" :md="8" :xl="6">
                            <a-typography-paragraph>问题单编号:</a-typography-paragraph>
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            <a-typography-paragraph type="primary">
                                {{ props.data.ident }}
                            </a-typography-paragraph>
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            <a-typography-paragraph>问题名称:</a-typography-paragraph>
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            <a-typography-paragraph>
                                {{ props.data.name }}
                            </a-typography-paragraph>
                        </a-col>
                    </a-row>
                    <a-row :gutter="24" class="flex items-center ml-0 pl-0">
                        <a-col :xs="12" :md="8" :xl="6">
                            <a-typography-paragraph>问题状态:</a-typography-paragraph>
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            <a-typography-paragraph>
                                {{ problem_status }}
                            </a-typography-paragraph>
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            <a-typography-paragraph>闭环方式:</a-typography-paragraph>
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            <a-typography-paragraph>
                                <a-space size="mini">
                                    <template v-if="problem_method.length > 0">
                                        <template v-for="item of problem_method">
                                            <a-tag :color="item === '修改文档' ? 'blue' : 'green'">{{ item }} </a-tag>
                                        </template>
                                    </template>
                                    <template v-else>
                                       <a-tag color="red">还未闭环</a-tag>
                                    </template>
                                </a-space>
                            </a-typography-paragraph>
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            <a-typography-paragraph>缺陷等级:</a-typography-paragraph>
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            <a-typography-paragraph>
                                {{ problem_grade }}
                            </a-typography-paragraph>
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            <a-typography-paragraph>缺陷类型:</a-typography-paragraph>
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            <a-typography-paragraph>
                                {{ problem_type }}
                            </a-typography-paragraph>
                        </a-col>
                    </a-row>
                </a-tab-pane>
                <a-tab-pane title="问题详情" key="problem_detail">
                    <a-row :gutter="24" class="flex items-center ml-0 pl-0 leading-10">
                        <a-col :xs="12" :md="8" :xl="6" class="text-center"> 操作步骤： </a-col>
                        <a-col :xs="8" :md="16" :xl="12">
                            {{ props.data.operation }}
                        </a-col>
                    </a-row>
                    <a-row :gutter="24" class="flex items-center ml-0 pl-0 leading-10">
                        <a-col :xs="12" :md="8" :xl="6" class="text-center"> 期望结果： </a-col>
                        <a-col :xs="8" :md="16" :xl="12">
                            {{ props.data.expect }}
                        </a-col>
                    </a-row>
                    <a-row :gutter="24" class="flex items-center ml-0 pl-0 leading-10">
                        <a-col :xs="12" :md="8" :xl="6" class="text-center"> 问题结果： </a-col>
                        <a-col :xs="8" :md="16" :xl="12">
                            {{ props.data.result }}
                        </a-col>
                    </a-row>
                    <a-row :gutter="24" class="flex items-center ml-0 pl-0 leading-10">
                        <a-col :xs="12" :md="8" :xl="6" class="text-center"> 违反规则： </a-col>
                        <a-col :xs="8" :md="16" :xl="12">
                            {{ props.data.rules }}
                        </a-col>
                    </a-row>
                    <a-row :gutter="24" class="flex items-center ml-0 pl-0 leading-10">
                        <a-col :xs="12" :md="8" :xl="6" class="text-center"> 修改建议： </a-col>
                        <a-col :xs="8" :md="16" :xl="12">
                            {{ props.data.suggest }}
                        </a-col>
                    </a-row>
                </a-tab-pane>
                <a-tab-pane title="人员信息" key="person_detail">
                    <a-row :gutter="24" class="flex items-center ml-0 pl-0 leading-10">
                        <a-col :xs="12" :md="8" :xl="6" class="text-center"> 提单人员： </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            {{ props.data.postPerson }}
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6" class="text-center"> 提单时间： </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            {{ props.data.postDate }}
                        </a-col>
                    </a-row>
                    <a-row :gutter="24" class="flex items-center ml-0 pl-0 leading-10">
                        <a-col :xs="12" :md="8" :xl="6" class="text-center"> 设计师上级： </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            {{ props.data.designerPerson }}
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6" class="text-center"> 签署时间： </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            {{ props.data.designDate }}
                        </a-col>
                    </a-row>
                    <a-row :gutter="24" class="flex items-center ml-0 pl-0 leading-10">
                        <a-col :xs="12" :md="8" :xl="6" class="text-center"> 验证人员： </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            {{ props.data.verifyPerson }}
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6" class="text-center"> 签署时间： </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            {{ props.data.verifyDate }}
                        </a-col>
                    </a-row>
                    <a-row :gutter="24" class="flex items-center ml-0 pl-0 leading-10">
                        <a-col :xs="12" :md="8" :xl="6" class="text-center"> 撤销人： </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            {{ props.data.revokePerson }}
                        </a-col>
                        <a-col :xs="12" :md="8" :xl="6" class="text-center"> 签署时间： </a-col>
                        <a-col :xs="12" :md="8" :xl="6">
                            {{ props.data.revokeDate }}
                        </a-col>
                    </a-row>
                </a-tab-pane>
            </a-tabs>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue"
import commonApi from "@/api/common"
const props = defineProps({
    data: {
        type: Object,
        default: () => ({})
    }
})
const isProblemData = ref(false)
// 当前tab栏
const activeTab = ref("basic_detail")
// 处理字典
const problem_status = ref("")
const problem_type = ref("")
const problem_grade = ref("")
const problem_method = ref([])
const getDict = async () => {
    let problemStatu = await commonApi.getDict("problemStatu")
    let problemType = await commonApi.getDict("problemType")
    let problemGrade = await commonApi.getDict("problemGrade")
    let closeMethod = await commonApi.getDict("closeMethod")
    problemStatu.data.forEach((item) => {
        if (item.key === props.data.status) {
            problem_status.value = item.title
        }
    })
    problemType.data.forEach((item) => {
        if (item.key === props.data.type) {
            problem_type.value = item.title
        }
    })
    problemGrade.data.forEach((item) => {
        if (item.key === props.data.grade) {
            problem_grade.value = item.title
        }
    })
    closeMethod.data.forEach((item) => {
        for (let method in props.data.closeMethod) {
            if (item.key == props.data.closeMethod[method]) {
                problem_method.value.push(item.title)
            }
        }
    })
}
getDict()
</script>

<style lang="less" scoped>
.description {
    width: 1076px;
}
.atabs {
    text-align: left;
    padding-left: 5px;
}
</style>
