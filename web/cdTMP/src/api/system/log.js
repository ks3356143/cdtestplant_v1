import { request } from "@/api/request"

export default {
    /**
     * 获取当前用户的登录日志
     * @returns 日志列表
     */
    getLoginLog(params = {}) {
        return request({
            url: "/system/log/list",
            method: "get",
            params
        })
    },
    /**
     * 获取当前用户的登录日志
     * @returns 日志列表
     */
    getOperationLog(params = {}) {
        return request({
            url: "/system/log/operations",
            method: "get",
            params
        })
    }
}
