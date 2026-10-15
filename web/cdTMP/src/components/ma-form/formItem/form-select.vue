<template>
    <ma-form-item
        v-if="typeof props.component.display == 'undefined' || props.component.display === true"
        :component="props.component"
        :custom-field="props.customField"
    >
        <slot :name="`form-${props.component.dataIndex}`" v-bind="props.component">
            <a-select
                v-model:model-value="value"
                :options="props.component.data ?? dictList[dictIndex] ?? []"
                :multiple="props.component.multiple"
                :size="props.component.size"
                :allow-clear="props.component.allowClear ?? true"
                :disabled="props.component.disabled"
                :readonly="props.component.readonly"
                :error="props.component.error"
                :placeholder="props.component.placeholder ?? `请选择${props.component.title}`"
                :loading="props.component.loading ?? loading"
                :allow-search="props.component.allowSearch ?? true"
                :allow-create="props.component.allowCreate"
                :max-tag-count="props.component.maxTagCount ?? 1"
                :bordered="props.component.bordered"
                :unmount-on-close="props.component.unmountOnClose"
                :popup-container="props.component.popupContainer"
                :filter-option="props.component.filterOption"
                :virtual-list-props="props.component.virtualListProps"
                :trigger-props="props.component.triggerProps"
                :format-label="props.component.formatLabel"
                :fallback-option="props.component.fallbackOption ?? handlerFallback"
                :show-extra-options="props.component.showExtraOptions ?? false"
                :value-key="props.component.valueKey"
                :search-delay="props.component.searchDelay"
                :limit="props.component.limit"
                :field-names="props.component.fieldNames"
                :scrollbar="props.component.scrollbar"
                @input-value-change="rv('onInputValueChange', $event)"
                @change="handleCascaderChangeEvent($event)"
                @remove="rv('onRemove', $event)"
                @popup-visible-change="rv('onPopupVisibleChange', $event)"
                @dropdown-scroll="rv('onDropdownScroll')"
                @dropdown-reach-bottom="rv('onDropdownReachBottom')"
                @exceed-limit="rv('onExceedLimit', $event)"
                @search="rv('onSearch', $event)"
            >
                <template #header v-if="props.component.multiple && props.component.multipleTools">
                    <div style="padding: 6px 12px">
                        <a-space fill>
                            <a-checkbox
                                v-if="
                                    isBoolean(props.component.multipleTools) || props.component.multipleTools.selectAll
                                "
                                :model-value="checkedAll"
                                :indeterminate="indeterminate"
                                :disabled="loading"
                                @change="handleSelectAll"
                                >全选/清除</a-checkbox
                            >

                            <a-button
                                v-if="isBoolean(props.component.multipleTools) || props.component.multipleTools.inverse"
                                class="ml-2"
                                size="mini"
                                type="outline"
                                :disabled="loading"
                                @click="handleInverse"
                                >反选</a-button
                            >

                            <a-popover
                                :content-style="{ padding: '0px', width: '256px' }"
                                position="rt"
                                trigger="click"
                                v-if="
                                    isBoolean(props.component.multipleTools) ||
                                    props.component.multipleTools.showSelectAll
                                "
                            >
                                <a-button class="ml-2" size="mini">已选 {{ value.length }}</a-button>
                                <template #title>
                                    <a-space fill style="padding: 12px 12px 8px 12px">
                                        <a-button
                                            :disabled="loading || !value.length"
                                            size="mini"
                                            status="danger"
                                            @click="value = []"
                                            >清空 {{ value.length }}</a-button
                                        >
                                        <a-input-search v-model="keyword" size="mini" allow-clear />
                                    </a-space>
                                </template>
                                <template #content>
                                    <a-scrollbar style="height: 200px; overflow: auto">
                                        <a-checkbox-group
                                            v-if="
                                                (value.length && keyword === '') ||
                                                Object.keys(filteredOptions).length > 0
                                            "
                                            direction="vertical"
                                            v-model="value"
                                        >
                                            <div v-for="item in filteredOptions" class="select-all-options">
                                                <a-checkbox :value="item.value">{{ item.label }}</a-checkbox>
                                            </div>
                                        </a-checkbox-group>
                                        <a-empty v-else />
                                    </a-scrollbar>
                                </template>
                            </a-popover>
                        </a-space>
                    </div>
                </template>
                <template #footer v-if="props.component?.dict?.openPage ?? false">
                    <div class="flex justify-center">
                        <a-pagination
                            class="p-2"
                            size="mini"
                            :total="dataTotal"
                            :page-size="props.component.dict.pageOption.pageSize"
                            :disabled="loading"
                            simple
                            @change="handlePage"
                        >
                            <template #page-item-step="{ type }">
                                <div>{{ type === "previous" ? "上一页" : "下一页" }}</div>
                            </template>
                        </a-pagination>
                    </div>
                </template>
                <!-- 改动1、2、3：下面template都是改动内容 -->
                <template #footer v-else-if="component.allowCreate">
                    <div style="padding: 6px 0; text-align: center">
                        <!-- 新增columns属性：onCreate -->
                        <a-popover
                            :title="component.createInfo ? component.createInfo.title : '无标题'"
                            trigger="click"
                        >
                            <a-button size="small" type="primary">点击新增</a-button>
                            <template #content>
                                <a-row :wrap="false">
                                    <a-input
                                        :style="{ width: '320px' }"
                                        :placeholder="`请输入新增的${component.createInfo.title}`"
                                        allow-clear
                                        v-model="createItem"
                                    />
                                    <a-button
                                        type="primary"
                                        @click="handleCreteSubmit(component.onCreate)"
                                        :loading="createLoading"
                                        >提交</a-button
                                    >
                                </a-row>
                            </template>
                        </a-popover>
                    </div>
                </template>
                <template #footer v-else-if="component.allowNew && !component.allowCreate">
                    <div style="padding: 6px 0; text-align: center">
                        <a-popover :title="component.newInfo ? component.newInfo.title : '无标题'" trigger="click">
                            <a-button size="small" type="primary">快速新增</a-button>
                            <template #content>
                                <ma-form
                                    @submit="handleContactFormSubmit"
                                    v-model="contactFormData"
                                    :columns="contactFormOptions"
                                    ref="contactForm"
                                ></ma-form>
                            </template>
                        </a-popover>
                    </div>
                </template>
                <template #footer v-else-if="component.allowAbbrNew && !component.allowCreate && !component.allowNew">
                    <div style="padding: 6px 0; text-align: center">
                        <a-popover
                            :title="component.abbrNewInfo ? component.abbrNewInfo.title : '无标题'"
                            trigger="click"
                        >
                            <a-button size="small" type="primary">快速新增缩略语</a-button>
                            <template #content>
                                <ma-form
                                    @submit="handleAbbrFormSubmit"
                                    v-model="abbrFormData"
                                    :columns="abbrFormOptions"
                                    ref="abbrForm"
                                ></ma-form>
                            </template>
                        </a-popover>
                    </div>
                </template>
                <template
                    #footer
                    v-else-if="
                        component.allowStd && !component.allowAbbrNew && !component.allowCreate && !component.allowNew
                    "
                >
                    <div style="padding: 6px 0; text-align: center">
                        <a-popover :title="component.stdInfo ? component.stdInfo.title : '无标题'" trigger="click">
                            <a-button size="small" type="primary">快速新增依据标准</a-button>
                            <template #content>
                                <ma-form
                                    @submit="handleStdFormSubmit"
                                    v-model="stdFormData"
                                    :columns="stdFormOptions"
                                    ref="stdForm"
                                ></ma-form>
                            </template>
                        </a-popover>
                    </div>
                </template>
            </a-select>
        </slot>
    </ma-form-item>
