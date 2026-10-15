import { request } from "@/api/request"
export default {
    /**
     * 根据项目id、round、designDemand信息，请求详细testDemand数据
     * @returns 测试需求数据
     */
    getTestDemandList(params = {}) {
        return request({
            url: `project/getTestDemandList`,
            method: "get",
            params
        })
    },
    /**
     * 获取单个测试项信息
     * @returns 单个测试项信息
     */
    getTestDemandOne(params = {}) {
        return request({
            url: `project/getTestDemandOne`,
            method: "get",
            params
        })
    },
    /**
     * 查询单个测试项-id
     * @returns 单个测试项数据
     */
    getDemandOneById(id) {
        return request({
            url: `project/getTestDemandOneById?id=${id}`,
            method: "get"
        })
    },
    /**
     * 添加测试项
     * @returns
     */
    save(params = {}) {
        return request({
            url: "/project/testDemand/save",
            method: "post",
            data: params
        })
    },
    /**
     * 批量新增添加测试项
     * @returns
     */
    batchSave(data = {}) {
        return request({
            url: "/project/testDemand/multi_save",
            method: "post",
            data
        })
    },
    /**
     * 更新dut
     * @returns
     */
    update(id, data = {}) {
        return request({
            url: "/project/testDemand/update/" + id,
            method: "put",
            data
        })
    },
    /**
     * 删除dut
     * @returns
     */
    delete(data) {
        return request({
            url: "/project/testDemand/delete",
            method: "delete",
            data
        })
    },
    /**
     * 请求一个项目的所有测试需求（即测试项）
     * @returns
     */
    getRelatedTestDemand(params = {}) {
        return request({
            url: "/project/testDemand/getRelatedTestDemand",
            method: "get",
            params
        })
    },
    /**
     * 设计需求关联测试需求（测试项）的接口请求
     * @returns
     */
    solveRelatedTestDemand(params = {}) {
        return request({
            url: "/project/testDemand/solveRelatedTestDemand",
            method: "post",
            data: params
        })
    },
    /**
     * 根据当前设计需求design，找出已关联非自己的测试项
     * @returns
     */
    getExistRelatedTestDemand(params = {}) {
        return request({
            url: "/project/testDemand/getExistRelatedTestDemand",
            method: "post",
            data: params
        })
    },
    /**
     * 复制demand到指定design下面
     * @returns 复制是否成功
     */
    copyToDesign(params = {}) {
        return request({
            url: "/project/testDemand/copy_to_design",
            method: "post",
            data: params
        })
    },
    /**
     * 提交选择的行、列，被替换内容，替换内容，请求后端替换
     * @returns
     */
    replace(data) {
        return request({
            url: "/project/testDemand/replace/",
            method: "post",
            data
        })
    },
    /**
     * 选择行后，批量修改“优先级”
     * @returns
     */
    priorityReplace(data = { selectRows: [], priority: "" }) {
        return request({
            url: "/project/testDemand/priorityReplace/",
            method: "post",
            data
        })
    }
}
