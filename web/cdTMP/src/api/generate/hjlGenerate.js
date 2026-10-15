import { request } from "@/api/request"
export default {
    /**
     * 生成回归测试说明的被测软件基本信息
     * @returns
     */
    createBasicInfo(params = {}) {
        return request({
            url: `/generateHJL/create/basicInformation`,
            method: "get",
            params
        })
    },
    /**
     * 生成回归测试说明的用例信息
     * @returns
     */
    createCaseinfo(params = {}) {
        return request({
            url: `/generateHJL/create/caseinfo`,
            method: "get",
            params
        })
    },
    /**
     * 删除回归测试记录output/hjl里面的所有文件
     * @returns
     */
    deleteHJLFiles(params = {}) {
        return request({
            url: `/generateHJL/create/deleteHJLDocument`,
            method: "get",
            params
        })
    },
}
