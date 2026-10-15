import { request } from "@/api/request"

export default {
    /**
     * 请求缩略语列表
     * @returns 请求缩略语的数据
     */
    getlist(params = {}) {
        return request({
            url: `system/abbreviation/getlist`,
            method: "get",
            params
        })
    },
    /**
     * 添加缩略语数据
     * @returns 返回已添加的缩略语
     */
    save(data = {}) {
        return request({
            url: "system/abbreviation/save",
            method: "post",
            data
        })
    },
    /**
     * 更新缩略语
     * @returns
     */
    update(id, data = {}) {
        return request({
            url: "system/abbreviation/update/" + id,
            method: "put",
            data
        })
    },
    /**
     * 删除缩略语
     * @returns
     */
    delete(data) {
        return request({
            url: "system/abbreviation/delete",
            method: "delete",
            data
        })
    }
}
