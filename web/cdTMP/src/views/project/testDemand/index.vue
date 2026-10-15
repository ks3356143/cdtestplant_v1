<template>
    <div class="ma-content-block lg:flex justify-between p-4">
        <div class="lg:w-full w-full lg:ml-4 mt-5 lg:mt-0">
            <!-- CRUD组件 -->
            <ma-crud
                :options="crudOptions"
                :columns="crudColumns"
                ref="crudRef"
                id="basic-table-case-normal"
                @beforeCancel="handleBeforeCancel"
                :parent-key="route.query.key"
            >
                <template #ident="{ record }">
                    {{ showType(record) }}
                </template>
                <!-- 表格前置扩展槽:添加关联按钮 -->
                <template #tableAfterButtons>
                    <a-space>
                        <a-divider direction="vertical" type="double" />
                        <a-button type="outline" @click="handleReplaceClick">批量替换</a-button>
                        <a-divider direction="vertical" type="double" />
                        <a-button type="outline" @click="handlePerpleModal">批量修改人员</a-button>
                        <a-button type="outline" @click="handleExetimeModal">批量修改时间</a-button>
                    </a-space>
                </template>
            </ma-crud>
        </div>
        <problem-form ref="problemFormRef" :title="title"></problem-form>
        <ReplaceModel
            ref="replaceModal"
            :api="caseApi.replace"
            :columns="[
                { dataIndex: 'name', title: '名称' },
                { dataIndex: 'summarize', title: '用例综述' },
                { dataIndex: 'testStep', title: '测试步骤' }
            ]"
            key="modal-case-normal"
            popup-key="case-normal"
            @replaceSuccess="replaceSuccessHandle"
        />
        <!-- 批量替换人员组件 -->
        <replace-person :selectRows="undefined" @modify-success="crudRef.refresh()" ref="replacePersonModalRef" />
        <!-- 批量替换时间 -->
        <replace-exetime :selectRows="undefined" @modify-success="crudRef.refresh()" ref="replaceExetimeModalRef" />
    </div>
</template>

<script setup lang="jsx">
import { ref } from "vue"
import ProblemForm from "@/views/project/case/components/ProblemForm.vue"
import useCrudOpMore from "./hooks/useCrudOpMore"
import useColumn from "./hooks/useColumn"
import { Message } from "@arco-design/web-vue"
import caseApi from "@/api/project/case"
import { useRoute } from "vue-router"
import ReplaceModel from "@/views/project/opeSets/components/DesignTable/ReplaceModal.vue"
// 批量修改人员
import ReplacePerson from "@/views/project/opeSets/components/CaseTable/ReplacePerson.vue"
// 批量修改时间
import ReplaceExetime from "@/views/project/opeSets/components/CaseTable/ReplaceExetime.vue"

const route = useRoute()
const problemFormRef = ref(null)
const title = ref("问题单表单")
const crudRef = ref()
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

// 批量修改人员
const replacePersonModalRef = ref()
const handlePerpleModal = () => {
    replacePersonModalRef.value.open(crudRef.value.getSelecteds)
}

// 批量修改时间
const replaceExetimeModalRef = ref()
const handleExetimeModal = () => {
    replaceExetimeModalRef.value.open(crudRef.value.getSelecteds)
}

// 标识重新定义
const showType = (record) => {
    let key_string = parseInt(record.key.substring(record.key.lastIndexOf("-") + 1)) + 1
    return "YL-" + record.testType + "-" + record.ident + "-" + key_string.toString().padStart(3, "0")
}

const { handleBeforeCancel, crudOptions } = useCrudOpMore(crudRef)
const crudColumns = useColumn(crudRef, problemFormRef)

// 暴露刷新表格方法给外部
const refreshCrudTable = () => {
    crudRef.value.refresh()
}
defineExpose({ refreshCrudTable })

defineOptions({
    name: "testDemand"
})
</script>

<style lang="less" scoped>
/* 下面让modal的蒙层不交互，让用户可以复制table的文字 */
div:deep(.arco-modal-container) {
    pointer-events: none;
}
:deep(.arco-modal.arco-modal-draggable) {
    pointer-events: auto;
}
</style>
