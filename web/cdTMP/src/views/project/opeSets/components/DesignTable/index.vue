<template>
    <ope-sets-data-table
        ref="tableRef"
        class="design-table-container"
        table-id="basic-table-design"
        :api="designApi.getDesignDemandList"
        :columns="columns"
        :delete-api="designApi.delete"
        :replace-api="designApi.replace"
        replace-key="design"
        parent-title="对应被测件"
        :parent-width="150"
        @edit="(record) => formRef?.open(record)"
        @selection-change="(rows) => (selecteds = rows)"
    >
        <template #cell-demandType="{ record }">
            {{ showType(record) }}
        </template>
        <template #parent-cell="{ record }">
            <Trigger :dutInfo="record.dut" @refresh="tableRef?.refresh()" />
        </template>
    </ope-sets-data-table>
    <!-- 设计需求-表单页面 -->
    <Form ref="formRef" @refresh="tableRef?.refresh()"></Form>
</template>

<script setup lang="ts">
import { provide, ref } from "vue"
import designApi from "@/api/project/designDemand"
import useShowType from "@/views/project/opeSets/components/DesignTable/useShowType"
import OpeSetsDataTable from "@/views/project/opeSets/components/TableCommonComponent/OpeSetsDataTable.vue"
import Form from "./form.vue"
import Trigger from "./Trigger.vue"

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
        showType: (text: string) => text,
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

const tableRef = ref<InstanceType<typeof OpeSetsDataTable> | null>(null)
const formRef = ref<InstanceType<typeof Form> | null>(null)

// 2.获取 demandType 的名称
const showType = useShowType("demandType")

// 行选择：由公共表格同步
const selecteds = ref<any[]>([])
</script>

<style scoped lang="less">
.search-container {
    margin-bottom: 10px;
}
</style>
