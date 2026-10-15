<template>
    <div class="case-table-container">
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
                <a-button type="outline" @click="handlePerpleModal">批量修改人员</a-button>
                <a-button type="outline" @click="handleExetimeModal">批量修改时间</a-button>
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
            id="basic-table-case"
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
                        <!-- 专门为dataIndex===testStep构造的数据列 -->
                        <a-table-column v-bind="column" v-if="column.dataIndex === 'testStep'">
                            <template #cell="{ record }">
                                <div v-for="(step, index) in record[column.dataIndex]" :key="index">
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
                                    <template v-if="record[column.dataIndex].length !== index + 1">
                                        <a-divider></a-divider>
                                    </template>
                                </div>
                            </template>
                        </a-table-column>
                        <!-- 正常的数据列 -->
                        <a-table-column v-bind="column" v-else tooltip>
                            <!-- 如果column有isHyperText属性，则直接渲染html -->
                            <template #cell="{ record }" v-if="column.isHyperText">
                                <div v-html="record[column.dataIndex]"></div>
                            </template>
                        </a-table-column>
                    </template>
                </template>
                <!-- 上级节点列 -->
                <a-table-column title="对应测试项" align="center" :width="120" fixed="right">
                    <template #cell="{ record, column, rowIndex }">
                        <Trigger :demandInfo="record.test" @refresh="fetchData()" />
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
        <!-- 测试用例-表单页面 -->
        <Form ref="formRef" @refresh="fetchData()"></Form>
        <!-- 表格设置 -->
        <my-setting ref="settingRef" @onChangeColumnHide="changeColumn"></my-setting>
        <!-- 批量替换组件 -->
        <replace-modal
            ref="replaceModal"
            :selectRows="selecteds"
            :api="caseApi.replace"
            :columns="columns.filter((it) => it.dataIndex !== 'ident')"
            key="modal-case"
            popup-key="case"
            @replaceSuccess="replaceSuccessHandle"
        />
        <!-- 批量替换人员组件 -->
        <replace-person :selectRows="selecteds" ref="replacePersonModalRef" />
        <!-- 批量替换时间 -->
        <replace-exetime :selectRows="selecteds" ref="replaceExetimeModalRef" />
    </div>
</template>

<script setup lang="ts">
import { ref, provide } from "vue"
import caseApi from "@/api/project/case"
import type { ISearchFormCase } from "@/views/project/opeSets/components/DesignTable/types"
import useSettings from "@/views/project/opeSets/components/DesignTable/useSettings"
import MySetting from "@/views/project/opeSets/components/TableCommonComponent/Setting.vue"
import useFetchData from "@/views/project/opeSets/hooks/useFetchData"
import Search from "@/views/project/opeSets/components/DesignTable/Search.vue"
import Form from "./form.vue"
import Trigger from "./Trigger.vue"
import useDelete from "@/views/project/opeSets/components/DesignTable/useDelete"
import { Message } from "@arco-design/web-vue"
import ReplaceModal from "@/views/project/opeSets/components/DesignTable/ReplaceModal.vue"
// case专属组件
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
        search: false, // 要搜索
        formType: "input", // 搜索输入框形式
        bodyCellClass: "hyperTextCell-table-chen",
        fixed: ""
    }
])
provide("columns", columns)

// 3.query查询和分页相关
const { tableData, isFetching, fetchData, total, pageChange, pageSizeChange, searchParams } = useFetchData(caseApi.getCaseList, columns)

// 4.表单相关
const formRef = ref<InstanceType<typeof Form> | null>(null)

// 5.表格设置相关
const { options, clickSetting, changeColumn, settingRef } = useSettings()

// 6.行选择器相关-注意在fetchData时候没有清空（一定注意!!!）
const selecteds = ref([])

// 7.1.批量删除相关
const { deletesMultipleAction } = useDelete(caseApi.delete, fetchData, selecteds)

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
const searchSubmit = (data: ISearchFormCase) => {
    searchParams.value = { ...data }
    fetchData(true)
}

// 9.批量修改人员
const replacePersonModalRef = ref<InstanceType<typeof ReplacePerson>>()
const handlePerpleModal = () => {
    replacePersonModalRef.value!.open(undefined)
}

// 10.批量修改时间
const replaceExetimeModalRef = ref<InstanceType<typeof ReplaceExetime>>()
const handleExetimeModal = () => {
    replaceExetimeModalRef.value!.open(undefined)
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
</style>
