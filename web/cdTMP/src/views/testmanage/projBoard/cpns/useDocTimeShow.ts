import { ref, computed } from "vue"
import projectApi from "@/api/project/project"
import { PROJECT_ENDTIME_ERROR_CODE } from "@/config/backendErrorCodes"
export function useDocTimeShow(projectId: number, showError: Function) {
    const visible = ref<boolean>(false)
    const handleModalVisible = (): void => {
        visible.value = true
    }
    // 获取时间模块
    const timeTemp = ref<any[]>([])
    const getTimeByBackend = async () => {
        try {
            const res = await projectApi.getDocumentTimeShow(projectId)
            timeTemp.value = res.data
        } catch (e: any) {
            // 如果检测到项目时间错误，则处理一些东西
            if (e.data.flag === PROJECT_ENDTIME_ERROR_CODE) {
                showError()
            }
        }
    }
    getTimeByBackend()
    const timeList = computed(() => {
        timeTemp.value.forEach((item) => {
            // 遍历所有属性，对值格式进行处理
            Object.keys(item).forEach((key) => {
                if (Array.isArray(item[key])) {
                    item[key] = item[key].join("~")
                } else {
                    if (item[key].includes("年")) {
                        item[key] = item[key].replace("年", "").replace("月", "").replace("日", "")
                    }
                }
            })
        })
        return timeTemp.value
    })
    return {
        visible,
        handleModalVisible,
        timeList
    }
}
