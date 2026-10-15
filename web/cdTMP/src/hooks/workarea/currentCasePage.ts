import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import caseApi from "@/api/project/case"
import { Message } from "@arco-design/web-vue"
/**
 * 用于在组件挂载时，根据route.key/project_id获取当前数据页面的case用例信息
 */
export default function () {
    // global
    const route = useRoute()
    // ref
    const tempCaseInfo = ref<any>(null)
    // 项目id和当前case的key
    const { id, key } = route.query
    const fetchCaseOneStatus = async () => {
        try {
            const res = await caseApi.getCaseOne({ key, projectId: id })
            tempCaseInfo.value = res.data
        } catch (err) {
            Message.error("获取用例信息失败，请检查服务器")
        }
    }
    // 在初次加载时更新状态，如何在用例更新后再次加载呢
    onMounted(() => {
        fetchCaseOneStatus()
    })
    // hook里面判断函数：判断是否该用例未执行或未通过
    const caseIsNotPassedOrNotExe = function (): boolean {
        if (tempCaseInfo.value) {
            const testSteps: any[] = tempCaseInfo.value.testStep
            if (testSteps.length > 0) {
                return testSteps.some((it) => it.passed === "2")
            }
            return false
        } else {
            return false
        }
    }
    return {
        tempCaseInfo,
        caseIsNotPassedOrNotExe,
        fetchCaseOneStatus
    }
}

// hook外面判断函数
export const caseIsPassed = function (caseInfo: any): boolean {
    if (caseInfo) {
        const testSteps: any[] = caseInfo.testStep
        if (testSteps.length > 0) {
            return testSteps.some((it) => it.passed === "2")
        }
        return false
    } else {
        return false
    }
}
