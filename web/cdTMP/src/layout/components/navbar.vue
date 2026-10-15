<template>
    <div class="navbar">
        <div class="left-side">
            <a-space>
                <div class="logo-container">
                    <img src="@/assets/img/wxwx-logo.svg" class="logo" alt="logo" @click="handleClickLogo" />
                </div>
                <a-typography-title class="title" @click="handleClickLogo" :style="{ margin: 0, fontSize: '18px' }" :heading="5">
                    <div class="font-extrabold bg-clip-text text-transparent bg-linear-to-r from-blue-500 to-purple-600">测试管理平台</div>
                </a-typography-title>
                <a-typography-title :heading="6" class="version">v{{ $version }}</a-typography-title>
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
                    <a-button class="nav-btn" type="outline" :shape="'circle'">
                        <template #icon>
                            <icon-search />
                        </template>
                    </a-button>
                </a-tooltip>
            </li>
            <li>
                <a-tooltip content="切换主题">
                    <a-button @click="handleChangeTheme" class="nav-btn" type="outline" :shape="'circle'">
                        <template #icon>
                            <icon-moon-fill />
                        </template>
                    </a-button>
                </a-tooltip>
            </li>
            <li>
                <a-tooltip :content="isFullscreen ? '退出全屏' : '进入全屏'">
                    <a-button class="nav-btn" type="outline" :shape="'circle'" @click="toggleFullScreen">
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
                            <a-space @click="switchRoles">
                                <icon-tag />
                                <span> 切换角色 </span>
                            </a-space>
                        </a-doption>
                        <a-doption>
                            <a-space @click="$router.push({ name: 'usercenter' })">
                                <icon-user />
                                <span> 用户中心 </span>
                            </a-space>
                        </a-doption>
                        <a-doption>
                            <a-space @click="$router.push({ name: 'usercenter' })">
                                <icon-settings />
                                <span> 用户设置 </span>
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
import { Message } from "@arco-design/web-vue"
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
// appStore里面设置
const setVisible = () => {
    console.log("在appStore里面设置全局{ globalSettings: true }，暂无做")
    appStore.updateSettings({ globalSettings: true })
}
// 右上角下拉
const setDropDownVisible = () => {
    const event = new MouseEvent("click", {
        view: window,
        bubbles: true,
        cancelable: true
    })
    triggerBtn.value.dispatchEvent(event)
}
/// 切换角色
const switchRoles = async () => {
    Message.success("模拟切换角色")
}
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
    perspective: 1000px;
    .logo {
        width: 35px;
        height: 35px;
        cursor: pointer;
        transition: all 0.3s;
    }
}

.logo-container:hover {
    .logo {
        transform: rotateX(-25deg) rotateY(1440deg);
    }
}

.navbar {
    display: flex;
    justify-content: space-between;
    height: 100%;
    background-color: var(--color-bg-2);
    border-bottom: 1px solid var(--color-border);
}

.left-side {
    display: flex;
    align-items: center;
    padding-left: 20px;
}

.center-side {
    flex: 1;
}

.right-side {
    display: flex;
    padding-right: 20px;
    list-style: none;
    :deep(.locale-select) {
        border-radius: 20px;
    }
    li {
        display: flex;
        align-items: center;
        padding: 0 10px;
    }

    a {
        color: var(--color-text-1);
        text-decoration: none;
    }
    .nav-btn {
        border-color: rgb(var(--gray-2));
        color: rgb(var(--gray-8));
        font-size: 16px;
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
.version {
    color: #666;
    user-select: none;
}

.title {
    cursor: pointer;
    font-weight: 700;
    transition: all 0.3s;
    text-shadow: 2px 2px 20px rgba(0, 0, 0, 0.2);
    &:hover {
        color: #fff;
        -webkit-animation: neon6 0.5s ease-in-out infinite alternate;
        -moz-animation: neon6 0.5s ease-in-out infinite alternate;
        animation: neon6 0.5s ease-in-out infinite alternate;
    }
}

// 根据浏览器宽度调整
.project-name {
    font-size: 1.2rem;
    flex: 1;
    text-align: center;
}

@media (max-width: 1024px) {
    .project-name {
        font-size: 0.8rem;
    }
}

@media (max-width: 1280px) {
    .project-name {
        font-size: 1rem;
    }
}

@keyframes neon6 {
    from {
        text-shadow:
            0 0 10px #fff,
            0 0 20px #2563eb,
            0 0 30px #2563eb,
            0 0 40px #2563eb;
    }
    to {
        text-shadow:
            0 0 5px #fff,
            0 0 10px #2563eb,
            0 0 15px #2563eb,
            0 0 20px #2563eb;
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
