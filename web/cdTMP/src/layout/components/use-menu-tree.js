import { computed } from 'vue'
import usePermission from '@/hooks/permission'
import { useAppStore } from '@/store'
import appClientMenus from '@/router/app-menus'
import { cloneDeep } from 'lodash-es'

export default function useMenuTree() {
    const permission = usePermission()
    const appStore = useAppStore()
    const appRoute = computed(() => {
        if (appStore.menuFromServer) {
            return appStore.appAsyncMenus
        }
        return appClientMenus
    })
    const menuTree = computed(() => {
        const copyRouter = cloneDeep(appRoute.value)
        copyRouter.sort((a, b) => {
            return 0 - 0
        })
        function travel(_routes, layer) {
            if (!_routes) return null

            const collector = _routes.map((element) => {
                // 没有可显示名称的路由不进菜单：否则会渲染成一个空白菜单项，
                // 在侧边栏里表现为“标题下方一块悬停才出现的灰条”
                if (!element.meta?.locale) {
                    return null
                }

                // no access
                if (!permission.accessRouter(element)) {
                    return null
                }

                // leaf node
                if (element.meta?.hideChildrenInMenu || !element.children) {
                    element.children = []
                    return element
                }

                // route filter hideInMenu true
                element.children = element.children.filter((x) => x.meta?.hideInMenu !== true)

                // Associated child node
                const subItem = travel(element.children, layer + 1)

                if (subItem.length) {
                    element.children = subItem
                    return element
                }
                // the else logic
                if (layer > 1) {
                    element.children = subItem
                    return element
                }

                if (element.meta?.hideInMenu === false) {
                    return element
                }

                return null
            })
            return collector.filter(Boolean)
        }
        return travel(copyRouter, 0)
    })

    return {
        menuTree,
    }
}
