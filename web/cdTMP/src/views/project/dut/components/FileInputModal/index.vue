<template>
    <div class="file-input-container">
        <a-modal
            v-model:visible="modalVisible"
            width="80%"
            title="批量导入设计需求"
            :unmount-on-close="true"
            :mask-closable="false"
            ok-text="录入"
            :esc-to-close="false"
            :on-before-ok="handleModalSubmit"
        >
            <div class="uploadContainer">
                <span :style="{ marginBottom: '10px', flex: '0 1 150px' }">上传需求.docx:</span>
                <a-upload
                    :style="{ marginBottom: '10px', marginLeft: '9px' }"
                    :limit="1"
                    accept=".docx"
                    :action="tool.apiUrl(`/api/dut_upload/upload_xq_docx/?parseChapter=${parseChapter}`)"
                    @change="handleUploadChange"
                    @success="handleUploadSuccess"
                    @error="handleUploadError"
                    :disabled="parseChapter.trim() === ''"
                ></a-upload>
            </div>
            <div class="flex items-center gap-3">
                <span class="w-87.5">要解析的章节名称：</span>
                <a-input placeholder="输入要解析的章节名称" v-model="parseChapter"></a-input>
                <span class="w-87.5">选择需求录入类型：</span>
                <a-select allow-search v-model="selectValue">
                    <a-option v-for="item in demandType" :key="item.key" :value="item.key">{{ item.title }}</a-option>
                </a-select>
            </div>
            <a-alert :style="{ margin: '10px 0' }" type="warning">
                只能上传.docx，<span class="important-text">如果有visio图请替换为普通图片上传</span>，请在需求规格说明文档中操作 ->
                <span class="important-text">引用 -> 目录 -> 自定义目录 -> 显示级别改为6</span>以上保存后上传
            </a-alert>
            <div class="operation-container">
                <span :style="{ marginRight: '10px', fontWeight: 700 }">操作按钮:</span>
                <a-space>
                    <a-button type="primary" @click="handleCreateAtLatest">新增一条</a-button>
                    <a-button type="outline" status="warning" @click="handleResetData">重置数据</a-button>
                </a-space>
            </div>
            <a-spin :loading="loading" tip="解析word完成，正在渲染界面..." :style="{ width: '100%' }">
                <div class="demand-container">
                    <a-list @page-change="handlePageChange" :data="htmlData" :pagination-props="{ defaultPageSize: 15, total: htmlData.length }">
                        <template #item="{ item, index }">
                            <a-list-item>
                                <div class="item-container">
                                    <a-input-group>
                                        <a-input placeholder="章节号" v-model="item.chapter" :style="{ width: '100px' }" @click.stop.prevent></a-input>
                                        <a-input placeholder="标题" v-model="item.title" :style="{ width: '300px' }" @click.stop.prevent></a-input>
                                        <a-input placeholder="标识" v-model="item.ident" :style="{ width: '200px' }" @click.stop.prevent></a-input>
                                        <a-select :style="{ width: '150px' }" placeholder="请选择设计需求类型" @click.stop.prevent v-model="item.demandType">
                                            <a-option v-for="it in demandType" :key="it.key" :value="it.key">{{ it.title }}</a-option>
                                        </a-select>
                                    </a-input-group>
                                    <a-button-group>
                                        <a-button type="primary" status="success" size="small" @click.stop.prevent="handledownCreate(index)">
                                            <template #icon>
                                                <icon-plus />
                                            </template>
                                            下方新增
                                        </a-button>
                                        <a-button type="primary" status="danger" size="small" @click.stop.prevent="handleDelete(index)">
                                            <template #icon>
                                                <icon-delete />
                                            </template>
                                            删除该条
                                        </a-button>
                                    </a-button-group>
                                </div>
                                <div class="content">
                                    <MaEditor v-model="item.content" />
                                </div>
                            </a-list-item>
                        </template>
                    </a-list>
                </div>
            </a-spin>
        </a-modal>
    </div>
</template>

<script setup>
import { ref, watch } from "vue"
import dictApi from "@/api/system/dict"
import demandApi from "@/api/project/designDemand"
import { useRoute } from "vue-router"
import { useTreeDataStore } from "@/store"
import MaEditor from "@/components/ma-editor/index.vue"
import { Message } from "@arco-design/web-vue"
import tool from "@/utils/tool"
import useUpload from "./useUpload"
import useListOperaton from "./useListOperation"
// 定义录入完毕的事件，给父组件刷新表格
const emit = defineEmits(["enterFinish"])
// 其他初始化数据
const route = useRoute()
const treeDataStore = useTreeDataStore()
// ~~~刚开始就加载字典数据，给选择框使用~~~
const demandType = ref([])
const getDictDemandType = async function () {
    const res = await dictApi.getDictByCode({ code: "demandType" })
    demandType.value = res.data
}
getDictDemandType()
// 弹窗显示ref
const modalVisible = ref(false)
// 全部html数据-给a-list展示
const htmlData = ref([])

// ~~~~1.list~~~~
const { loading, handleCreateAtLatest, handleResetData, handledownCreate, handlePageChange, handleDelete } = useListOperaton(htmlData)

// ~~~~2.upload~~~~
const { handleUploadSuccess, handleUploadError, parseChapter, selectValue } = useUpload(htmlData)

// 打开弹窗并初始化form数据
const open = function () {
    // 打开时候传入对象可初始化from
    modalVisible.value = true
}
// 为了性能，监听modal关闭则清空数据
watch(
    () => modalVisible.value,
    (newValue) => {
        if (!newValue) {
            htmlData.value = []
        }
    }
)
// 提交事件
const handleModalSubmit = async () => {
    if (!htmlData.value.length) {
        Message.error("请添加设计需求后再提交...")
        return false
    }
    // 校验每一条需要填写的字段
    for (let i = 0; i < htmlData.value.length; i++) {
        const item = htmlData.value[i]
        const idx = i + 1 // 第几条，用户友好提示
        if (!item.chapter?.trim()) {
            Message.error(`第 ${idx} 条需求的章节号不能为空`)
            return false
        }
        if (!item.title?.trim()) {
            Message.error(`第 ${idx} 条需求的标题不能为空`)
            return false
        }
        // 标识、内容都可以为空
        if (!item.demandType) {
            Message.error(`第 ${idx} 条需求的设计需求类型不能为空`)
            return false
        }
        // content 可以为空，不校验
    }
    const res = await demandApi.multiSave({
        projectId: route.query.id,
        key: route.query.key,
        data: htmlData.value
    })
    if (res.code === 200) {
        treeDataStore.updateDesignDemandTreeData(res.data, route.query.id)
        // 给父元素说明我已经完成了
        emit("enterFinish")
        Message.success("批量新增设计需求成功...")
        return true
    }
    return false
}

// 当upload组件发生变化时候-性能配置
const handleUploadChange = (files) => {
    files.length ? (files.length = 1) : (htmlData.value = [])
}

// 暴露该组件ref的方法
defineExpose({ open })
</script>

<style lang="less" scoped>
.uploadContainer {
    display: flex;
    align-items: center;
    & span {
        font-size: 1em;
        font-weight: 700;
    }
}
.demand-container {
    width: 100%;
    height: 55vh;
    padding: 5px;
    overflow: auto;
}
.operation-container {
    margin-bottom: 5px;
}
.important-text {
    font-weight: 700;
    color: red;
}
.item-container {
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 5px 5px;
    border: 1px solid #ccc;
    border-bottom: none;
}
</style>
