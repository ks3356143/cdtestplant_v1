<template>
    <div class="demand-table-container">
        <search v-show="searchVisible" @submit="searchSubmit" />
        <div class="lg:flex justify-between mb-2">
            <a-space>
                <a-popconfirm content="确定要删除数据吗? 这会删除全部下级数据!" position="bottom" @ok="deletesMultipleAction">
                    <a-button type="primary" status="danger">
                        批量删除
                        <template #icon><icon-delete /></template>
                    </a-button>
                </a-popconfirm>
                <a-button type="primary" @click="handleOpenReplaceModal">
                    批量替换
                    <template #icon><icon-swap /></template>
                </a-button>
                <a-divider direction="vertical"></a-divider>
                <a-button type="outline" @click="handleOpenReplacePriority">批量修改优先级</a-button>
            </a-space>
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
            id="basic-table-demand"
            v-bind="options"
            hoverable
            column-resizable
            ref="tableRef"
            :scroll="{ x: '100%' }"
            :row-selection="{ type: 'checkbox', showCheckedAll: true, onlyCurrent: true }"
            row-key="id"
            v-model:selectedKeys="selecteds"
            :loading="isFetching"
            :data="tableData"
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
                <!-- 数据列 -->
                <template v-for="column in columns" :key="column.dataIndex">
                    <template v-if="!column.hide">
                        <!-- 正常的数据列 -->
                        <a-table-column v-bind="column" v-if="!column.showType && column.dataIndex !== 'testContent'" tooltip>
                            <!-- 如果column有isHyperText属性，则直接渲染html -->
                            <template #cell="{ record }" v-if="column.isHyperText">
                                <div v-html="record[column.dataIndex]"></div>
                            </template>
                        </a-table-column>
                        <!-- 对testContent单独渲染，区别很大!!! -->
                        <a-table-column v-bind="column" v-else-if="column.dataIndex === 'testContent'">
                            <template #cell="{ record }">
                                <div v-if="record[column.dataIndex].length > 0">
                                    <!-- 如果有测试子项即subStep -->
                                    <template v-for="(sub, idx) in record[column.dataIndex]" :key="idx">
                                        <!-- 这是每个测试子项 -->
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
                        </a-table-column>
                        <!-- 表示有showType字段 -->
                        <a-table-column v-bind="column" v-else-if="column.dataIndex === 'priority'" ellipsis tooltip>
                            <template #cell="{ record }">
                                {{ showType(record) }}
                            </template>
                        </a-table-column>
                        <a-table-column v-bind="column" v-else-if="column.dataIndex === 'testType'" ellipsis tooltip>
                            <template #cell="{ record }">
                                {{ showTestType(record) }}
                            </template>
                        </a-table-column>
                    </template>
                </template>
                <!-- 上级节点列 -->
                <a-table-column title="对应设计需求" align="center" :width="120" fixed="right">
                    <template #cell="{ record, column, rowIndex }">
                        <Trigger :designInfo="record.design" @refresh="fetchData()" />
                    </template>
                </a-table-column>
                <!-- 操作列 -->
                <a-table-column title="操作" align="center" :width="100" fixed="right">
                    <template #cell="{ record }">
                        <a-scrollbar type="track" style="overflow: auto">
                            <a-space size="mini">
                                <a-link @click="(formRef as any).open(record)">
                                    修改
                                    <template #icon>
                                        <icon-edit />
                                    </template>
                                </a-link>
                            </a-space>
                        </a-scrollbar>
                    </template>
                </a-table-column>
            </template>
        </a-table>
        <!-- 测试项-表单页面 -->
        <Form ref="formRef" @refresh="fetchData()"></Form>
        <!-- 表格设置 -->
        <my-setting ref="settingRef" @onChangeColumnHide="changeColumn"></my-setting>
        <!-- 批量替换组件 -->
        <replace-modal
            ref="replaceModal"
            :selectRows="selecteds"
            :api="demandApi.replace"
            :columns="columns.filter((it) => it.dataIndex !== 'priority' && it.dataIndex !== 'testType')"
            key="modal-demand"
            popup-key="demand"
            @replaceSuccess="replaceSuccessHandle"
        />
        <!-- 批量修改优先级 -->
        <ReplacePriority ref="replacePriorityRef" @modifySuccess="fetchData()" :selected-rows="selecteds" />
    </div>
