<template>
    <div class="w-full" ref="containerRef" id="form-main-id">
        <a-spin :loading="formLoading" :tip="options.loadingText" class="w-full ma-form-spin">
            <div v-if="options.showFormTitle" :class="['ma-form-title', options.formTitleClass]" :style="options.formTitleStyle">
                {{ options.formTitle }}
            </div>
            <a-form
                ref="maFormRef"
                :model="form"
                :class="['ma-form', options?.customClass]"
                :label-align="options?.labelAlign"
                :layout="options?.layout"
                :size="options?.size"
                :disabled="options?.disabled"
                :rules="options?.rules"
                @submit="formSubmit"
                :key="componentKey"
            >
                <slot name="formContent">
                    <template v-for="(component, componentIndex) in columns" :key="componentIndex">
                        <component
                            :is="getComponentName(component?.formType ?? 'input')"
                            :component="component"
                            :ref="setDialogRef"
                            @swichTableAndGroup="handleChangeDisplay"
                        >
                            <template v-for="slot in Object.keys($slots)" #[slot]="component">
                                <slot :name="slot" v-bind="component" />
                            </template>
                        </component>
                    </template>
                    <div class="text-center" v-if="options.showButtons">
                        <a-space>
                            <slot name="formBeforeButtons" />
                            <slot name="formButtons">
                                <a-button :type="options.submitType" :status="options.submitStatus" v-if="options.submitShowBtn" html-type="submit">
                                    <template #icon v-if="options?.submitIcon">
                                        <component :is="options.submitIcon" />
                                    </template>
                                    {{ options.submitText }}
                                </a-button>
                                <a-button :type="options.resetType" :status="options.resetStatus" v-if="options.resetShowBtn" @click="resetForm">
                                    <template #icon v-if="options?.resetIcon">
                                        <component :is="options.resetIcon" />
                                    </template>
                                    {{ options.resetText }}
                                </a-button>
                            </slot>
                            <slot name="formAfterButtons" />
                        </a-space>
                    </div>
                </slot>
            </a-form>
            <!-- 修改源码：判断是否传入parentKey -->
            <template v-if="parentKey">
                <ParentPreview :parent-key="parentKey"></ParentPreview>
            </template>
            <!-- ctrl+F的替换功能：仅支持用例、测试项 -->
            <template v-if="form.testStep || form.testContent">
                <teleport to="body">
                    <div class="alert-container">
                        <a-alert show-icon type="info">
                            <p>支持</p>
                            <p>Ctrl+F</p>
                            <p>替换</p>
                        </a-alert>
                    </div>
                </teleport>
                <BulkReplaceModal ref="replaceModalRef" :parent-form="form" />
            </template>
        </a-spin>
    </div>
</template>

<script setup>
import { ref, watch, provide, onMounted, onUnmounted, nextTick, getCurrentInstance, inject, computed } from "vue"
import { isNil, set, get, cloneDeep } from "lodash-es"
import defaultOptions from "./js/defaultOptions.js"
import { getComponentName, toHump, interactiveControl, handleFlatteningColumns, insertGlobalCssToHead, insertGlobalFunctionsToHtml } from "./js/utils.js"
import { loadDict, handlerCascader } from "./js/networkRequest.js"
import arrayComponentDefault from "./js/defaultArrayComponent.js"
import ColumnService from "./js/columnService.js"

import { runEvent } from "./js/event.js"
import { Message } from "@arco-design/web-vue"
// 修改源码导入：查找和替换组件
import BulkReplaceModal from "@/components/ma-form/Customs/BulkReplaceModal.vue"

const formLoading = ref(false)
const maFormRef = ref()
const dialogRefs = ref({})
const flatteningColumns = ref([])
const dictList = ref({})
const cascaderList = ref([])
const form = ref({})

// ~~~custom start0 - 查找和替换组件
const replaceModalRef = ref()
const containerRef = ref()
const handleKeydown = (e) => {
    if (e.ctrlKey && e.key === "f") {
        e.preventDefault()
        replaceModalRef.value && replaceModalRef.value.open()
    }
}
onMounted(() => {
    document.addEventListener("keydown", handleKeydown)
})
onUnmounted(() => {
    document.removeEventListener("keydown", handleKeydown)
})

// ~~~custom start1 - 新增功能利用key强制更新form表单组件
const componentKey = ref(0)
const updateKey = () => {
    componentKey.value += 1
    if (componentKey.value > 20000) {
        componentKey.value = 0
    }
}
const handleChangeDisplay = (type) => {
    updateKey()
}
// ~~~custom end

// ~~~~custom start2
// 2025年5月14日新增功能hover查看上级节点
import ParentPreview from "@/views/project/ParentPreview/index.vue"
// 判断是否有
const formKey = computed(() => {
    // 去掉双击被测件：即key.split("").length > 1
    if (form.value.key && typeof form.value.key !== "number" && form.value.key && form.value.key.split("-").length > 2) {
        // 如果存在则取前面的
        return form.value.key.split("-").slice(0, -1).join("-")
    }
    return ""
})

const parentKey = computed(() => {
    return props.parentKey || formKey.value || ""
})
// ~~~~custom end

const props = defineProps({
    modelValue: { type: Object, default: {} },
    columns: { type: Array },
    options: { type: Object, default: {} },
    // 2025年5月14日新增属性-非必须，后面根据非必须判断
    parentKey: { type: String, default: "" }
})