</template>

<script setup>
import { ref, inject, onMounted, nextTick, watch, computed } from "vue"
import MaFormItem from "./form-item.vue"
import { get, isUndefined, set, xor, isObject, isBoolean } from "lodash-es"
import { runEvent } from "../js/event.js"
import { handlerCascader, loadDict } from "../js/networkRequest.js"
import { Message, Notification } from "@arco-design/web-vue"

// 改动2：快速新增联系单位信息[耦合内容] - start
import { columnsOptions as contactColumnOption } from "@/views/datamanage/projContact/crudColumns"
import { columnsOptions as abbrColumnOption } from "@/views/datamanage/abbreviation/columnsOptions"
import useDictItemCrud from "@/views/datamanage/dictmanage/DataList/useCrudRef.ts"
import tool from "@/utils/tool"
import contactApi from "@/api/system/contact"
import abbrApi from "@/api/system/abbreviation"
import dictApi from "@/api/system/dict"
//// 1. 处理快速新增单位
const contactFormOptions = ref(
    tool.renameKeyInArray(
        contactColumnOption.filter((it) => it.dataIndex !== "id"),
        "commonRules",
        "rules"
    )
)
const contactFormData = ref({})
const handleContactFormSubmit = async (data, done) => {
    done(true)
    try {
        const res = await contactApi.save(data)
        // 更新当前select的选项
        const newInfo = {
            label: res.data.name,
            value: res.data.name,
            disabled: false,
            indeterminate: false
        }
        dictList.value["entrust_unit"].push(newInfo)
        dictList.value["test_unit"].push(newInfo)
        dictList.value["dev_unit"].push(newInfo)
        // 清空当前数据
        contactFormData.value = {}
        Notification.success("添加成功，请回到输入框进行选择")
    } catch (err) {
        Notification.error("请求错误，请重试或在数据管理页面添加")
    } finally {
        done(false)
    }
}
//// 2. 处理快速新增缩略语
const abbrFormOptions = ref(
    tool.renameKeyInArray(
        abbrColumnOption.filter((it) => it.dataIndex !== "id"),
        "commonRules",
        "rules"
    )
)
const abbrFormData = ref({})
const handleAbbrFormSubmit = async (data, done) => {
    done(true)
    try {
        const res = await abbrApi.save(data)
        // 更新当前select的选项
        const newInfo = {
            label: res.data.title,
            value: res.data.title,
            disabled: false,
            indeterminate: false
        }
        dictList.value["abbreviation"].push(newInfo)
        // 清空当前数据
        abbrFormData.value = {}
        Notification.success("添加成功，请回到输入框进行选择")
    } catch (err) {
        Notification.error("请求错误，请重试或在数据管理页面添加")
    } finally {
        done(false)
    }
}
//// 3. 处理快速依据标准
const { columns: dictColumnOptions } = useDictItemCrud()
const initStdFormData = {
    status: "1",
    code: "standard",
    sort: 1
}
const stdFormData = ref(initStdFormData)
const stdFormOptions = computed(() => {
    const options = tool.renameKeyInArray(
        dictColumnOptions.value.filter(
            (it) => it.dataIndex !== "id" && it.dataIndex !== "update_datetime" && it.dataIndex !== "key"
        ),
        "commonRules",
        "rules"
    )
    return options.map((it) => {
        if (it.dataIndex === "doc_name") {
            return {
                ...it,
                rules: [{ required: true, message: "文档名称必填" }]
            }
        }
        if (it.dataIndex === "publish_date") {
            return {
                ...it,
                rules: [{ required: true, message: "发布日期必填" }]
            }
        }
        if (it.dataIndex === "source") {
            return {
                ...it,
                rules: [{ required: true, message: "来源机构必填" }]
            }
        }
        return it
    })
})
const handleStdFormSubmit = async (data, done) => {
    done(true)
    try {
        const res = await dictApi.createDictItemStdFast(data)
        // 更新当前select的选项
        const newInfo = {
            label: res.data.doc_name,
            value: res.data.key,
            disabled: false,
            indeterminate: false
        }
        dictList.value["standard"].push(newInfo)
        // 清空当前数据
        stdFormData.value = { ...initStdFormData }
        Notification.success("添加成功，请回到输入框进行选择")
    } catch (err) {
        Notification.error("请求错误，请重试或在数据管理页面添加")
    } finally {
        done(false)
    }
}
// 改动2结束 - end

