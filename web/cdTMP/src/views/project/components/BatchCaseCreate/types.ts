export interface CaseUserType {
    parent_key: string // 关键：给后端一个测试项的key
    name: string
    initialization?: string // 软件正常启动，正常运行
    premise?: string // 软件正常启动，外部接口运行正常
    summarize?: string // 综述，取测试项？
    test_step: string // 给后端传字符串，后端解析
    // 后面是时序图
    sequence?: string // 时序图Base64-FPGA
}

export interface CasesSubmitType {
    project_id: number
    cases: CaseUserType[]
}
