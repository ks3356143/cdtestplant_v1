<template>
    <!-- 完成自定义表格 -->
    <div class="fontnote">
        <a-space class="w-full">
            <span>题注：</span>
            <a-input v-model="fontnote" :style="{ width: '500px' }"></a-input>
        </a-space>
        <a-alert type="warning" class="mt-2"
            >表格第一行为[表头]，和轮次无关均会渲染，自定义表格外例如软/硬件环境、测评数据、环境差异性分析会自动添加[序号]</a-alert
        >
    </div>
    <div class="arco-table arco-table-size-large arco-table-border arco-table-stripe arco-table-hover">
        <div class="arco-table-container">
            <table class="arco-table-element" cellpadding="0" cellspacing="0">
                <thead>
                    <tr class="arco-table-tr">
                        <th class="arco-table-th" v-for="(_, colIndex) in datas![0]" :key="colIndex">
                            <span class="arco-table-cell items-center justify-center">
                                <a-tooltip content="此列后新增列">
                                    <a-button type="text" size="mini" @click="addColumn(colIndex)" class="delete-col-btn">
                                        <template #icon>
                                            <icon-plus />
                                        </template>
                                    </a-button>
                                </a-tooltip>
                                <a-tooltip content="删除该列">
                                    <a-button
                                        type="text"
                                        size="mini"
                                        status="danger"
                                        @click="deleteColumn(colIndex)"
                                        :disabled="datas![0].length <= 1"
                                        class="delete-col-btn"
                                    >
                                        <template #icon>
                                            <icon-close />
                                        </template>
                                    </a-button>
                                </a-tooltip>
                            </span>
                        </th>
                        <th class="arco-table-th w-25" :style="{ textAlign: 'center' }">
                            <span>适应轮次/操作</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="arco-table-tr" v-for="(row, rowIndex) in datas" :key="rowIndex">
                        <td class="arco-table-td" v-for="(col, colIndex) in row" :key="colIndex">
                            <span class="arco-table-cell">
                                <a-textarea auto-size v-model="datas![rowIndex][colIndex]" />
                            </span>
                        </td>
                        <td class="arco-table-td">
                            <span class="arco-table-cell items-center justify-center">
                                <template v-if="datasRounds && rowIndex !== 0">
                                    <a-select size="mini" multiple :style="{ width: '140px' }" placeholder="渲染轮次" v-model="datasRounds![rowIndex]">
                                        <a-option v-for="item in roundOptions" :key="item.value" :value="item.value">{{ item.label }}</a-option>
                                    </a-select>
                                </template>
                                <a-tooltip content="此行后新增行">
                                    <a-button type="text" size="mini" @click="addRow(rowIndex)" class="delete-col-btn">
                                        <template #icon>
                                            <icon-plus />
                                        </template>
                                    </a-button>
                                </a-tooltip>
                                <a-tooltip content="删除该行">
                                    <a-button size="mini" type="text" status="danger" @click="deleteRow(rowIndex)" :disabled="datas!.length <= 1">
                                        <template #icon>
                                            <icon-delete />
                                        </template>
                                    </a-button>
                                </a-tooltip>
                            </span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup lang="ts">
// 从仓库读取有多少轮次
import { computed } from "vue"
import { useTreeDataStore } from "@/store"
// 导入中文轮次数组
import tool from "@/utils/tool"

const treeDataStore = useTreeDataStore()
const treeLength = computed(() => treeDataStore.treeData.length)
const roundOptions = computed(() => Array.from({ length: treeLength.value }, (_, i) => ({ value: String(i), label: tool.chnRoundNameArray[i] })))
// 该组件储存数据
const fontnote = defineModel<string>("fontnote")
const datas = defineModel<string[][]>()
// 这里设置undefined一定要判断了
const datasRounds = defineModel<string[][]>("rowRounds", { default: undefined })
// 行列操作
const deleteRow = (rowIndex: number) => {
    datas.value!.splice(rowIndex, 1)
    if (datasRounds.value) {
        datasRounds.value.splice(rowIndex, 1)
    }
}
const deleteColumn = (colIndex: number) => {
    datas.value!.forEach((row) => {
        row.splice(colIndex, 1)
    })
}
const addRow = (rowIndex: number) => {
    const newRow = new Array(datas.value![0].length).fill("")
    datas.value!.splice(rowIndex + 1, 0, newRow)
    if (datasRounds.value) {
        datasRounds.value.splice(rowIndex + 1, 0, ["0"])
    }
}
const addColumn = (colIndex: number) => {
    // 处理空表格的特殊情况
    if (datas.value!.length === 0) {
        datas.value!.push([""])
        return
    }
    // 新增后续列
    datas.value!.forEach((row) => {
        const insertPosition = colIndex === -1 ? row.length : colIndex + 1
        row.splice(insertPosition, 0, "")
    })
}
</script>

<style scoped lang="less">
.fontnote {
    margin: 10px 0;
    width: 100%;
}

.arco-textarea {
    min-width: 120px;
}

.arco-table-cell {
    padding: 5px;
}
</style>
