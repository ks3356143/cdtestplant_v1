<template>
    <div class="proj-board-container" v-loading="isDataLoading">
        <a-layout-content class="flex flex-col gap-2" v-if="!isDataLoading && hasData">
            <!-- 返回前面一页的按钮，以及项目整体情况 -->
            <Title :pInfo="loadingData"></Title>
            <!-- 时间线显示项目情况 -->
            <time-line :pInfo="loadingData" :projectId="route.params.projectId"></time-line>
            <!-- 以轮次为合集展示需求下面的测试项数、用例数，测试类型下面测试项和用例数量 -->
            <round-info v-for="(item, index) in loadingData.statistics" :key="index" :data="item"></round-info>
        </a-layout-content>
        <!-- 无权访问或项目不存在时给出空状态，避免模板读取空对象导致报错 -->
        <a-result v-else-if="!isDataLoading" status="warning" title="暂无看板数据"
                  subtitle="项目不存在、当前账号没有该项目的访问权限，或项目尚未初始化。">
            <template #extra>
                <a-button type="primary" @click="$router.push('/testmanage/projmanage')">返回项目列表</a-button>
            </template>
        </a-result>
    </div>
</template>

<script setup>
import Title from "./cpns/Title.vue"
import TimeLine from "./cpns/TimeLine.vue"
import projectApi from "@/api/project/project"
import { computed } from "vue"
import { useRoute } from "vue-router"
import RoundInfo from "./cpns/RoundInfo.vue"
const route = useRoute()
// hooks
import useFetchData from "@/hooks/fetchData"
const fetchData = async () => {
    return projectApi.getBoardInfo(route.params.projectId)
}
const { data: loadingData, isLoading: isDataLoading } = useFetchData({}, fetchData)
// 看板数据必须包含 time_line 才能渲染，否则按空状态处理
const hasData = computed(() => Boolean(loadingData.value && loadingData.value.time_line))

defineOptions({
    name: "projBoard"
})
</script>

<style lang="less" scoped>
// 直角扁平风格：容器使用细线分隔，不再叠加阴影
:deep(.ma-content-block) {
    box-shadow: none;
}
</style>
