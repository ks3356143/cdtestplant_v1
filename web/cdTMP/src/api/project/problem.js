import { request } from "@/api/request"

export default {
    /**
     * 根据项目id、round、designDemand、testDemand、case信息，请求问题单列表
     * @returns 属于case的问题单列表
     */
    getProblemList(params = {}) {
        return request({
            url: `project/getProblemList`,
            method: "get",
            params
        })
    },
    /**
     * 添加问题单
     * @returns
     */
    save(params = {}) {
        return request({
            url: "/project/problem/save",
            method: "post",
            data: params
        })
    },
    /**
     * 更新问题单
     * @returns
     */
    update(id, data = {}) {
        return request({
            url: "/project/problem/update/" + id,
            method: "put",
            data
        })
    },
    /**
     * 删除问题单
     * @returns
     */
    delete(data) {
        return request({
            url: "/project/problem/delete",
            method: "delete",
            data
        })
    },
    /* 预览问题单/关联问题单的请求table接口 */
    /**
     * 关联问题单界面-查询所有的问题单
     * @returns 一个项目的所有问题单（分页）
     */
    searchAllProblem(params = {}) {
        return request({
            url: "/project/problem/searchAllProblem",
            method: "get",
            params
        })
    },
    /**
     * 单独去掉dut、designDemand、test等等的更新请求
     * @returns 去掉各种id只留projectId请求后端的接口
     */
    modalupdate(id, data = {}) {
        return request({
            url: "/project/problem/modalupdate/" + id,
            method: "put",
            data
        })
    },
    /**
     * 1.case信息 2.问题单的id 3.现在的值是什么
     * @returns 让case关联问题单
     */
    relateProblem(params = {}) {
        return request({
            url: "/project/problem/relateProblem",
            method: "get",
            params
        })
    }
}
