<template>
    <a-form-item
        v-if="typeof props.component.display == 'undefined' || props.component.display === true"
        :label="props.component.title"
        :field="props.component.dataIndex"
        :tooltip="props.component.tooltip"
        :show-colon="props.component.showColon"
        :label-col-flex="props.component.labelColFlex ?? 'auto'"
        :label-col-style="{
            width: props.component.labelWidth ? props.component.labelWidth : options.labelWidth || '100px'
        }"
        :rules="props.component.rules || []"
        :disabled="props.component.disabled"
        :help="props.component.help"
        :extra="props.component.extra"
        :required="props.component.required"
        :hide-label="props.component.hideLabel"
        :content-class="props.component.contentClass"
        :feedback="props.component.feedback"
        :validate-trigger="props.component.validateTrigger"
        :validate-status="props.component.validateStatus"
        :class="[props.component.customClass]"
    >
        <a-collapse
            :default-active-key="defaultOpenKeys"
            expand-icon-position="right"
            v-if="(props.component?.type ?? 'group') === 'group'"
            :show-expand-icon="false"
        >
            <a-collapse-item
                v-for="(item, itemIndex) in formModel[props.component.dataIndex]"
                :key="itemIndex"
                :header="`${props.component.title} 第${itemIndex + 1}项 ${item.subName ? item.subName : ''}`"
            >
                <template #extra>
                    <a-space>
                        <!-- 修改源码：添加向上和向下 -->
                        <a-tooltip content="向上移动" v-if="!(props.component.hideAdd ?? false)">
                            <a-button :tabindex="-1" @click.stop="moveUp(itemIndex)" type="primary" size="small" shape="round">
                                <template #icon><icon-arrow-rise /></template>
                            </a-button>
                        </a-tooltip>
                        <a-tooltip content="向下移动" v-if="!(props.component.hideAdd ?? false)">
                            <a-button :tabindex="-1" @click.stop="moveDown(itemIndex)" type="primary" size="small" shape="round">
                                <template #icon><icon-arrow-fall /></template>
                            </a-button>
                        </a-tooltip>
                        <icon-oblique-line />
                        <!-- 修改源码：新增复制该项新增 -->
                        <a-tooltip content="复制该项添加" v-if="!(props.component.hideAdd ?? false)">
                            <a-button :tabindex="-1" @click.stop="addItem(item)" type="primary" size="small" shape="round" status="warning">
                                <template #icon><icon-copy /></template>
                            </a-button>
                        </a-tooltip>
                        <a-tooltip content="添加新子项" v-if="!(props.component.hideAdd ?? false)">
                            <a-button :tabindex="-1" @click.stop="addItem()" type="primary" size="small" shape="round">
                                <template #icon><icon-plus /></template>
                            </a-button>
                        </a-tooltip>
                        <a-tooltip content="删除该子项" v-if="!(props.component.hideDelete ?? false)">
                            <a-button
                                :tabindex="-1"
                                @click.stop="deleteItem(itemIndex)"
                                :disabled="formModel[props.component.dataIndex].length === 1"
                                type="primary"
                                size="small"
                                shape="round"
                                status="danger"
                            >
                                <template #icon><icon-close /></template>
                            </a-button>
                        </a-tooltip>
                    </a-space>
                </template>
                <template v-for="(component, componentIndex) in viewFormList[itemIndex]" :key="componentIndex">
                    <component
                        v-if="!containerItems.includes(component.formType)"
                        :is="getComponentName(component?.formType ?? 'input')"
                        :component="component"
                        :customField="getChildrenDataIndex(itemIndex, component.dataIndex)"
                    >
                        <template v-for="slot in Object.keys($slots)" #[slot]="component">
                            <slot :name="slot" v-bind="component" />
                        </template>
                    </component>
                </template>
            </a-collapse-item>
        </a-collapse>

        <div v-else class="arco-table arco-table-size-large arco-table-border arco-table-stripe arco-table-hover">
            <div class="arco-table-container">
                <table class="arco-table-element" cellpadding="0" cellspacing="0">
                    <thead>
                        <tr class="arco-table-tr">
                            <th class="arco-table-th" width="60">
                                <span class="arco-table-cell arco-table-cell-align-center">
                                    <a-button :tabindex="-1" type="primary" @click="addItem()" size="small" shape="round">
                                        <template #icon>
                                            <icon-plus />
                                        </template>
                                    </a-button>
                                </span>
                            </th>
                            <th class="arco-table-th" :width="60">
                                <span class="arco-table-cell arco-table-cell-align-center">
                                    <span class="arco-table-th-title">序号</span>
                                </span>
                            </th>
                            <template v-for="component in viewFormList[0]">
                                <th class="arco-table-th" :width="component.width">
                                    <span class="arco-table-cell arco-table-cell-align-center">
                                        <span class="arco-table-th-title">{{ component.title }}</span>
                                    </span>
                                </th>
                            </template>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="(item, index) in formModel[props.component.dataIndex]">
                            <tr class="arco-table-tr">
                                <td class="arco-table-td">
                                    <span class="arco-table-cell">
                                        <a-button
                                            :tabindex="-1"
                                            type="primary"
                                            status="danger"
                                            size="small"
                                            shape="round"
                                            :disabled="formModel[props.component.dataIndex].length === 1"
                                            @click="deleteItem(index)"
                                        >
                                            <template #icon><icon-close /></template>
                                        </a-button>
                                    </span>
                                </td>
                                <td class="arco-table-td">
                                    <span class="arco-table-cell">
                                        <span class="arco-table-td-content">{{ index + 1 }}</span>
                                    </span>
                                </td>
                                <template v-for="component in viewFormList[index]">
                                    <td class="arco-table-td">
                                        {{ component.hideLabel = true ? "" : "" }}
                                        <span class="arco-table-cell">
                                            <component
                                                v-if="!containerItems.includes(component.formType)"
                                                :is="getComponentName(component.formType ?? 'input')"
                                                :component="component"
                                                :customField="getChildrenDataIndex(index, component.dataIndex)"
                                            >
                                                <template v-for="slot in Object.keys($slots)" #[slot]="component">
                                                    <slot :name="slot" v-bind="component" />
                                                </template>
                                            </component>
                                        </span>
                                    </td>
                                </template>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>
        </div>
        <!-- 修改源码：切换显示形态 -->
        <Teleport to="body">
            <a-popover>
                <template #title>切换{{ props.component.type === "group" ? "表格" : "聚合" }}显示</template>
                <div class="sticky-container" @click="swapTableOrGroupDisplay">
                    <div class="sticky-button">
                        <icon-swap />
                    </div>
                </div>
            </a-popover>
        </Teleport>
    </a-form-item>
