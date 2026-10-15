<template>
    <div class="ma-content-block p-3 mt-3 bg-white">
        <a-spin class="chartContainer" :loading="isPending" tip="图标数据加载中...">
            <div class="flex justify-center items-center" v-if="!isPending">
                <template v-if="isError">
                    <img class="w-50 h-75" src="@/assets/img/ErrorLoad.svg" alt="" />
                </template>
                <template v-else>
                    <VueUiXy :dataset="chartData" :config="chartConfig" :style="{ padding: '10px' }" />
                </template>
            </div>
        </a-spin>
    </div>
</template>

<script setup>
import commonApi from "@/api/common"
import { VueUiXy } from "vue-data-ui"
import useVueDataUI from "@/views/dashboard/workplace/components/cpns/hooks/vueDataUI"
import { useQuery } from "@tanstack/vue-query"

// vue-query请求图表接口
const { isPending, data, isError } = useQuery({
    queryKey: ["chart"],
    queryFn: commonApi.getChartData,
    refetchOnWindowFocus: false
})

// vue-data-ui图表
const { chartData, chartConfig } = useVueDataUI(data)

// 暗黑模式配置
</script>

<style lang="less" scoped>
.chartContainer {
    width: 100%;
    // height: 300px;
}
</style>
