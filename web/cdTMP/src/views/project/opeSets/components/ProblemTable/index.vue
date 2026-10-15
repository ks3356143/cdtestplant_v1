<template>
    <div class="problem-table-container">
        <search v-show="searchVisible" @submit="searchSubmit" />
        <div class="lg:flex justify-between mb-2">
            <a-space> </a-space>
            <a-space>
                <a-space class="lg:mt-0 mt-2">
                    <slot name="tools"></slot>
                    <a-tooltip content="刷新表格">
                        <a-button shape="circle" @click="fetchData()"><icon-refresh /></a-button>
                    </a-tooltip>
                    <a-tooltip content="显隐搜索" @click="searchVisible = !searchVisible">
                        <a-button shape="circle"><icon-search /></a-button>
                    </a-tooltip>
                    <a-tooltip content="设置">
                        <a-button shape="circle" @click="clickSetting"><icon-settings /></a-button>
                    </a-tooltip>
                </a-space>
            </a-space>
        </div>
        <a-table
            id="basic-table-problem"
            v-bind="options"
            hoverable
            column-resizable
            ref="tableRef"
            row-key="id"
            :columns="columns"
            :loading="isFetching || problemStatusLoading || problemGradeLoading"
            :data="tableData"
            :scroll="{ x: '100%' }"
            :pagination="{
                showTotal: true,
                showPageSize: true,
                total: total,
                pageSizeOptions: [10, 20, 50, 1000],
                hideOnSinglePage: false
            }"
            @page-change="pageChange"
            @page-size-change="pageSizeChange"
        >
            <template #columns>
                <template v-for="column in columns" :key="column.dataIndex">
                    <template v-if="!column.hide">
                        <a-table-column v-bind="column" v-if="column.dataIndex === 'operation'">
                            <template #cell="{ record }" v-if="column.isHyperText">
                                <div v-html="record[column.dataIndex]"></div>
                            </template>
                        </a-table-column>
                        <a-table-column v-bind="column" v-else tooltip>
                            <template #cell="{ record }">
                                <template v-if="column.dataIndex === 'ident'"> PT_{{ route.query.ident }}_{{ record.ident }} </template>
                                <template v-else-if="column.dataIndex === 'problemStatu'">
                                    <a-tag :color="changeColor(record.status)">
                                        {{ problemStatus[record.status] }}
                                    </a-tag>
                                </template>
                                <template v-else-if="column.dataIndex === 'problemGrade'">
                                    <a-tag :color="changeGradeColor(record.grade)">
                                        {{ gradeOptions[record.grade] }}
                                    </a-tag>
                                </template>
                                <template v-else>
                                    {{ record[column.dataIndex] }}
                                </template>
                            </template>
                        </a-table-column>
                    </template>
                </template>
                <!-- 所属用例列 -->
                <a-table-column title="所属用例" align="center" :width="110" fixed="right">
                    <template #cell="{ record }">
                        <a-tag v-if="record.hang" color="red">无关联用例</a-tag>
                        <a-button v-else color="green" type="primary" @click="seeRelatedCases(record)">
                            <icon-eye />
                        </a-button>
                    </template>
                </a-table-column>
                <!-- 操作列 -->
                <a-table-column title="操作" align="center" :width="120" fixed="right">
                    <template #cell="{ record }">
                        <a-link @click="handleOpenProblemModify(record)">
                            修改
                            <template #icon>
                                <icon-edit />
                            </template>
                        </a-link>
                    </template>
                </a-table-column>
            </template>
        </a-table>
        <!-- 问题单表单页面 -->
        <ProblemForm ref="problemRef" @updateProblem="refresh()" />
        <!-- 表格设置 -->
        <my-setting ref="settingRef" @onChangeColumnHide="changeColumn"></my-setting>
        <case-modal ref="caseModalRef" />
    </div>
</template>

<script setup lang="ts">
import { provide, ref } from "vue"
import useColumns from "./hooks/useColumns"
import useFetchData from "@/views/project/opeSets/hooks/useFetchData"
import useSettings from "@/views/project/opeSets/components/DesignTable/useSettings"
import problemApi from "@/api/project/problem"
import { useRoute } from "vue-router"
import useProblemStatu from "./hooks/useProblemStatu"
import useProblemGrade from "./hooks/useProblemGrade"
import problemSingleApi from "@/api/project/singleProblem"
import CaseModal from "@/views/project/case/components/CaseModal.vue"
import MySetting from "@/views/project/opeSets/components/TableCommonComponent/Setting.vue"
import Search from "@/views/project/opeSets/components/DesignTable/Search.vue"
import ProblemForm from "./form.vue"
import type { ISearchFormProblem } from "../DesignTable/types"

const route = useRoute()
const caseModalRef = ref<InstanceType<typeof CaseModal> | null>(null)
const problemRef = ref<InstanceType<typeof ProblemForm> | null>(null)

// 加载初始字典数据
const { loading: problemStatusLoading, problemStatus, changeColor } = useProblemStatu()
const { loading: problemGradeLoading, gradeOptions, changeGradeColor } = useProblemGrade()

// 定义表格列
const { columns } = useColumns()
provide("columns", columns)

// 请求初始数据钩子
const { tableData, isFetching, fetchData, total, pageChange, pageSizeChange, searchParams } = useFetchData(problemApi.searchAllProblem, columns)

// 查看关联用例
const seeRelatedCases = async (record: any) => {
    const problemId = record.id
    const res = await problemSingleApi.getRelativeCases({ id: problemId })
    caseModalRef.value && caseModalRef.value.open(res.data)
}

// 表格设置相关
const { options, clickSetting, changeColumn, settingRef } = useSettings()

// 搜索相关内容
const searchVisible = ref(true)
const searchSubmit = (data: ISearchFormProblem) => {
    searchParams.value = { ...data }
    fetchData(true)
}

// 点击修改
const handleOpenProblemModify = (record: any) => {
    problemRef.value?.open(record)
}

// 刷新表格显示
const refresh = () => {
    fetchData()
}
</script>

<style scoped>
.max-height-class {
    max-height: 300px;
    overflow-y: auto;
    white-space: normal;
    word-break: break-all;
}
</style>
