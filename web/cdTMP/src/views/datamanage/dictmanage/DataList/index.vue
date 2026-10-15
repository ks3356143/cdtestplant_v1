<template>
    <a-modal v-model:visible="visible" width="80%" draggable :footer="false">
        <template #title>维护数据字典 →【{{ currentRow.name }}】</template>
        <!-- crud组件 -->
        <div class="lg:w-full w-full lg:mt-0">
            <ma-crud :options="crudOptions" :columns="columns" ref="crudRef">
                <!-- 排序列 -->
                <template #sort="{ record }">
                    <a-input-number
                        :default-value="record.sort"
                        mode="button"
                        @change="changeSort($event, record.id)"
                        :min="0"
                        :max="1000"
                    />
                </template>
                <!-- 状态列 -->
                <template #status="{ record }">
                    <a-switch
                        :checked-value="1"
                        unchecked-value="2"
                        @change="changeStatus($event, record.id)"
                        :default-checked="record.status == 1"
                    />
                </template>
            </ma-crud>
        </div>
    </a-modal>
</template>

<script setup>
import { ref } from "vue"
import useCrudRef from "./useCrudRef"
import useOpenChangeModal from "./useOpenChangeModal"

const currentRow = ref({ id: undefined, name: undefined }) // 当前选择的行
const { crudRef, crudOptions, columns } = useCrudRef(currentRow)

const { visible, changeSort, changeStatus, open } = useOpenChangeModal(crudRef, currentRow)
// 暴露自己的open方法
defineExpose({ open })
</script>

<style lang="less" scoped></style>