const emit = defineEmits(["submit", "update:modelValue"])

watch(
    () => props.modelValue,
    (vl) => (form.value = vl),
    { immediate: true, deep: true }
)

watch(
    () => form.value,
    (vl) => {
        interactiveControl(vl, flatteningColumns.value, { getColumnService, dictList })
        emit("update:modelValue", vl)
    },
    { deep: true }
)

const options = ref({})

// 初始化
const init = async () => {
    const containerList = import.meta.glob("./containerItem/*.vue", { eager: true })
    const componentList = import.meta.glob("./formItem/*.vue", { eager: true })
    const _this = getCurrentInstance()?.appContext ?? undefined

    if (_this) {
        for (const path in containerList) {
            const name = path.match(/([A-Za-z0-9_-]+)/g)[1]
            const containerName = `Ma${toHump(name)}`
            if (!_this.components[containerName]) {
                _this.app.component(containerName, containerList[path].default)
            }
        }

        for (const path in componentList) {
            const name = path.match(/([A-Za-z0-9_-]+)/g)[1]
            const componentName = `Ma${toHump(name)}`
            if (!_this.components[componentName]) {
                _this.app.component(componentName, componentList[path].default)
            }
        }
    }

    formLoading.value = true

    handleFlatteningColumns(props.columns, flatteningColumns.value)

    // 收集数据列表
    flatteningColumns.value.map((item) => {
        if (item.cascaderItem && item.cascaderItem.length > 0) {
            cascaderList.value.push(...item.cascaderItem)
        }
    })

    // 初始化数据
    flatteningColumns.value.map(async (item) => {
        if (isNil(form.value[item.dataIndex])) {
            form.value[item.dataIndex] = undefined
            if (arrayComponentDefault.includes(item.formType)) {
                form.value[item.dataIndex] = []
            }
        }

        // 处理带点的字段
        if (typeof item.dataIndex === "string") {
            if (item.dataIndex.indexOf(".") > -1) {
                const value = cloneDeep(form.value[item.dataIndex])
                delete form.value[item.dataIndex]
                set(form.value, item.dataIndex, value)
            }
        }

        // 字典
        if (!cascaderList.value.includes(item.dataIndex) && item.dict) {
            await loadDict(dictList.value, item, options.value.sourceList, {
                formModel: form.value,
                getColumnService,
                columns: flatteningColumns.value
            })
        }

        // 联动
        await handlerCascader(get(form.value, item.dataIndex), item, flatteningColumns.value, dictList.value, form.value, false)
    })

    await nextTick(() => {
        interactiveControl(form.value, flatteningColumns.value, { getColumnService, dictList })
        formLoading.value = false
    })
}

const setDialogRef = async (ref) => {
    await nextTick(() => {
        if (ref?.getDataIndex) {
            dialogRefs.value[ref.getDataIndex()] = ref
            if (!form.value[ref.getDataIndex()]) {
                form.value[ref.getDataIndex()] = {}
            }
        }
    })
}

// maEvent.handleCommonEvent(options.value, 'onCreated')

onMounted(async () => {
    updateOptions()
    insertGlobalCssToHead(options.value.globalCss)
    insertGlobalFunctionsToHtml(options.value.globalFunction)
    // maEvent.handleCommonEvent(options.value, 'onMounted')
    options.value.init && (await init())
    // maEvent.handleCommonEvent(options.value, 'onInit')
})

const done = (status) => (formLoading.value = status)
const validateForm = async () => {
    const valid = await maFormRef.value.validate()
    if (valid) {
        let message = ""
        for (let name in valid) message += valid[name].message + "、"
        Message.error(message.substring(0, message.length - 1))
    }
    return valid
}
const resetForm = async () => await maFormRef.value.resetFields()
const clearValidate = async () => await maFormRef.value.clearValidate()

const formSubmit = async () => {
    if (await validateForm()) {
        return false
    }
    emit("submit", form.value, done)
}

/**
 * 获取column属性服务类
 * @returns ColumnService
 */
const getColumnService = (strictMode = true) => {
    return new ColumnService(
        {
            columns: flatteningColumns.value,
            cascaders: cascaderList.value,
            dicts: dictList.value,
            refs: dialogRefs.value
        },
        strictMode
    )
}

const getFormRef = () => maFormRef.value
const getDictList = () => dictList.value
const getColumns = () => flatteningColumns.value
const getCascaderList = () => cascaderList.value
const getFormData = () => form.value
const updateOptions = () => (options.value = Object.assign(cloneDeep(defaultOptions), props.options))

provide("options", options.value)
provide("columns", flatteningColumns)
provide("dictList", dictList)
provide("formModel", form)
provide("formLoading", formLoading)
provide("getColumnService", getColumnService)
provide("maFormRef", maFormRef)

defineExpose({
    init,
    getFormRef,
    getColumns,
    getDictList,
    getColumnService,
    getCascaderList,
    getFormData,
    validateForm,
    resetForm,
    clearValidate,
    updateOptions
})
</script>

<style lang="less" scoped>
div:deep(.arco-modal-container) {
    pointer-events: none;
}
:deep(.arco-modal.arco-modal-draggable) {
    pointer-events: auto;
}
.ma-form-title {
    font-size: 18px;
    text-align: center;
}
.alert-container {
    position: fixed;
    bottom: 50%;
    user-select: none;
    width: 113px;
    z-index: 9999;
}
</style>
