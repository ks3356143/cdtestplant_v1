/**
 * 接口：从后端请求关联的case信息类型
 */
export interface IRelatedCaseItem {
    id: number
    case: string
    demand: string
    demand_ident: string
    dut: string
    round: string
}

interface IDescription {
    label: string
    value: string
}
/**
 * CaseForm传过来数据类型
 */
export interface ICaseFormInData {
    id: number
    case: string
    showData: IDescription[]
}
