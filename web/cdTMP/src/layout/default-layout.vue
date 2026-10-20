<template>
    <a-layout class="layout" :class="{ mobile: appStore.hideMenu }">
        <div class="navbar layout-navbar">
            <NavBar />
        </div>
        <a-layout class="layout">
            <a-layout class="layout">
                <a-layout-sider
                    v-if="renderMenu"
                    v-show="!hideMenu"
                    class="layout-sider"
                    breakpoint="xl"
                    :collapsed="collapsed"
                    :collapsible="true"
                    :width="menuWidth"
                    :style="{ paddingTop: navbar ? '60px' : '' }"
                    :hide-trigger="true"
                    @collapse="setCollapsed"
                >
                    <div class="menu-wrapper">
                        <Menu />
                    </div>
                </a-layout-sider>
                <a-drawer v-if="hideMenu" :visible="drawerVisible" placement="left" :footer="false" mask-closable :closable="false" @cancel="drawerCancel">
                    <Menu />
                </a-drawer>
                <a-layout class="layout-content" :style="paddingStyle">
                    <TabBar v-if="appStore.tabBar" />
                    <a-layout-content class="work-area">
                        <PageLayout />
                    </a-layout-content>
                    <Footer v-if="footer" />
                </a-layout>
            </a-layout>
        </a-layout>
    </a-layout>
</template>

<script setup>
import { ref, computed, watch, provide, onMounted } from "vue"
import { useRoute } from "vue-router"
import { useAppStore, useUserStore } from "@/store"
import NavBar from "@/layout/components/navbar.vue"
import Menu from "@/layout/components/menu.vue"
import TabBar from "@/layout/components/tab-bar.vue"
import PageLayout from "@/layout/page-layout.vue"
import usePermission from "@/hooks/permission"
import Footer from "@/layout/components/footer.vue"
import useResponsive from "@/hooks/responsive"
const appStore = useAppStore()
const userStore = useUserStore()
const route = useRoute()
const permission = usePermission()
// 响应式屏幕
useResponsive(true)
// 初始化数据
const isInit = ref(false)
const footer = computed(() => appStore.footer)
// 是否渲染左侧菜单
const renderMenu = computed(() => appStore.menu && !appStore.topMenu)
const hideMenu = computed(() => appStore.hideMenu)
// 菜单收缩
const collapsed = computed(() => {
    return appStore.menuCollapse
})
const setCollapsed = (val) => {
    if (!isInit.value) return // 针对页面初始化菜单状态问题
    appStore.updateSettings({ menuCollapse: val })
}
// 菜单宽度
const menuWidth = computed(() => {
    return appStore.menuCollapse ? 48 : appStore.menuWidth
})
// 角色监控
watch(
    () => userStore.role,
    (roleValue) => {
        if (roleValue && !permission.accessRouter(route)) router.push({ name: "notFound" })
    }
)
// 缩小后的menu菜单
const drawerVisible = ref(false)
const drawerCancel = () => {
    drawerVisible.value = false
}
provide("toggleDrawerMenu", () => {
    drawerVisible.value = !drawerVisible.value
})
// 确认加载完毕
onMounted(() => {
    isInit.value = true
})
// 右侧内容区padding的响应式
const navbar = computed(() => appStore.navbar)
const navbarHeight = `60px`
const paddingStyle = computed(() => {
    const paddingLeft = renderMenu.value && !hideMenu.value ? { paddingLeft: `${menuWidth.value}px` } : {}
    const paddingTop = navbar.value ? { paddingTop: navbarHeight } : {}
    return { ...paddingLeft, ...paddingTop }
})
</script>

<style scoped lang="less">
@nav-size-height: 60px;
@layout-max-width: 1100px;

.layout {
    width: 100%;
    height: 100%;
}

.layout-navbar {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 100;
    width: 100%;
    height: @nav-size-height;
}

.layout-sider {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 99;
    height: 100%;
    background-color: var(--app-sidebar, #ffffff);
    transition: all 0.2s cubic-bezier(0.34, 0.69, 0.1, 1);
    &::after {
        position: absolute;
        top: 0;
        right: -1px;
        display: block;
        width: 1px;
        height: 100%;
        background-color: var(--app-sidebar-line, #e4e7eb);
        content: "";
    }

    > :deep(.arco-layout-sider-children) {
        overflow-y: hidden;
    }
}
.work-area {
    position: relative; // 注意这个是改变v-loading这些东西
}
.menu-wrapper {
    height: 100%;
    overflow: auto;
    overflow-x: hidden;

    // 侧边栏：浅底 + 青绿选中块（暗色主题由 --app-sidebar* 令牌切回墨黑）
    :deep(.arco-menu) {
        background-color: transparent;
        color: var(--app-sidebar-text, #374151);

        ::-webkit-scrollbar {
            width: 12px;
            height: 4px;
        }

        ::-webkit-scrollbar-thumb {
            border: 4px solid transparent;
            background-clip: padding-box;
            border-radius: 0;
            background-color: var(--app-line-strong, #cfd5dc);
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: var(--app-muted, #6b7280);
        }
    }

    :deep(.arco-menu-item),
    :deep(.arco-menu-inline-header) {
        margin: 2px 8px;
        width: auto;
        border-radius: 0;
        background-color: transparent;
        color: var(--app-sidebar-text, #374151);
        line-height: 40px;
        height: 40px;
    }

    :deep(.arco-menu-inline-content) {
        background-color: transparent;
    }

    :deep(.arco-menu-item:hover),
    :deep(.arco-menu-inline-header:hover) {
        background-color: var(--app-sidebar-2, #f2f4f6);
        color: var(--app-sidebar-hover-text, #0f172a);
    }

    :deep(.arco-menu-item.arco-menu-selected) {
        background-color: rgb(var(--primary-6)) !important;
        color: #ffffff !important;
    }

    :deep(.arco-menu-icon) {
        color: var(--app-sidebar-muted, #8a94a3);
    }

    :deep(.arco-menu-item.arco-menu-selected .arco-menu-icon) {
        color: #ffffff;
    }

    // Arco 会把选中项的 svg 图标单独染成主色，青绿底上会“消失”，这里显式覆盖
    :deep(.arco-menu-item.arco-menu-selected .arco-menu-icon .arco-icon),
    :deep(.arco-menu-item.arco-menu-selected .arco-menu-icon svg) {
        color: #ffffff;
    }

    :deep(.arco-menu-inline-header:hover .arco-menu-icon) {
        color: var(--app-sidebar-hover-text, #0f172a);
    }

    :deep(.arco-menu-inline-header:hover .arco-menu-icon .arco-icon),
    :deep(.arco-menu-inline-header:hover .arco-menu-icon svg) {
        color: var(--app-sidebar-hover-text, #0f172a);
    }

    :deep(.arco-menu-icon-suffix) {
        color: var(--app-sidebar-muted, #8a94a3);
    }

    :deep(.arco-menu-collapse-button) {
        background-color: var(--app-sidebar-2, #f2f4f6);
        color: var(--app-sidebar-muted, #8a94a3);
        border: 1px solid var(--app-sidebar-line, #e4e7eb);
        border-radius: 0;
    }

    :deep(.arco-menu-collapse-button:hover) {
        background-color: rgb(var(--primary-6));
        color: #ffffff;
    }
}

.layout-content {
    min-height: 100vh;
    overflow-y: auto;
    background-color: var(--app-canvas, #f2f4f6);
    transition: padding 0.2s cubic-bezier(0.34, 0.69, 0.1, 1);
}
</style>
