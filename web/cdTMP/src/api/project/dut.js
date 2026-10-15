import { request } from "@/api/request"
import { head } from "lodash-es"

export default {
    /**
     * 根据项目id、round信息，请求dut
     * @returns dut数据
     */
    getDutList(params = {}) {
        return request({
            url: `/project/getDutList`,
            method: "get",
            params
        })
    },
    /**
     * 根据项目id、round信息，请求dut
     * @returns dut数据
     */
    getDutOne(params = {}) {
        return request({
            url: `/project/getDutOne`,
            method: "get",
            params
        })
    },
    /**
     * 查询单个设计需求-根据id
     * @returns 单个设计需求数据
     */
    getDutOneById(id) {
        return request({
            url: `project/getDutOneById?id=${id}`,
            method: "get"
        })
    },
    /**
     * 添加被测件
     * @returns
     */
    save(params = {}) {
        return request({
            url: "/project/dut/save",
            method: "post",
            data: params
        })
    },
    /**
     * 更新dut
     * @returns
     */
    update(id, data = {}) {
        return request({
            url: "/project/dut/update/" + id,
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
            url: "/project/dut/delete",
            method: "delete",
            data
        })
    },
    /**
     * 查询是否存在第一轮是否存在源代码dut
     * @returns {bool} 第一轮是否存在源代码dut
     */
    getSoExists(params = {}) {
        return request({
            url: "/project/dut/soExist",
            method: "get",
            params
        })
    },
    /**
     * 强制弹窗提交的第一轮源代码被测件-新增接口
     * @returns
     */
    createR1SoDut(params = {}) {
        return request({
            url: "/project/dut/createR1Sodut",
            method: "post",
            data: params
        })
    },
    /**
     * 请求打开dut.vue页面，查看当前dut的类型“XQ/XY/SO等”
     * @returns
     */
    getDutType(params = {}) {
        return request({
            url: "/project/dut/dut_type",
            method: "get",
            params
        })
    }
}
