<template>
    <div class="project-modal-container">
        <a-modal
            v-model:visible="visible"
            width="80%"
            draggable
            :on-before-ok="handleSyncOk"
            unmount-on-close
            ok-text="确认保存"
            cancel-text="关闭不保存"
            :maskClosable="false"
            @close="handleOnClose"
        >
            <template #title>{{ title }}</template>
            <div class="mb-2">
                <a-space>
                    <a-dropdown>
                        <a-button type="primary">新增元素<icon-plus /></a-button>
                        <template #content>
                            <a-doption @click="addTextRow">文字</a-doption>
                            <a-doption @click="addPicRow">图片</a-doption>
                            <a-doption @click="addTableRow">表格</a-doption>
                        </template>
                    </a-dropdown>
                    <a-alert type="warning" style="height: 32px">段落（文）会在word渲染时自动缩进2个字符</a-alert>
                </a-space>
            </div>
            <a-table :columns="columns" :show-header="false" :data="data" @change="handleChange" :draggable="{ type: 'handle', width: 40 }"> </a-table>
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { ref, getCurrentInstance } from "vue"
import useTable from "./hooks/useTable"
import projectApi from "@/api/project/project"
import { useRoute } from "vue-router"
import { Message } from "@arco-design/web-vue"

const { proxy } = getCurrentInstance() as any

const route = useRoute()

const { reset } = defineProps<{
    reset: () => void
}>()

const visible = ref(false)
const title = ref("")
const category = ref("软件概述")

const { columns, data, handleChange, addTextRow, addPicRow, addTableRow, handleOnClose } = useTable(reset)

// enums - 维护一个obj来储存同类对应的内容
const dictMap = {
    软件概述: {
        createTitle: "软件概述-新增",
        modifyTitle: "软件概述-修改",
        getFunc: projectApi.getSoftSummary,
        postFunc: projectApi.postSoftSummary,
        errorMsg: "获取软件概述失败"
    },
    动态环境描述: {
        createTitle: "动态环境描述-新增",
        modifyTitle: "动态环境描述-修改",
        errorMsg: "获取动态环境描述失败",
        getFunc: projectApi.getDynamicDescription,
        postFunc: projectApi.postDynamicDescription
    }
}

// functions and events
const handleSyncOk = async () => { 
    try {
        await dictMap[category.value].postFunc({ id: route.query.id, data: data.value })
        visible.value = false
        Message.success("保存成功")
    } catch (e) {
        console.log(e);
        Message.error("提交时发送错误，请联系管理员")
    }
    return false
}

const open = async (category_str: string) => {
    proxy?.$loading?.show("数据加载中...")
    category.value = category_str
    const currentCate = dictMap[category.value]
    try {
        const res = await currentCate.getFunc(route.query.id)
        const code = res.code // 25001表示有数据，25002表示没有数据
        title.value = code === 25001 ? currentCate.modifyTitle : currentCate.createTitle
        data.value = res.data
        visible.value = true
    } catch (e) {
        Message.error(currentCate.errorMsg)
    } finally {
        proxy?.$loading?.hide()
    }
}

defineExpose({ open })

defineOptions({
    name: "ProjectModal"
})
</script>

<style scoped></style>
