import { request } from "@/api/request"
export default {
    /**
     * 生成回归测试说明的被测软件基本信息
     * @returns
     */
    createBasicInfo(params = {}) {
        return request({
            url: `/generateHSM/create/basicInformation`,
            method: "get",
            params
        })
    },
    /**
     * 生成非第一轮的多轮文档概述
     * @returns
     */
    createDocSummary(params = {}) {
        return request({
            url: `/generateHSM/create/docsummary`,
            method: "get",
            params
        })
    },
    /**
     * 生成非第一轮的多轮技术依据文件
     * @returns
     */
    createJstech(params = {}) {
        return request({
            url: `/generateHSM/create/jstech`,
            method: "get",
            params
        })
    },
    /**
     * 生成非第一轮的软件更改部分
     * @returns
     */
    createChangePart(params = {}) {
        return request({
            url: `/generateHSM/create/changePart`,
            method: "get",
            params
        })
    },
    /**
     * 生成非第一轮软件测试项
     * @returns
     */
    createHdemand(params = {}) {
        return request({
            url: `/generateHSM/create/hdemand`,
            method: "get",
            params
        })
    },
    /**
     * 生成非回归测试用例概述那张表
     * @returns
     */
    createCaseListDesc(params = {}) {
        return request({
            url: `/generateHSM/create/caseListDesc`,
            method: "get",
            params
        })
    },
    /**
     * 生成非第一轮回归测试用例
     * @returns
     */
    createCaseList(params = {}) {
        return request({
            url: `/generateHSM/create/caseList`,
            method: "get",
            params
        })
    },
    /**
     * 生成非第一轮的追踪
     * @returns
     */
    createTrack(params = {}) {
        return request({
            url: `/generateHSM/create/track`,
            method: "get",
            params
        })
    },
    /**
     * 删除output/hsm中的所有文件，例如：防止没有第三轮，出现第三轮
     * @returns
     */
    deleteHSMFiles(params = {}) {
        return request({
            url: `/generateHSM/create/deleteHSMDocument`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-静态软件项
     */
    createHsmStaticSoft(params = {}) {
        return request({
            url: `/generateHSM/create/static_soft`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-静态硬件和固件项
     */
    createHsmStaticHard(params = {}) {
        return request({
            url: `/generateHSM/create/static_hard`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-动态软件项
     */
    createHsmDynamicSoft(params = {}) {
        return request({
            url: `/generateHSM/create/dynamic_soft`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-动态硬件项
     */
    createHsmDynamicHard(params = {}) {
        return request({
            url: `/generateHSM/create/dynamic_hard`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-测试数据
     */
    createHsmTestData(params = {}) {
        return request({
            url: `/generateHSM/create/test_data`,
            method: "get",
            params
        })
    }
}
