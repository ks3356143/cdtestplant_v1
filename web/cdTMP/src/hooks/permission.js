import { useUserStore } from "@/store"

export default function usePermission() {
    const userStore = useUserStore()
    return {
        // 返回的函数可自定义路由权限
        accessRouter(route) {
            // 沿匹配链逐级校验：父级限制（如日志监控仅 auditadmin）必须对子路由同样生效，
            // 否则子路由未写 roles 时会被 !route.meta.roles 短路放行
            const chain = route?.matched?.length ? route.matched : [route]
            return chain.every((item) => {
                const requiresAuth = item.meta?.requiresAuth
                const roles = item.meta?.roles
                return (
                    !requiresAuth ||
                    !roles ||
                    roles.includes("*") ||
                    roles.includes(userStore.role)
                )
            })
        },
        // 返回第一个可访问的路径（只取叶子路由，避免落到没有内容的父级布局）
        findFirstPermissionRoute(_routers, role = "admin") {
            const walk = (routes) => {
                for (const item of routes) {
                    const roles = item.meta?.roles
                    const allowed =
                        !item.meta?.requiresAuth ||
                        !roles ||
                        roles.includes("*") ||
                        roles.includes(role)
                    if (!allowed) continue
                    if (item.children?.length) {
                        const child = walk(item.children)
                        if (child) return child
                        continue
                    }
                    if (item.name) return { name: item.name }
                }
                return null
            }
            return walk(_routers)
        }
        // 你可以添加任何规则
    }
}
