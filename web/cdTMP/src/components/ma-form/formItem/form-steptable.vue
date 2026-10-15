<template>
    <!-- 组件外部的 form-item -->
    <ma-form-item
        v-if="typeof props.component.display == 'undefined' || props.component.display === true"
        :component="props.component"
        :custom-field="props.customField"
    >
        <slot :name="`form-${props.component.dataIndex}`" v-bind="props.component">
            <!-- 调用自己开发的自定义组件，具体名称改成自己的 -->
            <ChenDemandList v-model="value"></ChenDemandList>
        </slot>
    </ma-form-item>
</template>

<script setup>
// ~~~~start~~~~
import ChenDemandList from "../Customs/ChenDemandList.vue"
// ~~~~end~~~~
import { ref, inject, onMounted, watch } from "vue"
// 引入处理索引的函数
import { get, set } from "lodash-es"
// 引入 MaFormItem 组件
import MaFormItem from "./form-item.vue"
// 引入处理事件的函数
import { maEvent } from "../js/formItemMixin.js"
// 组件都需要定义以下的props
const props = defineProps({
    component: Object,
    customField: { type: String, default: undefined }
})
// form数据列表
const formModel = inject("formModel")
// 该组件在form数据的索引名称
const index = props.customField ?? props.component.dataIndex
// 该组件的表单数据
const value = ref(get(formModel.value, index))

// 监听组件数据的改变
watch(
    () => get(formModel.value, index),
    (vl) => (value.value = vl)
)
watch(
    () => value.value,
    (v) => set(formModel.value, index, v)
)

// 绑定组件事件
maEvent.handleCommonEvent(props.component, "onCreated")
onMounted(() => {
    maEvent.handleCommonEvent(props.component, "onMounted")
})
</script>
