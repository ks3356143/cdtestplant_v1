import { DEFAULT_LAYOUT } from "../base"

const DASHBOARD = {
    path: "/dashboard",
    name: "dashboard",
    component: DEFAULT_LAYOUT, // () => import("@/layout/default-layout.vue")
    meta: {
        requiresAuth: true,
        icon: "icon-home",
        order: 99,
        locale: "首页",
        title: "首页"
    },
    children: [
        {
            path: "workplace",
            name: "workplace",
            component: () => import("@/views/dashboard/workplace/index.vue"),
            meta: {
                requiresAuth: true,
                roles: ["*"],
                locale: "工作台",
                icon: "icon-dashboard",
                title: "工作台",
                ignoreCache: true
            }
        },
        {
            path: "usercenter",
            name: "usercenter",
            component: () => import("@/views/dashboard/usercenter/index.vue"),
            meta: {
                requiresAuth: true,
                roles: ["*"],
                locale: "用户中心",
                icon: "icon-user",
                title: "用户中心"
            }
        },
        {
            path: "usermanage",
            name: "usermanage",
            component: () => import("@/views/dashboard/usermanage/index.vue"),
            meta: {
                requiresAuth: true,
                roles: ["admin"], // 只有管理员admin才看得到
                locale: "用户管理",
                icon: "icon-user-group",
                title: "用户管理"
            }
        }
    ]
}

export default DASHBOARD
