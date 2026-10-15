<template>
    <a-modal fullscreen unmount-on-close v-model:visible="visible" title="批量新增测试项" ok-text="批量新增" :on-before-ok="handleSubmit">
        <a-form ref="formRef" :model="formData" layout="vertical">
            <a-table
                :data="formData"
                :columns="filterDemandColumns"
                :pagination="false"
                :hoverable="false"
                :scroll="{ x: 2500, y: 600 }"
                :bordered="{ wrapper: true, cell: true }"
                :draggable="{ type: 'handle', width: 40 }"
                @change="handleDraggleChange"
            >
                <template #xuhao="{ rowIndex }">
                    {{ rowIndex + 1 }}
                </template>
                <template #parent_key="{ rowIndex }">
                    <a-form-item help="测试所归属的需求" :field="`${rowIndex}.parent_key`" :rules="validationRules.parent_key" hide-label>
                        <a-cascader
                            :style="{ width: '80%' }"
                            allow-search
                            allow-clear
                            :options="casecadeOptions"
                            placeholder="请选择归属的设计需求"
                            v-model="formData[rowIndex].parent_key"
                        />
                        <a-button type="primary" :style="{ width: '20%' }" :disabled="rowIndex < 1" @click="handleTongshang($event, rowIndex, 'parent_key')">
                            同上
                        </a-button>
                    </a-form-item>
                </template>
                <template #ident="{ rowIndex }">
                    <a-form-item help="测试项标识" :field="`${rowIndex}.ident`" :rules="validationRules.ident" hide-label>
                        <a-input allow-clear v-model="formData[rowIndex].ident"></a-input>
                    </a-form-item>
                </template>
                <template #name="{ rowIndex }">
                    <a-form-item help="测试项名称" :field="`${rowIndex}.name`" :rules="validationRules.name" hide-label>
                        <a-input allow-clear v-model="formData[rowIndex].name"></a-input>
                    </a-form-item>
                </template>
                <template #priority="{ rowIndex }">
                    <a-form-item help="选择优先级" :field="`${rowIndex}.priority`" :rules="validationRules.priority" hide-label>
                        <a-select :options="priorityOptions" v-model="formData[rowIndex].priority"></a-select>
                    </a-form-item>
                </template>
                <template #adequacy="{ rowIndex }">
                    <a-form-item help="充分性描述，\a表示word换行" :field="`${rowIndex}.adequacy`" :rules="validationRules.adequacy" hide-label>
                        <a-textarea allow-clear auto-size v-model="formData[rowIndex].adequacy"></a-textarea>
                    </a-form-item>
                </template>
                <template #testMethod="{ rowIndex }">
                    <a-form-item help="选择测试手段" :field="`${rowIndex}.testMethod`" :rules="validationRules.testMethod" hide-label>
                        <a-select multiple :options="testMethodOptions" v-model="formData[rowIndex].testMethod"></a-select>
                        <a-button type="primary" :style="{ width: '20%' }" :disabled="rowIndex < 1" @click="handleTongshang($event, rowIndex, 'testMethod')">
                            同上
                        </a-button>
                    </a-form-item>
                </template>
                <template #testType="{ rowIndex }">
                    <a-form-item help="选择测试类型" :field="`${rowIndex}.testType`" :rules="validationRules.testType" hide-label>
                        <a-select allow-search :options="testTypeOptions" v-model="formData[rowIndex].testType"></a-select>
                        <a-button type="primary" :style="{ width: '20%' }" :disabled="rowIndex < 1" @click="handleTongshang($event, rowIndex, 'testType')">
                            同上
                        </a-button>
                    </a-form-item>
                </template>
                <template #testDesciption="{ rowIndex }">
                    <a-form-item help="填写测试项描述" :field="`${rowIndex}.testDesciption`" :rules="validationRules.testDesciption" hide-label>
                        <a-textarea allow-clear auto-size v-model="formData[rowIndex].testDesciption"></a-textarea>
                    </a-form-item>
                </template>
                <template #testContent="{ rowIndex }">
                    <a-form-item :field="`${rowIndex}.testContent`" hide-label :rules="validationRules.testContent">
                        <a-textarea allow-clear auto-size v-model="formData[rowIndex].testContent"></a-textarea>
                        <YonghuTs type="demand" />
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
import type { demandBatchType, demandOneType } from "./type"
import { Message, type FormInstance, type TableColumnData } from "@arco-design/web-vue"
import { lineInitialData, validationRules, priorityOptions } from "./consts"
import { useRoute } from "vue-router"
import { useTreeDataStore } from "@/store"
import useColumns from "./useColumn"
import useCasecadeOptions from "./hooks/useCasecadeOptions"
import useTestMethodOptions from "./hooks/useTestMethodOptions"
import useTestTypeOptions from "./hooks/useTestTypeOptions"
import tool from "@/utils/tool"
import YonghuTs from "./components/YongHuTs"
import demandApi from "@/api/project/testDemand"

