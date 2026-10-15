import { request } from "@/api/request"
export default {
    /**
     * 获取当前项目非第一轮有几轮测试
     */
    getHgRoundNumber(params: { id: number }) {
        return request({
            url: `/createfragment/get_round_exit`,
            method: "get",
            params
        })
    }
}
