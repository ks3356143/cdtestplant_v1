<template>
    <!-- 该组件是表格查看上级节点的列（a-table-column） -->
    <div class="trigger-container">
        <a-trigger position="left" auto-fit-position update-at-scroll>
            <a-link @click="(formRef as any).open(designInfo)">
                {{ designInfo.title }}
                <template #icon>
                    <icon-edit />
                </template>
            </a-link>
            <template #content>
                <div class="trigger-content">
                    <ma-info :columns="columns" :data="designInfoJudge"></ma-info>
                </div>
            </template>
        </a-trigger>
        <!-- dutForm组件 -->
        <DesignForm ref="formRef" v-bind="$attrs" />
    </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue"
import MaInfo from "@/components/ma-info/index.vue"
import DesignForm from "./DesignForm.vue"
import useColumn from "@/views/project/dut/hooks/useColumns"

// refs
const formRef = ref(null)

// 0.props-表示不通用代码
const { designInfo } = defineProps<{ designInfo: any }>()

// 计算属性单独处理
const designInfoJudge = computed(() => {
    return designInfo
})

// 1.导入crud的columns属性，然后去掉不需要展示的内容，给ma-info传递信息
const originColumns = useColumn(undefined)
const columns = computed(() => {
    return originColumns.value
})
</script>

<style lang="less" scoped>
.trigger-content {
    padding: 10px;
    width: 50vw;
    background-color: var(--color-bg-popup);
    box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.15);
}
</style>
