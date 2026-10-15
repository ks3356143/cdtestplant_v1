import { request } from "@/api/request"
export default {
    /**
     * 查询工作台的统计信息
     * @returns 统计用户和项目情况
     */
    getStatistics(params = {}) {
        return request({
            url: `/system/workplace/statistics`,
            method: "get",
            params
        })
    }
}
