<template>
    <div class="ope-sets-table-container">
        <search v-show="searchVisible" @submit="searchSubmit" />
        <div class="lg:flex justify-between mb-2">
            <a-space>
                <a-popconfirm
                    v-if="deleteApi"
                    content="确定要删除数据吗? 这会删除全部下级数据!"
                    position="bottom"
                    @ok="deletesMultipleAction"
                >
                    <a-button type="primary" status="danger" :loading="isDeleting">
                        批量删除
                        <template #icon><icon-delete /></template>
                    </a-button>
                </a-popconfirm>
                <a-button v-if="replaceApi" type="primary" @click="handleOpenReplaceModal">
                    批量替换
                    <template #icon><icon-swap /></template>
                </a-button>
                <slot name="toolbar-extra"></slot>
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
            :id="tableId"
            v-bind="options"
            hoverable
            column-resizable
            :scroll="{ x: '100%' }"
            :row-selection="showSelection ? { type: 'checkbox', showCheckedAll: true, onlyCurrent: true } : undefined"
            row-key="id"
            v-model:selectedKeys="selecteds"
            :loading="isFetching || loading"
            :data="tableData"
            :pagination="{
                showTotal: true,
                showPageSize: true,
                total: total,
                pageSizeOptions: [10, 20, 50, 100],
                hideOnSinglePage: false
            }"
            @page-change="pageChange"
            @page-size-change="pageSizeChange"
        >
            <template #columns>
                <!-- 数据列：特殊单元格通过动态插槽 cell-<dataIndex> 由各业务表提供 -->
                <template v-for="column in columns" :key="column.dataIndex">
                    <template v-if="!column.hide">
                        <a-table-column
                            v-bind="column"
                            :tooltip="!['testStep', 'testContent', 'operation'].includes(column.dataIndex)"
                        >
                            <template #cell="{ record }">
                                <slot :name="`cell-${column.dataIndex}`" :record="record">
                                    <div v-if="column.isHyperText" v-html="record[column.dataIndex]"></div>
                                    <template v-else>{{ record[column.dataIndex] }}</template>
                                </slot>
                            </template>
                        </a-table-column>
                    </template>
                </template>
                <!-- 上级节点列 -->
                <a-table-column v-if="parentTitle" :title="parentTitle" align="center" :width="parentWidth" fixed="right">
                    <template #cell="{ record }">
                        <slot name="parent-cell" :record="record"></slot>
                    </template>
                </a-table-column>
                <!-- 操作列 -->
                <a-table-column title="操作" align="center" :width="operationWidth" fixed="right">
                    <template #cell="{ record }">
                        <a-scrollbar type="track" style="overflow: auto">
                            <a-space size="mini">
                                <slot name="operation" :record="record">
                                    <a-link @click="emit('edit', record)">
                                        修改
                                        <template #icon>
                                            <icon-edit />
                                        </template>
                                    </a-link>
                                </slot>
                            </a-space>
                        </a-scrollbar>
                    </template>
                </a-table-column>
            </template>
        </a-table>
        <!-- 表格设置 -->
        <my-setting ref="settingRef" @onChangeColumnHide="changeColumn"></my-setting>
        <!-- 批量替换组件 -->
        <replace-modal
            v-if="replaceApi"
            ref="replaceModal"
            :selectRows="selecteds"
            :api="replaceApi"
            :columns="replaceColumns || columns"
            :popup-key="replaceKey"
            @replaceSuccess="replaceSuccessHandle"
        />
    </div>
</template>

<script setup lang="ts">
import { ref, toRef, watch } from "vue"
import { Message } from "@arco-design/web-vue"
import Search from "@/views/project/opeSets/components/DesignTable/Search.vue"
import useSettings from "@/views/project/opeSets/components/DesignTable/useSettings"
import MySetting from "@/views/project/opeSets/components/TableCommonComponent/Setting.vue"
import ReplaceModal from "@/views/project/opeSets/components/DesignTable/ReplaceModal.vue"
import useFetchData from "@/views/project/opeSets/hooks/useFetchData"
import useDelete from "@/views/project/opeSets/components/DesignTable/useDelete"

/**
 * opeSets 四张表（设计需求/测试项/测试用例/问题单）的公共表格骨架：
 * 工具栏、搜索、分页、行选择、批量删除、批量替换、表格设置统一在此维护，
 * 各业务表只提供列定义与差异单元格插槽。
 */
const props = defineProps({
    api: { type: Function, required: true },
    columns: { type: Array, required: true },
    tableId: { type: String, required: true },
    deleteApi: { type: Function, default: null },
    replaceApi: { type: Function, default: null },
    replaceColumns: { type: Array, default: null },
    replaceKey: { type: String, default: "" },
    parentTitle: { type: String, default: "" },
    parentWidth: { type: Number, default: 120 },
    operationWidth: { type: Number, default: 100 },
    showSelection: { type: Boolean, default: true },
    loading: { type: Boolean, default: false }
})

const emit = defineEmits(["edit", "selection-change"])

// 查询与分页（useFetchData 需要 Ref 形式的列定义）
const columnsRef = toRef(props, "columns")
const { tableData, isFetching, fetchData, total, pageChange, pageSizeChange, searchParams } = useFetchData(
    props.api,
    columnsRef
)

// 表格设置
const { options, clickSetting, changeColumn, settingRef } = useSettings()

// 行选择：表格数据变化（翻页/搜索/刷新）时清空，避免批量操作作用到不可见行
const selecteds = ref<any[]>([])
watch(tableData, () => {
    selecteds.value = []
})
watch(selecteds, (value) => emit("selection-change", value))

// 批量删除（未配置删除接口时不展示按钮，这里传空实现占位）
const { deletesMultipleAction, isDeleting } = useDelete(
    props.deleteApi || (async () => ({ success: false })),
    fetchData,
    selecteds
)

// 批量替换
const replaceModal = ref<InstanceType<typeof ReplaceModal> | null>(null)
const handleOpenReplaceModal = () => {
    replaceModal.value?.open(undefined)
}
const replaceSuccessHandle = async (count: number) => {
    Message.success(`批量更新成功，尝试更新行数：${count}`)
    await fetchData()
}

// 搜索
const searchVisible = ref(true)
const searchSubmit = (data: any) => {
    searchParams.value = { ...data }
    fetchData(true)
}

const refresh = () => fetchData()

defineExpose({ fetchData, refresh, selecteds, tableData, searchParams })
</script>

<style scoped lang="less">
// search 根组件间距
.search-container {
    margin-bottom: 10px;
}
/* 下面让 modal 的蒙层不交互，让用户可以复制 table 的文字 */
:deep(.arco-modal-container) {
    pointer-events: none;
}
:deep(.arco-modal.arco-modal-draggable) {
    pointer-events: auto;
}
</style>

<style lang="less">
.hyperTextCell-table-chen {
    // 长文本单元格内部滚动：统一顶端对齐，滚动条收细避免在表格中间形成一条粗线
    .arco-table-td {
        vertical-align: top;
    }

    .arco-table-td-content {
        max-height: 15em;
        overflow-y: auto;
        line-height: 1.5em;
        word-break: break-word;
        scrollbar-width: thin;
    }

    .arco-table-td-content::-webkit-scrollbar {
        width: 6px;
    }

    .arco-table-td-content::-webkit-scrollbar-thumb {
        background-color: var(--app-line-strong, #cfd5dc);
    }

    .arco-table-td-content::-webkit-scrollbar-track {
        background-color: transparent;
    }
}
.arco-tabs-content-list {
    height: 120%;
}
.arco-table-pagination {
    margin-bottom: 40px;
}
</style>
