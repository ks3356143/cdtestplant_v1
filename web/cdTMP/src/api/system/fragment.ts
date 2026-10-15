import { request } from "@/api/request"
import { IFragSearchCondition, IFragUpdateObject } from "./types/fragmentTypes"
export class FragApi {
    /**
     * 根据参数获取文档片段
     * @returns 文档片段数组
     */
    static getFragList(params: IFragSearchCondition = {}) {
        return request({
            url: "system/userField/getFragment",
            method: "get",
            params
        })
    }
    /**
     * 根据用户填写新增文档片段
     * @returns 新增是否成功
     */
    static add(data: IFragUpdateObject) {
        return request({
            url: "system/userField/add",
            method: "post",
            data
        })
    }
    /**
     * 根据fragment的对象更新数据库
     * @returns 是否更新成功
     */
    static update(id: any, data: IFragUpdateObject) {
        return request({
            url: "system/userField/update/" + id,
            method: "put",
            data
        })
    }
    /**
     * 根据id删除fragment
     * @returns 返回被删除的id或错误消息
     */
    static delete(data) {
        return request({
            url: "system/userField/delete",
            method: "delete",
            data
        })
    }
}