const props = defineProps({
    component: Object,
    customField: { type: String, default: undefined }
})

if (isObject(props.component.dict)) {
    props.component.dict.pageOption = {
        page: 1,
        pageSize: props.component?.dict?.pageOption?.pageSize ?? props.component?.dict?.pageSize ?? 15
    }
}

const formModel = inject("formModel")
const dictList = inject("dictList")
const formLoading = inject("formLoading")
const columns = inject("columns")
const getColumnService = inject("getColumnService")
const rv = async (ev, value = "") => {
    await runEvent(props.component, ev, { formModel, getColumnService, columns }, value)
}

const index = props.customField ?? props.component.dataIndex
const dictIndex = index.match(/^(\w+\.)\d+\./)
    ? index.match(/^(\w+\.)\d+\./)[1] + props.component.dataIndex
    : props.component.dataIndex
const value = ref(get(formModel.value, index, ""))
const dataTotal = ref(0)
const loading = ref(false)
const optionMap = ref({})
const keyword = ref("")

// 改动1：新增按钮处理
const createItem = ref("") // 新增string
const createLoading = ref(false) // 新增loading状态
const handleCreteSubmit = async (onCreate) => {
    // 判断是否为空
    if (!createItem.value.trim()) {
        Message.error("请填写新增内容")
        return
    }
    createLoading.value = true
    try {
        const code = await onCreate(createItem.value)
        // 处理回显内容-更新当前select的选项
        const optionList = dictList.value[code]
        const new_dict_item = {
            label: createItem.value,
            value: (optionList.length + 1).toString(),
            disabled: false,
            indeterminate: false
        }
        optionList.push(new_dict_item)
    } catch (err) {
        // 弹出错误
        Message.error("新增出错")
    } finally {
        createItem.value = ""
        createLoading.value = false
        Notification.success("新增成功，请重新选择新增内容")
    }
}
// 改动1结束

