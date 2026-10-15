<template>
    <div class="replace-modal-container">
        <a-modal
            v-model:visible="visible"
            :mask="false"
            width="40%"
            unmount-on-close
            ok-text="替换选择的行和列"
            cancel-text="关闭"
            :popup-container="`#basic-table-${popupKey}`"
            draggable
            :on-before-ok="submitReplace"
            :modal-style="{
                boxShadow: '0 0 10px rgba(0, 0, 0, 0.5)'
            }"
        >
            <template #title>替换选择行和列</template>
            <div class="content-container">
                <a-form ref="formRef" :model="formData" scroll-to-first-error>
                    <a-form-item
                        field="selectColumn"
                        label="选择列"
                        show-colon
                        :rules="[{ type: 'array', required: true, message: '至少选择一列数据进行替换' }]"
                    >
                        <a-checkbox-group v-model="formData.selectColumn">
                            <a-checkbox
                                v-for="columnItem in columns"
                                :value="columnItem.dataIndex"
                                :key="columnItem.dataIndex"
                            >
                                {{ columnItem.title }}
                            </a-checkbox>
                        </a-checkbox-group>
                    </a-form-item>
                    <a-form-item
                        field="originText"
                        label="替换内容"
                        show-colon
                        :rules="[{ required: true, message: '请输入被替换文字' }]"
                        :validate-trigger="['change', 'input']"
                    >
                        <a-input v-model="formData.originText" placeholder="请输入替换内容" allow-clear />
                    </a-form-item>
                    <a-form-item field="replaceText" label="替换为" :validate-trigger="['change', 'input']" show-colon>
                        <a-input
                            v-model="formData.replaceText"
                            placeholder="请输入替换为的内容，支持空格则替换为空格"
                            allow-clear
                        />
                    </a-form-item>
                </a-form>
            </div>
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { Form, Message } from "@arco-design/web-vue"
import { useRoute } from "vue-router"

// refs
const visible = ref(false)
const route = useRoute()
// 保存获取选择行的函数
const selectedGetFunc = ref<() => number[] | undefined>(() => [])

// ref
const formRef = ref<InstanceType<typeof Form>>()

// props
/// 已选择的行数据的id列表
const {
    selectRows = undefined,
    columns,
    api,
    popupKey
} = defineProps<{
    selectRows?: number[]
    columns: any[]
    api: Function
    popupKey: string
}>()

// emits
const emit = defineEmits(["replaceSuccess"])

// 1.form表单相关内容
/// 表单初始化数据
const initialFormData = {
    selectColumn: [], // 选择影响的列
    originText: "", // 被替换的文本
    replaceText: "" // 替换的文本
}
/// 定义表单数据
const formData = ref(initialFormData)

// 2.提交替换申请
const submitReplace = async () => {
    // 验证表单
    const validate = await formRef.value.validate()
    if (!validate) {
        // 判断使用selectedRows还是selectedOpenIn
        let selecteds = selectRows || selectedGetFunc.value!() || []
        // 进入这里表示验证通过，手动验证是否选择了行
        if (selecteds.length < 1) {
            // 提示用户需要先选择table的行
            Message.error("您还未选择行...")
            return false
        }
        // 都验证后提交给后端操作
        try {
            // 首先该组件两个地方使用，需要处理key的问题
            const round_key = {
                key: route.query.key as string
            }
            if (round_key.key && round_key.key.split("-").length > 1) {
                round_key.key = round_key.key.split("-")[0]
            }
            const res = await api({
                project_id: route.query.id,
                round_key: round_key.key,
                selectRows: selecteds,
                ...formData.value
            })
            // 批量修改成功放出信号给父组件更新表格
            emit("replaceSuccess", res.data.count)
        } catch (e) {
            return false
        }
        return true
    }
    return false
}

// expose functions
const open = (selectedIdsGetFunc: (() => number[]) | undefined) => {
    // 保存获取用户选择行的函数, 可能是undefined
    if (selectedIdsGetFunc) {
        selectedGetFunc.value = selectedIdsGetFunc
    }
    // 每次打开初始化表单数据
    formData.value = {
        ...initialFormData
    }
    visible.value = true
}
defineExpose({ open })
</script>

<style scoped lang="less"></style>
