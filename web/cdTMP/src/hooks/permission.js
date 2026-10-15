import { useUserStore } from "@/store"

export default function usePermission() {
    const userStore = useUserStore()
    return {
        // 返回的函数可自定义路由权限
        accessRouter(route) {
            return (
                !route.meta?.requiresAuth ||
                !route.meta?.roles ||
                route.meta?.roles?.includes("*") ||
                route.meta?.roles?.includes(userStore.role)
            )
        },
        // 返回第一个可访问的路径
        findFirstPermissionRoute(_routers, role = "admin") {
            const cloneRouters = [..._routers]
            while (cloneRouters.length) {
                const firstElement = cloneRouters.shift()
                if (
                    firstElement?.meta?.roles?.find((el) => {
                        return el.includes("*") || el.includes(role)
                    })
                )
                    return { name: firstElement.name }
                if (firstElement?.children) {
                    cloneRouters.push(...firstElement.children)
                }
            }
            return null
        }
        // 你可以添加任何规则
    }
}
