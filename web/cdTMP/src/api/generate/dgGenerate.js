import { request } from "@/api/request"
export default {
    /**
     *
     * @returns 大纲测试项数据
     */
    createTestDemand(params = {}) {
        return request({
            url: `/generate/create/testdemand`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 大纲依据数据
     */
    createYiju(params = {}) {
        return request({
            url: `/generate/create/yiju`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 顶层技术依据文件
     */
    createTopFile(params = {}) {
        return request({
            url: `/generate/create/top_file`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成联系方式
     */
    createContact(params = {}) {
        return request({
            url: `/generate/create/contact`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成技术依据文件部分
     */
    createTechYiju(params = {}) {
        return request({
            url: `/generate/create/techyiju`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成测评大纲-测评时间和地点
     */
    createTimeaddress(params = {}) {
        return request({
            url: `/generate/create/timeaddress`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成测评大纲-测评对象的软件组成描述
     */
    createSoftComposition(params = {}) {
        return request({
            url: `/generate/create/softComposition`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成测评大纲-被测软件接口
     */
    createInterface(params = {}) {
        return request({
            url: `/generate/create/interface`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成测评大纲-被测软件基本信息
     */
    createBaseInformation(params = {}) {
        return request({
            url: `/generate/create/baseInformation`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-静态测试环境说明
     */
    createStaticEnvironment(params = {}) {
        return request({
            url: `/generate/create/static_env`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-静态软件项文档片段
     */
    createStaticSoft(params = {}) {
        return request({
            url: `/generate/create/static_soft`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-静态硬件和固件项
     */
    createStaticHard(params = {}) {
        return request({
            url: `/generate/create/static_hard`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-动态测试环境说明
     */
    createDynamicEnv(params = {}) {
        return request({
            url: `/generate/create/dynamic_env`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-动态软件项
     */
    createDynamicSoft(params = {}) {
        return request({
            url: `/generate/create/dynamic_soft`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-动态硬件项
     */
    createDynamicHard(params = {}) {
        return request({
            url: `/generate/create/dynamic_hard`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-测试数据
     */
    createTestData(params = {}) {
        return request({
            url: `/generate/create/test_data`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-环境差异性分析
     */
    createEnvDiff(params = {}) {
        return request({
            url: `/generate/create/env_diff`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成测评大纲-测试级别和测试类型
     */
    createLevelAndType(params = {}) {
        return request({
            url: `/generate/create/levelAndType`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成测评大纲-测试策略
     */
    createStrategy(params = {}) {
        return request({
            url: `/generate/create/strategy`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-测试内容充分性及测试方法有效性
     */
    createAdequacyEffectiveness(params = {}) {
        return request({
            url: `/generate/create/adequacy_effectiveness`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-测评组织及分工
     */
    createGroup(params = {}) {
        return request({
            url: `/generate/create/group`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-测评条件和保障
     */
    createGuarantee(params = {}) {
        return request({
            url: `/generate/create/guarantee`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-缩略语
     */
    createAbbreviation(params = {}) {
        return request({
            url: `/generate/create/abbreviation`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-研制总要求-测试项对比表
     */
    createYzComparison(params = {}) {
        return request({
            url: `/generate/create/yzComparison`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-需求规格说明追踪表
     */
    createXqComparison(params = {}) {
        return request({
            url: `/generate/create/xqComparison`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-反向测试项-需求规格说明追踪表
     */
    createFanXqComparison(params = {}) {
        return request({
            url: `/generate/create/fanXqComparison`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-代码质量度量分析表
     */
    createCodeQuality(params = {}) {
        return request({
            url: `/generate/create/codeQuality`,
            method: "get",
            params
        })
    },
    /**
     *
     * @returns 生成-代码质量度量分析表
     */
    createIndicates(params = {}) {
        return request({
            url: `/generate/create/indicators`,
            method: "get",
            params
        })
    }
}
