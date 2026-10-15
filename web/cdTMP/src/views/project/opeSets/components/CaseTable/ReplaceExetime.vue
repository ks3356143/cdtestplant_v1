<template>
    <!-- 注意该组件强制绑定caseTable页面，不要使用在其他地方了 -->
    <div class="replace-person-container">
        <a-modal v-model:visible="visible" width="40%" unmount-on-close ok-text="替换执行时间" cancel-text="关闭" draggable :on-before-ok="submitReplace">
            <template #title>替换执行时间</template>
            <div class="content-container">
                <a-form ref="exeTime" :model="formData" scroll-to-first-error>
                    <a-form-item field="exetime" label="执行时间">
                        <a-range-picker v-model="exetime" style="width: 400px" :shortcuts="shortcuts" />
                    </a-form-item>
                </a-form>
            </div>
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { Message } from "@arco-design/web-vue"
import caseApi from "@/api/project/case"
import { isEmpty } from "lodash-es"
import dayjs from "dayjs"

const visible = ref(false)
const formData = ref({})
const exetime = ref<string[]>([])
const getSelectedsFunc = ref<any>(() => [])

// props
const { selectRows } = defineProps<{ selectRows?: any }>()

// emits
const emit = defineEmits(["modifySuccess"])

// 2.异步执行替换操作，返回boolean-true则关闭弹窗
const submitReplace = async () => {
    // 不再非受控验证，手动验证
    if (isEmpty(exetime.value)) {
        Message.error("请选择时间后，进行替换操作")
        return false
    }
    const selecteds = selectRows || getSelectedsFunc.value() || []
    if (selecteds.length && selecteds.length > 0) {
        // 判断是否选择了行
        // 请求后台执行
        try {
            await caseApi.exetimeReplace({
                selectRows: selecteds,
                exetime: exetime.value as any
            })
            emit("modifySuccess")
            Message.success("批量替换成功...")
            return true
        } catch (e) {
            return false
        }
    }
    Message.error("请在表格中选择行...")
    return false
}

// 给时间范围选择器的快捷选择数组
const shortcuts = [
    {
        label: "后六天",
        value: () => [dayjs(), dayjs().add(6, "day")]
    },
    {
        label: "前六天",
        value: () => [dayjs(), dayjs().subtract(6, "day")]
    },
    {
        label: "前后各一周",
        value: () => [dayjs().subtract(7, "day"), dayjs().add(7, "day")]
    }
]

// 其他：打开modal
const open = (getFunc: (() => number[]) | undefined) => {
    if (getFunc) getSelectedsFunc.value = getFunc
    exetime.value = []
    visible.value = true
}
defineExpose({ open })
</script>

<style lang="less" scoped></style>
