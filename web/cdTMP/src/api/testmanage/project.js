import { request } from "@/api/request"
export default {
    /**
     * 获取项目列表信息
     * @returns {Array}
     */
    getPageList(params = {}) {
        return request({
            url: "testmanage/project/index",
            method: "get",
            params
        })
    },
    /**
     * 获取单个项目信息
     * @returns 单个项目信息
     */
    getProjectById(id) {
        return request({
            url: "testmanage/project/findOneById/" + id,
            method: "get"
        })
    },
    /**
     * 添加项目
     * @returns
     */
    save(params = {}) {
        return request({
            url: "testmanage/project/save",
            method: "post",
            data: params
        })
    },
    /**
     * 更新数据
     * @returns
     */
    update(id, data = {}) {
        return request({
            url: "testmanage/project/update/" + id,
            method: "put",
            data
        })
    },
    /**
     * 删除项目
     * @returns
     */
    delete(data) {
        return request({
            url: "testmanage/project/delete",
            method: "delete",
            data
        })
    }
}
