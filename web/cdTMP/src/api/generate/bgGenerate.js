import { request } from "@/api/request"
export default {
    /**
     * 生成技术依据文件
     * @returns
     */
    createBgTechYiju(params = {}) {
        return request({
            url: `/generateBG/create/techyiju`,
            method: "get",
            params
        })
    },
    /**
     * 生成测评时间和地点
     * @returns
     */
    createBgTimeaddress(params = {}) {
        return request({
            url: `/generateBG/create/timeaddress`,
            method: "get",
            params
        })
    },
    /**
     * 在报告生成多个版本被测软件基本信息
     * @returns
     */
    createBgBaseInformation(params = {}) {
        return request({
            url: `/generateBG/create/baseInformation`,
            method: "get",
            params
        })
    },
    /**
     * 生成测评完成情况
     * @returns
     */
    createBgCompletionstatus(params = {}) {
        return request({
            url: `/generateBG/create/completionstatus`,
            method: "get",
            params
        })
    },
    /**
     * 生成综述
     * @returns
     */
    createBgSummary(params = {}) {
        return request({
            url: `/generateBG/create/summary`,
            method: "get",
            params
        })
    },
    /**
     * 生成测试内容和结果[报告非常关键的一环-大模块]
     * @returns
     */
    createBgContentandresults1(params = {}) {
        return request({
            url: `/generateBG/create/contentandresults_1`,
            method: "get",
            params
        })
    },
    /**
     * 查询除第一轮以外，生成其他轮次测试内容和结果
     * @returns
     */
    createBgContentandresults2(params = {}) {
        return request({
            url: `/generateBG/create/contentandresults_2`,
            method: "get",
            params
        })
    },
    /**
     * 测试有效性充分性说明
     * @returns
     */
    createBgEffectAndAdquacy(params = {}) {
        return request({
            url: `/generateBG/create/effect_and_adquacy`,
            method: "get",
            params
        })
    },
    /**
     * 需求指标符合性情况
     * @returns
     */
    createBgDemandEffective(params = {}) {
        return request({
            url: `/generateBG/create/demand_effective`,
            method: "get",
            params
        })
    },
    /**
     * 软件质量评价
     * @returns
     */
    createBgQualityEvaluate(params = {}) {
        return request({
            url: `/generateBG/create/quality_evaluate`,
            method: "get",
            params
        })
    },
    /**
     * 软件总体结论
     * @returns
     */
    createBgEntire(params = {}) {
        return request({
            url: `/generateBG/create/entire`,
            method: "get",
            params
        })
    },
    /**
     * 研总需求追踪 - 注意生成每个轮次的追踪 # TODO：优先完成回归测试说明文档
     * @returns
     */
    createBgYzxqTrack(params = {}) {
        return request({
            url: `/generateBG/create/yzxq_track`,
            method: "get",
            params
        })
    },
    /**
     * 生成问题汇总表
     * @returns
     */
    createBgProblemsSummary(params = {}) {
        return request({
            url: `/generateBG/create/problems_summary`,
            method: "get",
            params
        })
    },
    /**
     * 生成-软件问题统计-2025年4月27日新增
     * @returns
     */
    createProblemStatistics(params = {}) {
        return request({
            url: `/generateBG/create/problem_statistics`,
            method: "get",
            params
        })
    },
    /**
     * 生成摸底清单-依据测试项
     * @returns
     */
    createBgModiList(params = {}) {
        return request({
            url: `/generateBG/create/modi_list`,
            method: "get",
            params
        })
    },
    /**
     * 删除output/bg中所有文件，防止之前数据干扰
     * @returns
     */
    deleteBGFiles(params = {}) {
        return request({
            url: `/generateBG/create/deleteBGDocument`,
            method: "get",
            params
        })
    }
}
