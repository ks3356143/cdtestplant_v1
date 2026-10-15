import { request } from "@/api/request"

export default {
  // 获取登录失败锁定策略（系统安全员）
  getPolicy() {
    return request({ url: "/system/security/policy", method: "get" })
  },
  // 更新登录失败锁定策略（系统安全员）
  updatePolicy(data) {
    return request({ url: "/system/security/policy", method: "put", data })
  }
}
