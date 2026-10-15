<template>
    <div class="chen-demand-list">
        <div class="arco-table arco-table-size-large arco-table-border arco-table-stripe arco-table-hover">
            <div class="arco-table-container">
                <table class="arco-table-element" cellpadding="0" cellspacing="0">
                    <thead>
                        <tr class="arco-table-tr">
                            <th class="arco-table-th" :width="20">
                                <span class="arco-table-cell arco-table-cell-align-center">
                                    <a-tooltip content="添加步骤">
                                        <a-button :tabindex="-1" type="primary" size="mini" shape="round" @click="addItem"> 新增步骤+ </a-button>
                                    </a-tooltip>
                                </span>
                            </th>
                            <th class="arco-table-th" :width="18">
                                <span class="arco-table-cell arco-table-cell-align-center">
                                    <span class="arco-table-th-title">序号</span>
                                </span>
                            </th>
                            <th class="arco-table-th" :width="400">
                                <span class="arco-table-cell arco-table-cell-align-center">
                                    <span class="arco-table-th-title">操作</span>
                                </span>
                            </th>
                            <th class="arco-table-th" :width="310">
                                <span class="arco-table-cell arco-table-cell-align-center">
                                    <span class="arco-table-th-title">预期</span>
                                </span>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- 根据subStep渲染 -->
                        <template v-if="modelValue && modelValue.length > 0" v-for="(stepItem, index) in modelValue" :key="index">
                            <tr class="arco-table-tr">
                                <td class="arco-table-td">
                                    <span class="arco-table-cell justify-center gap-1.5">
                                        <!-- 删除单项按钮 -->
                                        <a-button
                                            :tabindex="-1"
                                            type="primary"
                                            status="danger"
                                            size="mini"
                                            shape="round"
                                            @click="deleteItem(index)"
                                            :disabled="modelValue.length <= 1"
                                        >
                                            <template #icon><icon-close /></template>
                                        </a-button>
                                        <a-tooltip content="复制该项添加">
                                            <a-button :tabindex="-1" type="primary" status="warning" size="mini" shape="round" @click="copyItem(index)">
                                                <template #icon>
                                                    <icon-copy />
                                                </template>
                                            </a-button>
                                        </a-tooltip>
                                        <a-button-group shape="round" size="mini">
                                            <a-button :tabindex="-1" type="primary" @click="moveUp(index)">
                                                <icon-arrow-rise />
                                            </a-button>
                                            <a-button :tabindex="-1" type="primary" @click="moveDown(index)">
                                                <icon-arrow-fall />
                                            </a-button>
                                        </a-button-group>
                                    </span>
                                </td>
                                <td class="arco-table-td text-center!">
                                    <a-badge class="mt-1" :count="index + 1" :dotStyle="{ background: '#E5E6EB', color: '#86909C' }" />
                                </td>
                                <td class="arco-table-td">
                                    <span class="arco-table-cell">
                                        <a-textarea auto-size v-model="stepItem.operation"></a-textarea>
                                    </span>
                                </td>
                                <td class="arco-table-td">
                                    <span class="arco-table-cell">
                                        <a-textarea auto-size v-model="stepItem.expect"></a-textarea>
                                    </span>
                                </td>
                            </tr>
                        </template>
                        <template v-else>
                            <tr>
                                <td colspan="3">
                                    <div class="flex justify-center items-center p-2 border">
                                        <a-alert>暂无测试子项条目，请添加</a-alert>
                                    </div>
                                </td>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { type Ref, nextTick } from "vue"
import { cloneDeep } from "lodash-es"

// 辅助函数：当modelValue不是列表时候
function handleIsNotArray() {
    if (Array.isArray(modelValue.value)) return
    modelValue.value = []
}

// 定义value数据
interface ISubStep {
    operation: string
    expect: string
}
// 绑定外部数据，预期是列表，有operation、expect两个字段
const modelValue = defineModel() as unknown as Ref<ISubStep[]>

// 单纯新增 - modalValue新增一行
const addItem = async () => {
    handleIsNotArray()
    await nextTick() // 因为要等待modelValue值变化DOM渲染完毕
    modelValue.value.push({ operation: "", expect: "" })
}

// 删除指定行
const deleteItem = (index: number) => {
    modelValue.value = modelValue.value.filter((_, idx) => idx !== index)
}

// 复制单项
const copyItem = (index: number) => {
    const newItem = cloneDeep(modelValue.value[index])
    modelValue.value = [...modelValue.value, newItem]
}

// 辅助函数交换列表两个元素
function swapItems(idx1: number, idx2: number) {
    const arr = modelValue.value
    ;[arr[idx1], arr[idx2]] = [arr[idx2], arr[idx1]]
}

// 向下移动
const moveDown = (index: number) => {
    if (index === modelValue.value.length - 1) return
    swapItems(index, index + 1)
}

// 向上移动
const moveUp = (index: number) => {
    if (index === 0) return
    swapItems(index, index - 1)
}
</script>

<style lang="less" scoped>
:deep(.arco-form-item-content-flex) {
    display: block;
}
:deep(.arco-table-cell .arco-form-item) {
    margin-bottom: 0;
}
</style>
