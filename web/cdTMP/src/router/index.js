import { createRouter, createWebHistory } from "vue-router"
// appRoutes为modules下面的所有路由
import { appRoutes } from "./routes"
// 引入基本重定向路由和notFound路由
import { REDIRECT_MAIN, NOT_FOUND_ROUTE, PROJECT_LAYOUT } from "./routes/base"
import createRouteGuard from "@/router/guard/index"

// 定义工作区路由名称，为了不写死
export const WORK_AREA_NAME = "project"

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: "/",
            redirect: "login"
        },
        {
            path: "/login",
            name: "login",
            component: () => import("@/views/login.vue"),
            meta: {
                requiresAuth: false
            }
        },
        // 项目工作区路由
        {
            path: "/project",
            name: "project",
            component: PROJECT_LAYOUT,
            meta: {
                requiresAuth: true,
                ignoreCache: true, // 忽略缓存
                roles: ["*"],
                order: 0,
                locale: "项目工作区",
                icon: "icon-home",
                hideInMenu: true
            },
            children: [
                {
                    path: "round",
                    name: "round",
                    component: () => import("@/views/project/round/index.vue"),
                    meta: {
                        requiresAuth: true,
                        ignoreCache: true,
                        roles: ["*"],
                        locale: "轮次信息",
                        icon: "icon-arrow-right"
                    }
                },
                {
                    path: "dut",
                    name: "dut",
                    component: () => import("@/views/project/dut/index.vue"),
                    meta: {
                        requiresAuth: true,
                        ignoreCache: true,
                        roles: ["*"],
                        locale: "被测件信息",
                        icon: "icon-arrow-right"
                    }
                },
                {
                    path: "designDemand",
                    name: "designDemand",
                    component: () => import("@/views/project/design-demand/index.vue"),
                    meta: {
                        requiresAuth: true,
                        ignoreCache: true,
                        roles: ["*"],
                        locale: "设计需求",
                        icon: "icon-arrow-right"
                    }
                },
                {
                    path: "testDemand",
                    name: "testDemand",
                    component: () => import("@/views/project/testDemand/index.vue"),
                    meta: {
                        requiresAuth: true,
                        ignoreCache: true,
                        roles: ["*"],
                        locale: "测试需求",
                        icon: "icon-arrow-right"
                    }
                },
                {
                    path: "case",
                    name: "case",
                    component: () => import("@/views/project/case/index.vue"),
                    meta: {
                        requiresAuth: true,
                        ignoreCache: true,
                        roles: ["*"],
                        locale: "测试用例",
                        icon: "icon-arrow-right"
                    }
                },
                {
                    path: "problem",
                    name: "problem",
                    component: () => import("@/views/project/problem/index.vue"),
                    meta: {
                        requiresAuth: true,
                        ignoreCache: true,
                        roles: ["*"],
                        locale: "问题单详情",
                        icon: "icon-arrow-right"
                    }
                },
                {
                    path: "opeSets",
                    name: "opeSets",
                    component: () => import("@/views/project/opeSets/index.vue"),
                    meta: {
                        requiresAuth: true,
                        ignoreCache: true,
                        roles: ["*"],
                        locale: "操作集合",
                        icon: "icon-arrow-right"
                    }
                }
            ]
        },
        // 后台管理的路由以及404和重定向路由
        ...appRoutes,
        REDIRECT_MAIN,
        NOT_FOUND_ROUTE
    ],
    scrollBehavior() {
        // 页面跳转后滚动到顶部
        return { top: 0 }
    }
})
createRouteGuard(router)

export default router
