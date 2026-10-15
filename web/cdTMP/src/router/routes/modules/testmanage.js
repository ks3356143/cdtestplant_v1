import { DEFAULT_LAYOUT } from "../base"

const TESTMANAGE = {
    path: "/testmanage",
    name: "testmanage",
    component: DEFAULT_LAYOUT, // () => import("@/layout/default-layout.vue")
    meta: {
        requiresAuth: true,
        icon: "icon-apps",
        order: 98,
        locale: "测试管理",
        title: "测试管理"
    },
    children: [
        {
            path: "projmanage",
            name: "projmanage",
            component: () => import("@/views/testmanage/projmanage/index.vue"),
            meta: {
                requiresAuth: true,
                roles: ["*"],
                locale: "项目管理",
                icon: "icon-folder",
                title: "项目管理"
            }
        },
        // 二级路由（非三级路由，但是想办法把左侧菜单删除）
        {
            path: "/projBoard/:projectId",
            name: "projBoard",
            component: () => import("@/views/testmanage/projBoard/index.vue"),
            meta: {
                requiresAuth: true,
                roles: ["*"],
                locale: "项目看板",
                icon: "icon-folder",
                hideInMenu: true,
                ignoreCache: false,
                noAffix: true,
                title: "项目看板"
            }
        },
        // 二级路由：单独显示项目所属的文档片段
        {
            path: "/projFragment/:projectId",
            name: "projFragment",
            component: () => import("@/views/testmanage/projFragment/index.vue"),
            meta: {
                locale: "项目文档片段",
                icon: "icon-copy",
                hideInMenu: true,
                ignoreCache: false,
                noAffix: true,
                title: "项目文档片段"
            }
        }
    ]
}

export default TESTMANAGE
