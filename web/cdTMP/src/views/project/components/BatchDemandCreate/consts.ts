import { demandOneType } from "./type"

// 初始化数据
export const lineInitialData: demandOneType = {
    parent_key: "",
    ident: "",
    name: "",
    priority: "1",
    adequacy: "测试用例覆盖测试子项要求的全部内容。\a所有用例执行完毕，对于未执行的用例说明未执行原因。",
    testContent: "",
    testMethod: ["4"],
    testType: "4",
    testDesciption: ""
}

export const validationRules = {
    parent_key: [{ required: true, message: "必须选择归属需求" }],
    ident: [{ required: true, message: "标识不能为空" }],
    name: [{ required: true, message: "名称不能为空" }],
    priority: [],
    adequacy: [{ required: true, message: "充分性不能为空" }],
    testMethod: [],
    testType: [{ required: true, message: "请选择测试类型" }],
    testDesciption: [],
    testContent: [{ required: true, message: "测试子项不能为空" }]
}

export const priorityOptions = [
    { label: "高", value: "1" },
    { label: "中", value: "2" },
    { label: "低", value: "3" }
]
