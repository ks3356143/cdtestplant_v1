<template>
    <div class="text-table-container">
        <a-modal
            v-model:visible="visible"
            width="50%"
            draggable
            :on-before-ok="handleSyncOk"
            unmount-on-close
            ok-text="确认保存"
            cancel-text="关闭不保存"
            :maskClosable="false"
            @close="handleOnClose"
        >
            <template #title>{{ theTitle }}</template>
            <a-space direction="vertical" fill>
                <a-card title="差异性段落描述" hoverable>
                    <a-textarea auto-size placeholder="请填写差异性分析和'见下表所示'" v-model="description"></a-textarea>
                </a-card>
                <a-card title="表格" hoverable>
                    <WordLikeTable v-model="tableDatas" v-model:fontnote="fontnote" />
                </a-card>
            </a-space>
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { Message } from "@arco-design/web-vue"
import { getCurrentInstance, ref } from "vue"
import { useRoute } from "vue-router"
import WordLikeTable from "./projectModal/wordLikeTable/index.vue"
import { cloneDeep } from "lodash-es"
import projectApi from "@/api/project/project"

const { proxy } = getCurrentInstance() as any
const route = useRoute()

// datas
const description = ref("")
const initialTableData = [
    ["", "", ""],
    ["", "", ""],
    ["", "", ""]
]
const fontnote = ref("")
const tableDatas = ref(initialTableData)

// props
const { reset } = defineProps<{
    reset: () => void
}>()

const visible = ref(false)
const theTitle = ref("")

const handleSyncOk = async () => {
    // 验证输入文字是否为空
    if (description.value.trim().length <= 0) {
        Message.error("请输入分析内容再提交")
        return false
    }
    try {
        // 请求接口
        await projectApi.postEnvAnalysis({
            id: route.query.id,
            table: tableDatas.value,
            fontnote: fontnote.value,
            description: description.value
        })
        Message.success("保存成功")
    } catch (e) {
        return false
    }
}

const handleOnClose = () => {
    // 用来清空数据
    fontnote.value = ""
    description.value = ""
    tableDatas.value = cloneDeep(initialTableData)
    reset()
}

const open = async (category_str: string) => {
    proxy?.$loading?.show("数据加载中...")
    theTitle.value = category_str
    try {
        // 获取数据并赋值给tableData
        const res = await projectApi.getEnvAnalysis(route.query.id)
        if (res.code === 25001) {
            tableDatas.value = res.data.table
            fontnote.value = res.data.fontnote || ""
            description.value = res.data.description || ""
        }
        visible.value = true
    } catch (e) {
    } finally {
        proxy?.$loading?.hide()
    }
}

defineExpose({
    open
})
</script>

<style scoped></style>
