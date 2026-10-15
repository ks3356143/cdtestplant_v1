/**
 * @description: 路由的白名单常量对象
 * @type: 数组
 */
export const WHITE_LIST = [
    { name: "notFound", children: [] },
    { name: "login", children: [] }
]
/**
 * @description: NOTFOUND常量对象{name:'notFound'}
 * @type: object
 */
export const NOT_FOUND = {
    name: "notFound"
}

export const REDIRECT_ROUTE_NAME = "redirect"

export const DEFAULT_ROUTE_NAME = "workplace"

/**
 * @description: 默认路由对象没有component,固定在router/constants.js文件查看
 * @type: object
 */
export const DEFAULT_ROUTE = {
    title: "工作台",
    name: DEFAULT_ROUTE_NAME,
    fullPath: "/dashboard/workplace"
}
