<template>
    <a-modal fullscreen unmount-on-close v-model:visible="visible" title="批量新增测试用例" ok-text="批量新增" :on-before-ok="handleSubmit">
        <a-form ref="formRef" :model="formData" layout="vertical">
            <a-table
                :data="formData"
                :columns="filterCaseColumns"
                :pagination="false"
                :hoverable="false"
                :scroll="isFPGA ? { x: 3000, y: 600 } : { x: 2500, y: 600 }"
                :bordered="{ wrapper: true, cell: true }"
                :draggable="{ type: 'handle', width: 40 }"
                @change="handleDraggleChange"
            >
                <template #xuhao="{ rowIndex }">
                    {{ rowIndex + 1 }}
                </template>
                <template #parent_key="{ rowIndex }">
                    <a-form-item help="归属当前轮次的测试项" :field="`${rowIndex}.parent_key`" :rules="validationRules.parent_key" hide-label>
                        <a-cascader
                            :style="{ width: '80%' }"
                            allow-search
                            allow-clear
                            :options="casecadeOptions"
                            placeholder="请选择归属的测试项"
                            v-model="formData[rowIndex].parent_key"
                        />
                        <a-button type="primary" :style="{ width: '20%' }" :disabled="rowIndex < 1" @click="handleTongshang($event, rowIndex, 'parent_key')">
                            同上
                        </a-button>
                    </a-form-item>
                </template>
                <template #name="{ rowIndex }">
                    <a-form-item help="填写用例名称" :field="`${rowIndex}.name`" :rules="validationRules.name" hide-label>
                        <a-input allow-clear v-model="formData[rowIndex].name"></a-input>
                    </a-form-item>
                </template>
                <template #initialization="{ rowIndex }">
                    <a-form-item help="请填写用例初始化" :field="`${rowIndex}.initialization`" hide-label>
                        <a-textarea allow-clear auto-size v-model="formData[rowIndex].initialization"></a-textarea>
                        <a-button
                            type="primary"
                            :style="{ width: '20%' }"
                            :disabled="rowIndex < 1"
                            @click="handleTongshang($event, rowIndex, 'initialization')"
                        >
                            同上
                        </a-button>
                    </a-form-item>
                </template>
                <template #premise="{ rowIndex }">
                    <a-form-item help="用例的前提与约束" :field="`${rowIndex}.premise`" hide-label>
                        <a-textarea allow-clear auto-size v-model="formData[rowIndex].premise"></a-textarea>
                        <a-button type="primary" :style="{ width: '20%' }" :disabled="rowIndex < 1" @click="handleTongshang($event, rowIndex, 'premise')">
                            同上
                        </a-button>
                    </a-form-item>
                </template>
                <template #summarize="{ rowIndex }">
                    <a-form-item help="填写用例综述" :field="`${rowIndex}.summarize`" hide-label>
                        <a-textarea allow-clear auto-size v-model="formData[rowIndex].summarize"></a-textarea>
                        <a-button type="primary" :style="{ width: '20%' }" :disabled="rowIndex < 1" @click="handleTongshang($event, rowIndex, 'summarize')">
                            同上
                        </a-button>
                    </a-form-item>
                </template>
                <template #sequence="{ rowIndex }">
                    <a-form-item :field="`${rowIndex}.sequence`" hide-label>
                        <ma-editor v-model="formData[rowIndex].sequence" style="width: 100%" :id="'sequence' + rowIndex"></ma-editor>
                    </a-form-item>
                </template>
                <template #test_step="{ rowIndex }">
                    <a-form-item :field="`${rowIndex}.test_step`" hide-label :rules="validationRules.test_step">
                        <a-textarea allow-clear auto-size v-model="formData[rowIndex].test_step"></a-textarea>
                        <PopupYonghu type="case" />
                    </a-form-item>
                </template>
                <template #caozuo="{ rowIndex }">
                    <a-space>
                        <a-button type="text" @click="handlePlusIcon">
                            <template #icon>
                                <span class="icon"><icon-plus-circle /></span>
                            </template>
                        </a-button>
                        <template v-if="!isLastOne">
                            <a-button type="text" status="danger" @click="handleDelete(rowIndex)">
                                <template #icon>
                                    <span class="icon"><icon-delete /></span>
                                </template>
                            </a-button>
                        </template>
                    </a-space>
                </template>
            </a-table>
        </a-form>
    </a-modal>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from "vue"
