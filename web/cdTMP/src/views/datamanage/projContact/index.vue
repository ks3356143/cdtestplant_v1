<template>
    <div class="ma-content-block lg:flex justify-between p-4">
        <div class="lg:w-full w-full lg:ml-4 mt-5 lg:mt-0">
            <!-- crud组件 -->
            <ma-crud :options="crudOptions" :columns="crudColumns" ref="crudRef"></ma-crud>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue"
import contactApi from "@/api/system/contact"
import { columnsOptions } from "./crudColumns"

const crudRef = ref()
const crudOptions = ref({
    autoRequest: true,
    api: contactApi.getlist,
    add: { show: true, api: contactApi.save },
    edit: { show: true, api: contactApi.update },
    delete: { show: true, api: contactApi.delete },
    operationWidth: 160,
    operationColumn: true,
    operationColumnAlign: "center",
    showIndex: false,
    searchColNumber: 3,
    tablePagination: false,
    rowSelection: { showCheckedAll: true },
    afterDelete() {
        crudRef.value.tableRef.selectAll(false)
    }
})
const crudColumns = ref(columnsOptions)
</script>

<style lang="less" scoped></style>