watch(
    () => get(formModel.value, index),
    (vl) => (value.value = vl)
)
watch(
    () => value.value,
    (v) => {
        if (props.component.multiple) {
            v.forEach((k) => {
                if (!optionMap.value[k]) {
                    optionMap.value[k] = dictList.value[dictIndex].find((i) => i.value === k)
                }
            })
            for (const k in optionMap.value) {
                if (!v.includes(k)) delete optionMap.value[k]
            }
        }
        set(formModel.value, index, v)
        index.indexOf(".") > -1 && delete formModel.value[index]
    }
)
watch(
    () => dictList.value[index],
    async (v) => {
        dataTotal.value = v?.pageInfo?.total || 0
    }
)

const checkedAll = computed(() => {
    const { multiple, multipleTools } = props.component
    const currentDicts = dictList.value[dictIndex]

    if (multiple && multipleTools && currentDicts) {
        return currentDicts.every((item) => value.value.includes(item.value))
    }

    return false
})

const filteredOptions = computed(() => {
    const { multiple, multipleTools } = props.component
    if (multiple && multipleTools && keyword.value !== "") {
        const lowerCaseKeyword = keyword.value.toLowerCase()
        return Object.values(optionMap.value).filter((option) => option.label.toLowerCase().includes(lowerCaseKeyword))
    }
    return optionMap.value
})

const indeterminate = computed(() => {
    if (props.component.multiple && props.component.multipleTools && checkedAll.value == false) {
        const currentDicts = dictList.value[dictIndex]
        return currentDicts.some((item) => value.value.includes(item.value))
    }
    return false
})

if (value.value === "") {
    value.value = props.component.multiple === true ? [] : ""
} else if (
    !isUndefined(value.value) &&
    props.component.dict &&
    (props.component.dict.name || props.component.dict.data) &&
    !props.component.multiple
) {
    value.value = value.value + ""
}

if (isUndefined(props.component.multipleTools)) props.component.multipleTools = true
const handleSelectAll = (status) => {
    if (isUndefined(value.value)) {
        value.value = []
    }
    if (status) {
        const currentSet = new Set(value.value)
        const newValues = dictList.value[dictIndex]
            .filter((item) => !currentSet.has(item.value))
            .map((item) => item.value)
        value.value = [...value.value, ...newValues]
    } else {
        value.value = []
    }
}

const handleInverse = () => {
    if (isUndefined(value.value)) {
        value.value = []
    }
    const ids = []
    dictList.value[dictIndex].map((item) => ids.push(item.value))
    value.value = xor(value.value, ids)
}

const handlePage = async (page) => {
    loading.value = true
    props.component.dict.pageOption.page = page
    await loadDict(dictList.value, props.component)
    loading.value = false
}

// 搜索当前字典内容
const handlerFallback = (key) => {
    return optionMap.value[key] || key
}
const handleCascaderChangeEvent = async (value) => {
    formLoading.value = true
    const component = props.component
    // 执行自定义事件
    if (component.onChange) {
        rv("onChange", value)
    }

    // 处理联动
    if (!index.match(/^(\w+)\.\d+\./)) {
        await handlerCascader(value, component, columns.value, dictList.value, formModel.value)
    }
    nextTick(() => (formLoading.value = false))
}

rv("onCreated")
onMounted(() => {})
</script>
<style lang="less" scoped>
.arco-checkbox-group {
    width: 100%;
    .select-all-options {
        width: 100%;
        height: 36px;
        padding: 0 15px 0 7px;
        color: inherit;
        background-color: transparent;
        transition: all 0.1s cubic-bezier(0, 0, 1, 1);
        ::v-deep(.arco-checkbox .arco-checkbox-label) {
            height: 36px;
            line-height: 36px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
        &:hover {
            color: var(--color-text-1);
            background-color: var(--color-fill-2);
        }
    }
}
</style>
