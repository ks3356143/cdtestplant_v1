<template>
    <div class="navbar">
        <div class="left-side">
            <a-space>
                <div class="logo-container">
                    <img src="@/assets/img/wxwx-logo.svg" class="logo" alt="logo" @click="handleClickLogo" />
                </div>
                <a-typography-title class="title" @click="handleClickLogo" :style="{ margin: 0, fontSize: '18px' }" :heading="5">
                    <div class="brand-title">测试管理平台</div>
                </a-typography-title>
                <span class="version-chip">v{{ $version }}</span>
                <icon-menu-fold v-if="!topMenu && appStore.device === 'mobile'" style="font-size: 22px; cursor: pointer" @click="toggleDrawerMenu" />
            </a-space>
        </div>
        <div class="center-side flex items-center font-bold text-lg justify-center">
            <div class="fix-side" v-if="route.query.id">
                <project-info-other />
            </div>
            <template v-if="title">
                <a-typography-title
                    class="project-name"
                    :heading="3"
                    :ellipsis="{
                        rows: 2
                    }"
                >
                    <div>项目名称：{{ $route.query.ident }}-{{ title }}</div>
                </a-typography-title>
            </template>
            <Menu v-if="topMenu"></Menu>
        </div>
        <ul class="right-side">
            <li>
                <a-tooltip content="搜索-暂无">
                    <a-button class="nav-btn" type="outline" shape="square">
                        <template #icon>
                            <icon-search />
                        </template>
                    </a-button>
                </a-tooltip>
            </li>
            <li>
                <a-tooltip content="切换主题">
                    <a-button @click="handleChangeTheme" class="nav-btn" type="outline" shape="square">
                        <template #icon>
                            <icon-moon-fill />
                        </template>
                    </a-button>
                </a-tooltip>
            </li>
            <li>
                <a-tooltip :content="isFullscreen ? '退出全屏' : '进入全屏'">
                    <a-button class="nav-btn" type="outline" shape="square" @click="toggleFullScreen">
                        <template #icon>
                            <icon-fullscreen-exit v-if="isFullscreen" />
                            <icon-fullscreen v-else />
                        </template>
                    </a-button>
                </a-tooltip>
            </li>
            <li>
                <a-dropdown trigger="click">
                    <a-avatar :size="32" :style="{ marginRight: '8px', cursor: 'pointer' }">
                        <img alt="avatar" src="@/assets/img/avatar.jpg" />
                    </a-avatar>
                    <template #content>
                        <a-doption>
                            <a-space @click="$router.push({ name: 'usercenter' })">
                                <icon-user />
                                <span> 用户中心 </span>
                            </a-space>
                        </a-doption>
                        <a-doption>
                            <a-space @click="handleLogout">
                                <icon-export />
                                <span> 退出登录 </span>
                            </a-space>
                        </a-doption>
                    </template>
                </a-dropdown>
            </li>
        </ul>
    </div>
</template>

<script setup>
import { computed, inject } from "vue"
import { useAppStore } from "@/store"
import { useFullscreen } from "@vueuse/core"
// 这个hook就是退出登录跳转的
import useUser from "@/hooks/logout"
import Menu from "@/layout/components/menu.vue"
import { useRouter, useRoute } from "vue-router"
// 项目信息录入组件
import projectInfoOther from "./projectInfoOther/index.vue"

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

// 切换暗黑主题
const handleChangeTheme = () => {
    appStore.toggleTheme()
}
// title管理-默认在后台
const props = defineProps({
    title: {
        type: String,
        default: ""
    }
})
// 是否menu在顶部-暂时不用
const topMenu = computed(() => appStore.topMenu && appStore.menu)
// 全屏设置,使用了@vueuse/core
const { isFullscreen, toggle: toggleFullScreen } = useFullscreen()
/// 退出登录
const { logout } = useUser()
const handleLogout = () => {
    logout()
}
// 注入事件
const toggleDrawerMenu = inject("toggleDrawerMenu")
// 点击图标返回首页
const handleClickLogo = () => {
    router.push({ name: "workplace" })
}
</script>

<style scoped lang="less">
.fix-side {
    // 项目设置按钮
    margin-left: 50px;
    margin-top: 10px;
}

.logo-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background-color: var(--app-brand-tile, #0f172a);
    cursor: pointer;
    transition: background-color 0.15s ease;

    .logo {
        width: 24px;
        height: 24px;
        filter: brightness(0) invert(1);
        transition: opacity 0.15s ease;
    }

    &:hover {
        background-color: rgb(var(--primary-6));

        .logo {
            opacity: 0.9;
        }
    }
}

.brand-title {
    color: var(--app-ink, #111827);
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.02em;
    white-space: nowrap;
}

.version-chip {
    display: inline-flex;
    align-items: center;
    height: 20px;
    padding: 0 6px;
    border: 1px solid var(--app-line, #e4e7eb);
    color: var(--app-muted, #6b7280);
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.04em;
    user-select: none;
}

// 窄屏：隐藏版本号、压缩标题，避免标题被挤成多行
.title div {
    white-space: nowrap;
}

@media (max-width: 576px) {
    .version-chip {
        display: none;
    }
    .brand-title {
        font-size: 15px;
    }
    .right-side li .nav-btn {
        display: none;
    }
}

.navbar {
    display: flex;
    justify-content: space-between;
    height: 100%;
    background-color: var(--app-surface, #fff);
    border-bottom: 1px solid var(--app-line, #e4e7eb);
}

.left-side {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-left: 16px;
}

.center-side {
    flex: 1;
}

.right-side {
    display: flex;
    padding-right: 16px;
    list-style: none;
    :deep(.locale-select) {
        border-radius: 0;
    }
    li {
        display: flex;
        align-items: center;
        padding: 0 6px;
    }

    a {
        color: var(--app-ink, #111827);
        text-decoration: none;
    }
    .nav-btn {
        width: 32px;
        height: 32px;
        border-color: var(--app-line, #e4e7eb);
        color: var(--app-ink-2, #374151);
        font-size: 15px;
    }

    .nav-btn:hover {
        border-color: rgb(var(--primary-6));
        color: rgb(var(--primary-6));
        background-color: rgb(var(--primary-1));
    }

    :deep(.arco-avatar) {
        border-radius: 0;
    }

    .trigger-btn,
    .ref-btn {
        position: absolute;
        bottom: 14px;
    }
    .trigger-btn {
        margin-left: 14px;
    }
}

.title {
    cursor: pointer;
    font-weight: 700;
    transition: opacity 0.15s ease;

    &:hover {
        opacity: 0.72;
    }
}

// 根据浏览器宽度调整
.project-name {
    margin: 0 !important;
    font-size: 14px;
    font-weight: 600;
    line-height: 60px;
    flex: 1;
    text-align: center;
    color: var(--app-ink-2, #374151);
}

@media (max-width: 1024px) {
    .project-name {
        font-size: 12px;
    }
}

@media (max-width: 1280px) {
    .project-name {
        font-size: 13px;
    }
}
</style>

<style lang="less">
.message-popover {
    .arco-popover-content {
        margin-top: 0;
    }
}
</style>
