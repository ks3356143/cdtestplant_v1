import { DEFAULT_ROUTE, DEFAULT_ROUTE_NAME, REDIRECT_ROUTE_NAME } from "@/router/constants"
import { WORK_AREA_NAME } from "@/router"
import { defineStore } from "pinia"
import { isString } from "@/utils/is"
const formatTag = (route) => {
    const { name, meta, fullPath, query } = route
    return {
        title: meta.locale || "",
        name: String(name),
        fullPath,
        query,
        ignoreCache: meta.ignoreCache
    }
}
// 去除的页面名称，这里去除项目工作区页面
const BAN_LIST = [REDIRECT_ROUTE_NAME, WORK_AREA_NAME]
const useTabBarStore = defineStore("tabBar", {
    state: () => ({
        // 修改：添加"用户中心到缓存"
        cacheTabList: new Set([DEFAULT_ROUTE_NAME]),
        tagList: [DEFAULT_ROUTE]
    }),
    getters: {
        getTabList() {
            return this.tagList
        },
        getCacheList() {
            // Array.from将对象去掉key，拿value作为数组
            return Array.from(this.cacheTabList)
        }
    },
    actions: {
        updateTabList(route) {
            if (BAN_LIST.includes(route.name)) return
            this.tagList.push(formatTag(route))
            if (!route.meta.ignoreCache) {
                this.cacheTabList.add(route.name)
            }
        },
        deleteTag(idx, tag) {
            this.tagList.splice(idx, 1)
            this.cacheTabList.delete(tag.name)
        },
        addCache(name) {
            if (isString(name) && name !== "") this.cacheTabList.add(name)
        },
        deleteCache(tag) {
            this.cacheTabList.delete(tag.name)
        },
        freshTabList(tags) {
            this.tagList = tags
            this.cacheTabList.clear()
            // 要先判断ignoreCache
            this.tagList
                .filter((el) => !el.ignoreCache)
                .map((el) => el.name)
                .forEach((x) => this.cacheTabList.add(x))
        },
        resetTabList() {
            this.tagList = [DEFAULT_ROUTE]
            this.cacheTabList.clear()
            this.cacheTabList.add(DEFAULT_ROUTE_NAME)
        }
    }
})

export default useTabBarStore
