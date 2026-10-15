import { DEFAULT_LAYOUT } from "../base"

const DATAMANAGE = {
    path: "/datamanage",
    name: "datamanage",
    component: DEFAULT_LAYOUT, // () => import("@/layout/default-layout.vue")
    meta: {
        requiresAuth: true,
        icon: "icon-storage",
        order: 99,
        locale: "数据管理",
        title: "数据管理"
    },
    children: [
        {
            path: "dictmanage",
            name: "dictmanage",
            component: () => import("@/views/datamanage/dictmanage/index.vue"),
            meta: {
                requiresAuth: true,
                roles: ["*"],
                locale: "字典管理",
                icon: "icon-book",
                title: "字典管理"
            }
        },
        {
            path: "projContact",
            name: "projContact",
            component: () => import("@/views/datamanage/projContact/index.vue"),
            meta: {
                requiresAuth: true,
                roles: ["*"],
                locale: "项目联系信息",
                icon: "icon-phone",
                title: "项目联系信息"
            }
        },
        {
            path: "abbreviation",
            name: "abbreviation",
            component: () => import("@/views/datamanage/abbreviation/index.vue"),
            meta: {
                requiresAuth: true,
                roles: ["*"],
                locale: "缩略语",
                icon: "icon-scissor",
                title: "缩略语"
            }
        }
    ]
}

export default DATAMANAGE
