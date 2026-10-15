<template>
    <a-modal v-model:visible="visible" width="1200px" :footer="false" :mask-closable="false">
        <template #title>{{ title }}</template>
        <!-- crud组件 -->
        <div class="lg:w-full w-full">
            <ma-crud :options="crudOptions" :columns="columns" ref="crudRef">
                <!-- 自定义字段名为 related 的插槽 -->
                <!-- record 当前数据行的数据、column 当前列信息、rowIndex 当前数据行索引 -->
                <template #related="{ record }">
                    <a-switch
                        v-model="record.related"
                        @change="handleRelatedChange(record)"
                        type="round"
                        checked-color="green"
                        unchecked-color="#F53F3F"
                        :loading="loading"
                    >
                        <template #checked> 已关联 </template>
                        <template #unchecked> 未关联 </template>
                    </a-switch>
                </template>
                <!-- ident插槽 -->
                <template #ident="{ record }">
                    {{ "PT_" + route.query.ident + "_" + record.ident.padStart(3, "0") }}
                </template>
                <!-- table按钮后置插槽：这里用于提醒 -->
                <template #tableAfterButtons>
                    <a-alert banner class="alert">
                        表格问题单右键可以查看<span :style="{ color: 'red', fontWeight: 700 }">关联用例信息</span>
                    </a-alert>
                </template>
            </ma-crud>
            <case-modal ref="caseModalRef"></case-modal>
        </div>
    </a-modal>
</template>

<script setup lang="jsx">
// 本组件位置：1.在右键轮次问题单 2.用例界面关联问题单
import { nextTick, ref } from "vue"
import problemApi from "@/api/project/problem"
import problemSingleApi from "@/api/project/singleProblem"
import { Message, Notification } from "@arco-design/web-vue"
import { useRoute } from "vue-router"
import CaseModal from "./CaseModal.vue"
import useTreeStore from "@/store/project/treeData"
import { caseIsPassed } from "@/hooks/workarea/currentCasePage"
const route = useRoute()
const treeStore = useTreeStore()
// 定义props
const props = defineProps({
    hasRelated: {
        type: String,
        default: "relatedProblem"
    },
    title: {
        type: String,
        default: "添加关联问题单"
    }
})
// 定义emits
const emits = defineEmits(["deleted", "relatedOrunrelated"])

// ~~~定义关联的switch-值改变处理~~~ 该函数返回false或返回Promise[reject]则停止切换
/// 定义个switch的加载loading属性
const loading = ref(false)
/// 储存打开时赋值的caseInfo
const caseInfo = ref(null)
const handleRelatedChange = async (record) => {
    // 因为switch绑定了record.related所以可以动态改变
    loading.value = true
    // 判断该用例是否是未通过，如果未执行或已通过则不允许关联问题单
    // 修改：当用户取消关联时应该不判断是否caseIsPassed
    if (record.related && !caseIsPassed(caseInfo.value)) {
        Message.error("该用例没有缓存或无未通过步骤，请切换页面或设置未通过步骤后添加问题单!")
        loading.value = false
        record.related = !record.related
        crudRef.value.refresh()
        return false
    }
    const res = await problemApi
        .relateProblem({
            case_key: route.query.key,
            problem_id: record.id,
            val: record.related
        })
        .catch((err) => {
            // 如果出错则保持不变
            record.related = !record.related
            loading.value = false
        })
    if (res) {
        if (!res.data.isOK) {
            // 后端返回失败则回退switch状态
            record.related = !record.related
            loading.value = false
        }
    }
    loading.value = false
    emits("relatedOrunrelated")
    // 重新刷新表格请求
    crudRef.value.refresh()
}

// 数据定义
const crudRef = ref(null)
const visible = ref(false)
const caseModalRef = ref(null)

