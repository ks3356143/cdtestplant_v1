import { DEFAULT_LAYOUT } from "../base"

// 三权分立之系统安全员（secadmin）：安全策略配置
const SECURITY = {
    path: "/security",
    name: "security",
    component: DEFAULT_LAYOUT,
    meta: {
        requiresAuth: true,
        icon: "icon-safe",
        order: 2,
        locale: "安全策略",
        title: "安全策略",
        roles: ["secadmin"] // 只有系统安全员（secadmin）才看到安全策略菜单
    },
    children: [
        {
            path: "policy",
            name: "policy",
            component: () => import("@/views/security/policy/index.vue"),
            meta: {
                requiresAuth: true,
                locale: "登录失败锁定策略",
                icon: "icon-lock",
                title: "登录失败锁定策略",
                roles: ["*"]
            }
        }
    ]
}

export default SECURITY
