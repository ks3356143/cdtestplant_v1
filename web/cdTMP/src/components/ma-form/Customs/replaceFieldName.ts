import { Message } from "@arco-design/web-vue"

// 注意该白名单仅支持替换“字符串”and“数组”，其他不行!
const replaceField = [
    "initialization", // 用例：初始化
    "name", // 各个form的名称
    "premise", // 用例：前提和约束
    "summarize", // 用例：综述
    "testStep", // 用例：步骤，数组包含{operation:"",expect:""}
    "testDesciption", // 测试项：测试项描述
    "testContent" // 测试项：子项
]

const handleSubmit = (record: { values: any; error: any }, parentForm: any, formData: any) => {
    if (record.error) return
    // 替换逻辑
    Object.keys(parentForm).forEach((fieldName) => {
        if (replaceField.includes(fieldName)) {
            // 如果存在白名单里面，在判断是文本还是数组
            const lineData = parentForm[fieldName]
            if (typeof lineData === "string") {
                // string则直接替换
                parentForm[fieldName] = parentForm[fieldName].replaceAll(
                    formData.value.originText,
                    formData.value.replaceText
                )
            } else if (Array.isArray(lineData)) {
                parentForm[fieldName].forEach(
                    (obj: { operation: string; expect: string; result: string; subName: string; subStep: string }) => {
                        // 用例：数组只能替换对象operation、expect、result
                        if (obj.operation) {
                            obj.operation = obj.operation.replaceAll(
                                formData.value.originText,
                                formData.value.replaceText
                            )
                        }
                        if (obj.expect) {
                            obj.expect = obj.expect.replaceAll(formData.value.originText, formData.value.replaceText)
                        }
                        if (obj.result) {
                            obj.result = obj.result.replaceAll(formData.value.originText, formData.value.replaceText)
                        }
                        // 测试项：嵌套两层
                        if (obj.subName) {
                            obj.subName = obj.subName.replaceAll(formData.value.originText, formData.value.replaceText)
                            if (obj.subStep && Array.isArray(obj.subStep)) {
                                obj.subStep.forEach((step) => {
                                    if (step.operation) {
                                        step.operation = step.operation.replaceAll(
                                            formData.value.originText,
                                            formData.value.replaceText
                                        )
                                    }
                                    if (step.expect) {
                                        step.expect = step.expect.replaceAll(
                                            formData.value.originText,
                                            formData.value.replaceText
                                        )
                                    }
                                })
                            }
                        }
                    }
                )
            } else {
                return
            }
        }
    })
    Message.success("替换成功")
}

export default handleSubmit
