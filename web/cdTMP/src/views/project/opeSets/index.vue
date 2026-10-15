<template>
    <div class="ma-content-block lg:flex justify-between p-4">
        <div class="lg:w-full w-full lg:ml-4 mt-5 lg:mt-0 h-full">
            <!-- 1.标题：提示用户第几轮次 -->
            <div class="heading-1">{{ title }}测试过程数据</div>
            <!-- 2.容器：tab切换 -->
            <a-tabs default-active-key="design" type="card-gutter" size="large" destroy-on-hide justify>
                <a-tab-pane key="design" title="设计需求">
                    <ProTable type="design"></ProTable>
                </a-tab-pane>
                <a-tab-pane key="demand" title="测试项">
                    <ProTable type="demand"></ProTable>
                </a-tab-pane>
                <a-tab-pane key="case" title="测试用例">
                    <ProTable type="case"></ProTable>
                </a-tab-pane>
                <a-tab-pane key="problem" title="本轮问题单">
                    <ProTable type="problem"></ProTable>
                </a-tab-pane>
            </a-tabs>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router"
import tool from "@/utils/tool"
import ProTable from "./ProTable/index.vue"

const route = useRoute()

// 1.标题
const title: string = tool.chnRoundNameArray[+route.query.key!]
</script>

<style lang="less" scoped>
.heading-1 {
    font-size: 20px;
    font-weight: 600;
    color: #333333;
    margin-bottom: 10px;
}
</style>
