<template>
    <div class="pro-table-container">
        <component :is="mapColumn[type]"></component>
    </div>
</template>

<script setup lang="ts">
import DesignTable from "../components/DesignTable/index.vue"
import DemandTable from "../components/DemandTable/index.vue"
import CaseTable from "../components/CaseTable/index.vue"
import ProblemTable from "../components/ProblemTable/index.vue"

/* 导入columns看能不能行 */
// useColumns使用对应关系
const mapColumn = {
    design: DesignTable,
    demand: DemandTable,
    case: CaseTable,
    problem: ProblemTable
}
// props
const { type } = defineProps<{
    type: string
}>()

// query - 根据不同类型进行请求，传递轮次
</script>

<style lang="less" scoped>
.pro-table-container {
    padding: 5px;
}
</style>
