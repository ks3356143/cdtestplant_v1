import { setRouteEmitter } from "@/utils/route-listener"
import setupUserLoginInfoGuard from "./userLoginInfo"
import setupPermissionGuard from "@/router/guard/permisstion"
// 导入设置title的工具
import { setRouteTitle } from "@/utils/title"
// 为了已登录用户直接进入login
import { useUserStore } from "@/store"
import NProgress from "nprogress" // progress bar
import "nprogress/nprogress.css"

function setupPageGuard(router) {
    router.beforeEach(async (to) => {
        // 发出路由改变的事件
        setRouteEmitter(to)
    })
    // 设置站点document.title
    router.afterEach((to, from) => {
        setRouteTitle(to.meta.title)
        NProgress.done()
    })
    // 设置如果已登录用户进入login页面则直接进入工作台
    router.beforeEach((to) => {
        const userStore = useUserStore()
        if (to.name === "login") {
            if (userStore.isLogin()) {
                return {
                    name: "workplace"
                }
            }
        }
    })
}

export default function createRouteGuard(router) {
    setupPageGuard(router)
    setupUserLoginInfoGuard(router)
    setupPermissionGuard(router)
}
