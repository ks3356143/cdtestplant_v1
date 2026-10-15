import { computed, ref } from "vue"
import Empty from "@/components/Empty/index.vue"
import MaInfo from "@/components/ma-info/index.vue"
import useDutColumn from "@/views/project/round/hooks/useColumn"
import useDesignColumn from "@/views/project/dut/hooks/useColumns"
import useDemandColumn from "@/views/project/design-demand/hooks/useColumns"
import tool from "@/utils/tool"
import { useRoute } from "vue-router"

export default function useKeyToMaInfo() {
    const route = useRoute()
    // 初始状态为空
    let maInfoDom = ref(<Empty></Empty>)
    // 3个列信息
    // ma-info变量
    const dutOriginColumns = useDutColumn(undefined)
    const dutColumns = computed(() => {
        // 去掉上传字段
        return dutOriginColumns.value.filter((it) => it.dataIndex !== "upload")
    })
    const designColumns = useDesignColumn(undefined)
    const demandColumns = useDemandColumn(undefined)
    // 如果是FPGA则测试项ma-info去掉“测试项描述列”
    const demandColumnsNew = computed(() => {
        if (tool.checkForCpuOrFPGA(route.query.plant_type)) {
            return demandColumns.value
        }
        return demandColumns.value.filter((item) => item.dataIndex !== "testDesciption")
    })

    // 函数：传入switch后的Promise以及是什么类型展示信息
    const fetchNodeDataAndSetMaInfo = async (resPromise: Promise<any>, nodeType: string) => {
        const res = await resPromise
        switch (nodeType) {
            case "dut":
                const dutInfo = res.data
                const dutInfoJudge = computed(() => {
                    if (dutInfo.type === "SO") {
                        // 计算注释率：注释行/总行数
                        dutInfo.comment_percent = (dutInfo.comment_lines / dutInfo.total_lines) * 100 + "%"
                    } else {
                        // 如果是非源代码被测件行数均填写：“不适用”
                        dutInfo.comment_lines = "不适用"
                        dutInfo.comment_percent = "不适用"
                        dutInfo.effective_lines = "不适用"
                        dutInfo.total_lines = "不适用"
                    }
                    return dutInfo
                })
                maInfoDom.value = <MaInfo columns={dutColumns.value} data={dutInfoJudge.value} tableLayout="auto"></MaInfo>
                break
            case "design":
                maInfoDom.value = <MaInfo columns={designColumns.value} data={res.data} tableLayout="auto"></MaInfo>
                break
            case "demand":
                maInfoDom.value = <MaInfo columns={demandColumnsNew.value} data={res.data} tableLayout="auto"></MaInfo>
                break
            default:
                break
        }
    }
    return { maInfoDom, fetchNodeDataAndSetMaInfo }
}
