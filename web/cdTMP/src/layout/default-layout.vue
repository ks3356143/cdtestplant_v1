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
    transition: all 0.2s cubic-bezier(0.34, 0.69, 0.1, 1);
    &::after {
        position: absolute;
        top: 0;
        right: -1px;
        display: block;
        width: 1px;
        height: 100%;
        background-color: var(--color-border);
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
    :deep(.arco-menu) {
        ::-webkit-scrollbar {
            width: 12px;
            height: 4px;
        }

        ::-webkit-scrollbar-thumb {
            border: 4px solid transparent;
            background-clip: padding-box;
            border-radius: 3px;
            background-color: var(--color-text-4);
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: var(--color-text-3);
        }
    }
}

.layout-content {
    min-height: 100vh;
    overflow-y: auto;
    background-color: var(--color-fill-2);
    transition: padding 0.2s cubic-bezier(0.34, 0.69, 0.1, 1);
}
</style>
