<template>
    <div class="ma-content-block lg:flex justify-between p-4">
        <div class="lg:w-full w-full lg:ml-4 mt-5 lg:mt-0">
            <!-- CRUD组件 -->
            <ma-crud :options="crudOptions" :columns="crudColumns" ref="crudRef">
                <template #ident="{ record }">
                    {{ "PT_" + route.query.ident + "_" + record.ident.padStart(3, "0") }}
                </template>
                <!-- 表格前置扩展槽:添加关联按钮 -->
                <template #tableAfterButtons>
                    <a-button type="outline" status="warning" @click="handleRelatedProblem">
                        <template #icon>
                            <icon-plus-circle />
                        </template>
                        添加关联问题单
                    </a-button>
                </template>
            </ma-crud>
        </div>
        <problem-choose ref="problemchoose" @deleted="related_reload" @relatedOrunrelated="related_reload"></problem-choose>
    </div>
</template>

<script setup lang="jsx">
import { ref } from "vue"
import { useRoute } from "vue-router"
import problemApi from "@/api/project/problem"
import { useTreeDataStore } from "@/store"
import ProblemChoose from "./components/ProblemChoose.vue"
import { Message } from "@arco-design/web-vue"
import getCaseInfoHook from "@/hooks/workarea/currentCasePage"
import { useUserStore } from "@/store"

const treeDataStore = useTreeDataStore()
const userStore = useUserStore()
const route = useRoute()
// hook-获取当前用例信息
const { tempCaseInfo, caseIsNotPassedOrNotExe, fetchCaseOneStatus } = getCaseInfoHook()

// const router = useRouter()
const roundNumber = route.query.key.split("-")[0]
const dutNumber = route.query.key.split("-")[1]
const designDemandNumber = route.query.key.split("-")[2]
const testDemandNumber = route.query.key.split("-")[3]
const caseNumber = route.query.key.split("-")[4]
const crudRef = ref()
const projectId = ref(route.query.id)
const problemchoose = ref()
// ~~~~关联问题单逻辑~~~~
//// 点击关联按钮
const handleRelatedProblem = () => {
    problemchoose.value.open(tempCaseInfo.value)
}
//// 当关联a-modal删除一个问题单时，通知我刷新表格
const related_reload = () => {
    crudRef.value.refresh()
}

const crudOptions = ref({
    api: problemApi.getProblemList,
    add: { show: true, api: problemApi.save, text: "新增问题单" },
    edit: { show: true, api: problemApi.update },
    delete: { show: true, api: problemApi.delete },
    operationColumnAlign: "center", // 操作列居中
    beforeOpenAdd: function () {
        // 0.判断当前用例的是否为未通过/未执行
        if (!caseIsNotPassedOrNotExe()) {
            Message.error("该用例没有缓存或无未通过步骤，请切换页面或设置未通过步骤后添加问题单!")
            return false
        }
        // 1.先判断是否已经有个问题单了，如果有则不让用户创建问题单
        if (crudRef.value.getTableData().length >= 1) {
            Message.error("该用例已经存在问题单了，可在轮次树节点右键添加无关联问题单")
            return false
        }
        // 下面是弹窗的标题路径
        let key_split = route.query.key.split("-")
        let round_key = key_split[0]
        let dut_key = key_split[1]
        let design_key = key_split[2]
        let test_key = key_split[3]
        let case_key = key_split[4]
        let td = treeDataStore.treeData
        crudRef.value.crudFormRef.actionTitle = `${route.query.ident} >
        ${td[round_key].title} > ${td[round_key].children[dut_key].title} >
        ${td[round_key].children[dut_key].children[design_key].title} >
        ${td[round_key].children[dut_key].children[design_key].children[test_key].title} >
        ${td[round_key].children[dut_key].children[design_key].children[test_key].children[case_key].title} > 问题单-`
        return true
    },
    beforeOpenEdit: function (record) {
        let key_split = route.query.key.split("-")
        let round_key = key_split[0]
        let dut_key = key_split[1]
        let design_key = key_split[2]
        let test_key = key_split[3]
        let case_key = key_split[4]
        let td = treeDataStore.treeData
        crudRef.value.crudFormRef.actionTitle = `${route.query.ident} >
        ${td[round_key].title} > ${td[round_key].children[dut_key].title} >
        ${td[round_key].children[dut_key].children[design_key].title} >
        ${td[round_key].children[dut_key].children[design_key].children[test_key].title} >
        ${td[round_key].children[dut_key].children[design_key].children[test_key].children[case_key].title}
        >用例[${record.name}]-`
        return true
    },
    parameters: {
        projectId: route.query.id,
        round: roundNumber,
        dut: dutNumber,
        designDemand: designDemandNumber,
        testDemand: testDemandNumber,
        case: caseNumber
    },
    afterDelete(response) {
        crudRef.value.tableRef.selectAll(false)
    },
    // 请求后置处理-用于新增/删除更新树状的用例关联问题单状态
    afterRequest(tableData) {
        // 调用更新是否有未通过变量
        fetchCaseOneStatus()
        const caseQuery = { key: route.query.key }
        treeDataStore.updateCaseTreeData(caseQuery, route.query.id)
        // 新版本mime必须返回
        return tableData
    },
    showIndex: false,
    operationColumnAlign: "center",
    rowSelection: { showCheckedAll: true },
    searchColNumber: 3,
    tablePagination: false,
    operationColumn: true,
    scroll: { x: "100%", y: "100%" },
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
    }
})
const crudColumns = ref([
    {
        title: "名称",
        align: "left",
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
        width: 200,
        dataIndex: "closeMethod",
        addDefaultValue: [],
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
            // 如果用户选择其他闭环方式
            return <a-space size="mini">{tagObj}</a-space>
        }
    },
    {
        title: "问题描述",
        hide: true,
        search: true,
        align: "center",
        dataIndex: "operation",
        formType: "editor"
    },
    {
        title: "问题影响",
        hide: true,
        align: "center",
        dataIndex: "result",
        formType: "textarea"
    },
    {
        title: "原因分析",
        hide: true,
        align: "center",
        dataIndex: "analysis",
        formType: "textarea"
    },
    {
        title: "影响域分析",
        hide: true,
        align: "center",
        dataIndex: "effect_scope",
        formType: "textarea"
    },
    {
        title: "改正措施",
        hide: true,
        align: "center",
        dataIndex: "solve",
        formType: "textarea"
    },
    {
        title: "回归结果",
        hide: true,
        align: "center",
        dataIndex: "verify_result",
        formType: "editor"
    },
    {
        title: "测试人员",
        dataIndex: "postPerson",
        search: true,
        align: "center",
        formType: "select",
        addDefaultValue: userStore.name,
        commonRules: [{ required: true, message: "测试人员必填" }],
        dict: {
            url: "system/user/list",
            params: { project_id: route.query.id },
            translation: true,
            props: { label: "name", value: "name" }
        }
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

// 暴露给route-view的刷新表格函数
const refreshCrudTable = () => {
    crudRef.value.refresh()
}

defineExpose({ refreshCrudTable })

defineOptions({
    name: "case"
})
</script>

<style lang="less" scoped></style>
