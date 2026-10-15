import { request } from "@/api/request"
export default {
    /**
     * 如果缺少部分文件给与提示
     * @returns 根据output_dir生成最终大纲文档
     */
    createDagangSeiTai(data = {}) {
        return request({
            url: `/create/dgDocument`,
            method: "post",
            data,
        })
    },
    /**
     * 如果缺少部分文件给与提示
     * @returns 根据output_dir以及output_dir/sm中文档生成测试说明
     */
    createShuomingSeiTai(data = {}) {
        return request({
            url: `/create/smDocument`,
            method: "post",
            data,
        })
    },
    /**
     * TODO:如果缺少部分文件给与提示
     * @returns 根据output_dir以及output_dir/JL中文档生成测试记录
     */
    createJiluSeiTai(data = {}) {
        return request({
            url: `/create/jlDocument`,
            method: "post",
            data,
        })
    },
    /**
     * TODO:如果缺少部分文件给与提示
     * @returns 根据output_dir以及output_dir/hsm中文档生成回归测试说明（特殊多个文件）
     */
    createHsmDocument(data = {}) {
        return request({
            url: `/create/hsmDocument`,
            method: "post",
            data,
        })
    },
    /**
     * TODO:如果缺少部分文件给与提示
     * @returns 根据output_dir以及output_dir/hjl中文档生成回归测试记录（特殊多个文件）
     */
    createHjlDocument(data = {}) {
        return request({
            url: `/create/hjlDocument`,
            method: "post",
            data,
        })
    },
    /**
     * TODO:生成最终问题单
     * @returns 返回是否正确生成问题单
     */
    createWtdDocument(data = {}) {
        return request({
            url: `/create/wtdDocument`,
            method: "post",
            data,
        })
    },
    /**
     * TODO:如果缺少部分文件给与提示
     * @returns 根据output_dir以及output_dir/bg中文档生成测评报告
     */
    createBgDocument(data = {}) {
        return request({
            url: `/create/bgDocument`,
            method: "post",
            data,
        })
    },
    /**
     * 请求：取消生成文档标志设置为True
     * @returns 返回是否取消成功
     */
    cancel(params = {}) {
        return request({
            url: `/create/cancel`,
            method: "get",
            params
        })
    }
}
