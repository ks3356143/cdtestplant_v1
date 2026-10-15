import NProgress from "nprogress" // progress bar
import "nprogress/nprogress.css"

import usePermission from "@/hooks/permission"
import { useUserStore, useAppStore } from "@/store"
import { appRoutes } from "../routes"
import { WHITE_LIST, NOT_FOUND } from "../constants"
// 权限守卫
export default function setupPermissionGuard(router) {
    router.beforeEach(async (to, from) => {
        const appStore = useAppStore()
        const userStore = useUserStore()
        const Permission = usePermission()
        // 该函数根据角色返回是否有这个路由
        const permissionsAllow = Permission.accessRouter(to)
        if (appStore.menuFromServer) {
            // 针对来自服务端的菜单配置进行处理
            // Handle routing configuration from the server

            // 根据需要自行完善来源于服务端的菜单配置的permission逻辑
            // Refine the permission logic from the server's menu configuration as needed
            if (!appStore.appAsyncMenus.length && !WHITE_LIST.find((el) => el.name === to.name)) {
                await appStore.fetchServerMenuConfig()
            }
            const serverMenuConfig = [...appStore.appAsyncMenus, ...WHITE_LIST]

            let exist = false
            while (serverMenuConfig.length && !exist) {
                const element = serverMenuConfig.shift()
                if (element?.name === to.name) exist = true

                if (element?.children) {
                    serverMenuConfig.push(...element.children)
                }
            }
            if (exist && permissionsAllow) {
                return true
            } else {
                return NOT_FOUND
            }
        } else {
            // eslint-disable-next-line no-lonely-if
            if (permissionsAllow) {
                return true
            } else {
                const destination = Permission.findFirstPermissionRoute(appRoutes, userStore.role) || NOT_FOUND
                return destination
            }
        }
    })
}
