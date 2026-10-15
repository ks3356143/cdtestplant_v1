<template>
    <div class="ma-content-block lg:flex justify-between p-4">
        <div class="lg:w-full w-full lg:ml-4 mt-5 lg:mt-0">
            <!-- CRUD组件 -->
            <ma-crud id="basic-table-design-normal" :options="crudOptions" :columns="crudColumns" ref="crudRef" :parent-key="route.query.key">
                <template #ident="{ record }">
                    {{ showType(record) }}
                </template>
                <template #tableAfterButtons>
                    <a-space>
                        <a-button status="success" type="outline" @click="handleAddFileInputDemand" v-if="isXQ === 'XQ'">
                            <template #icon>
                                <icon-plus />
                            </template>
                            上传需求规格说明快捷录入
                        </a-button>
                        <a-divider direction="vertical" type="double" />
                        <a-dropdown-button type="primary" @click="handleBatchCreate">
                            批量建设计需求
                            <template #icon>
                                <icon-down />
                            </template>
                            <template #content>
                                <a-doption @click="handleBatchDemandCreate">批量创建测试项</a-doption>
                                <a-doption @click="handleBatchCaseCreate">批量创建测试用例</a-doption>
                            </template>
                        </a-dropdown-button>
                        <a-button type="outline" @click="handleReplaceClick">批量替换</a-button>
                    </a-space>
                </template>
                <!-- 字段的前缀后缀的插槽 -->
                <!-- 版本字段的插槽 -->
                <template #inputPrepend-ident> SJ-XX- </template>
                <!-- 操作列前置插槽 -->
                <template #operationBeforeExtend="{ record }">
                    <a-link @click="handleCopyCurrentNode($event, record)" :loading="copyLoading"><icon-copy />复制当前</a-link>
                </template>
            </ma-crud>
        </div>
        <file-input-modal ref="fileInputRef" @enterFinish="crudRef.refresh()"></file-input-modal>
        <!-- 批量替换组件 -->
        <ReplaceModel
            ref="replaceModal"
            :api="designApi.replace"
            :columns="[
                { dataIndex: 'ident', title: '标识' },
                { dataIndex: 'name', title: '名称' },
                { dataIndex: 'chapter', title: '章节号' },
                { dataIndex: 'description', title: '需求描述' }
            ]"
            key="modal-design-normal"
            popup-key="design-normal"
            @replaceSuccess="replaceSuccessHandle"
        />
        <!-- 批量新增设计需求组件 -->
        <BatchDesginCreate ref="batchCreateRef" :typeDict="demandTypeDict" @batchCreateFinish="refreshCrudTable" />
        <!-- 批量创建测试项组件 -->
        <BatchDemandCreate ref="batchCreateDemandRef" @batchDemandCreateComplete="refreshCrudTable" />
        <!-- 批量创建测试用例组件 -->
        <BatchCaseCreate ref="batchCreateCaseRef" @batchCaseCreateComplete="refreshCrudTable" />
    </div>
</template>

<script setup>
import { ref } from "vue"
import { useTreeDataStore } from "@/store"
import useCrudOptions from "@/views/project/dut/hooks/useCrudOptions"
import useColumns from "@/views/project/dut/hooks/useColumns"
import { Message } from "@arco-design/web-vue"
import { useRoute } from "vue-router"
import dutApi from "@/api/project/dut"
import designApi from "@/api/project/designDemand"
import commonApi from "@/api/common"
import FileInputModal from "./components/FileInputModal/index.vue"
import ReplaceModel from "@/views/project/opeSets/components/DesignTable/ReplaceModal.vue"
import BatchDesginCreate from "@/views/project/components/BatchDesignCreate"
import BatchDemandCreate from "@/views/project/components/BatchDemandCreate/index.vue"
import BatchCaseCreate from "@/views/project/components/BatchCaseCreate/index.vue"

const route = useRoute()
const crudRef = ref()
const projectId = ref(route.query.id)
const treeDataStore = useTreeDataStore()

// 5月28日新增功能：替换
const replaceModal = ref()
// 12月16日新增功能：批量添加
const batchCreateRef = ref()
const batchCreateDemandRef = ref()
const batchCreateCaseRef = ref()

const handleReplaceClick = () => {
    replaceModal.value?.open(crudRef.value.getSelecteds) // 把获取选中行的函数给传递给替换组件
}

const replaceSuccessHandle = async (count) => {
    Message.success(`批量更新成功，尝试更新行数：${count}`)
    // 批量更新后刷新表格
    crudRef.value.refresh()
}

// 5月8日修改设计需求标识就按SJ-FT-设计需求标识来
const demandTypeDict = ref([])
;(function () {
    commonApi.getDict("demandType").then((res) => {
        demandTypeDict.value = res
    })
})()

// 5月31日更新，获取当前dut的类型，以判断是否显示“需求录入”的按钮
const isXQ = ref("")
async function isXQdemand() {
    const res = await dutApi.getDutType({ key: route.query.key, project_id: projectId.value })
    isXQ.value = res.data.dut_type
}
isXQdemand()

const showType = (record) => {
    let len = demandTypeDict.value.data.length
    for (let i = 0; i < len; i++) {
        if (demandTypeDict.value.data[i].key === record.demandType) {
            let item = demandTypeDict.value.data[i]
            return "SJ-" + item.show_title + "-" + record.ident
        }
    }
}
// crud组件
const crudOptions = useCrudOptions(crudRef)
const crudColumns = useColumns(crudRef)

// ~~~大功能打开ma-form-modal~~~
const fileInputRef = ref(null)
const handleAddFileInputDemand = () => {
    fileInputRef.value.open()
}

// ~~~批量新增设计需求弹窗~~~
const handleBatchCreate = () => {
    batchCreateRef.value.open({})
}

// ~~~批量新增测试项弹窗~~~
const handleBatchDemandCreate = () => {
    batchCreateDemandRef.value.open({})
}

// ~~~批量新增测试用例弹窗~~~
const handleBatchCaseCreate = () => {
    batchCreateCaseRef.value.open({})
}

// 复制设计需求到当前dut
const copyLoading = ref(false)
const handleCopyCurrentNode = async (_, record) => {
    copyLoading.value = true
    try {
        await designApi.copy_current({ dut_id: record.dut.id, design_id: record.id })
        // 复制成功给提示
        Message.success("复制成功!")
        refreshCrudTable()
        treeDataStore.updateDesignDemandTreeData({ key: record.key }, projectId.value)
    } catch (e) {
        console.log("复制失败，后台打印错误：", e)
    } finally {
        copyLoading.value = false
    }
}

const refreshCrudTable = () => {
    crudRef.value.refresh()
}
defineExpose({ refreshCrudTable })

defineOptions({
    name: "dut"
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
