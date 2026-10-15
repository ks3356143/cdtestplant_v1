<template>
    <div class="title-container">
        <div class="ma-content-block rounded-xs flex-col justify-between w-full p-3 bg-color">
            <page-header :data="headerData"></page-header>
            <div class="title">基本信息</div>
            <div class="item-container">
                <a-card
                    class="item"
                    v-for="(val, key) in pInfo.title_info"
                    :style="{ width: '360px' }"
                    :title="key.toString()"
                    :key="key"
                    hoverable
                >
                    <ul class="li-container">
                        <li v-for="(v, k) in val" :key="k">
                            <div class="key">{{ k }}:</div>
                            <div class="value">{{ v }}</div>
                        </li>
                    </ul>
                </a-card>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, ComputedRef } from "vue"
import type { IPageHeaderProps } from "../../components/PageHeader/types"
import PageHeader from "@/views/testmanage/components/PageHeader/index.vue"
// 定义props
const props = defineProps({
    pInfo: {
        type: Object,
        required: true
    }
})
// 给头部组件的计算属性
const headerData: ComputedRef<IPageHeaderProps> = computed(() => {
    return {
        title: props.pInfo.ident as string,
        name: props.pInfo.name as string,
        step: props.pInfo.step
    }
})
</script>

<style lang="less" scoped>
:deep(.arco-page-header-main) {
    align-items: center;
}
.item-container {
    display: flex;
    align-items: center;
    justify-content: space-around;
    .item {
        height: 11rem;
        .li-container {
            display: flex;
            flex-direction: column;
            gap: 5px;
            li {
                display: flex;
                line-height: 1.5;
                gap: 5px;
                .value {
                    text-overflow: ellipsis;
                    overflow: hidden;
                    word-break: break-all;
                    white-space: nowrap;
                    font-weight: 700;
                }
            }
        }
    }
}
.title {
    margin: 10px;
    font-weight: 700;
    font-size: 1rem;
}
</style>
