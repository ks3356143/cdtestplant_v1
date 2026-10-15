import { IDictData } from "@/utils/types/CommonType"

type BeiceTypeT = {
    [K in keyof IDictData<string>]: string
}

const beiceType: BeiceTypeT[] = [
    { label: "源代码", value: "SO" },
    { label: "设计说明", value: "SJ" },
    { label: "需求文档", value: "XQ" },
    { label: "通信协议", value: "XY" },
    { label: "研制总要求/技术协议/顶层任务书等", value: "YZ" }
]

export default beiceType
