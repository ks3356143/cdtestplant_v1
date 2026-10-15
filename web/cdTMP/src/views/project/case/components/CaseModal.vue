<template>
    <div class="case-modal-container">
        <a-modal v-model:visible="visible" draggable unmount-on-close hide-cancel ok-text="关闭" width="900px">
            <template #title> 问题单关联用例列表 </template>
            <div>
                <a-list>
                    <a-list-item v-for="(item, index) in transformData" :key="index">
                        <div class="text-base mb-2 flex items-center">
                            <div class="flex-auto">用例名称：{{ item.case }}</div>
                            <a-space>
                                <div>
                                    <a-button type="primary" shape="round" @click="handleEditClick(item)"
                                        >修改用例</a-button
                                    >
                                </div>
                            </a-space>
                        </div>
                        <a-descriptions :data="item.showData" bordered :column="1" />
                    </a-list-item>
                </a-list>
            </div>
            <case-form ref="caseFormRef" @caseUpdate="handleCaseUpdate"></case-form>
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue"
import CaseForm from "./CaseForm/index.vue"
import { type IRelatedCaseItem } from "./types"

const visible = ref(false)
// 数据储存在这里
const data = ref<IRelatedCaseItem[]>([])
// 转换为描述数据
const transformData = computed(() => {
    return data.value.map((item) => {
        // 数组的每一项都要转为{ case:'xxx',showData:[{label:'xxx',value:'xxx2'}] }
        const showData: { label: any; value: any }[] = []
        for (let key in item) {
            let showKey = key
            if (key === "case") continue
            if (key === "dut") {
                showKey = "被测件"
            }
            if (key === "round") {
                showKey = "轮次"
            }
            if (key === "design") {
                showKey = "设计需求"
            }
            if (key === "demand") {
                showKey = "测试项"
            }
            if (key === "demand_ident") {
                showKey = "测试项标识"
            }
            if (key !== "id") {
                showData.push({
                    label: showKey,
                    value: item[key]
                })
            }
        }
        return {
            id: item.id,
            case: item.case,
            showData
        }
    })
})

// caseForm相关方法
const caseFormRef = ref<InstanceType<typeof CaseForm> | null>(null)
const handleEditClick = (item: any): void => {
    caseFormRef.value!.open(item)
}

// 处理caseForm子组件的case信息更变事件
const handleCaseUpdate = (successFormData: any) => {
    // 更新列表林的数据
    data.value = data.value.map((it) => {
        if (it.id === successFormData.id) {
            return {
                ...it,
                case: successFormData.name
            }
        }
        return it
    })
}

// 暴露方法
function open(caseList: IRelatedCaseItem[]) {
    visible.value = true
    data.value = caseList
}
defineExpose({
    open
})
</script>

<style lang="less" scoped></style>
