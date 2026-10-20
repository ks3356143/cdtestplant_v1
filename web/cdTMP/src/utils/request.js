import qs from "qs"
import { createRequest, createService } from "@/utils/request-core"

// ma-crud 等内部组件使用：保留历史 10 秒超时与 allowDots 序列化行为
const stringify = (data) => qs.stringify(data, { allowDots: true, encode: false })

export const service = createService()
export const request = createRequest(service, { timeout: 10000, stringify })
