<template>
    <div class="ai-modal-container">
        <a-modal v-model:visible="visible" width="90%" unmount-on-close draggable :footer="false">
            <template #title> AI生成测试项 </template>
            <div class="flex flex-col">
                <a-button type="primary" :disabled="generateLoading" @click="generateClick">{{
                    generateLoading ? "AI正在生成测试项中..." : "点击生成测试项"
                }}</a-button>
                <a-progress
                    :percent="percent"
                    :style="{ width: '100%' }"
                    size="large"
                    :show-text="false"
                    :color="{
                        '0%': 'rgb(var(--primary-6))',
                        '100%': 'rgb(var(--success-6))'
                    }"
                    class="mb-2"
                />
                <a-list :loading="listLoading" :data="dataList">
                    <template #header> 设计需求：{{ designObj?.name ?? "暂无内容" }} </template>
                    <template #item="{ item, index }">
                        <a-list-item>
                            <div class="item-container">
                                <a-input-group>
                                    <div class="index-hao">{{ indexTu[index] }}</div>
                                    <span class="label">测试项：</span>
                                    <a-input placeholder="测试项标识" v-model="item.ident" :style="{ width: '100px' }" @click.stop.prevent></a-input>
                                    <a-input placeholder="测试项名称" v-model="item.title" :style="{ width: '250px' }" @click.stop.prevent></a-input>
                                    <a-select placeholder="选择优先级" v-model="item.priority" :style="{ width: '150px' }">
                                        <a-option value="1">高</a-option>
                                        <a-option value="2">中</a-option>
                                        <a-option value="3">低</a-option>
                                    </a-select>
                                    <a-select placeholder="选择测试类型" v-model="item.testType" :style="{ width: '200px' }">
                                        <a-option v-for="type in testType" :key="type.key" :value="type.key">
                                            {{ type.title }}
                                        </a-option>
                                    </a-select>
                                    <a-select placeholder="选择测试手段" multiple v-model="item.testMethod" :style="{ width: '400px' }">
                                        <a-option v-for="method in testMethod" :key="method.key" :value="method.key">
                                            {{ method.title }}
                                        </a-option>
                                    </a-select>
                                </a-input-group>
                                <div class="m-2 flex justify-start items-center">
                                    <template v-if="isFPGA">
                                        <div class="label">测试项描述：</div>
                                        <div class="input flex-1">
                                            <a-input v-model="item.demandDescription"></a-input>
                                        </div>
                                    </template>
                                </div>
                                <div class="arco-table arco-table-size-large arco-table-border arco-table-stripe arco-table-hover">
                                    <div class="arco-table-container">
                                        <table class="arco-table-element" cellpadding="0" cellspacing="0">
                                            <thead>
                                                <tr class="arco-table-tr">
                                                    <th class="arco-table-th" :width="100">
                                                        <span class="arco-table-cell arco-table-cell-align-center">
                                                            <span class="arco-table-th-title label">子项序号</span>
                                                        </span>
                                                    </th>
                                                    <th class="arco-table-th" :width="200">
                                                        <span class="arco-table-cell arco-table-cell-align-center">
                                                            <span class="arco-table-th-title label">子项名称</span>
                                                        </span>
                                                    </th>
                                                    <template v-if="!isFPGA">
                                                        <th class="arco-table-th" :width="250">
                                                            <span class="arco-table-cell arco-table-cell-align-center">
                                                                <span class="arco-table-th-title label">测试子项描述</span>
                                                            </span>
                                                        </th>
                                                    </template>

                                                    <th class="arco-table-th" :width="800">
                                                        <span class="arco-table-cell arco-table-cell-align-center">
                                                            <span class="arco-table-th-title label">测试子项步骤</span>
                                                        </span>
                                                    </th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <!-- 这里tr要v-for渲染 -->
                                                <tr class="arco-table-tr" v-for="(row, idx) in item.children" :key="idx">
                                                    <td class="arco-table-td">
                                                        <span class="arco-table-cell arco-table-cell-align-center">
                                                            {{ Number(idx) + 1 }}
                                                        </span>
                                                    </td>
                                                    <td class="arco-table-td">
                                                        <span class="arco-table-cell">
                                                            <a-textarea auto-size placeholder="请填写测试子项名称" v-model="row.name"></a-textarea>
                                                        </span>
                                                    </td>
                                                    <template v-if="!isFPGA">
                                                        <td class="arco-table-td">
                                                            <span class="arco-table-cell">
                                                                <a-textarea
                                                                    auto-size
                                                                    placeholder="请填写测试子项描述"
                                                                    v-model="row.subDescription"
                                                                ></a-textarea>
                                                            </span>
                                                        </td>
                                                    </template>
                                                    <td class="arco-table-td">
                                                        <span class="arco-table-cell">
                                                            <OpeAndExpect v-model="row.subStep" />
                                                        </span>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </a-list-item>
                    </template>
                </a-list>
                <div class="luButton">
                    <a-button :loading="luButtonLoading" type="primary" @click="luButtonClick">确认录入测试项</a-button>
                </div>
            </div>
            <ParentPreview :parent-key="currentKey" />
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { onUnmounted, ref } from "vue"
import { useRoute } from "vue-router"
import designApi from "@/api/project/designDemand"
import dictApi from "@/api/common"
import OpeAndExpect from "./OpeAndExpect.vue" // 操作和预期子表格
import aiApi from "@/api/outs/aiApi"
import { Message } from "@arco-design/web-vue"
import tool from "@/utils/tool"
import { isEmpty } from "lodash-es"
import demandApi from "@/api/project/testDemand"
import ParentPreview from "@/views/project/ParentPreview/index.vue"

