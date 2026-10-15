import { DEFAULT_LAYOUT } from "../base"

const TESTMANAGE = {
    path: "/monitor",
    name: "monitor",
    component: DEFAULT_LAYOUT, // () => import("@/layout/default-layout.vue")
    meta: {
        requiresAuth: true,
        icon: "icon-desktop",
        order: 1,
        locale: "日志监控",
        title: "日志监控",
        roles: ["auditadmin"] // 三权分立：只有系统审计员（auditadmin）才看到日志监控
    },
    children: [
        {
            path: "operationLog",
            name: "operationLog",
            component: () => import("@/views/monitor/operationLog/index.vue"),
            meta: {
                requiresAuth: true,
                locale: "数据操作日志",
                icon: "icon-file",
                title: "数据操作日志"
            }
        },
        {
            path: "operations",
            name: "operations",
            component: () => import("@/views/monitor/operations/index.vue"),
            meta: {
                requiresAuth: true,
                roles: ["*"],
                locale: "接口操作日志",
                icon: "icon-file",
                title: "接口操作日志"
            }
        },
        {
            path: "loginLog",
            name: "loginLog",
            component: () => import("@/views/monitor/loginLog/index.vue"),
            meta: {
                requiresAuth: true,
                roles: ["*"],
                locale: "登录日志",
                icon: "icon-file",
                title: "登录日志"
            }
        }
    ]
}

export default TESTMANAGE
