<template>
    <div class="static-dynamic-table-container">
        <a-modal
            v-model:visible="visible"
            width="60%"
            draggable
            :on-before-ok="handleSyncOk"
            unmount-on-close
            ok-text="确认保存"
            cancel-text="关闭不保存"
            :maskClosable="false"
            @close="handleOnClose"
        >
            <template #title>{{ theTitle }}</template>
            <WordLikeTable v-model="tableData" v-model:fontnote="fontnote" v-model:rowRounds="tableDataRound" />
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { Message } from "@arco-design/web-vue"
import { getCurrentInstance, ref } from "vue"
import WordLikeTable from "./projectModal/wordLikeTable/index.vue"
import { useRoute } from "vue-router"
import { cloneDeep } from "lodash-es"
import projectApi from "@/api/project/project"

const { proxy } = getCurrentInstance() as any
const route = useRoute()

// props
const { reset } = defineProps<{
    reset: () => void
}>()

const visible = ref(false)
const theTitle = ref("")

const tableInitValue = [
    ["", "", ""],
    ["", "", ""],
    ["", "", ""]
]

const tableData = ref(tableInitValue)
const fontnote = ref("")

// 新增：一个行属性，附带到tableData中
const tableDataRoundInitValue = tableInitValue.map((_) => ["0"])
const tableDataRound = ref(tableDataRoundInitValue)

const handleSyncOk = async () => {
    // 验证题注是否为空
    if (tableData.value?.length <= 0) {
        Message.error("请输入表格内容再提交")
        return false
    }
    try {
        // 请求接口
        await projectApi.postStaticDynamicItems({
            id: route.query.id,
            category: theTitle.value,
            table: tableData.value,
            fontnote: fontnote.value,
            rounds: tableDataRound.value
        })
        Message.success("保存成功")
    } catch (e) {
        return false
    }
}

const handleOnClose = () => {
    // 用来清空数据
    tableData.value = cloneDeep(tableInitValue)
    fontnote.value = ""
    reset()
}

const open = async (title: string) => {
    proxy?.$loading?.show("数据加载中...")
    theTitle.value = title
    try {
        // 获取数据并赋值给tableData
        const res = await projectApi.getStaticDynamicItems(route.query.id, title)
        if (res.code === 25001) {
            const data = res.data
            tableData.value = data.table
            fontnote.value = data.fontnote || ""
            if (data.rounds && data.rounds.length === tableData.value.length) {
                tableDataRound.value = data.rounds
            } else {
                tableDataRound.value = (data.table || tableInitValue).map(() => ["0"])
            }
        }
        visible.value = true
    } catch (e) {
    } finally {
        proxy?.$loading?.hide()
    }
}

defineExpose({ open })
</script>

<style scoped></style>
