import { createRequest, createService } from "@/utils/request-core"

// 业务接口通用请求（与 utils/request 共用同一套拦截器实现）
export const service = createService()
export const request = createRequest(service)
