import { request } from "@/api/request"

export default {
    /**
     * 更新用户信息
     * @returns
     */
    updateInfo(data = {}) {
        return request({
            url: "system/user/updateInfo",
            method: "post",
            data
        })
    },
    /**
     * 用户修改密码
     * @returns
     */
    modifyPassword(data = {}) {
        return request({
            url: "system/user/modifyPassword",
            method: "post",
            data
        })
    },

    /**
     * 获取用户信息列表
     * @returns
     */
    getPageList(params = {}) {
        return request({
            url: "system/user/index",
            method: "get",
            params
        })
    },
    // ~~~~~~大表页面使用~~~~~~
    /**
     * 获取用户信息列表
     * @returns
     */
    getProjectList(project_id) {
        return request({
            url: "system/user/list",
            method: "get",
            params: { project_id }
        })
    },
    // ~~~~~~usermanage~~~~~~页面的
    /**
     * 添加用户
     * @returns
     */
    save(params = {}) {
        return request({
            url: "system/user/save",
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
            url: "system/user/update/" + id,
            method: "put",
            data
        })
    },
    /**
     * 移到回收站
     * @returns
     */
    delete(data) {
        return request({
            url: "system/user/delete",
            method: "delete",
            data
        })
    },
    /**
     * 真实删除
     * @returns
     */
    realDeletes(data) {
        return request({
            url: "system/user/realDelete",
            method: "delete",
            data
        })
    },
    /**
     * 恢复数据
     * @returns
     */
    recoverys(data) {
        return request({
            url: "system/user/recovery",
            method: "put",
            data
        })
    },
    /**
     * 请求所有user信息
     * @returns
     */
    getUserDict(params = {}) {
        return request({
            url: "system/user/dict",
            method: "get",
            params
        })
    },
    /**
     * 加载LDAP的用户数据
     * @returns
     */
    loadLDAPUsers(params = {}) {
        return request({
            url: "system/user/ldap",
            method: "get",
            params
        })
    },
    /**
     * 获取用户分组group的id和层级信息
     * @returns
     */
    getGroupList(params = {}) {
        return request({
            url: "system/user/group/list",
            method: "get",
            params
        })
    },
    /**
     * 改变用户启用/停用状态
     * @returns
     */
    changeUserStatus(params = {}) {
        return request({
            url: "system/user/change_status",
            method: "get",
            params
        })
    }
}
