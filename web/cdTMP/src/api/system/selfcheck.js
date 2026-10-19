import { request } from "@/api/request"

export default {
  // 执行系统安全性检测分析（GB/T 28452-2012 7.1.10）
  runSelfCheck() {
    return request({ url: "/system/security/selfcheck", method: "get" })
  }
}
