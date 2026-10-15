<template>
    <div class="design-table-container">
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
            id="basic-table-design"
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
                        <a-table-column v-bind="column" v-if="!column.showType" tooltip>
                            <!-- 如果column有isHyperText属性，则直接渲染html -->
                            <template #cell="{ record }" v-if="column.isHyperText">
                                <div v-html="record[column.dataIndex]"></div>
                            </template>
                        </a-table-column>
                        <a-table-column v-bind="column" v-else ellipsis tooltip>
                            <template #cell="{ record }">
                                {{ showType(record) }}
                            </template>
                        </a-table-column>
                    </template>
                </template>
                <!-- 上级节点列 -->
                <a-table-column title="对应被测件" align="center" :width="150" fixed="right">
                    <template #cell="{ record, column, rowIndex }">
                        <Trigger :dutInfo="record.dut" @refresh="fetchData()" />
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
        <!-- 设计需求-表单页面 -->
        <Form ref="formRef" @refresh="fetchData()"></Form>
        <!-- 表格设置 -->
        <my-setting ref="settingRef" @onChangeColumnHide="changeColumn"></my-setting>
        <!-- 批量替换组件 -->
        <replace-modal
            ref="replaceModal"
            :selectRows="selecteds"
            :api="designApi.replace"
            :columns="columns"
            key="modal-design"
            popup-key="design"
            @replaceSuccess="replaceSuccessHandle"
        />
    </div>
</template>

<script setup lang="ts">
import { provide, ref } from "vue"
import { Message } from "@arco-design/web-vue"
import designApi from "@/api/project/designDemand"
import useShowType from "@/views/project/opeSets/components/DesignTable/useShowType"
import useFetchData from "@/views/project/opeSets/hooks/useFetchData"
import Form from "./form.vue" // 表单组件
import Trigger from "./Trigger.vue" // 查看上级节点的触发器组件\
// 表格用户设置相关
import useSettings from "@/views/project/opeSets/components/DesignTable/useSettings"
import MySetting from "@/views/project/opeSets/components/TableCommonComponent/Setting.vue"
import useDelete from "@/views/project/opeSets/components/DesignTable/useDelete"
// 批量替换弹窗组件
import ReplaceModal from "@/views/project/opeSets/components/DesignTable/ReplaceModal.vue"
import Search from "@/views/project/opeSets/components/DesignTable/Search.vue"
import type { ISearchForm } from "./types"

// 1.数据columns相关
const columns = ref([
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
        title: "标识",
        dataIndex: "ident",
        align: "center",
        width: 100,
        hide: false,
        ellipsis: true,
        search: true,
        formType: "input",
        fixed: ""
    },
    {
        title: "章节号",
        dataIndex: "chapter",
        align: "center",
        width: 80,
        hide: false,
        ellipsis: true,
        search: true,
        formType: "input",
        fixed: ""
    },
    {
        title: "类型",
        dataIndex: "demandType",
        align: "center",
        width: 150,
        hide: false,
        ellipsis: true,
        search: true,
        formType: "select",
        showType: (text: string) => {
            return text
        },
        dict: true,
        fixed: ""
    },
    {
        title: "需求描述",
        dataIndex: "description",
        align: "left",
        hide: false,
        ellipsis: false,
        formType: "input",
        // 设置内容单元格样式-注意作用与<td>
        bodyCellClass: "hyperTextCell-table-chen",
        isHyperText: true,
        fixed: ""
    }
])
provide("columns", columns)

// 2.获取demandType的名称
const showType = useShowType("demandType")

// 3.query查询和分页相关
const { tableData, isFetching, fetchData, total, pageChange, pageSizeChange, searchParams } = useFetchData(designApi.getDesignDemandList, columns)

// 4.表单相关
const formRef = ref<InstanceType<typeof Form> | null>(null)

// 5.表格设置相关
const { options, clickSetting, changeColumn, settingRef } = useSettings()

// 6.行选择器相关-注意在fetchData时候没有清空（一定注意!!!）
const selecteds = ref([])

// 7.1.批量删除相关
const { deletesMultipleAction } = useDelete(designApi.delete, fetchData, selecteds)

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
const searchSubmit = (data: ISearchForm) => {
    searchParams.value = { ...data }
    fetchData(true)
}
</script>

<style scoped lang="less">
/* 下面让modal的蒙层不交互，让用户可以复制table的文字 */
div:deep(.arco-modal-container) {
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