// 常量
const route = useRoute()
const indexTu = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚"
const isFPGA = tool.checkForCpuOrFPGA(route.query.plant_type)

// 初始化测试类型-一起请求处理错误
const testType = ref<any>([])
const testMethod = ref<any>([])
const fetchTestType = async () => {
    try {
        const [typeResponse, methodResponse] = await Promise.all([
            dictApi.getDictByCode({ code: "testType" }),
            dictApi.getDictByCode({ code: "testMethod" })
        ])
        testType.value = typeResponse.data
        testMethod.value = methodResponse.data
    } catch (e) {
        Message.error("初始化测试类型或测试手段错误，请检查网络后重试!")
    }
}
fetchTestType()

const designObj: any = ref()

// 初始化设计需求
const currentKey: string = route.query.key as string
const getDesign = async () => {
    try {
        const resResult = await designApi.getDesignDemandOne({ project_id: route.query.id, key: route.query.key })
        designObj.value = resResult.data
    } catch (e) {
        Message.error("初始化设计需求信息错误，请检查网络后重试!")
    }
}
getDesign()

// 进度条和列表加载loading
const percent = ref(0.0)
const listLoading = ref(false)

// 根据测试项生成按钮
const generateLoading = ref(false)
const generateClick = async () => {
    try {
        generateLoading.value = true
        listLoading.value = true
        percent.value = 0.1 // 开始进度
        startProgressSimulation()
        // 变量：给AI的问题
        const question = tool.htmlToTextWithDOM(designObj.value?.description || "")
        // 请求后处理结果
        const res = await aiApi.getAiTestItemBackend({ question: question, project_type: isFPGA ? "fpga" : "cpu" })
        // AI 返回格式异常时给出明确提示，避免静默失败
        let solveRes: any
        try {
            const historyItem = res.data?.history?.[0]
            const answer = Array.isArray(historyItem) ? historyItem.at(-1) : historyItem
            if (!answer) throw new Error("empty")
            solveRes = JSON.parse(answer)
        } catch {
            percent.value = 0.0
            Message.error("AI 返回内容格式异常，无法解析测试项，请重试")
            return
        }
        // 给Vue渲染测试项
        dataList.value = solveRes
        dataList.value.forEach((it: any) => {
            it.ident = designObj.value.ident
            it.priority = "1"
            it.testType = "4"
            it.testMethod = ["4"]
        })
        percent.value = 1.0 // 完成进度
        Message.success("生成测试项成功，请完善信息后录入数据")
    } catch (e) {
        percent.value = 0.0
        Message.error("生成测试项失败，请检查 AI 服务是否可用后重试")
    } finally {
        stopProgressSimulation()
        generateLoading.value = false
        setTimeout(() => {
            listLoading.value = false
        }, 500)
    }
}

