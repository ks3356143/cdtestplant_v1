/**
 * 接口：文档片段查询条件
 */
export interface IFragSearchCondition {
    name?: string
    is_main?: boolean
    projectId?: string
}

/**
 * 接口：更新文档片段的对象
 */
export interface IFragUpdateObject extends IFragSearchCondition {
    field_seq?: string
}
