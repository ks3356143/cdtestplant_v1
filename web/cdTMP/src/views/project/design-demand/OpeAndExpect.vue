<template>
    <div class="arco-table arco-table-size-large arco-table-border arco-table-stripe arco-table-hover">
        <div class="arco-table-container">
            <table class="arco-table-element" cellpadding="0" cellspacing="0">
                <thead>
                    <tr class="arco-table-tr">
                        <th class="arco-table-th" :width="400">
                            <span class="arco-table-cell arco-table-cell-align-center">
                                <span class="arco-table-th-title label">操作</span>
                            </span>
                        </th>
                        <th class="arco-table-th" :width="400">
                            <span class="arco-table-cell arco-table-cell-align-center">
                                <span class="arco-table-th-title label">预期</span>
                            </span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="arco-table-tr" v-for="(record, idx) in modelValue" :key="idx">
                        <td class="arco-table-td">
                            <span class="arco-table-cell arco-table-cell-align-center">
                                <a-textarea auto-size placeholder="请填写步骤" v-model="record.operation"></a-textarea>
                            </span>
                        </td>
                        <td class="arco-table-td">
                            <span class="arco-table-cell arco-table-cell-align-center">
                                <a-textarea auto-size placeholder="请填写预期" v-model="record.expect"></a-textarea>
                            </span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup lang="ts">
const modelValue = defineModel<
    {
        operation: string
        expect: string
    }[]
>()
</script>

<style scoped></style>
