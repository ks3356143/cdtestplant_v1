<template>
    <div class="tab-bar-container">
        <a-affix ref="affixRef" :offset-top="offsetTop">
            <div class="tab-bar-box">
                <div class="tab-bar-scroll">
                    <div class="tags-wrap">
                        <tab-item v-for="(tag, index) in tagList" :key="tag.fullPath" :index="index" :item-data="tag" />
                    </div>
                </div>
                <div class="tag-bar-operation"></div>
            </div>
        </a-affix>
    </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from "vue"
import { listenerRouteChange } from "@/utils/route-listener"
import { useAppStore, useTabBarStore } from "@/store"
import tabItem from "./tab-item.vue"

const appStore = useAppStore()
const tabBarStore = useTabBarStore()

const affixRef = ref()
const tagList = computed(() => {
    return tabBarStore.getTabList
})
const offsetTop = computed(() => {
    return appStore.navbar ? 60 : 0
})

watch(
    () => appStore.navbar,
    () => {
        affixRef.value.updatePosition()
    }
)
const removeRouteChangeListener = listenerRouteChange((route) => {
    if (!route.meta.noAffix && !tagList.value.some((tag) => tag.fullPath === route.fullPath)) {
        tabBarStore.updateTabList(route)
    }
}, true)

onUnmounted(() => {
    // 只注销本组件注册的监听，避免误删菜单等其它组件的路由监听
    removeRouteChangeListener()
})
</script>

<style scoped lang="less">
.tab-bar-container {
    position: relative;
    background-color: var(--app-surface, #fff);
    .tab-bar-box {
        display: flex;
        padding: 0 0 0 12px;
        background-color: var(--app-surface, #fff);
        border-bottom: 1px solid var(--app-line, #e4e7eb);
        .tab-bar-scroll {
            height: 34px;
            flex: 1;
            overflow: hidden;
            .tags-wrap {
                padding: 5px 0;
                height: 48px;
                white-space: nowrap;
                overflow-x: auto;

                :deep(.arco-tag) {
                    display: inline-flex;
                    align-items: center;
                    height: 24px;
                    margin-right: 6px;
                    padding: 0 8px;
                    border: 1px solid var(--app-line, #e4e7eb);
                    background-color: transparent;
                    color: var(--app-muted, #6b7280);
                    border-radius: 0;
                    cursor: pointer;
                    transition:
                        background-color 0.15s ease,
                        border-color 0.15s ease,
                        color 0.15s ease;

                    &:hover {
                        background-color: var(--app-surface-soft, #f7f8fa);
                        color: var(--app-ink, #111827);
                    }

                    &:first-child {
                        .arco-tag-close-btn {
                            display: none;
                        }
                    }
                }
            }
        }
    }

    .tag-bar-operation {
        width: 100px;
        height: 34px;
    }
}
</style>
