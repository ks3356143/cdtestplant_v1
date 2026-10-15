import { request } from "@/api/request"
export default {
    /**
     * 分页查询操作日志
     * @returns 操作日志分页结果
     */
    getOperationsLogs(params = { pageSize: 10, page: 1 }) {
        return request({
            url: `/system/log/operation_list`,
            method: "get",
            params
        })
    },
    /**
     * 操作日志删除
     * @returns 后台返回的删除信息
     */
    deleteOperationLogs(params = { day: 7 }) {
        return request({
            url: `/system/log/operation_delete`,
            method: "get",
            params
        })
    }
}
