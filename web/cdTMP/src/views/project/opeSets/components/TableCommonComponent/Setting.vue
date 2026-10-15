<template>
    <a-drawer :visible="visible" unmountOnClose :footer="false" width="55%" @cancel="onCancel">
        <template #title>设置</template>

        <a-space class="mt-3">
            <span>表格大小：</span>
            <a-radio-group type="button" v-model="options.size">
                <a-radio value="mini">迷你</a-radio>
                <a-radio value="small">小</a-radio>
                <a-radio value="medium">中</a-radio>
                <a-radio value="large">大</a-radio>
            </a-radio-group>
            <span class="ml-3">表格边框：</span>
            <a-radio-group type="button" v-model="bordered" @change="changeBordered">
                <a-radio value="hide">不显示外边框</a-radio>
                <a-radio value="show">全部显示</a-radio>
                <a-radio value="row">不显示行</a-radio>
                <a-radio value="column">不显示列</a-radio>
            </a-radio-group>
            <a-checkbox v-model="options.stripe" class="ml-3">斑马纹</a-checkbox>
        </a-space>

        <a-table
            :data="allowShowColumns"
            :pagination="false"
            :bordered="{ wrapper: true, cell: false }"
            :draggable="{ type: 'handle', width: 40 }"
            @change="onTableChange"
            stripe
            class="mt-3"
        >
            <template #columns>
                <a-table-column title="列名称" data-index="title" align="center">
                    <template #cell="{ record }">{{ record.title }}</template>
                </a-table-column>
                <a-table-column title="宽度" data-index="width" align="center">
                    <template #cell="{ record }">
                        <a-input-number
                            v-if="!['__index', '__operation'].includes(record.dataIndex)"
                            style="width: 150px"
                            placeholder="列宽度"
                            v-model="record.width"
                            mode="button"
                            @change="changeColumn($event, 'width', record.dataIndex)"
                        />
                        <span v-else> / </span>
                    </template>
                </a-table-column>
                <a-table-column title="搜索隐藏" data-index="hide" align="center">
                    <template #cell="{ record }"
                        ><a-checkbox v-model="record.search" @change="changeColumn($event, 'search', record.dataIndex)"
                    /></template>
                </a-table-column>
                <a-table-column title="表格隐藏" data-index="hide" align="center">
                    <template #cell="{ record }"
                        ><a-checkbox v-model="record.hide" @change="changeColumn($event, 'hide', record.dataIndex)"
                    /></template>
                </a-table-column>
                <a-table-column title="固定" data-index="fixed" align="center">
                    <template #cell="{ record }">
                        <a-space v-if="!['__index', '__operation'].includes(record.dataIndex)">
                            <a-radio
                                v-model="record.fixed"
                                value=""
                                @change="changeColumn($event, 'fixed', record.dataIndex)"
                                >无</a-radio
                            >
                            <a-radio
                                v-model="record.fixed"
                                value="left"
                                @change="changeColumn($event, 'fixed', record.dataIndex)"
                                >左</a-radio
                            >
                            <a-radio
                                v-model="record.fixed"
                                value="right"
                                @change="changeColumn($event, 'fixed', record.dataIndex)"
                                >右</a-radio
                            >
                        </a-space>
                        <span v-else> / </span>
                    </template>
                </a-table-column>
            </template>
        </a-table>
    </a-drawer>
</template>

<script setup lang="ts">
import { inject, ref, toRef, watch } from "vue"

const visible = ref(false)
const bordered = ref("show")
const options = inject("options") as any
const columns = inject("columns") as any
const allowShowColumns = ref([])

// 设置列
const setShowColumns = () => {
    allowShowColumns.value = columns.value.filter((item) => {
        return !(item?.settingHide ?? false)
    })
}

// 边框设置
const changeBordered = (v: string) => {
    if (v === "hide") {
        options.bordered = { wrapper: false, cell: false }
    }
    if (v === "show") {
        options.bordered = { wrapper: true, cell: true }
    }
    if (v === "row") {
        options.bordered = { wrapper: false, cell: true }
    }
    if (v === "column") {
        options.bordered = { wrapper: true, cell: false }
    }
}

const onTableChange = (_data) => {
    columns.value = _data
    setShowColumns()
}

const open = () => {
    setShowColumns()
    visible.value = true
}

const onCancel = () => {
    visible.value = false
}

const emit = defineEmits(["onChangeSearchHide", "onChangeColumnHide"])

const changeColumn = (ev: string, type: any, name: any) => {
    const column = columns.value.find((item: { dataIndex: any }) => item.dataIndex === name)
    switch (type) {
        case "hide":
            emit("onChangeColumnHide")
            break
        case "search":
            emit("onChangeSearchHide")
            break
    }
}

defineExpose({ open })
</script>

<style lang="less" scoped></style>
