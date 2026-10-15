import { request } from "@/api/request"
export default {
    /**
     * 根据项目id、round、designDemand、testDemand信息，请求详细case数据
     * @returns 测试用例数据
     */
    getCaseList(params = {}) {
        return request({
            url: `project/getCaseList`,
            method: "get",
            params
        })
    },
    /**
     * 请求单个case信息
     * @params 传入case完整的key
     * @params 项目id
     */
    getCaseOne(params = {}) {
        return request({
            url: "/project/getCaseOne",
            method: "get",
            params
        })
    },
    /**
     * 查询单个测试项-id
     * @returns 单个测试项数据
     */
    getCaseOneById(id) {
        return request({
            url: `project/getCaseOneById?id=${id}`,
            method: "get"
        })
    },
    /**
     * 添加测试用例
     * @returns
     */
    save(params = {}) {
        return request({
            url: "/project/case/save",
            method: "post",
            data: params
        })
    },
    /**
     * 添加测试用例
     * @returns
     */
    batchSave(data = {}) {
        return request({
            url: "/project/case/multi_save",
            method: "post",
            data
        })
    },
    /**
     * 更新测试用例
     * @returns
     */
    update(id, data = {}) {
        return request({
            url: "/project/case/update/" + id,
            method: "put",
            data
        })
    },
    /**
     * 删除测试用例
     * @returns
     */
    delete(data) {
        return request({
            url: "/project/case/delete",
            method: "delete",
            data
        })
    },
    /**
     * 右键点击需求创建测试用例
     * @returns 成功或失败信息
     */
    createByDemand(params = {}) {
        return request({
            url: "/project/case/create_by_demand",
            method: "post",
            data: params
        })
    },
    /**
     * 拖拽大功能：拖拽测试用例到测试项节点，移动还是复制
     * @returns 返回case的key用于刷新树状图的数据
     */
    copyOrMoveCaseToDemand(params = {}) {
        return request({
            url: "/project/case/copy_or_move_to_demand",
            method: "get",
            params
        })
    },
    /**
     * 拖拽大功能：拖拽测试用例到用例节点（都是用例）,移动还是复制
     * @returns 返回case的key用于刷新树状图的数据
     */
    copyOrMoveCaseByCase(params = {}) {
        return request({
            url: "/project/case/copy_or_move_by_case",
            method: "get",
            params
        })
    },
    /**
     * 提交选择的行、列，被替换内容，替换内容，请求后端替换
     * @returns
     */
    replace(data) {
        return request({
            url: "/project/case/replace/",
            method: "post",
            data
        })
    },
    /**
     * 批量修改设计人员、执行人员、审核人员
     * @returns
     */
    personReplace(data = { selectRows: [], designPerson: "不替换", testPerson: "不替换", monitorPerson: "不替换" }) {
        return request({
            url: "/project/case/personReplace/",
            method: "post",
            data
        })
    },
    /**
     * 批量替换事件
     * @returns
     */
    exetimeReplace(data = { selectRows: [], exetime: [] }) {
        return request({
            url: "/project/case/timeReplace/",
            method: "post",
            data
        })
    },
    /**
     * 请求上一轮次，级联选择器的cases数据
     * @returns
     */
    getRelatedCases(id, round_key) {
        return request({
            url: "/project/case/getRelatedCase",
            method: "get",
            params: { id, round_key }
        })
    }
}