</template>

<script setup lang="ts">
import { provide, ref } from "vue"
import type { ISearchFormDemand } from "@/views/project/opeSets/components/DesignTable/types"
import useSettings from "@/views/project/opeSets/components/DesignTable/useSettings"
import MySetting from "@/views/project/opeSets/components/TableCommonComponent/Setting.vue"
import useFetchData from "@/views/project/opeSets/hooks/useFetchData"
import demandApi from "@/api/project/testDemand"
import useShowType from "@/views/project/opeSets/components/DesignTable/useShowType"
import Form from "./form.vue"
import Trigger from "./Trigger.vue"
import Search from "@/views/project/opeSets/components/DesignTable/Search.vue"
import useDelete from "@/views/project/opeSets/components/DesignTable/useDelete"
import ReplaceModal from "@/views/project/opeSets/components/DesignTable/ReplaceModal.vue"
import ReplacePriority from "@/views/project/opeSets/components/DemandTable/ReplacePriority.vue"
import { Message } from "@arco-design/web-vue"

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
        // 只是指明a-table-column渲染v-if
        showType: (text: string) => {
            return text
        },
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
        showType: (text: string) => {
            return text
        },
        fixed: ""
    },
    {
        title: "测项描述",
        dataIndex: "testDesciption",
        align: "left",
        width: 200,
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
        title: "测试子项",
        dataIndex: "testContent",
        align: "left",
        width: 400,
        hide: false,
        ellipsis: false,
        search: false, // 要搜索
        formType: "input", // 搜索输入框形式
        bodyCellClass: "hyperTextCell-table-chen",
        fixed: ""
    }
])
provide("columns", columns)

// 2.获取demandType的名称
const showType = useShowType("priority")
const showTestType = useShowType("testType")

// 3.query查询和分页相关
const { tableData, isFetching, fetchData, total, pageChange, pageSizeChange, searchParams } = useFetchData(demandApi.getTestDemandList, columns)

// 4.表单相关
const formRef = ref<InstanceType<typeof Form> | null>(null)

// 5.表格设置相关
const { options, clickSetting, changeColumn, settingRef } = useSettings()

// 6.行选择器相关-注意在fetchData时候没有清空（一定注意!!!）
const selecteds = ref([])

// 7.1.批量删除相关
const { deletesMultipleAction } = useDelete(demandApi.delete, fetchData, selecteds)

// 7.2.批量替换相关
const replaceModal = ref<InstanceType<typeof ReplaceModal> | null>(null)
const handleOpenReplaceModal = () => {
    replaceModal.value?.open(undefined)
}
const replaceSuccessHandle = async (count: number) => {
    Message.success(`批量更新成功，尝试更新行数：${count}`)
    // 批量更新后刷新表格（疑问？是否要清除行选择？）
    await fetchData()
}

// 8.搜索组件相关-注意这里submit其实就是给维护的搜索参数传参
const searchVisible = ref(true)
const searchSubmit = (data: ISearchFormDemand) => {
    searchParams.value = { ...data }
    fetchData(true)
}

// 9.批量修改优先级-priority
const replacePriorityRef = ref<InstanceType<typeof ReplacePriority> | null>(null)
const handleOpenReplacePriority = () => {
    replacePriorityRef.value?.open(undefined)
}
</script>

<style scoped lang="less">
/* 下面让modal的蒙层不交互，让用户可以复制table的文字 */
:deep(.arco-modal-container) {
    pointer-events: none;
}
:deep(.arco-modal.arco-modal-draggable) {
    pointer-events: auto;
}

// search根组件
.search-container {
    margin-bottom: 10px;
}
</style>

<style lang="less">
.hyperTextCell-table-chen {
    .arco-table-td-content {
        max-height: 15em;
        overflow-y: auto;
        line-height: 1.5em;
        word-break: break-word;
    }
}
.arco-tabs-content-list {
    height: 120%;
}
.arco-table-pagination {
    margin-bottom: 40px;
}
// 对测试项子项步骤进行显示
.subTitle {
    overflow: hidden;
    font-size: 16px;
}
.text-bold {
    font-weight: bold;
}
</style>
