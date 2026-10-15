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
const roundNumber = route.query.key.split("-")[0]
const dutNumber = route.query.key.split("-")[1]
const designDemandNumber = route.query.key.split("-")[2]
const testDemandNumber = route.query.key.split("-")[3]
const caseNumber = route.query.key.split("-")[4]
const problemNumber = route.query.key.split("-")[5]
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
        console.log(data.value)
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
