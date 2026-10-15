<template>
    <div class="replace-priority-container">
        <modalDom />
    </div>
</template>

<script setup lang="tsx">
import { ref } from "vue"
import { Modal, Form, FormItem, Select, Option, Message } from "@arco-design/web-vue"
import demandApi from "@/api/project/testDemand"
// props
const { selectedRows = undefined } = defineProps<{
    selectedRows?: number[]
}>()

// refs
const visible = ref(false)
const formData = ref({})
const priority = ref("")
const getSelectedsFunc = ref<() => number[]>(() => [])

// emits
const emit = defineEmits(["modifySuccess"])

// 异步提交修改
const submitReplace = async () => {
    // 不再非受控验证，手动验证
    if (priority.value === "") {
        Message.error("请选择优先级后进行提交")
        return false
    }
    const selecteds = selectedRows || getSelectedsFunc.value() || []
    if (selecteds.length && selecteds.length > 0) {
        // 判断是否选择了行
        // 请求后台执行
        await demandApi.priorityReplace({
            selectRows: selecteds as any,
            priority: priority.value
        })
        emit("modifySuccess")
        Message.success("批量替换成功...")
        return true
    }
    Message.error("请在表格中选择行...")
    return false
}

// 弹窗主DOM
const modalDom = () => {
    return (
        <Modal
            v-model={[visible.value, "visible"]}
            width="40%"
            cancel-text="关闭"
            ok-text="确认修改"
            unmount-on-close
            draggable
            on-before-ok={submitReplace}
        >
            {{
                title: () => "批量修改优先级",
                default: () => (
                    <div class="content-container">
                        <Form model={formData.value} scroll-to-first-error>
                            <FormItem field="priority" label="优先级">
                                <Select placeholder="请选择要修改成为的优先级" v-model={priority.value}>
                                    <Option value="1">高</Option>
                                    <Option value="2">中</Option>
                                    <Option value="3">低</Option>
                                </Select>
                            </FormItem>
                        </Form>
                    </div>
                )
            }}
        </Modal>
    )
}

// open expose
const open = (getFunc: (() => number[]) | undefined) => {
    if (getFunc) getSelectedsFunc.value = getFunc
    visible.value = true
}
defineExpose({ open })

// component options
defineOptions({ name: "ReplacePriority" })
</script>

<style lang="less" scoped></style>
