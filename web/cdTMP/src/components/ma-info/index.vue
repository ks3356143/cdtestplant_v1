<template>
    <a-space direction="vertical" size="large" fill>
        <a-descriptions
            :data="descriptions"
            :column="props.column"
            :title="props.title"
            :layout="props.layout"
            :bordered="props.bordered"
            :table-layout="props.tableLayout"
            :size="props.size"
            :label-style="props.labelStyle"
            :value-style="props.valueStyle"
        >
            <a-descriptions-item v-for="item in descriptions" :label="item.label" :span="item.span ? item.span : isArray(item.value) ? props.column : 1">
                <template v-if="item.formType === 'upload'">
                    <a-image-preview-group infinite v-if="isArray(item.value)">
                        <a-space>
                            <a-image v-for="src in item.value" :src="tool.viewImage(src)" width="50" />
                        </a-space>
                    </a-image-preview-group>
                    <a-image v-else :src="tool.viewImage(item.value)" width="50"></a-image>
                </template>
                <template v-else-if="item.infoSlot">
                    <slot :name="item.dataIndex" :row="item" :data="data"></slot>
                </template>
                <!-- 修改源码-如果dataIndex为testContent -->
                <template v-else-if="item.dataIndex === 'testContent'">
                    <div class="overflow-y-auto max-h-80">
                        <template v-if="item.value.length > 0">
                            <template v-for="(sub, idx) in item.value" :key="idx">
                                <!-- 这是每个测试子项 -->
                                <div class="subTitle mt-1">{{ idx + 1 }}.{{ sub.subName }}</div>
                                <div>测试子项描述：{{ sub.subDescription }}</div>
                                <template v-for="(step, index) in sub.subStep" :key="index">
                                    <span class="text-amber-700">步骤{{ index + 1 }}）</span>
                                    <div class="operation"><span class="text-bold">操作：</span>{{ step.operation }}</div>
                                    <div class="mb-1"><span class="text-bold">预期：</span>{{ step.expect }}</div>
                                </template>
                            </template>
                        </template>
                        <template v-else>暂无信息</template>
                    </div>
                </template>
                <template v-else-if="item.formType === 'radio' || item.formType === 'select' || item.formType === 'checkbox'">
                    <template v-if="isArray(item.value)">
                        <!-- 修改源码 -->
                        <a-space>
                            <a-tag v-for="v in item.value" color="magenta">
                                <template v-if="v.length > 0">
                                    {{ item.dict.data.find((row) => row.value == v)?.label }}
                                </template>
                            </a-tag>
                        </a-space>
                    </template>
                    <template v-else>
                        <a-tag color="blue">
                            {{ item.dict.data.find((row) => row.value == item.value)?.label }}
                        </a-tag>
                    </template>
                </template>
                <div v-else><div class="white-space-change" v-html="item.value"></div></div>
            </a-descriptions-item>
        </a-descriptions>
    </a-space>
</template>

<script setup>
import { getCurrentInstance, inject, provide, ref, watch } from "vue"
import tool from "@/utils/tool"
import { get, isArray, isBoolean, isEmpty, isFunction } from "lodash-es"
import { loadDict } from "@cps/ma-form/js/networkRequest.js"
import globalColumn from "@/config/column.js"

const dictList = {}
const app = getCurrentInstance().appContext.app
const columns = ref([])
const data = ref({})
const descriptions = ref([])
const dictData = ref([])
const props = defineProps({
    columns: { type: Array, default: [] },
    data: {},
    column: { default: 3 },
    title: {
        default: ""
    },
    bordered: {
        default: true
    },
    layout: {
        default: "vertical"
    },
    labelStyle: {
        default: {}
    },
    valueStyle: {
        default: {}
    },
    size: {
        default: "large"
    },
    // 新增
    tableLayout: { type: String, default: "fixed" }
})

watch(
    () => props.columns,
    (vl) => {
        columns.value = vl
    },
    { deep: true, immediate: true }
)

const reset = async (vl) => {
    data.value = vl
    descriptions.value = []
    if (!columns.value) {
        return
    }
    for (let item of columns.value) {
        let value = null
        if (isEmpty(item) || item.dataIndex === "__operation" || item.infoShow === false) {
            // return
            // 上面是源码 -> 修改源码：源码错误!
            continue
        }
        if (isBoolean(item.common) && item.common && globalColumn[item.dataIndex]) {
            item = globalColumn[item.dataIndex]
        }
        if (item.dict) {
            await loadDict(dictList, item)
            item.dict.data = dictList[item.dataIndex] ?? []
        }
        if (isFunction(item.customRender)) {
            value = item.customRender({ record: data.value })
        }
        descriptions.value.push({
            ...item,
            label: item.title,
            value: value ?? get(data.value, item.dataIndex)
        })
    }
}

watch(
    () => props.data,
    (vl) => {
        reset(vl)
    },
    { deep: true, immediate: true }
)

defineExpose({ reset })
</script>

<style scoped>
.white-space-change {
    max-height: 68vh;
    white-space: normal;
    overflow-y: auto;
}
</style>
