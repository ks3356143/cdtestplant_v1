/**
 * 该文件是配合请求后端生成各文档的二段文档
 */
import { ref } from "vue"
import dgGenerateApi from "@/api/generate/dgGenerate"
import smGenerateApi from "@/api/generate/smGenerate"
import jlGenerateApi from "@/api/generate/jlGenerate"
import bgGenerateApi from "@/api/generate/bgGenerate"
import hsmGenerateApi from "@/api/generate/hsmGenerate"
import hjlGenerateApi from "@/api/generate/hjlGenerate"
import wtdGenerateApi from "@/api/generate/wtdGenerate"

const useGenerateSecond = function () {
    // refs
    const isGenerating = ref(false) // 在二级文档生成过程中禁用按钮点击
    // 用于显示是否正在加载（全部按钮各一个）
    const isDgLoading = ref(false)
    const isSmLoading = ref(false)
    const isBgLoading = ref(false)
    const isJlloading = ref(false)
    const ishsmLoading = ref(false)
    const ishjlLoading = ref(false)
    const isWtdLoading = ref(false)
    // events
    // 大纲生成二级文档
    const createDgItem = async (id: number) => {
        isGenerating.value = true
        isDgLoading.value = true
        await Promise.all([
            dgGenerateApi.createTestDemand({ id }), // 生成第一轮测试项
            dgGenerateApi.createYiju({ id }), // 生成依据文件
            dgGenerateApi.createTechYiju({ id }), // 技术依据文件
            dgGenerateApi.createContact({ id }), // 生成联系人和方式
            dgGenerateApi.createTimeaddress({ id }), // 生成测评时间和地点
            dgGenerateApi.createSoftComposition({ id }), // 生成测评对象-软件组成
            dgGenerateApi.createAdequacyEffectiveness({ id }), // 生成测试充分性（adequancy）和有效性（effectiveness）说明
            dgGenerateApi.createGroup({ id }), // 生成测评组织及分工
            dgGenerateApi.createGuarantee({ id }), // 生成测评保障
            dgGenerateApi.createAbbreviation({ id }), // 生成缩略语
            dgGenerateApi.createInterface({ id }), // 生成-被测软件接口
            dgGenerateApi.createBaseInformation({ id }), // 生成-被测软件基本信息
            dgGenerateApi.createLevelAndType({ id }), // 生成-测试级别和测试类型 -【修改】
            dgGenerateApi.createStrategy({ id }), // 生成-测试策略 -【新增】
            dgGenerateApi.createYzComparison({ id }), // 生成-研总-测试项对照表
            dgGenerateApi.createXqComparison({ id }), // 生成-需求规格说明-测试项对照表
            dgGenerateApi.createFanXqComparison({ id }), // 生成-反向测试项-需求规格说明对照表
            dgGenerateApi.createCodeQuality({ id }), // 生成-代码质量度量分析表
            // 2025年4月29日新增 - 顶层技术文件
            dgGenerateApi.createTopFile({ id }), // 生成顶层技术文件
            // 新增拆分接口
            dgGenerateApi.createStaticEnvironment({ id }), // 生成-静态测试环境说明
            dgGenerateApi.createStaticSoft({ id, current_round: "0" }), // 生成-静态软件项
            dgGenerateApi.createStaticHard({ id, current_round: "0" }), // 生成-静态硬件和固件项
            dgGenerateApi.createDynamicEnv({ id }), // 生成-动态测试环境说明
            dgGenerateApi.createDynamicSoft({ id, current_round: "0" }), // 生成-动态软件项
            dgGenerateApi.createDynamicHard({ id, current_round: "0" }), // 生成-动态硬件和固件项
            dgGenerateApi.createTestData({ id, current_round: "0" }), // 生成-测评数据
            dgGenerateApi.createEnvDiff({ id }), // 生成-环境差异性分析
            // 2025年4月21日新增
            dgGenerateApi.createIndicates({ id }) // 生成主要功能和性能指标（包括摸底）
        ]).finally(() => {
            isGenerating.value = false
            isDgLoading.value = false
        })
    }
    // 说明生成二级文档
    const createSmItem = async (id: number) => {
        isGenerating.value = true
        isSmLoading.value = true
        await Promise.all([
            dgGenerateApi.createSoftComposition({ id }), // 生成测评对象 - 和大纲一样
            dgGenerateApi.createInterface({ id }), // 生成被测软件接口 - 和大纲重复 - 可能会删除
            dgGenerateApi.createBaseInformation({ id }), // 生成被测软件基本信息 - 和大纲重复 - 可能会删除
            dgGenerateApi.createYiju({ id }), // 生成标准类引用文档 - 和大纲重复 - 可能会删除
            smGenerateApi.createSMTechyiju({ id }), // 生成技术类引用文档列表 -> 在大纲基础上添加《测评大纲》
            // 拆分软硬件环境
            dgGenerateApi.createStaticEnvironment({ id }), // 生成-静态测试环境说明
            dgGenerateApi.createStaticSoft({ id, current_round: "0" }), // 生成-静态软件项
            dgGenerateApi.createStaticHard({ id, current_round: "0" }), // 生成-静态硬件和固件项
            dgGenerateApi.createDynamicEnv({ id }), // 生成-动态测试环境说明
            dgGenerateApi.createDynamicSoft({ id, current_round: "0" }), // 生成-动态软件项
            dgGenerateApi.createDynamicHard({ id, current_round: "0" }), // 生成-动态硬件和固件项
            dgGenerateApi.createTestData({ id, current_round: "0" }), // 生成-测评数据
            dgGenerateApi.createEnvDiff({ id }), // 生成-环境差异性分析
            // ~~~
            smGenerateApi.createSMCaseList({ id }), // 生成用例全
            smGenerateApi.createSMCaseBreifList({ id }), // 生成用例列表-那个表格
            smGenerateApi.createSMTrack({ id }) // 生成说明追踪
        ]).finally(() => {
            isGenerating.value = false
            isSmLoading.value = false
        })
    }
    // 记录生成二级文档
    const createJLItem = async (id: number) => {
        isGenerating.value = true
        isJlloading.value = true
        await Promise.all([
            // 生成-被测软件基本信息 - 和大纲一样
            dgGenerateApi.createBaseInformation({ id }),
            // 记录相关片段
            jlGenerateApi.createJLcaserecord({ id })
        ]).finally(() => {
            isGenerating.value = false
            isJlloading.value = false
        })
    }
    // 回归测试说明二级文档
    const createHsmItem = async (id: number) => {
        isGenerating.value = true
        ishsmLoading.value = true
        await Promise.all([
            hsmGenerateApi.deleteHSMFiles({ id }), // 先删除以前文件
            hsmGenerateApi.createBasicInfo({ id }),
            hsmGenerateApi.createDocSummary({ id }),
            hsmGenerateApi.createJstech({ id }),
            hsmGenerateApi.createChangePart({ id }),
            hsmGenerateApi.createHdemand({ id }),
            hsmGenerateApi.createCaseListDesc({ id }),
            hsmGenerateApi.createCaseList({ id }),
            hsmGenerateApi.createTrack({ id }),
            // 拆分大纲软硬件环境-大纲内容
            dgGenerateApi.createSoftComposition({ id }), // 生成测评对象-软件组成
            dgGenerateApi.createYiju({ id }), // 生成依据文件
            dgGenerateApi.createInterface({ id }), // 生成-被测软件接口 - 和大纲一样
            dgGenerateApi.createStaticEnvironment({ id }), // 生成-静态测试环境说明
            hsmGenerateApi.createHsmStaticSoft({ id, current_round: "not0" }), // 生成-静态软件项
            hsmGenerateApi.createHsmStaticHard({ id, current_round: "not0" }), // 生成-静态硬件和固件项
            dgGenerateApi.createDynamicEnv({ id }), // 生成-动态测试环境说明
            hsmGenerateApi.createHsmDynamicSoft({ id, current_round: "not0" }), // 生成-动态软件项
            hsmGenerateApi.createHsmDynamicHard({ id, current_round: "not0" }), // 生成-动态硬件和固件项
            hsmGenerateApi.createHsmTestData({ id, current_round: "not0" }), // 生成-测评数据
            dgGenerateApi.createEnvDiff({ id }) // 生成-环境差异性分析
        ]).finally(() => {
            isGenerating.value = false
            ishsmLoading.value = false
        })
    }
    // 回归测试记录二级文档
    const createHjlItem = async (id: number) => {
        isGenerating.value = true
        ishjlLoading.value = true
        await Promise.all([
            hjlGenerateApi.deleteHJLFiles({ id }), // 先调用删除文件夹里面文件
            hjlGenerateApi.createBasicInfo({ id }),
            hjlGenerateApi.createCaseinfo({ id })
        ]).finally(() => {
            isGenerating.value = false
            ishjlLoading.value = false
        })
    }
    // 问题单二级文档
    const createWtdItem = async (id: number) => {
        isGenerating.value = true
        isWtdLoading.value = true
        await wtdGenerateApi.createWtdTable({ id }).finally(() => {
            isGenerating.value = false
            isWtdLoading.value = false
        })
    }
    // 报告生成二级文档
    const createBgItem = async (id: number) => {
        isGenerating.value = true
        isBgLoading.value = true
        await Promise.all([
            bgGenerateApi.deleteBGFiles({ id }), // 删除output/bg文件夹下文件
            bgGenerateApi.createBgTechYiju({ id }),
            bgGenerateApi.createBgTimeaddress({ id }),
            bgGenerateApi.createBgBaseInformation({ id }),
            bgGenerateApi.createBgCompletionstatus({ id }),
            bgGenerateApi.createBgSummary({ id }),
            bgGenerateApi.createBgContentandresults1({ id }),
            bgGenerateApi.createBgContentandresults2({ id }),
            bgGenerateApi.createBgEffectAndAdquacy({ id }),
            bgGenerateApi.createBgDemandEffective({ id }),
            bgGenerateApi.createBgQualityEvaluate({ id }),
            bgGenerateApi.createBgEntire({ id }),
            bgGenerateApi.createBgYzxqTrack({ id }),
            bgGenerateApi.createBgProblemsSummary({ id }),
            // 2025年4月27日新增：软件问题统计
            bgGenerateApi.createProblemStatistics({ id }), // 生成软件问题统计
            // 2025年4月28日新增：摸底清单
            bgGenerateApi.createBgModiList({ id }), // 生成摸底清单
            // 拆分软硬件环境-大纲内容
            dgGenerateApi.createSoftComposition({ id }), // 生成测评对象 - 大纲内容
            dgGenerateApi.createYiju({ id }), // 生成依据文件
            dgGenerateApi.createInterface({ id }), // 生成-被测软件接口 - 大纲内容
            dgGenerateApi.createAbbreviation({ id }), // 生成缩略语 - 大纲内容
            dgGenerateApi.createStaticEnvironment({ id }), // 生成-静态测试环境说明
            dgGenerateApi.createStaticSoft({ id, current_round: "last" }), // 生成-静态软件项
            dgGenerateApi.createStaticHard({ id, current_round: "last" }), // 生成-静态硬件和固件项
            dgGenerateApi.createDynamicEnv({ id }), // 生成-动态测试环境说明
            dgGenerateApi.createDynamicSoft({ id, current_round: "last" }), // 生成-动态软件项
            dgGenerateApi.createDynamicHard({ id, current_round: "last" }), // 生成-动态硬件和固件项
            dgGenerateApi.createTestData({ id, current_round: "last" }), // 生成-测评数据
            dgGenerateApi.createEnvDiff({ id }), // 生成-环境差异性分析
            // 2025年4月29日新增 - 顶层技术文件
            dgGenerateApi.createTopFile({ id }) // 生成顶层技术文件
        ]).finally(() => {
            isGenerating.value = false
            isBgLoading.value = false
        })
    }
    return {
        isGenerating,
        isDgLoading,
        isSmLoading,
        isBgLoading,
        isJlloading,
        ishsmLoading,
        ishjlLoading,
        isWtdLoading,
        createJLItem,
        createSmItem,
        createDgItem,
        createBgItem,
        createHsmItem,
        createHjlItem,
        createWtdItem
    }
}

export default useGenerateSecond
