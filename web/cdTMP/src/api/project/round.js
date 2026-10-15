import { request } from "@/api/request"
export default {
    /**
     * 根据项目名、第{roundNumber}查询该轮次信息
     * @returns 返回一个轮次的信息
     */
    getOneRoundInfo(params = {}) {
        return request({
            url: "/project/getOneRoundInfo",
            method: "get",
            params
        })
    },
    /**
     * 添加轮次，并自动添加文档审查、代码审查、静态分析设计需求
     * @returns
     */
    save(project_id, params = {}) {
        return request({
            url: "project/round/save",
            method: "post",
            data: params,
            params: { project_id }
        })
    },
    /**
     * 更新轮次
     * @returns
     */
    update(id, data = {}) {
        return request({
            url: "project/round/update/" + id,
            method: "put",
            data
        })
    },
    /**
     * 删除轮次
     * @returns
     */
    delete(project_id, data = {}) {
        return request({
            url: "project/round/delete",
            method: "delete",
            data,
            params: { project_id }
        })
    },
    /**
     * 获取影响域分析
     * @returns 获取数据或code=25002
     */
    getInfluence(id, round_key) {
        return request({
            url: "project/round/get_influence",
            method: "get",
            params: { id, round_key }
        })
    },
    /**
     * 新增或修改影响域分析
     * @returns null
     */
    postInfluence(data) {
        return request({
            url: "project/round/create_influence",
            method: "post",
            data
        })
    },
    /**
     * 查看轮次的影响域分析是否有数据
     * @returns data: boolean
     */
    getInfluenceStatus(id, round_key) {
        return request({
            url: "project/round/get_status_influence",
            method: "get",
            params: { id, round_key }
        })
    }
}
