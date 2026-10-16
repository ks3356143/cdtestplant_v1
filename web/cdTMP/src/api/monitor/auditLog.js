import { request } from "@/api/request"
export default {
    /**
     * 统一审计日志分页查询（多维度检索：账号/时间/事件类型/告警/IP）
     */
    getAuditLogs(params = { pageSize: 10, page: 1 }) {
        return request({
            url: `/system/log/auditLogList`,
            method: "get",
            params
        })
    },
    /**
     * 审计事件类型可用值
     */
    getAuditEventTypes() {
        return request({
            url: `/system/log/auditEventTypes`,
            method: "get"
        })
    }
}
