<template>
    <div class="ma-content-block lg:flex justify-between p-4">
        <div class="lg:w-full w-full lg:ml-4 mt-5 lg:mt-0">
            <a-spin :loading="loading" tip="正在加载中，请稍等...">
                <template #icon>
                    <icon-sync />
                </template>
                <problemDescription :data="data"></problemDescription>
            </a-spin>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue"
import problemDescription from "./cpns/problemDescription.vue"
import { useRoute } from "vue-router"
import singleProblemApi from "@/api/project/singleProblem"
import { Message } from "@arco-design/web-vue"
const route = useRoute()
const data = ref([])
const loading = ref(true)
// key 可能缺失（刷新/直链），统一解析一次并兜底，避免 setup 阶段抛错
const keyParts = String(route.query.key || "").split("-")
const roundNumber = keyParts[0]
const dutNumber = keyParts[1]
const designDemandNumber = keyParts[2]
const testDemandNumber = keyParts[3]
const caseNumber = keyParts[4]
const problemNumber = keyParts[5]
// 请求展示problem数据函数
const fetchProblemData = async (
    params = {
        projectId: route.query.id,
        round: roundNumber,
        dut: dutNumber,
        designDemand: designDemandNumber,
        testDemand: testDemandNumber,
        case: caseNumber,
        problem: problemNumber
    }
) => {
    loading.value = true
    try {
        const problemData = await singleProblemApi.getSingleProblem(params)
        data.value = problemData.data // 是个对象
    } catch (e) {
        Message.error("请求失败，请检测网络")
    } finally {
        loading.value = false
    }
}
fetchProblemData()

defineOptions({
    name: "problem"
})
</script>

<style lang="less" scoped></style>
