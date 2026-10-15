<template>
    <div class="search-container">
        <a-spin :loading="searchLoading" class="w-full" tip="正在加载中...">
            <a-form :model="searchForm" layout="inline" label-align="right" ref="searchRef" @submit="handlerSearch">
                <div class="grid w-full lg:grid-cols-3">
                    <template v-for="column in columns" :key="column.dataIndex">
                        <a-form-item
                            class="w-full"
                            :field="column.dataIndex"
                            :label="column.title"
                            :label-col-style="{ minWidth: '80px' }"
                        >
                            <slot :name="`${column.dataIndex}`" v-bind="{ searchForm, column }">
                                <component
                                    :is="getComponentName(column.searchFormType ?? column.formType)"
                                    :component="column"
                                />
                            </slot>
                        </a-form-item>
                    </template>
                </div>
                <div class="text-right mt-1 mr-6 w-full">
                    <a-space>
                        <a-button html-type="submit" type="primary">
                            <template #icon><icon-search /></template>
                            搜索
                        </a-button>
                        <a-button type="outline" @click="resetSearchForm">
                            <template #icon><icon-refresh /></template>
                            重置
                        </a-button>
                    </a-space>
                </div>
            </a-form>
        </a-spin>
        <a-divider></a-divider>
    </div>
</template>

<script setup lang="ts">
import { inject, markRaw, provide, ref } from "vue"
import { Form } from "@arco-design/web-vue"
import MaFormInput from "@/components/ma-crud/components/searchFormItem/form-input.vue"
import MaFormSelect from "@/components/ma-crud/components/searchFormItem/form-select.vue"
import dictApi from "@/api/system/dict"
import type { ISearchForm } from "./types"

const columns = inject("columns") as any // 传入的列信息

const emit = defineEmits(["submit"])

const searchLoading = ref(false)
const searchRef = ref<InstanceType<typeof Form>>()

const searchForm = ref({}) // 搜索表单数据
provide("searchForm", searchForm)

// 点击搜索按钮
const handlerSearch = (data: { values: ISearchForm }) => {
    emit("submit", data.values)
}

// 点击重置按钮
const resetSearchForm = () => {
    searchRef.value.resetFields()
    emit("submit", searchForm.value)
}

// 5.获取搜索框的类型组件
const componentList = ref({
    MaFormInput: markRaw(MaFormInput),
    MaFormSelect: markRaw(MaFormSelect)
})

const getComponentName = (formType: string) => {
    if (["select", "radio", "checkbox", "transfer"].includes(formType)) {
        return componentList.value["MaFormSelect"]
    } else {
        return componentList.value["MaFormInput"]
    }
}

// 6.dicts - 需要根据dict来请求后端
const dicts = ref({})
provide("dicts", dicts)
columns.value.map(async (it: any) => {
    searchLoading.value = true
    // 处理带dict和formType为select的
    if (it.dict && it.formType === "select") {
        const res = await dictApi.getDictByCode({ code: it.dataIndex })
        dicts.value[it.dataIndex] = res.data.map((it) => ({
            label: it.title,
            value: it.key
        }))
    }
    searchLoading.value = false
})
</script>

<style lang="less" scoped>
div:deep(.arco-form-layout-inline) {
    width: 100%;
}
@media (min-width: 1024px) {
    .lg\:grid-cols-1 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
    }
    .lg\:grid-cols-2 {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .lg\:grid-cols-3 {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    .lg\:grid-cols-4 {
        grid-template-columns: repeat(4, minmax(0, 1fr));
    }
    .lg\:grid-cols-5 {
        grid-template-columns: repeat(5, minmax(0, 1fr));
    }
    .lg\:grid-cols-6 {
        grid-template-columns: repeat(6, minmax(0, 1fr));
    }
    .lg\:grid-cols-7 {
        grid-template-columns: repeat(7, minmax(0, 1fr));
    }
    .lg\:grid-cols-8 {
        grid-template-columns: repeat(8, minmax(0, 1fr));
    }
    .lg\:grid-cols-9 {
        grid-template-columns: repeat(9, minmax(0, 1fr));
    }
    .lg\:grid-cols-10 {
        grid-template-columns: repeat(10, minmax(0, 1fr));
    }
    .lg\:grid-cols-11 {
        grid-template-columns: repeat(11, minmax(0, 1fr));
    }
    .lg\:grid-cols-12 {
        grid-template-columns: repeat(12, minmax(0, 1fr));
    }
}
</style>
