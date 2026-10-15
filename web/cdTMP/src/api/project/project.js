import { request } from "@/api/request"
// 该api集合主要是tree动态加载项
export default {
    /**
     * 根据项目名确定round初始节点
     * @returns round初始节点
     */
    getRoundInfo(projectId) {
        return request({
            url: `project/getRoundInfo/${projectId}`,
            method: "get"
        })
    },
    /**
     * 根据项目名、树节点等级和key查找被测件
     * @returns 被测件
     */
    getDutInfo(projectId, key, level) {
        return request({
            url: `project/getDutInfo`,
            method: "get",
            params: {
                projectId: projectId,
                key: key,
                level: level
            }
        })
    },
    /**
     * 根据项目名、树节点等级和key查找测试项
     * @returns 设计需求树状节点信息
     */
    getDemandInfo(projectId, key, level) {
        return request({
            url: `project/getDesignDemandInfo`,
            method: "get",
            params: {
                projectId: projectId,
                key: key,
                level: level
            }
        })
    },
    /**
     * 根据项目id和轮次key
     * @returns 测试项级联数据
     */
    getRoundRelatedDemand(id, round) {
        return request({
            url: `project/getRelatedTestDemand`,
            method: "get",
            params: {
                id,
                round
            }
        })
    },
    /**
     * 根据项目名、树节点等级和key查找测试项
     * @returns 返回测试项testDemand
     */
    getTestInfo(projectId, key, level) {
        return request({
            url: `project/getTestdemandInfo`,
            method: "get",
            params: {
                projectId: projectId,
                key: key,
                level: level
            }
        })
    },
    /**
     * 根据项目名、树节点等级和key查找测试用例
     * @returns 返回测试用例
     */
    getCaseInfo(projectId, key, level) {
        return request({
            url: `project/getCaseInfo`,
            method: "get",
            params: {
                projectId: projectId,
                key: key,
                level: level
            }
        })
    },
    /**
     * 根据项目id查询项目->看板的所有信息
     * @returns 返回看板所有信息
     */
    getBoardInfo(projectId) {
        return request({
            url: `/testmanage/project/board`,
            method: "get",
            params: {
                id: projectId
            }
        })
    },
    /**
     * 根据项目id查询项目->查看全部时间
     * @returns 返回看板所有信息
     */
    getDocumentTimeShow(projectId) {
        return request({
            url: `/testmanage/project/document_time_show`,
            method: "get",
            params: {
                id: projectId
            }
        })
    },
    /**
     * 新增或者修改软件概述
     * @returns null
     */
    postSoftSummary(data) {
        return request({
            url: "/testmanage/project/soft_summary/",
            method: "post",
            data: data
        })
    },
    /**
     * 新增或者修改动态环境描述
     * @returns null
     */
    postDynamicDescription(data) {
        return request({
            url: "/testmanage/project/dynamic_description/",
            method: "post",
            data: data
        })
    },
    /**
     * 获取项目的软件概述
     * @returns 返回软件概述数据
     */
    getSoftSummary(id) {
        return request({
            url: "/testmanage/project/get_soft_summary/",
            method: "get",
            params: { id: id }
        })
    },
    /**
     * 获取动态环境描述
     * @returns 返回动态环境描述结构化数据
     */
    getDynamicDescription(id) {
        return request({
            url: "/testmanage/project/dynamic_des/",
            method: "get",
            params: { id: id }
        })
    },
    /**
     * 提交修改或新增软件接口图
     * @returns 返回新增或修改是否成功
     */
    postInterfaceImage(id, data) {
        return request({
            url: "/testmanage/project/interface_image/",
            method: "post",
            params: { id: id },
            data
        })
    },
    /**
     * 提交修改或新增软件接口图
     * @returns 返回新增或修改是否成功
     */
    getInterfaceImage(id) {
        return request({
            url: "/testmanage/project/get_interface_image/",
            method: "get",
            params: { id: id }
        })
    },
    /**
     * 获取静态软件项、静态硬件项、动态软件项、动态硬件项的数据
     * @returns 返回数据
     */
    getStaticDynamicItems(id, category) {
        return request({
            url: "/testmanage/project/get_static_dynamic_items/",
            method: "get",
            params: { id: id, category }
        })
    },
    /**
     * 获取环境差异性分析数据
     * @returns 返回数据
     */
    getEnvAnalysis(id) {
        return request({
            url: "/testmanage/project/get_env_analysis/",
            method: "get",
            params: { id: id }
        })
    },
    /**
     * 提交环境差异性数据
     * @returns null
     */
    postEnvAnalysis(data) {
        return request({
            url: "/testmanage/project/post_env_analysis/",
            method: "post",
            data
        })
    },
    /**
     * 提交修改或新增静态软件项、静态硬件项、动态软件项、动态硬件项
     * @returns null
     */
    postStaticDynamicItems(data) {
        return request({
            url: "/testmanage/project/post_static_dynamic_item/",
            method: "post",
            data
        })
    },
    /**
     * 获取所有状态
     * @returns 返回是否填写软件概述等等是否已经填写
     */
    getAllStatus(id) {
        return request({
            url: "/testmanage/project/project_info_status/",
            method: "get",
            params: { id: id }
        })
    }
}
