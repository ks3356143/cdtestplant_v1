<template>
    <!-- 注意该组件强制绑定caseTable页面，不要使用在其他地方了 -->
    <div class="replace-person-container">
        <a-modal
            v-model:visible="visible"
            width="40%"
            unmount-on-close
            ok-text="执行替换人员"
            cancel-text="关闭"
            draggable
            :on-before-ok="submitReplace"
        >
            <template #title>替换人员</template>
            <div class="content-container">
                <a-form ref="formRef" :model="formData" scroll-to-first-error>
                    <a-form-item field="designPerson" label="设计人员">
                        <a-select v-model="designPerson">
                            <a-option v-for="person in persons" :key="person" :value="person">
                                {{ person }}
                            </a-option>
                            <a-option value="不替换">不替换</a-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item field="testPerson" label="执行人员">
                        <a-select v-model="testPerson">
                            <a-option v-for="person in persons" :key="person" :value="person">
                                {{ person }}
                            </a-option>
                            <a-option value="不替换">不替换</a-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item field="monitorPerson" label="审核人员">
                        <a-select v-model="monitorPerson">
                            <a-option v-for="person in persons" :key="person" :value="person">
                                {{ person }}
                            </a-option>
                            <a-option value="不替换">不替换</a-option>
                        </a-select>
                    </a-form-item>
                </a-form>
            </div>
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useRoute } from "vue-router"
import userApi from "@/api/system/user"
import { Message } from "@arco-design/web-vue"
import caseApi from "@/api/project/case"

const route = useRoute()
const visible = ref(false)
const formData = ref({})
const designPerson = ref("不替换")
const testPerson = ref("不替换")
const monitorPerson = ref("不替换")
const getSelectedsFunc = ref<any>(() => [])

// props
const { selectRows } = defineProps<{ selectRows: any }>()

// emits
const emit = defineEmits(["modifySuccess"])

// 1.在created时候直接请求后端项目人员信息
const persons = ref([])
async function fetchPersonByProject() {
    const res = await userApi.getProjectList(route.query.id)
    persons.value = res.data.map((it: { name: string }) => it.name)
}
fetchPersonByProject()

// 2.异步执行替换操作，返回boolean-true则关闭弹窗
const submitReplace = async () => {
    // 如果都选择不替换，则不请求
    if (designPerson.value === "不替换" && testPerson.value === "不替换" && monitorPerson.value === "不替换") {
        Message.error("至少选择一项替换")
        return false
    }
    const selecteds = selectRows || getSelectedsFunc.value() || []
    if (selecteds.length && selecteds.length > 0) {
        // 判断是否选择了行
        // 请求后台执行
        await caseApi.personReplace({
            selectRows: selecteds,
            designPerson: designPerson.value,
            testPerson: testPerson.value,
            monitorPerson: monitorPerson.value
        })
        emit("modifySuccess")
        Message.success("批量替换成功...")
        return true
    }
    Message.error("请在表格中选择行...")
    return false
}

// 其他：打开modal
const open = (getFunc: (() => number[]) | undefined) => {
    if (getFunc) getSelectedsFunc.value = getFunc
    designPerson.value = "不替换"
    testPerson.value = "不替换"
    monitorPerson.value = "不替换"
    visible.value = true
}
defineExpose({ open })
</script>

<style lang="less" scoped></style>