</template>

<script setup>
import { ref, inject, onMounted, watch, nextTick } from "vue"
import { cloneDeep, isArray, isUndefined } from "lodash-es"
import { getComponentName, containerItems } from "../js/utils.js"
import { runEvent } from "../js/event.js"
import { loadDict } from "../js/networkRequest.js"

const props = defineProps({ component: Object })
const formList = props.component.formList
const viewFormList = ref([])
const options = inject("options")
const formModel = inject("formModel")
const dictList = inject("dictList")
const getColumnService = inject("getColumnService")
const columns = inject("columns")

// ~~~~修改源码-start
const emit = defineEmits(["swichTableAndGroup"])
const swapTableOrGroupDisplay = () => {
    props.component.type = props.component.type === "group" ? "table" : "group"
    emit("swichTableAndGroup", props.component.type)
}
watch(
    () => props.component.type,
    (newVal) => {
        if (newVal === "group") {
            formList.forEach((item) => (item.hideLabel = false))
        }
    },
    { immediate: true }
)
// ~~~~修改源码-end

const rv = async (ev, value = undefined) => await runEvent(props.component, ev, { formModel, getColumnService, columns }, value)

const defaultOpenKeys = [0]

if (!formModel.value[props.component.dataIndex]) {
    formModel.value[props.component.dataIndex] = []
}

formList.map(async (item) => {
    const tmp = cloneDeep(item)
    tmp["dataIndex"] = [props.component.dataIndex, tmp.dataIndex].join(".")
    await loadDict(dictList.value, tmp)
})

watch(
    () => formModel.value[props.component.dataIndex],
    (value) => {
        if (isArray(value)) {
            value.forEach((data, index) => {
                if (isArray(data)) {
                    value[index] = Object.fromEntries(data)
                }
                viewFormList.value[index] = cloneDeep(formList)
                rv("onAdd", { formList: viewFormList.value[index], data, index })
            })
        }
    },
    {
        immediate: true
    }
)

