<template>
    <ope-sets-data-table
        ref="tableRef"
        class="case-table-container"
        table-id="basic-table-case"
        :api="caseApi.getCaseList"
        :columns="columns"
        :delete-api="caseApi.delete"
        :replace-api="caseApi.replace"
        :replace-columns="replaceColumns"
        replace-key="case"
        parent-title="对应测试项"
        @edit="(record) => formRef?.open(record)"
        @selection-change="(rows) => (selecteds = rows)"
    >
        <template #toolbar-extra>
            <a-divider direction="vertical"></a-divider>
            <a-button type="outline" @click="handlePerpleModal">批量修改人员</a-button>
            <a-button type="outline" @click="handleExetimeModal">批量修改时间</a-button>
        </template>
        <!-- 测试步骤：富文本 + 执行结果 -->
        <template #cell-testStep="{ record }">
            <div v-for="(step, index) in record.testStep" :key="index">
                <span class="text-amber-700">步骤{{ index + 1 }}）</span>
                <div class="operation">
                    <span class="text-lime-700">操作：</span>
                    <div v-html="step.operation"></div>
                </div>
                <div class="expect">
                    <span class="text-teal-700">预期：</span>
                    <div>{{ step.expect }}</div>
                </div>
                <div class="expect">
                    <span class="text-rose-700">执行结果：</span>
                    <div v-html="step.result"></div>
                </div>
                <template v-if="record.testStep.length !== index + 1">
                    <a-divider></a-divider>
                </template>
            </div>
        </template>
        <template #parent-cell="{ record }">
            <Trigger :demandInfo="record.test" @refresh="tableRef?.refresh()" />
        </template>
    </ope-sets-data-table>
    <!-- 测试用例-表单页面 -->
    <Form ref="formRef" @refresh="tableRef?.refresh()"></Form>
    <!-- 批量替换人员组件 -->
    <replace-person :selectRows="selecteds" ref="replacePersonModalRef" />
    <!-- 批量替换时间 -->
    <replace-exetime :selectRows="selecteds" ref="replaceExetimeModalRef" />
</template>

<script setup lang="ts">
import { computed, provide, ref } from "vue"
import caseApi from "@/api/project/case"
import OpeSetsDataTable from "@/views/project/opeSets/components/TableCommonComponent/OpeSetsDataTable.vue"
import Form from "./form.vue"
import Trigger from "./Trigger.vue"
import ReplacePerson from "@/views/project/opeSets/components/CaseTable/ReplacePerson.vue"
import ReplaceExetime from "@/views/project/opeSets/components/CaseTable/ReplaceExetime.vue"

const columns = ref([
    {
        title: "标识",
        dataIndex: "ident",
        align: "center",
        width: 80,
        hide: false,
        ellipsis: true,
        search: true,
        formType: "input",
        fixed: ""
    },
    {
        title: "名称",
        dataIndex: "name",
        align: "left",
        width: 120,
        hide: false,
        ellipsis: true,
        search: true,
        formType: "input",
        fixed: ""
    },
    {
        title: "用例综述",
        dataIndex: "summarize",
        align: "left",
        width: 150,
        hide: false,
        ellipsis: false,
        search: false, // 不搜索
        formType: "input", // 搜索输入框形式
        isHyperText: false,
        bodyCellClass: "hyperTextCell-table-chen",
        fixed: ""
    },
    {
        // 这是单独处理的字段，只声明Search组件相关属性
        title: "测试步骤",
        dataIndex: "testStep",
        align: "left",
        width: 400,
        hide: false,
        ellipsis: false,
        search: false,
        formType: "input",
        bodyCellClass: "hyperTextCell-table-chen",
        fixed: ""
    }
])
provide("columns", columns)

const tableRef = ref<InstanceType<typeof OpeSetsDataTable> | null>(null)
const formRef = ref<InstanceType<typeof Form> | null>(null)
// 供批量替换弹窗使用的列（去掉标识列）
const replaceColumns = computed(() => columns.value.filter((it) => it.dataIndex !== "ident"))

// 行选择：由公共表格同步过来，供批量修改人员/时间使用
const selecteds = ref<any[]>([])

// 批量修改人员
const replacePersonModalRef = ref<InstanceType<typeof ReplacePerson>>()
const handlePerpleModal = () => {
    replacePersonModalRef.value!.open(undefined)
}

// 批量修改时间
const replaceExetimeModalRef = ref<InstanceType<typeof ReplaceExetime>>()
const handleExetimeModal = () => {
    replaceExetimeModalRef.value!.open(undefined)
}
</script>

<style scoped lang="less">
// search根组件
.search-container {
    margin-bottom: 10px;
}
</style>
