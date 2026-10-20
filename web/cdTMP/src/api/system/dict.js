import { request } from "@/api/request"
import { clearDictCache, getCachedDict } from "@/utils/dictCache"

// 字典/字典项变更后清空短缓存，下次读取拿到最新数据
const invalidateCache = (promise) => promise.finally(() => clearDictCache())

export default {
    /**
     * 传入字段的code，返回所属code信息
     * @returns 返回所属code信息
     */
    getDictByCode(params = {}) {
        // 仅按 code 查询时走短缓存；带其它条件（管理页筛选）时保持直连
        if (Object.keys(params).length === 1 && params.code) {
            return getCachedDict(params.code, () =>
                request({
                    url: `system/dataDict/list`,
                    method: "get",
                    params
                })
            )
        }
        return request({
            url: `system/dataDict/list`,
            method: "get",
            params
        })
    },
    /**
     * 请求dict全部数据
     * @returns dict全部数据
     */
    getDictIndex(params = {}) {
        return request({
            url: `system/dataDict/index`,
            method: "get",
            params
        })
    },
    /**
     * 切换字典状态
     * @returns 切换成功或失败标志
     */
    changeStatus(data = {}) {
        return invalidateCache(request({
            url: "system/dataDict/changeStatus",
            method: "put",
            data
        }))
    },
    /**
     * 获取字典详情列表
     * @returns 字典详情列表
     */
    getDictItemAll(params = {}) {
        return request({
            url: "system/dataDict/dictItemAll",
            method: "get",
            params
        })
    },
    /**
     * 数字运算操作
     * @returns
     */
    numberOperation(data = {}) {
        return invalidateCache(request({
            url: "system/dataDict/numberOperation",
            method: "put",
            data
        }))
    },
    /**
     * 切换字典item状态
     * @returns 切换成功或失败标志
     */
    changeItemStatus(data = {}) {
        return invalidateCache(request({
            url: "system/dataDict/changeItemStatus",
            method: "put",
            data
        }))
    },
    /**
     * 添加dictItem数据
     * @returns
     */
    saveDictItem(data = {}) {
        return invalidateCache(request({
            url: "system/dataDict/saveitem",
            method: "post",
            data
        }))
    },
    /**
     * 更新dictItem数据
     * @returns
     */
    updateDictItemData(id, data = {}) {
        return invalidateCache(request({
            url: "system/dataDict/update/" + id,
            method: "put",
            data
        }))
    },
    /**
     * 真实删除
     * @returns
     */
    realDeleteItem(data) {
        return invalidateCache(request({
            url: "system/dictType/realDeleteItem",
            method: "delete",
            data
        }))
    },
    /**
     * 快速新增字典项（非字典）
     * @returns 成功或失败
     */
    createDictItemFast(data = {}) {
        return invalidateCache(request({
            url: "system/dataDict/fastSave",
            method: "post",
            data
        }))
    },
    /**
     * 快速新增依据标准字典项（非字典）
     * @returns 成功或失败
     */
    createDictItemStdFast(data = {}) {
        return invalidateCache(request({
            url: "system/dataDict/saveStdItem",
            method: "post",
            data
        }))
    }
}