// 定义open事件
const open = (row) => {
    nextTick(() => {
        if (props.hasRelated === "roundProblem") {
            const columnService = crudRef.value.getColumnService()
            columnService.get("related").setAttr("hide", true)
            crudRef.value.requestParams = { round_key: row }
            crudRef.value.requestData() // 这里要变化，请求的API变化
            visible.value = true
        }
        if (props.hasRelated === "relatedProblem") {
            crudRef.value.requestData() // 手动请求数据
            visible.value = true
            // 打开时赋值caseInfo
            caseInfo.value = row
        }
    })
}
// crudOptions设置
const crudOptions = ref({
    autoRequest: false, // 取消自己请求数据，后续自己调用方法请求
    api: problemApi.searchAllProblem, // 请求数据的API
    showIndex: false,
    rowSelection: { showCheckedAll: true },
    operationWidth: 160,
    operationColumnAlign: "center",
    add: { show: true, api: problemApi.save, text: "新增无关联用例的问题单" },
    edit: { show: true, api: problemApi.modalupdate },
    delete: { show: true, api: problemApi.delete },
    parameters: {
        projectId: route.query.id,
        key: route.query.key
    },
    operationColumn: true,
    operationColumnAlign: "center", // 操作列居中
    isDbClickEdit: false, // 双击不编辑当前列
    contextMenu: {
        enabled: true,
        items: [
            {
                operation: "scancase",
                icon: "icon-list",
                text: "查看关联用例",
                onCommand: async (args) => {
                    const hang = args.record.hang
                    const problemId = args.record.id
                    if (hang) {
                        Notification.warning("该问题单未关联用例")
                    }
                    const res = await problemSingleApi.getRelativeCases({ id: problemId })
                    caseModalRef.value.open(res.data)
                }
            }
        ]
    },
    bordered: { cell: true },
    formOption: {
        width: 1000,
        layout: [
            {
                formType: "grid",
                customClass: ["mt-0"],
                cols: [
                    { span: 12, formList: [{ dataIndex: "name" }] },
                    { span: 12, formList: [{ dataIndex: "ident" }] }
                ]
            },
            {
                formType: "grid",
                customClass: ["ml-4"],
                cols: [
                    { span: 12, formList: [{ dataIndex: "status" }] },
                    { span: 12, formList: [{ dataIndex: "closeMethod" }] }
                ]
            },
            {
                formType: "grid",
                customClass: ["ml-4"],
                cols: [
                    { span: 12, formList: [{ dataIndex: "grade" }] },
                    { span: 12, formList: [{ dataIndex: "type" }] }
                ]
            },
            {
                formType: "divider"
            },
            {
                formType: "grid",
                cols: [{ span: 24, formList: [{ dataIndex: "operation" }] }]
            },
            {
                formType: "grid",
                cols: [{ span: 24, formList: [{ dataIndex: "result" }] }]
            },
            {
                formType: "divider"
            },
            {
                formType: "grid",
                cols: [{ span: 24, formList: [{ dataIndex: "analysis" }] }]
            },
            {
                formType: "grid",
                cols: [{ span: 24, formList: [{ dataIndex: "effect_scope" }] }]
            },
            {
                formType: "grid",
                cols: [{ span: 24, formList: [{ dataIndex: "solve" }] }]
            },
            {
                formType: "divider"
            },
            {
                formType: "grid",
                cols: [{ span: 24, formList: [{ dataIndex: "verify_result" }] }]
            },
            {
                formType: "divider",
                title: "人员信息"
            },
            {
                formType: "grid",
                cols: [
                    { span: 12, formList: [{ dataIndex: "postPerson" }] },
                    { span: 12, formList: [{ dataIndex: "postDate" }] }
                ]
            },
            {
                formType: "grid",
                cols: [
                    { span: 12, formList: [{ dataIndex: "designerPerson" }] },
                    { span: 12, formList: [{ dataIndex: "designDate" }] }
                ]
            },
            {
                formType: "grid",
                cols: [
                    { span: 12, formList: [{ dataIndex: "verifyPerson" }] },
                    { span: 12, formList: [{ dataIndex: "verifyDate" }] }
                ]
            }
        ]
    },
    // 添加删除后置处理方法：让父组件知道我删除了，你必须刷新表格
    afterDelete(response, record) {
        emits("deleted")
        crudRef.value.tableRef.selectAll(false)
    }
})

