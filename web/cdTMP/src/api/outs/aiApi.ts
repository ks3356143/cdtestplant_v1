import { request } from "@/api/request"

interface DataRowType {
    question: string
    streaming: boolean
    model_name: string
    user_focus_points: string
    project_type: "cpu" | "fpga" | "other"
}

interface DataType {
    question: string
    project_type: "cpu" | "fpga" | "other"
}

export default {
    /**
     * 改为请求测试平台后端然后请求大模型方式
     */
    getAiTestItemBackend(data: DataType) {
        return request({
            url: "/local_doc_qa/testing_item",
            method: "post",
            timeout: 120000,
            data
        })
    }
}
