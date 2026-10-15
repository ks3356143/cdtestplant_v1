<template>
    <div class="ma-content-block lg:flex justify-between p-4">
        <div class="lg:w-full w-full lg:ml-4 mt-5 lg:mt-0">
            <!-- CRUD组件 -->
            <ma-crud
                :options="crudOptions"
                :columns="crudColumns"
                ref="crudRef"
                id="basic-table-demand-normal"
                @beforeCancel="handleBeforeCancel"
                :parent-key="route.query.key"
            >
                <template #ident="{ record }">
                    {{ showType(record) }}
                </template>
                <!-- 表格前置扩展槽:添加关联按钮 -->
                <template #tableAfterButtons>
                    <a-space>
                        <a-button type="outline" status="warning" @click="handleOpenRelationCSX">
                            <template #icon>
                                <icon-tags />
                            </template>
                            关联测试项
                        </a-button>
                        <a-divider direction="vertical" type="double" />
                        <a-button type="outline" @click="handleReplaceClick">批量替换</a-button>
                        <a-divider direction="vertical" type="double" />
                        <a-button type="outline" @click="handleOpenReplacePriority">批量修改优先级</a-button>
                        <a-divider direction="vertical" type="double" />
                        <AiButton @click="handleAiButtonClick" />
                    </a-space>
                </template>
                <!-- 版本字段的插槽 -->
                <template #inputPrepend-ident> XQ_XX_ </template>
            </ma-crud>
        </div>
        <!-- 关联的modal组件 -->
        <a-modal v-model:visible="visible" width="700px" draggable unmount-on-close :on-before-ok="handleRelatedOk">
            <template #title>关联测试项</template>
            <div class="pb-3">已存在的关联项:</div>
            <a-typography-paragraph>
                <ol class="ol-reset">
                    <li v-for="item in computedRelatedData">{{ item }}</li>
                </ol>
            </a-typography-paragraph>
            <div class="pb-3">选择关联的测试需求项:</div>
            <a-cascader
                :options="options"
                multiple
                allow-search
                placeholder="暂无关联测试项，请选择..."
                :loading="cascaderLoading"
                v-model:model-value="relatedData"
            />
        </a-modal>
        <ReplaceModel
            ref="replaceModal"
            :api="demandApi.replace"
            :columns="[
                { dataIndex: 'ident', title: '标识' },
                { dataIndex: 'name', title: '名称' },
                { dataIndex: 'testDesciption', title: '测试描述' },
                { dataIndex: 'testContent', title: '测试子项' }
            ]"
            key="modal-demand-normal"
            popup-key="demand-normal"
            @replaceSuccess="replaceSuccessHandle"
        />
        <!-- 批量修改优先级 -->
        <ReplacePriority @modifySuccess="crudRef.refresh()" ref="replacePriorityRef" />
        <!-- AI-Modal -->
        <AiModal @updateTable="handleAiRefresh" v-model:visible="ai_modal_visible"></AiModal>
    </div>
</template>

<script setup>
import { ref } from "vue"
import commonApi from "@/api/common"
import { useRoute } from "vue-router"
import { Message } from "@arco-design/web-vue"
import AiButton from "@/components/ai-button/index.vue"
import AiModal from "./AiModal.vue"
// hooks
import { useTreeDataStore } from "@/store"
import useCrudOpMore from "./hooks/useCrudOpMore"
import useColumn from "./hooks/useColumns"
import useRalateDemand from "./hooks/useRalateDemand"
import demandApi from "@/api/project/testDemand"
import ReplaceModel from "@/views/project/opeSets/components/DesignTable/ReplaceModal.vue"
import ReplacePriority from "@/views/project/opeSets/components/DemandTable/ReplacePriority.vue"

// inits
const route = useRoute()
const treeDataStore = useTreeDataStore()

// refs
const crudRef = ref(null)

// 2025年5月新增
const replaceModal = ref()
const handleReplaceClick = () => {
    replaceModal.value?.open(crudRef.value.getSelecteds) // 把获取选中行的函数给传递给替换组件
}
const replaceSuccessHandle = async (count) => {
    Message.success(`批量更新成功，尝试更新行数：${count}`)
    // 批量更新后刷新表格
    crudRef.value.refresh()
}

// 2025-05新增-批量修改优先级
const replacePriorityRef = ref(null)
const handleOpenReplacePriority = () => {
    replacePriorityRef.value?.open(crudRef.value.getSelecteds)
}

// 根据传参获取key，分别为轮次、设计需求的key
const { projectId, crudOptions, handleBeforeCancel } = useCrudOpMore(crudRef)
const crudColumns = useColumn(crudRef)

// 关联弹窗、关联的事件处理
const { visible, relatedData, options, cascaderLoading, computedRelatedData, handleOpenRelationCSX, handleRelatedOk } = useRalateDemand(projectId)

// 标识显示字段
const testTypeDict = ref([])
!(function () {
    commonApi.getDict("testType").then((res) => {
        testTypeDict.value = res
    })
})()
const showType = (record) => {
    let len = testTypeDict.value.data.length
    for (let i = 0; i < len; i++) {
        if (testTypeDict.value.data[i].key === record.testType) {
            let item = testTypeDict.value.data[i]
            return "XQ-" + item.show_title + "-" + record.ident
        }
    }
}

// AI-MODAL
const ai_modal_visible = ref(false)
const handleAiButtonClick = () => {
    ai_modal_visible.value = true
}
const handleAiRefresh = () => {
    refreshCrudTable()
}
// 暴露给route-view的刷新表格函数
const refreshCrudTable = () => {
    crudRef.value.refresh()
    treeDataStore.updateTestDemandTreeData({ key: route.query.key + "-0" }, projectId.value)
}
defineExpose({ refreshCrudTable })
defineOptions({
    name: "designDemand"
})
</script>

<style lang="less" scoped>
.ol-reset {
    list-style: auto;
}
/* 下面让modal的蒙层不交互，让用户可以复制table的文字 */
div:deep(.arco-modal-container) {
    pointer-events: none;
}
:deep(.arco-modal.arco-modal-draggable) {
    pointer-events: auto;
}
</style>
