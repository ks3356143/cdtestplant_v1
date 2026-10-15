<template>
    <div class="ma-content-block lg:flex justify-between p-4">
        <div class="lg:w-12/12 w-full lg:ml-4 mt-5 lg:mt-0">
            <!-- CRUD组件 -->
            <ma-crud :options="crudOptions" :columns="crudColumns" ref="crudRef">
                <template #status="{ record }">
                    <a-switch
                        :checked-value="1"
                        :unchecked-value="2"
                        :before-change="changeStatusWrapper(record)"
                        :default-checked="record.status == 1"
                    ></a-switch>
                </template>
            </ma-crud>
        </div>
    </div>
</template>

<script setup>
import { reactive, ref } from "vue"
import userApi from "@/api/system/user"
import user from "@/api/system/user"
import { Message } from "@arco-design/web-vue"
// 切换状态按钮
const changeStatusWrapper = (record) => {
    return async function (newVal) {
        const res = await userApi.changeUserStatus({ user_status: newVal, userId: record.id })
        if (res.data) {
            Message.success(res.data === "1" ? "启用成功" : "禁用成功")
            // 重新刷新页面保持数据一致性
            crudRef.value.refresh()
        }
    }
}
// crud组件
const crudRef = ref()
const crudOptions = reactive({
    // 顶部每行显示列数
    searchColNumber: 3,
    // 不开启table的分页，但开启我们自己的分页器
    tablePagination: false,
    // 是否显示索引列
    showIndex: false,
    // 行选择器
    rowSelection: {
        showCheckedAll: true
    },
    afterDelete(response) {
        crudRef.value.tableRef.selectAll(false)
    },
    // 是否显示操作列
    operationColumn: true,
    operationWidth: 200,
    // 设置列表数据API
    api: userApi.getPageList,
    // 设置新增接口-show为true则显示按钮
    add: {
        show: true,
        api: userApi.save
    },
    edit: {
        show: true,
        api: userApi.update
    },
    delete: {
        show: true,
        api: userApi.delete,
        realApi: user.realDeletes
    },
    recovery: { show: true, api: user.recoverys },
    // 是否开启双击编辑行
    isDbClickEdit: true,
    // 表单布局
    formOption: {
        viewType: "modal"
        // isFull: true
    },
    operationColumnAlign: "center",
    // 用户点击编辑/删除前的hook
    beforeOpenEdit: (record) => {
        if (record.id === 1) {
            Message.error("创始人不可编辑,请关闭窗口！")
            return false
        }
        return true
    },
    beforeDelete: (ids) => {
        if (ids.includes(1)) {
            Message.error("创始人不可删除")
            return false
        }
        return true
    }
})
const crudColumns = reactive([
    { title: "ID", dataIndex: "id", addDisplay: false, editDisplay: false, width: 50, hide: true },
    {
        title: "名称",
        align: "center",
        dataIndex: "name",
        search: true,
        width: 180,
        commonRules: [
            { required: true, message: "名称必填" },
            { maxLength: 50, message: "名称不能超过50个字符" }
        ]
    },
    {
        title: "用户名",
        dataIndex: "username",
        search: true,
        align: "center",
        commonRules: [
            { required: true, message: "用户名必填" },
            { maxLength: 18, message: "用户名不能超过18个字符" },
            { minLength: 5, message: "用户名不能少于5个字符" }
        ]
    },
    {
        title: "角色",
        dataIndex: "role",
        align: "center",
        width: 130,
        formType: "select",
        dict: { name: "user_role", props: { label: "title", value: "key" } },
        addDefaultValue: "user",
        addRules: [{ required: true, message: "角色必选" }]
    },
    {
        title: "密级许可",
        dataIndex: "clearance",
        align: "center",
        width: 130,
        formType: "select",
        dict: { name: "secret", props: { label: "title", value: "key" } },
        // 密级标记由系统安全员在"安全策略"页统一配置（三权分立），管理员仅可查看
        addDisplay: false,
        editDisplay: false
    },
    {
        title: "电话",
        align: "center",
        width: 150,
        dataIndex: "phone",
        search: true,
        commonRules: [{ match: /^1[3|4|5|6|7|8|9][0-9]\d{8}$/, message: "请输入正确的手机号码" }]
    },
    {
        title: "密码",
        dataIndex: "password",
        hide: true,
        autocomplete: "off",
        addDisabled: false,
        editDisabled: true,
        type: "password",
        addRules: [{ required: true, message: "密码必填" }],
        addDefaultValue: "123456",
        editDefaultValue: ""
    },
    {
        title: "状态",
        dataIndex: "status",
        align: "center",
        width: 100,
        search: true,
        formType: "radio",
        dict: { name: "data_status", props: { label: "title", value: "key" } },
        addDefaultValue: "1"
    },
    {
        title: "注册时间",
        dataIndex: "create_datetime",
        align: "center",
        width: 180,
        addDisplay: false,
        editDisplay: false,
        search: true,
        formType: "range"
    }
])

defineOptions({
    name: "usermanage"
})
</script>

<style lang="less" scoped></style>
