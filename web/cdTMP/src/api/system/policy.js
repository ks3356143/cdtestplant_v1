import { request } from "@/api/request"

export default {
  // 获取登录失败锁定策略（系统安全员）
  getPolicy() {
    return request({ url: "/system/security/policy", method: "get" })
  },
  // 更新登录失败锁定策略（系统安全员）
  updatePolicy(data) {
    return request({ url: "/system/security/policy", method: "put", data })
  },
  // 用户密级许可清单（系统安全员：敏感标记管理）
  getClearanceList() {
    return request({ url: "/system/security/clearance/list", method: "get" })
  },
  // 为用户配置密级许可（系统安全员）
  updateClearance(userId, data) {
    return request({ url: `/system/security/clearance/${userId}`, method: "put", data })
  },
  // 用户数据保密性保护总览（落库加密字段 / 传输加密 / 剩余信息措施）
  getConfidentiality() {
    return request({ url: "/system/security/confidentiality", method: "get" })
  },
  // 清理过期临时文件（剩余信息保护）
  purgeResidue(maxAgeHours = 24) {
    return request({ url: "/system/security/residue/purge", method: "post", params: { max_age_hours: maxAgeHours } })
  }
}