// outInit
const route = useRoute()
const treeDataStore = useTreeDataStore()
const isFPGA = ref(tool.checkForCpuOrFPGA(route.query.plant_type))

const emit = defineEmits(["batchDemandCreateComplete"])

// 表格数据-动态绑定
const formRef = ref<FormInstance>()
const formData = ref<demandOneType[]>([{ ...lineInitialData }])
const isLastOne = computed(() => formData.value.length <= 1)

// columns-根据isFPGA计算属性
const { demandColumns } = useColumns()
const filterDemandColumns = computed(() => {
    return demandColumns.value.filter((col: TableColumnData) => {
        return !(isFPGA.value === false && col.dataIndex === "testDesciption")
    })
})

// 初始化级联下拉框数据
const { fetchOptionsData, casecadeOptions } = useCasecadeOptions()
// 初始化测试手段数据
const { fetchDictData, testMethodOptions } = useTestMethodOptions()
// 初始化测试类型数据
const { fetchTestTypeDictData, testTypeOptions } = useTestTypeOptions()

const visible = ref(false)
const open = async () => {
    visible.value = true
    await nextTick()
    fetchOptionsData() // 打开时获取级联下拉框数据
    fetchDictData() // 打开时获取测试手段数据
    fetchTestTypeDictData() // 打开时获取测试类型数据
}

// 操作行
const handlePlusIcon = () => {
    formData.value.push({ ...lineInitialData })
}
const handleDelete = (index: number) => {
    formData.value.splice(index, 1)
}
const handleDeleteAll = () => {
    formData.value = [{ ...lineInitialData }]
}
const handleTongshang = (_: MouseEvent, index: number, key: string) => {
    if (Array.isArray(formData.value[index - 1][key])) {
        formData.value[index][key] = [...formData.value[index - 1][key]]
        return
    }
    formData.value[index][key] = formData.value[index - 1][key]
}
const handleDraggleChange = (_data: any) => {
    formData.value = _data // 拖拽处理
}

// 异步提交按钮
const handleSubmit = async () => {
    // 首先Form校验
    const validation = await formRef.value?.validate()
    if (validation === undefined) {
        const submitData: demandBatchType = {
            project_id: route.query.id as unknown as number,
            demands: formData.value
        }
        try {
            const res = await demandApi.batchSave({ ...submitData })
            // 单独接口：如果res.data==='ok'，则创建成功
            if (res.code === 200991) {
                handleDeleteAll()
                res.data.forEach((it: any) => {
                    treeDataStore.updateDesignDemandTreeData({ key: it }, route.query.id)
                })
                emit("batchDemandCreateComplete")
                Message.success("批量新增成功!")
                return true
            } else {
                if (res.code === 500102) {
                    // 有+但没有测试项名称-后面再处理
                    Message.error(res.message)
                } else if (res.code === 500103) {
                    // 有+的行解析错误
                    Message.error(res.message)
                } else if (res.code === 500104) {
                    // 有-但无+的行解析错误
                    Message.error(res.message)
                } else {
                    Message.error("测试子项字符串解析错误，请检查后重试!")
                }
                return false
            }
        } catch (e) {
            console.log("录入事后前端报错，报错信息如下:", e)
            return false
        }
    }
    return false
}

defineExpose({ open })
</script>

<style scoped>
.icon {
    font-size: 20px;
}
</style>
