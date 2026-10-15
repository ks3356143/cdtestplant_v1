import { request } from "@/api/request"
export default {
    /**
     * 生成问题单的多个表格
     * @returns Promise(message)
     */
    createWtdTable(params = {}) {
        return request({
            url: `/generateWtd/create/problem`,
            method: "get",
            params
        })
    }
}
