export interface demandOneType {
    parent_key: string // 设计需求的key
    ident: string
    name: string
    priority: string
    adequacy: string
    testMethod?: string[] | string
    testType: string
    testDesciption?: string
    testContent: string
}

export interface demandBatchType {
    project_id: number
    demands: demandOneType[]
}
