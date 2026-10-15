<template>
    <!-- 描述列表组件 -->
    <a-modal width="1000px" v-model:visible="visible" :footer="false" unmount-on-close>
        <template #title>项目名称：{{ previewRecord.name }}</template>
        <ma-info
            class="my-custom-class"
            :columns="props.columns"
            :data="previewRecord"
            :column="3"
            size="mini"
        ></ma-info>
    </a-modal>
</template>

<script setup>
import { ref } from "vue"
import MaInfo from "@/components/ma-info/index.vue"
// 提供open方法给外界，并获取整行数据
const visible = ref(false)
const previewRecord = ref({})
const props = defineProps({
    columns: {
        type: Array,
        default: () => []
    }
})
const open = (record) => {
    visible.value = true
    previewRecord.value = record
}
defineExpose({ open })
// MA-INFO的columns
</script>

<style lang="less" scoped>
.my-custom-class {
    :deep(.arco-space-horizontal) {
        flex-wrap: wrap;
    }
    :deep(.arco-space-item){
        margin-bottom: 2px;
    }
}
</style>
