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
     * 审计事件类型清单（{code,label,alert}，后端唯一事实源）
     */
    getAuditEventTypes() {
        return request({
            url: `/system/log/auditEventTypes`,
            method: "get"
        })
    },
    /**
     * 数据完整性核查（7.1.7）：批量重算完整性标签并比对
     */
    integrityCheck() {
        return request({
            url: `/system/log/integrityCheck`,
            method: "get"
        })
    }
}
