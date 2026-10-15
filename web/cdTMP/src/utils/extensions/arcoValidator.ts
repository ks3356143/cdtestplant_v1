/**
 * 表单验证器：验证输入trim空格后是否为空，例如项目标识必须不能为空格
 */
export function validateBlank(value: string | undefined, callback: (error?: string) => void): void {
    const val = value?.trim()
    if (val === "") {
        callback("注意标识不能为空格")
    }
}

/**
 * window文件名称检查器，不允许有字符/\:*?"<>|
 */
export function validateWindowFileNameInput(value: string | undefined, callback: (error?: string) => void): void {
    const val = value?.trim()
    const reg = /[\\\/\:\*\?\"\<\>\|]/
    const regPatchRes = val?.search(reg)
    regPatchRes === -1 ? undefined : callback('注意标识名称不能有 -> /\\:*?"<>|')
}
