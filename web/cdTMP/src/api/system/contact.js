import { request } from "@/api/request"

export default {
    /**
     * 请求委托方、研制方、测试方全部数据
     * @returns 请求委托方、研制方、测试方全部数据
     */
    getlist(params = {}) {
        return request({
            url: `system/contact/getlist`,
            method: "get",
            params
        })
    },
    /**
     * 添加委托方、研制方、测试方数据
     * @returns 返回已添加的contact数据
     */
    save(data = {}) {
        return request({
            url: "system/contact/save",
            method: "post",
            data
        })
    },
    /**
     * 更新委托方、研制方、测试方数据
     * @returns
     */
    update(id, data = {}) {
        return request({
            url: "system/contact/update/" + id,
            method: "put",
            data
        })
    },
    /**
     * 删除委托方、研制方、测试方数据
     * @returns
     */
    delete(data) {
        return request({
            url: "system/contact/delete",
            method: "delete",
            data
        })
    }
}
