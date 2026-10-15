import { ref, computed, type Ref } from "vue"
import testDemandApi from "@/api/project/testDemand"
import { Message } from "@arco-design/web-vue"
import { useRoute } from "vue-router"
/**
 * 关联测试项弹窗，并提供事件处理函数
 */
export default function useRalateDemand(projectId: Ref<string>) {
    // global
    const route = useRoute()
    const roundNumber = (route.query.key as string)!.split("-")[0]
    const dutNumber = (route.query.key as string)!.split("-")[1]
    const designDemandNumber = (route.query.key as string)!.split("-")[2]
    // refs
    const visible = ref(false) // 弹窗显示隐藏
    const relatedData: Ref<any[]> = ref([]) // 已关联数据
    const options = ref<any>([]) // 级联cascade组件options
    const cascaderLoading = ref(false) // 级联的加载圈
    const computedRelatedData = computed(() => {
        const labelResultList: any[] = []
        options.value.forEach((item: any) => {
            if (item.children) {
                item.children.forEach((child: any) => {
                    if (relatedData.value.includes(child.value)) {
                        labelResultList.push(child.label)
                    }
                })
            }
        })
        return labelResultList
    })
    // 点击关联测试项-button
    const handleOpenRelationCSX = async () => {
        // 请求接口获取数据
        cascaderLoading.value = true
        visible.value = true
        // 点击进入时清除关联
        relatedData.value = []
        const res = await testDemandApi.getRelatedTestDemand({ id: projectId.value, round: roundNumber })
        options.value = res.data
        // 找出本设计需求design对应已关联的测试项
        const res_exist = await testDemandApi.getExistRelatedTestDemand({
            project_id: projectId.value,
            roundNumber,
            dutNumber,
            designDemandNumber
        })
        relatedData.value = res_exist.data
        cascaderLoading.value = false
    }
    // 点击关联确定按钮
    const handleRelatedOk = async () => {
        // 获取级联数据
        const relationDestItemIds = relatedData.value
        if (relationDestItemIds.length > 0) {
            const res = await testDemandApi.solveRelatedTestDemand({
                data: relationDestItemIds,
                project_id: projectId.value,
                roundNumber,
                dutNumber,
                designDemandNumber
            })
            if (res.code == 200) {
                Message.success(res.message)
                return true
            }
        } else {
            const res = await testDemandApi.solveRelatedTestDemand({
                data: [],
                project_id: projectId.value,
                roundNumber,
                dutNumber,
                designDemandNumber
            })
            if (res.code == 200) {
                Message.success(res.message)
                return true
            }
        }
        return false
    }
    return {
        visible,
        relatedData,
        options,
        cascaderLoading,
        computedRelatedData,
        handleOpenRelationCSX,
        handleRelatedOk
    }
}
