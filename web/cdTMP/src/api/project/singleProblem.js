import { request } from "@/api/request"
export default {
    /**
     * 得到单个问题单信息
     */
    getSingleProblem(params = {}) {
        return request({
            url: "/project/getSingleProblem",
            method: "get",
            params
        })
    },
    /**
     * 参数是对象，对象里面1.id-问题单id
     * @returns 问题单关联的用例
     */
    getRelativeCases(params = {}) {
        return request({
            url: "/project/getRelativeCases",
            method: "get",
            params
        })
    }
}
