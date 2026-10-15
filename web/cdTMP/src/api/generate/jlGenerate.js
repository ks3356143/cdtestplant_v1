import { request } from "@/api/request"
export default {
    /**
     * 生成测试用例记录那一堆表格
     * @returns Promise(message)
     */
    createJLcaserecord(params = {}) {
        return request({
            url: `/generateJL/create/caserecord`,
            method: "get",
            params
        })
    }
}
