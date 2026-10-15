<template>
    <div class="effect-modal-container">
        <a-modal
            v-model:visible="visible"
            width="90%"
            :title="modalTitle"
            unmount-on-close
            ok-text="提交保存"
            cancel-text="取消保存"
            :on-before-ok="handleOk"
            draggable
            @close="handleCloseEnd"
        >
            <div class="mb-1 flex items-center justify-center">
                <a-button type="primary" @click="() => addRow(-1)">+ 新增一行</a-button>
                <a-alert type="warning" style="height: 32px">表格为空提交则清除数据储存</a-alert>
            </div>
            <a-table
                :columns="columns"
                row-key="id"
                :bordered="{
                    wrapper: true,
                    cell: true,
                    headerCell: true,
                    bodyCell: true
                }"
                @change="handleChange"
                :draggable="{ type: 'handle', width: 40 }"
                :data="datas"
            >
                <template #index="{ rowIndex }">
                    {{ rowIndex + 1 }}
                </template>
                <template #changeType="{ rowIndex }">
                    <a-input v-model="datas[rowIndex].change_type"></a-input>
                </template>
                <template #changeDes="{ rowIndex, record }">
                    <ma-editor v-model="datas[rowIndex].change_des" :key="`editor_${record.id}`"></ma-editor>
                </template>
                <template #changeInflu="{ rowIndex }">
                    <a-textarea v-model="datas[rowIndex].change_influ" auto-size></a-textarea>
                </template>
                <template #effectCases="{ rowIndex }">
                    <a-cascader
                        v-model="datas[rowIndex].effect_cases"
                        placeholder="请选择关联用例"
                        size="mini"
                        allow-search
                        allow-clear
                        :loading="cascaderLoading"
                        :options="casOptions"
                        :style="{ width: '180px' }"
                        multiple
                        :tag-nowrap="true"
                        :format-label="format"
                        :field-names="{
                            value: 'key',
                            label: 'label',
                            children: 'children'
                        }"
                    ></a-cascader>
                </template>
                <template #operator="{ rowIndex }">
                    <a-button type="text" status="danger" @click="() => deleteRow(rowIndex)">删除</a-button>
                </template>
            </a-table>
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { ref, inject, getCurrentInstance, nextTick } from "vue"
import useColumns from "../hooks/useColumns"
import { Message, type CascaderOption } from "@arco-design/web-vue"
import MaEditor from "@/components/ma-editor/index.vue"
import caseApi from "@/api/project/case"
import { useRoute } from "vue-router"
import { NodeDataInterface } from "../types"
import { DataInterface } from "./types"
import roundApi from "@/api/project/round"
import useDataOperation from "./useDataOperator"

// props
const { reset } = defineProps<{ reset: () => void }>()

// global
const { proxy } = getCurrentInstance() as any
const route = useRoute()
const nodeData: NodeDataInterface | undefined = inject("nodeData")

// hooks
const { columns } = useColumns()

// vars
const visible = ref(false)
const modalTitle = ref("影响域分析")

// datas
const datas = ref<DataInterface[]>([])
const { handleChange, addRow, deleteRow } = useDataOperation(datas)

// events
const handleOk = async () => {
    // 判断是否change_type是否填写
    if (!datas.value.every((item) => item.change_type.trim().length > 0)) {
        Message.error("请至少填写变更类型")
        return false
    }
    try {
        await roundApi.postInfluence({
            id: route.query.id,
            round_key: nodeData?.key,
            item_list: datas.value
        })
        Message.success("新增或修改成功")
    } catch (e) {
        return false
    }
}

const handleCloseEnd = async () => {
    // Iterator Helper
    datas.value.values().forEach((item) => {
        // 安全地检查并重置 change_des
        if (item && typeof item === "object" && "change_des" in item) {
            item.change_des = ""
        }
    })
    await nextTick()
    // 关闭清除数据
    datas.value = []
    casOptions.value = []
    reset()
}

// component functions
const cascaderLoading = ref(false)
const casOptions = ref([])
const format = (options: CascaderOption[]) => {
    return options.at(-1).label || "未获取用例名称"
}
const open = async () => {
    proxy?.$loading?.show("数据加载中...")
    // 打开时请求级联选择器数据
    try {
        cascaderLoading.value = true
        const res = await caseApi.getRelatedCases(route.query.id, nodeData?.key)
        casOptions.value = res.data
        // 获取影响域分析数据
        const res2 = await roundApi.getInfluence(route.query.id, nodeData?.key)
        if (res2.code !== 25002) {
            // 有影响域分析 - 注意使用了Iterator Helper，老版本浏览器可能会不支持
            datas.value = res2.data
                .values()
                .map((item: any) => ({
                    ...item,
                    id: item.id || `loaded_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
                }))
                .toArray()
        } else {
            Message.info("暂未填写影响域分析，请填写")
        }
    } catch (e) {
    } finally {
        cascaderLoading.value = false
        proxy?.$loading?.hide()
    }
    visible.value = true
}

defineExpose({ open })

defineOptions({
    name: "EffectModal"
})
</script>

<style scoped></style>
