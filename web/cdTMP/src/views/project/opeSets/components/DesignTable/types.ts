// 设计需求搜索字段
export interface ISearchForm {
    name: string
    demandType: string
    description: string
    ident: string
    chapter: string
}

// 测试项搜索字段
export interface ISearchFormDemand {
    ident: string
    name: string
    testContent: string
    testDesciption: string
    testType: string
}

// 用例搜索字段
export interface ISearchFormCase {
    
}

// 问题单搜索字段
export interface ISearchFormProblem {

}
