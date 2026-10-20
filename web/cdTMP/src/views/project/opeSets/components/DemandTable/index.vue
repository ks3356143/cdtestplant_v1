<template>
    <ope-sets-data-table
        ref="tableRef"
        class="demand-table-container"
        table-id="basic-table-demand"
        :api="demandApi.getTestDemandList"
        :columns="columns"
        :delete-api="demandApi.delete"
        :replace-api="demandApi.replace"
        :replace-columns="replaceColumns"
        replace-key="demand"
        parent-title="对应设计需求"
        @edit="(record) => formRef?.open(record)"
        @selection-change="(rows) => (selecteds = rows)"
    >
        <template #toolbar-extra>
            <a-divider direction="vertical"></a-divider>
            <a-button type="outline" @click="handleOpenReplacePriority">批量修改优先级</a-button>
        </template>
        <!-- 测试子项及步骤 -->
        <template #cell-testContent="{ record }">
            <div v-if="record.testContent?.length > 0">
                <template v-for="(sub, idx) in record.testContent" :key="idx">
                    <div class="subTitle mt-3">{{ idx + 1 }}.{{ sub.subName }}</div>
                    <div>测试子项描述：{{ sub.subDescription }}</div>
                    <template v-for="(step, index) in sub.subStep" :key="index">
                        <span class="text-amber-700">步骤{{ index + 1 }}）</span>
                        <div class="operation"><span class="text-bold">操作：</span>{{ step.operation }}</div>
                        <div class="mb-1"><span class="text-bold">预期：</span>{{ step.expect }}</div>
                    </template>
                </template>
            </div>
        </template>
        <template #cell-priority="{ record }">
            {{ showType(record) }}
        </template>
        <template #cell-testType="{ record }">
            {{ showTestType(record) }}
        </template>
        <template #parent-cell="{ record }">
            <Trigger :designInfo="record.design" @refresh="tableRef?.refresh()" />
        </template>
    </ope-sets-data-table>
    <!-- 测试项-表单页面 -->
    <Form ref="formRef" @refresh="tableRef?.refresh()"></Form>
    <!-- 批量修改优先级 -->
    <ReplacePriority ref="replacePriorityRef" @modifySuccess="tableRef?.refresh()" :selected-rows="selecteds" />
</template>

<script setup lang="ts">
import { computed, provide, ref } from "vue"
import demandApi from "@/api/project/testDemand"
import useShowType from "@/views/project/opeSets/components/DesignTable/useShowType"
import OpeSetsDataTable from "@/views/project/opeSets/components/TableCommonComponent/OpeSetsDataTable.vue"
import Form from "./form.vue"
import Trigger from "./Trigger.vue"
import ReplacePriority from "@/views/project/opeSets/components/DemandTable/ReplacePriority.vue"

// 0.[不同]定义列字段
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
        title: "优先级",
        dataIndex: "priority",
        align: "center",
        width: 70,
        hide: false,
        ellipsis: true,
        search: true,
        formType: "select",
        dict: true,
        // 只是指明 a-table-column 需要单独渲染
        showType: (text: string) => text,
        fixed: ""
    },
    {
        title: "测试类型",
        dataIndex: "testType",
        align: "center",
        width: 80,
        hide: false,
        ellipsis: true,
        search: true,
        formType: "select",
        dict: true,
        showType: (text: string) => text,
        fixed: ""
    },
    {
        title: "测项描述",
        dataIndex: "testDesciption",
        align: "left",
        width: 200,
        hide: false,
        ellipsis: false,
        search: false,
        formType: "input",
        isHyperText: false,
        bodyCellClass: "hyperTextCell-table-chen",
        fixed: ""
    },
    {
        // 这是单独处理的字段，只声明Search组件相关属性
        title: "测试子项",
        dataIndex: "testContent",
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

// 2.字典名称
const showType = useShowType("priority")
const showTestType = useShowType("testType")

// 供批量替换弹窗使用的列（去掉展示型字段）
const replaceColumns = computed(() =>
    columns.value.filter((it: any) => it.dataIndex !== "priority" && it.dataIndex !== "testType")
)

// 行选择：由公共表格同步过来，供批量修改优先级使用
const selecteds = ref<any[]>([])

// 批量修改优先级
const replacePriorityRef = ref<InstanceType<typeof ReplacePriority> | null>(null)
const handleOpenReplacePriority = () => {
    replacePriorityRef.value?.open(undefined)
}
</script>

<style scoped lang="less">
.search-container {
    margin-bottom: 10px;
}
</style>

<style lang="less">
// 对测试项子项步骤进行显示
.subTitle {
    overflow: hidden;
    font-size: 16px;
}
.text-bold {
    font-weight: bold;
}
</style>