if (props.component.type == "table") {
    formList.map((item) => {
        item["hideLabel"] = true
    })
} else {
    formModel.value[props.component.dataIndex].map((item, index) => {
        if (index > 0) defaultOpenKeys.push(index)
    })
}

// 辅助函数：交换数组两个元素
function swapItems(idx1, idx2) {
    const arr = formModel.value[props.component.dataIndex]
    ;[arr[idx1], arr[idx2]] = [arr[idx2], arr[idx1]]
}

// 辅助函数：触发充分性分析
// 2025-06-24：新增子项后需对触发更新
function updateChongFen() {
    if (formModel.value.testContent && formModel.value.testContent.length > 0) {
        // 如果有testContent则更新“充分性要求”
        const subItemFormData = formModel.value.testContent
        const mapRes = subItemFormData.map((subItem) => subItem.subName || "")
        formModel.value.adequacy &&
            (formModel.value.adequacy = `测试用例覆盖${mapRes.join("、")}子项要求的全部内容。\n所有用例执行完毕，对于未执行的用例说明未执行原因。`)
    }
}

// 修改源码：上移动和下移动
const moveUp = (itemIndex) => {
    const itemLength = formModel.value[props.component.dataIndex].length
    // 如果是第一个，不做操作
    if (itemIndex === 0) {
        return
    }
    // 进行移动
    swapItems(itemIndex, itemIndex - 1)
    // 2025-06-24修改
    updateChongFen()
}

const moveDown = (itemIndex) => {
    const itemLength = formModel.value[props.component.dataIndex].length
    // 如果是最后一个，不做操作
    if (itemIndex === itemLength - 1) {
        return
    }
    // 进行移动
    swapItems(itemIndex, itemIndex + 1)
    // 2025-06-24修改
    updateChongFen()
}

const addItem = async (data = {}) => {
    // 修改源码：深度复制
    let newData = cloneDeep(data)
    let index = formModel.value[props.component.dataIndex].length // 当前子项列表长度
    viewFormList.value[index] = cloneDeep(formList)
    rv("onAdd", { formList: viewFormList.value[index], newData, index }) // 修改源码：深度复制data->newData
    formModel.value[props.component.dataIndex].push(newData) // 修改源码：深度复制data->newData
    // 修改源码，触发充分性更新
    updateChongFen()
}

const deleteItem = async (index) => {
    let res = await rv("onDelete", { index })
    if (isUndefined(res) || res === true) {
        viewFormList.value.splice(index, 1)
        await nextTick()
        formModel.value[props.component.dataIndex].splice(index, 1)
    }
    // 2025-06-24修改
    updateChongFen()
}

const getChildrenDataIndex = (index, dataIndex) => {
    return [props.component.dataIndex, index, dataIndex].join(".")
}

rv("onCreated")
onMounted(async () => {
    if (formModel.value[props.component.dataIndex].length === 0) {
        for (let i = 0; i < (props.component.emptyRow ?? 1); i++) {
            await addItem()
        }
    }
    rv("onMounted")
})
</script>

<style scoped lang="less">
:deep(.arco-form-item-content-flex) {
    display: block;
    position: relative;
    .arco-radio-group {
        position: absolute;
        top: 50%;
        transform: translateY(-40%);
    }
}
:deep(.arco-table-cell .arco-form-item) {
    margin-bottom: 0;
}
// 切换按钮-以后单独封装一个组件
.sticky-container {
    position: fixed;
    right: 80px;
    top: 35%;
    z-index: 10000;
}
.sticky-button {
    width: 40px;
    height: 40px;
    font-size: 16px;
    border-radius: 50%;
    background-color: #fff;
    display: flex;
    justify-content: center;
    align-items: center;
    user-select: none;
    cursor: pointer;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.8);
    transition: all 0.1s;
    overflow: hidden;
    position: relative;
    span {
        white-space: nowrap;
        opacity: 0;
    }
}
.sticky-button:hover {
    transition: all 0.1s;
    border: 1px solid rgb(64, 128, 255);
    color: rgb(64, 128, 255);
}
</style>
