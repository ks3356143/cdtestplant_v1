<template>
    <router-view v-slot="{ Component, route }" class="mx-2 my-2">
        <template v-if="!Component">
            <Empty class="full-empty" />
        </template>
        <transition name="ma-slide-down" mode="out-in" appear>
            <!-- 这里主要在路由定义是否缓存页面 -->
            <component :is="Component" v-if="route.meta.ignoreCache" ref="viewChildRef" :key="route.fullPath" />
            <keep-alive v-else :include="cacheList">
                <component :is="Component" ref="viewChildRef" :key="route.fullPath"></component>
            </keep-alive>
        </transition>
    </router-view>
</template>

<script setup>
import { computed, ref } from "vue"
import { useTabBarStore } from "@/store"
import Empty from "@/components/Empty/index.vue"
// 获取缓存列表
const tabBarStore = useTabBarStore()
const cacheList = computed(() => tabBarStore.getCacheList)
// 调用router-view组件的刷新方法 - 并暴露给子节点
const viewChildRef = ref(null)
const refresh = () => {
    try {
        viewChildRef.value.refreshCrudTable()
    } catch (err) {
        console.log("无法找到router-view动态组件的刷新函数")
    }
}
defineExpose({ refresh })
</script>

<style lang="less" scoped>
.full-empty {
    width: 100%;
}
</style>
