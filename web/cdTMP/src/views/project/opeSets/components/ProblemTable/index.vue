<template>
    <ope-sets-data-table
        ref="tableRef"
        class="problem-table-container"
        table-id="basic-table-problem"
        :api="problemApi.searchAllProblem"
        :columns="columns"
        :loading="problemStatusLoading || problemGradeLoading"
        :show-selection="false"
        parent-title="所属用例"
        :parent-width="110"
        :operation-width="120"
        @edit="handleOpenProblemModify"
    >
        <template #cell-ident="{ record }"> PT_{{ route.query.ident }}_{{ record.ident }} </template>
        <template #cell-problemStatu="{ record }">
            <a-tag :color="changeColor(record.status)">
                {{ problemStatus[record.status] }}
            </a-tag>
        </template>
        <template #cell-problemGrade="{ record }">
            <a-tag :color="changeGradeColor(record.grade)">
                {{ gradeOptions[record.grade] }}
            </a-tag>
        </template>
        <template #parent-cell="{ record }">
            <a-tag v-if="record.hang" color="red">无关联用例</a-tag>
            <a-button v-else color="green" type="primary" @click="seeRelatedCases(record)">
                <icon-eye />
            </a-button>
        </template>
    </ope-sets-data-table>
    <!-- 问题单表单页面 -->
    <ProblemForm ref="problemRef" @updateProblem="tableRef?.refresh()" />
    <case-modal ref="caseModalRef" />
</template>

<script setup lang="ts">
import { provide, ref } from "vue"
import { useRoute } from "vue-router"
import problemApi from "@/api/project/problem"
import problemSingleApi from "@/api/project/singleProblem"
import OpeSetsDataTable from "@/views/project/opeSets/components/TableCommonComponent/OpeSetsDataTable.vue"
import CaseModal from "@/views/project/case/components/CaseModal.vue"
import ProblemForm from "./form.vue"
import useColumns from "./hooks/useColumns"
import useProblemStatu from "./hooks/useProblemStatu"
import useProblemGrade from "./hooks/useProblemGrade"

const route = useRoute()
const tableRef = ref<InstanceType<typeof OpeSetsDataTable> | null>(null)
const caseModalRef = ref<InstanceType<typeof CaseModal> | null>(null)
const problemRef = ref<InstanceType<typeof ProblemForm> | null>(null)

// 加载初始字典数据
const { loading: problemStatusLoading, problemStatus, changeColor } = useProblemStatu()
const { loading: problemGradeLoading, gradeOptions, changeGradeColor } = useProblemGrade()

// 定义表格列
const { columns } = useColumns()
provide("columns", columns)

// 查看关联用例
const seeRelatedCases = async (record: any) => {
    const res = await problemSingleApi.getRelativeCases({ id: record.id })
    caseModalRef.value && caseModalRef.value.open(res.data)
}

// 点击修改
const handleOpenProblemModify = (record: any) => {
    problemRef.value?.open(record)
}
</script>

<style scoped>
.max-height-class {
    max-height: 300px;
    overflow-y: auto;
    white-space: normal;
    word-break: break-all;
    scrollbar-width: thin;
}

.max-height-class::-webkit-scrollbar {
    width: 6px;
}

.max-height-class::-webkit-scrollbar-thumb {
    background-color: var(--app-line-strong, #cfd5dc);
}

.max-height-class::-webkit-scrollbar-track {
    background-color: transparent;
}
</style>
