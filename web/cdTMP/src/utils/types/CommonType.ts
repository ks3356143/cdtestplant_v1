/**
 * 接口：为MimeAdmin的dict远程数据设置的接口
 */
export interface IDictData<T> {
    label: T
    value: number
}

/**
 * 产品文件的类型
 */
export type DocumentType =
    | "测评大纲"
    | "测试说明"
    | "测试记录"
    | "回归测试说明"
    | "回归测试记录"
    | "问题单"
    | "测评报告"
