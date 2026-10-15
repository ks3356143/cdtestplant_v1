import { CaseUserType } from "./types"

export const initCaseData: CaseUserType = {
    parent_key: "",
    name: "",
    initialization: "软件正常启动，正常运行",
    premise: "软件正常启动，外部接口运行正常",
    summarize: "", // 用例综述
    test_step: "", // 综合字符串
    // FPGA
    sequence: "" // 时序图
}

export const validationRules = {
    parent_key: [{ required: true, message: "必须选择归属需求" }],
    name: [{ required: true, message: "用例名称必填" }],
    initialization: [],
    premise: [],
    summarize: [],
    test_step: [{ required: true, message: "字符串录入信息必填" }],
    sequence: []
}
