<template>
    <div class="round-info-container">
        <div class="ma-content-block rounded-xs flex-column justify-between w-full p-3 bg-color">
            <div class="title">{{ props.data.name }}信息</div>
            <div class="info-list">
                <a-list :gridProps="{ gutter: 0, span: 6 }" class="list-container">
                    <template #header><div class="header">设计需求下面测试项/用例统计信息</div></template>
                    <a-list-item v-for="(item, index) in props.data.desings" :key="index">
                        <a-list-item-meta class="meta" :title="`${item.name}`"></a-list-item-meta>
                        <div class="item-count">
                            测试项数 : <span class="count">{{ item.demand_count }}</span>
                        </div>
                        <div class="item-count">
                            用例数 : <span class="count">{{ item.case_count }}</span>
                        </div>
                    </a-list-item>
                </a-list>
                <a-list class="list-container">
                    <template #header><div class="header">测试类型统计信息</div></template>
                    <a-table
                        :bordered="false"
                        :data="resolveData"
                        :columns="columns"
                        size="small"
                        :pagination="false"
                    ></a-table>
                </a-list>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from "vue"
import columns from "./tableColumn.js"
const props = defineProps({
    data: {
        type: Object,
        required: true
    }
})
const resolveData = computed(() => {
    let resData = []
    let res = props.data.method_demand
    Object.keys(res).forEach((key) => {
        const value = res[key]
        resData.push({
            name: key,
            demand_count: value,
            case_count: 0
        })
    })
    let res2 = props.data.method_case
    Object.keys(res2).forEach((key) => {
        const value = res2[key]
        resData.forEach((item) => {
            if (item.name === key) {
                item.case_count = value
            }
        })
    })
    return resData
})
</script>

<style lang="less" scoped>
.round-info-container {
    width: 100%;
    height: 100%;
}
.title {
    margin: 10px;
    font-weight: 700;
    font-size: 1rem;
}
.count {
    font-weight: 700;
}
.meta {
    font-size: 15px;
    width: 80%;
    border-bottom: 1px dashed var(--color-text-4);
    margin-bottom: 2px;
    text-overflow: ellipsis;
    overflow: hidden;
    word-break: break-all;
    white-space: nowrap;
}
.list-container {
    transition: all 0.3s;
    &:hover {
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
}
.info-list {
    display: flex;
    flex-direction: column;
    gap: 5px;
}
.header {
    font-size: 14px;
    font-weight: 700;
    color: var(--color-text-3);
}
</style>