import { initCaseData, validationRules } from "./consts"
import { CasesSubmitType, CaseUserType } from "./types"
import { Message, type FormInstance, type TableColumnData } from "@arco-design/web-vue"
import { useRoute } from "vue-router"
import { useTreeDataStore } from "@/store"
import tool from "@/utils/tool"
import useColumn from "./useColumn"
import useCasecadeOptions from "./hooks/useCasecadeOptions"
import PopupYonghu from "../BatchDemandCreate/components/YongHuTs"
import caseApi from "@/api/project/case"

const visible = ref(false)
const route = useRoute()
const treeDataStore = useTreeDataStore()
const isFPGA = ref(tool.checkForCpuOrFPGA(route.query.plant_type))
const emit = defineEmits(["batchCaseCreateComplete"])

// columns
const { caseColumns } = useColumn()
const filterCaseColumns = computed(() => {
    return caseColumns.value.filter((col: TableColumnData) => {
        return !(isFPGA.value === false && col.dataIndex === "sequence")
    })
})

// 拖拽处理
const handleDraggleChange = (_data: any) => {
    formData.value = _data // 拖拽处理
}

// 表单和表格数据
const formRef = ref<FormInstance>()
const formData = ref<CaseUserType[]>([{ ...initCaseData }])
const isLastOne = computed(() => formData.value.length <= 1)

// hooks-提前获取信息
const { fetchOptionsData, casecadeOptions } = useCasecadeOptions() // 获取当前轮次归属测试项
const open = async () => {
    visible.value = true
    await nextTick()
    fetchOptionsData()
}

// 处理“同上”按钮
const handleTongshang = (_: MouseEvent, index: number, key: string) => {
    if (Array.isArray(formData.value[index - 1][key])) {
        formData.value[index][key] = [...formData.value[index - 1][key]]
        return
    }
    formData.value[index][key] = formData.value[index - 1][key]
}

// 按钮函数
const handlePlusIcon = () => {
    formData.value.push({ ...initCaseData })
}
const handleDelete = (index: number) => {
    formData.value.splice(index, 1)
}
const handleDeleteAll = () => {
    formData.value = [{ ...initCaseData }]
}

defineExpose({ open })
// 弹窗提交表单
const handleSubmit = async () => {
    const validation = await formRef.value?.validate()
    if (validation === undefined) {
        // 验证通过-组装POST
        const submitData: CasesSubmitType = {
            project_id: route.query.id as unknown as number,
            cases: formData.value
        }
        try {
            const res = await caseApi.batchSave({ ...submitData })
            if (res.code === 60000) {
                // 标识录入成功了
                handleDeleteAll()
                res.data.forEach((it: any) => {
                    treeDataStore.updateTestDemandTreeData({ key: it }, route.query.id)
                })
                emit("batchCaseCreateComplete")
                Message.success("批量新增用例成功!")
                return true
            } else {
                if (res.code === 60001) {
                    // 有字符但没有@情况
                    Message.error(res.message)
                } else if (res.code === 60002) {
                    // 操作输入为空，即@前面为空
                    Message.error(res.message)
                } else if (res.code === 60003) {
                    // 预期为空，即@后面为空
                    Message.error(res.message)
                } else {
                    Message.error("测试步骤快捷字符串录入错误，请检查!")
                }
            }
            return false
        } catch (e) {
            console.log("录入用例时后前端报错，报错信息如下:", e)
            return false
        }
    }
    return false
}
</script>

<style scoped>
.icon {
    font-size: 20px;
}
</style>
