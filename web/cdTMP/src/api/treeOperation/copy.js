import { request } from "@/api/request"
export default {
    /**
     * 传入用户选中的节点请求复制到第二轮
     * @returns 是否复制成功，并通知刷新节点树
     */
    copyCheckedNode(params = {}) {
        return request({
            url: `/treeOperation/copy`,
            method: "post",
            data: params
        })
    }
}
