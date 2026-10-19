import { request } from "@/api/request"

export default {
  // 备份现状概览（GB/T 28452-2012 7.1.9）
  getSummary() {
    return request({ url: "/system/backup/summary", method: "get" })
  },
  // 备份记录列表
  getList() {
    return request({ url: "/system/backup/list", method: "get" })
  },
  // 新建备份（全量/增量，可指定项目范围）
  create(data) {
    return request({ url: "/system/backup/create", method: "post", data })
  },
  // 按备份恢复数据
  restore(id) {
    return request({ url: `/system/backup/${id}/restore`, method: "post" })
  },
  // 删除备份
  remove(id) {
    return request({ url: `/system/backup/${id}`, method: "delete" })
  }
}