// columns数据
const columns = ref([
    {
        title: "名称",
        align: "center",
        search: true,
        dataIndex: "name",
        commonRules: [{ required: true, message: "名称是必填" }],
        validateTrigger: "blur-sm"
    },
    {
        title: "问题标识",
        align: "center",
        sortable: { sortDirections: ["ascend"] },
        width: 140,
        search: true,
        dataIndex: "ident",
        editDisabled: true,
        addDisabled: true,
        addDefaultValue: `${route.query.ident}`,
        validateTrigger: "blur-sm"
    },
    {
        title: "缺陷状态",
        align: "center",
        width: 80,
        search: true,
        dataIndex: "status",
        formType: "radio",
        addDefaultValue: "2",
        commonRules: [{ required: true, message: "缺陷状态是必填" }],
        dict: {
            name: "problemStatu",
            translation: true,
            props: { label: "title", value: "key" },
            tagColors: { 1: "green", 2: "blue", 3: "#FF7D00", 4: "red" }
        }
    },
    {
        title: "缺陷类型",
        align: "center",
        width: 80,
        dataIndex: "type",
        search: true,
        addDefaultValue: "3",
        formType: "radio",
        commonRules: [{ required: true, message: "缺陷类型必选" }],
        dict: {
            name: "problemType",
            translation: true,
            props: { label: "title", value: "key" }
        }
    },
    {
        title: "缺陷等级",
        align: "center",
        width: 80,
        dataIndex: "grade",
        search: true,
        addDefaultValue: "1",
        formType: "radio",
        commonRules: [{ required: true, message: "缺陷等级必填" }],
        dict: {
            name: "problemGrade",
            translation: true,
            props: { label: "title", value: "key" }
        }
    },
    {
        title: "闭环方式",
        align: "center",
        width: 150,
        dataIndex: "closeMethod",
        addDefaultValue: ["2"],
        search: true,
        formType: "checkbox",
        dict: {
            name: "closeMethod",
            translation: true,
            props: { label: "title", value: "key" }
        },
        customRender: ({ record }) => {
            // 判断是否具有1：修改文档
            if (!record.closeMethod.hasOwnProperty("0")) {
                if (!record.closeMethod.hasOwnProperty("1")) {
                    return (
                        <a-tag size="small" bordered color="magenta">
                            未选择闭环
                        </a-tag>
                    )
                }
            }
            const tagObj = []
            for (let item in record.closeMethod) {
                if (record.closeMethod[item] === "1") {
                    tagObj.push(
                        <a-tag size="small" bordered color="blue">
                            修改文档
                        </a-tag>
                    )
                } else if (record.closeMethod[item] === "2") {
                    tagObj.push(
                        <a-tag size="small" bordered color="green">
                            修改程序
                        </a-tag>
                    )
                } else if (record.closeMethod[item] === "3") {
                    tagObj.push(
                        <a-tag size="small" bordered color="red">
                            其他方式闭环
                        </a-tag>
                    )
                }
            }
            return <a-space size="mini">{tagObj}</a-space>
        }
    },
    {
        title: "问题描述",
        hide: true,
        search: false,
        dataIndex: "operation",
        formType: "editor"
    },
    {
        title: "问题影响",
        hide: true,
        dataIndex: "result",
        formType: "textarea"
    },
    {
        title: "原因分析",
        hide: true,
        dataIndex: "analysis",
        formType: "textarea"
    },
    {
        title: "影响域分析",
        hide: true,
        dataIndex: "effect_scope",
        formType: "textarea"
    },
    {
        title: "改正措施",
        hide: true,
        dataIndex: "solve",
        addDefaultValue: "",
        formType: "textarea"
    },
    {
        title: "回归结果",
        hide: true,
        dataIndex: "verify_result",
        formType: "editor"
    },
    {
        title: "测试人员",
        dataIndex: "postPerson",
        search: true,
        hide: true,
        formType: "select",
        commonRules: [{ required: true, message: "测试人员必填" }],
        dict: {
            url: "system/user/list",
            params: { project_id: route.query.id },
            translation: true,
            props: { label: "name", value: "name" }
        }
    },
    {
        title: "悬挂状态",
        dataIndex: "hang",
        search: true,
        formType: "select",
        addDisplay: false,
        editDisplay: false,
        dict: {
            data: [
                { label: "悬挂", value: "1" },
                { label: "已有关联", value: "2" }
            ]
        },
        align: "center",
        customRender: ({ record }) => {
            // 判断是否为悬挂状态record.hang[Boolean]
            let tagObj
            if (record.hang) {
                tagObj = (
                    <a-tag size="small" bordered color="red">
                        悬挂
                    </a-tag>
                )
            } else {
                tagObj = (
                    <a-tag size="small" bordered color="green">
                        有关联用例
                    </a-tag>
                )
            }
            return <a-space size="mini">{tagObj}</a-space>
        }
    },
    {
        title: "是否关联",
        dataIndex: "related",
        align: "center",
        formType: "switch",
        addDisplay: false,
        editDisplay: false
    },
    {
        title: "测试日期",
        hide: true,
        dataIndex: "postDate",
        formType: "date"
    },
    {
        title: "开发人员",
        hide: true,
        dataIndex: "designerPerson",
        formType: "input"
    },
    {
        title: "开发方日期",
        hide: true,
        dataIndex: "designDate",
        formType: "date"
    },
    {
        title: "回归人员",
        hide: true,
        dataIndex: "verifyPerson",
        formType: "select",
        dict: {
            url: "system/user/list",
            params: { project_id: route.query.id },
            translation: true,
            props: { label: "name", value: "name" }
        }
    },
    {
        title: "回归日期",
        hide: true,
        dataIndex: "verifyDate",
        formType: "date"
    }
])

// 暴露自己的open方法
defineExpose({ open })
</script>

<style lang="less" scoped>
.alert {
    max-height: 32px;
    background-color: transparent;
    user-select: none;
}
</style>
