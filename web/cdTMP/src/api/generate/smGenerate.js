import { request } from "@/api/request"
export default {
    /**
     *
     * @returns 大纲测试项数据
     */
    createSMTechyiju(params = {}) {
        return request({
            url: `/generateSM/create/techyiju`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成测试用例
     */
    createSMCaseList(params = {}) {
        return request({
            url: `/generateSM/create/caseList`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成测试用例那个表-测试名称/标识/测试用例综述
     */
    createSMCaseBreifList(params = {}) {
        return request({
            url: `/generateSM/create/caseBreifList`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成说明追踪
     */
    createSMTrack(params = {}) {
        return request({
            url: `/generateSM/create/smtrack`,
            method: "get",
            params
        })
    }
}
