import { request } from "@/api/request"

export default {
  // 抗抵赖证据列表（审计员）
  getEvidenceList(params = {}) {
    return request({ url: "/project/nonrepudiation/list", method: "get", params })
  }
}
