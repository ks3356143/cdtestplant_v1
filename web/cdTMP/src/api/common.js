import { request } from "@/api/request"

export default {
    /**
     * 获取公告信息
     * @returns
     */
    getNoticeList(params = {}) {
        return request({
            url: "system/getNoticeList",
            method: "get",
            params
        })
    },
    /**
     * 快捷查询字典
     */
    getDict(code) {
        return request({
            url: "system/dataDict/list?code=" + code,
            method: "get"
        })
    },
    /**
     * 获取项目一年内每月统计数据
     */
    getChartData() {
        return request({
            url: "system/statistics/chart",
            method: "get"
        })
    }
}
