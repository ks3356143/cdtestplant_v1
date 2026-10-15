import { request } from "@/api/request"

export default {
    /**
     * 根据项目id和文档类型获取文档片段名称
     * @returns 文档片段名称数组
     */
    getFragmentByDocumentType(params: { id: number; documentType: string }) {
        return request({
            url: `/createfragment/get_fragments`,
            method: "get",
            params
        })
    }
}