// 生成的AI测试项数据
const dataList = ref([])

// 进度条模拟变量和函数（定时器句柄无需响应式）
let progressInterval: NodeJS.Timeout | undefined
const startProgressSimulation = () => {
    progressInterval = setInterval(() => {
        if (percent.value < 0.8) {
            percent.value += (0.8 - percent.value) * 0.1
        }
    }, 200)
}

const stopProgressSimulation = () => {
    if (progressInterval) {
        clearInterval(progressInterval)
        progressInterval = undefined
    }
}

onUnmounted(() => {
    stopProgressSimulation()
})

// defineModel
const visible = defineModel<boolean>("visible", { default: false })

// 录入按钮相关
const luButtonLoading = ref(false)
const emit = defineEmits(["updateTable"])
const luButtonClick = async () => {
    // 1.检查是否还未生成测试项
    if (isEmpty(dataList.value)) {
        Message.warning("您还未生成测试项，请生成后再试")
        return
    }
    // 2.检查测试项标识、测试项名称、优先级、测试类型、测试手段是否填写
    const testItem: any = dataList.value.at(0)
    if (!testItem.title?.trim()) {
        Message.warning("请先填写测试项名称!")
        return
    }
    if (!testItem.demandDescription?.trim()) {
        Message.warning("请填写测试项描述后再试!")
        return
    }
    if (!testItem.testMethod?.length) {
        Message.warning("请先选择测试手段后再试!")
        return
    }
    // 3.组装接口需要的数据
    const projectId = route.query.id
    // key 可能缺失（直接访问/刷新），先兜底成空串，避免 setup 阶段抛错
    const splitKey: string[] = String(route.query.key || "").split("-")
    const round = splitKey[0]
    const dut = splitKey[1]
    // key 结构为 round-dut-design(-test-case)，设计需求固定取第 3 段
    const designDemand = splitKey[2] ?? splitKey.at(-1)
    const adequacy: string = "测试用例覆盖测试子项要求的全部内容。\n所有用例执行完毕，对于未执行用例说明未执行原因。"
    const ident = testItem.ident
    const name = testItem.title
    const testType = testItem.testType
    const testMethod = testItem.testMethod
    const testDesciption = testItem.demandDescription
    const priority = testItem.priority
    const testContent = (testItem.children ?? []).map(({ name: subName, ...rest }) => ({
        subName,
        ...rest
    }))
    // 4.异步录入啦
    try {
        // 首先设置状态
        luButtonLoading.value = true
        generateLoading.value = true
        await demandApi.save({
            projectId,
            round,
            dut,
            designDemand,
            adequacy,
            ident,
            name,
            testType,
            testMethod,
            testDesciption,
            priority,
            testContent
        })
        // 请求成功后需要：清除dataList内容，关闭弹窗，提示新增成功，刷新树状结构以及表格（给父组件刷新）
        dataList.value = []
        visible.value = false
        Message.success("录入测试项成功")
        emit("updateTable")
    } catch (e) {
    } finally {
        luButtonLoading.value = false
        generateLoading.value = false
    }
}

// 悬浮按钮显示上级设计需求内容
</script>

<style scoped lang="less">
.index-hao {
    font-size: 18px;
    padding: 0 9px;
    color: rgb(var(--primary-5));
}
:deep(.arco-list-item) {
    border: 1px solid #999 !important;
}
:deep(.arco-progress-line-bar) {
    border-radius: 0 !important;
}
:deep(.arco-progress-line) {
    border-radius: 0 !important;
}
.label {
    font-weight: 700;
}
.luButton {
    margin-left: auto;
    padding: 10px;
    padding-right: 0;
}
</style>
