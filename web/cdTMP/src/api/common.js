import { request } from "@/api/request"
import { getCachedDict } from "@/utils/dictCache"

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
     * 快捷查询字典（短缓存，同一 code 60 秒内复用；字典变更时由字典 API 主动失效）
     */
    getDict(code) {
        return getCachedDict(code, () =>
            request({
                url: "system/dataDict/list",
                method: "get",
                params: { code }
            })
        )
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
