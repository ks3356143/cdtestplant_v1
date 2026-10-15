<template>
    <div class="proj-board-container" v-loading="isDataLoading">
        <a-layout-content class="flex flex-col gap-2" v-if="!isDataLoading">
            <!-- 返回前面一页的按钮，以及项目整体情况 -->
            <Title :pInfo="loadingData"></Title>
            <!-- 时间线显示项目情况 -->
            <time-line :pInfo="loadingData" :projectId="route.params.projectId"></time-line>
            <!-- 以轮次为合集展示需求下面的测试项数、用例数，测试类型下面测试项和用例数量 -->
            <round-info v-for="item in loadingData.statistics" :data="item"></round-info>
        </a-layout-content>
    </div>
</template>

<script setup>
import Title from "./cpns/Title.vue"
import TimeLine from "./cpns/TimeLine.vue"
import projectApi from "@/api/project/project"
import { useRoute } from "vue-router"
import RoundInfo from "./cpns/RoundInfo.vue"
const route = useRoute()
// hooks
import useFetchData from "@/hooks/fetchData"
const fetchData = async () => {
    return projectApi.getBoardInfo(route.params.projectId)
}
const { loadingData, isDataLoading } = useFetchData({}, fetchData)

defineOptions({
    name: "projBoard"
})
</script>

<style lang="less" scoped>
:deep(.ma-content-block) {
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
}
</style>
