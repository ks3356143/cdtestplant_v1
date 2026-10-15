<template>
    <div class="ma-content-block lg:flex justify-between p-4">
        <div class="lg:w-full w-full lg:ml-4 mt-5 lg:mt-0">
            <!-- crud组件 -->
            <ma-crud :options="crudOptions" :columns="crudColumns" ref="crudRef"></ma-crud>
        </div>
    </div>
</template>

<script lang="jsx" setup>
import { ref } from "vue"
import abbreviationApi from "@/api/system/abbreviation"
import { columnsOptions } from "./columnsOptions.ts"

const crudRef = ref()
const crudOptions = ref({
    autoRequest: true,
    api: abbreviationApi.getlist,
    add: { show: true, api: abbreviationApi.save },
    edit: { show: true, api: abbreviationApi.update },
    delete: { show: true, api: abbreviationApi.delete },
    operationWidth: 160,
    operationColumn: true,
    operationColumnAlign: "center",
    showIndex: false,
    searchColNumber: 3,
    tablePagination: false,
    rowSelection: { showCheckedAll: true },
    afterDelete(response) {
        crudRef.value.tableRef.selectAll(false)
    }
})
const crudColumns = ref(columnsOptions)

defineOptions({
    name: "abbreviation"
})
</script>

<style lang="less" scoped></style>
