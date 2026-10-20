<template>
    <!-- 该组件是表格查看上级节点的列（a-table-column） -->
    <div class="trigger-container">
        <a-trigger position="left" auto-fit-position update-at-scroll>
            <a-link @click="(formRef as any).open(dutInfo)">
                {{ dutInfo.title }}
                <template #icon>
                    <icon-edit />
                </template>
            </a-link>
            <template #content>
                <div class="trigger-content">
                    <ma-info :columns="columns" :data="dutInfoJudge"></ma-info>
                </div>
            </template>
        </a-trigger>
        <!-- dutForm组件 -->
        <DutForm ref="formRef" v-bind="$attrs" />
    </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue"
import MaInfo from "@/components/ma-info/index.vue"
import DutForm from "./DutForm.vue"

// refs
const formRef = ref(null)
// 0.props-表示不通用代码
const { dutInfo } = defineProps<{ dutInfo: any }>()
// 计算属性保持纯粹：返回新对象，不改写 props；行数为 0/空时显示“不适用”而不是 Infinity/NaN
const dutInfoJudge = computed(() => {
    const info = { ...dutInfo }
    if (info.type === "SO") {
        const totalLines = Number(info.total_lines) || 0
        const commentLines = Number(info.comment_lines) || 0
        info.comment_percent = totalLines > 0 ? `${((commentLines / totalLines) * 100).toFixed(2)}%` : "不适用"
    } else {
        // 如果是非源代码被测件行数均填写：“不适用”
        info.comment_lines = "不适用"
        info.comment_percent = "不适用"
        info.effective_lines = "不适用"
        info.total_lines = "不适用"
    }
    return info
})

// 1.导入crud的columns属性，然后去掉不需要展示的内容
import useColumn from "@/views/project/round/hooks/useColumn"
const originColumns = useColumn(undefined)
const columns = computed(() => {
    // 去掉上传源代码字段
    const quUploadColumns = originColumns.value.filter((it) => it.dataIndex !== "upload")
    // 判断是否为源代码被测件
    return quUploadColumns
})
</script>

<style lang="less" scoped>
.trigger-content {
    padding: 10px;
    width: 30vw;
    background-color: var(--color-bg-popup);
    box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.15);
}
</style>
