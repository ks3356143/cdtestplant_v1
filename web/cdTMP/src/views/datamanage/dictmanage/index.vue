<template>
    <div class="ma-content-block lg:flex justify-between p-4" ref="crudRef">
        <div class="lg:w-full w-full lg:ml-4 mt-5 lg:mt-0">
            <!-- CRUD组件 -->
            <ma-crud :options="crudOptions" :columns="crudColumns">
                <!-- 字典标识列 -->
                <template #code="{ record }">
                    <a-tooltip content="点击查看字典数据">
                        <a-link @click="openDictList(record)">
                            {{ record.code }}
                        </a-link>
                    </a-tooltip>
                </template>
                <!-- 状态列 -->
                <template #status="{ record }">
                    <a-switch
                        :checked-value="1"
                        unchecked-value="2"
                        @change="changeStatus($event, record.id)"
                        :default-checked="record.status == 1"
                    >
                    </a-switch>
                </template>
                <template #operationBeforeExtend="{ record }">
                    <a-link @click="openDictList(record)"><icon-list /> 字典数据</a-link>
                </template>
            </ma-crud>
        </div>

        <data-list ref="datalistRef"></data-list>
    </div>
</template>

<script setup lang="jsx">
import DataList from "./DataList/index.vue"
import useDictCrud from "./useDictCrud"
import useDataListRef from "./useDataListRef"
// 1.useDictCrud
const { crudRef, changeStatus, crudOptions, crudColumns } = useDictCrud()
// 2.dataList.vue界面打开和ref定义
const { datalistRef, openDictList } = useDataListRef()
defineOptions({
    name: "dictmanage"
})
</script>

<style lang="less" scoped></style>
