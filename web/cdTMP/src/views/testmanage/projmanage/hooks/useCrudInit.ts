import { ref } from "vue"
import { validateBlank, validateWindowFileNameInput } from "@/utils/extensions/arcoValidator"
import textInfo from "@/config/textInfo"
import projectApi from "@/api/testmanage/project"
import dictApi from "@/api/system/dict"

const useCrudInit = function () {
    const crudRef = ref()
    const crudOptions = ref({
        rowSelection: { showCheckedAll: true },
        api: projectApi.getPageList,
        add: { show: true, api: projectApi.save, text: "新增项目" },
        edit: { show: true, api: projectApi.update, text: "编辑" }, // auth未空数组则所有都可以
        delete: { show: true, api: projectApi.delete },
        searchColNumber: 3,
        tablePagination: false,
        operationColumn: true,
        operationWidth: 500,
        showIndex: false,
        operationColumnWidth: 400, // 操作列宽度
        operationColumnAlign: "center", // 操作列对齐方式
        afterDelete(response: any) {
            crudRef.value.tableRef.selectAll(false)
        },
        // 处理弹窗的title
        beforeOpenAdd: function () {
            crudRef.value.crudFormRef.actionTitle = "项目"
            return true
        },
        beforeOpenEdit: function (record: any) {
            crudRef.value.crudFormRef.actionTitle = record.ident + "：" + record.name
            return true
        },
        formOption: {
            isFull: true,
            layout: [
                {
                    formType: "grid",
                    cols: [
                        { span: 8, formList: [{ dataIndex: "ident" }] },
                        { span: 8, formList: [{ dataIndex: "name" }] }
                    ]
                },
                {
                    formType: "divider"
                },
                {
                    formType: "grid",
                    cols: [
                        { span: 6, formList: [{ dataIndex: "beginTime" }] },
                        { span: 6, formList: [{ dataIndex: "endTime" }] },
                        { span: 6, formList: [{ dataIndex: "duty_person" }] },
                        { span: 6, formList: [{ dataIndex: "runtime" }] },
                        { span: 12, formList: [{ dataIndex: "member" }] },
                        { span: 6, formList: [{ dataIndex: "soft_type" }] },
                        { span: 6, formList: [{ dataIndex: "devplant" }] },
                        { span: 6, formList: [{ dataIndex: "abbreviation" }] },
                        { span: 6, formList: [{ dataIndex: "quality_person" }] },
                        { span: 6, formList: [{ dataIndex: "vise_person" }] },
                        { span: 6, formList: [{ dataIndex: "config_person" }] }
                    ]
                },
                {
                    formType: "grid",
                    cols: [
                        { span: 6, formList: [{ dataIndex: "security_level" }] },
                        { span: 6, formList: [{ dataIndex: "language" }] },
                        { span: 12, formList: [{ dataIndex: "plant_type" }] }
                    ]
                },
                {
                    formType: "grid",
                    cols: [{ span: 24, formList: [{ dataIndex: "test_level" }] }]
                },
                {
                    formType: "grid",
                    cols: [{ span: 24, formList: [{ dataIndex: "report_type" }] }]
                },
                {
                    formType: "grid",
                    cols: [{ span: 24, formList: [{ dataIndex: "standard" }] }]
                },
                {
                    formType: "grid-tailwind",
                    customClass: ["mt-0"],
                    colNumber: 3,
                    cols: [
                        {
                            formList: [
                                {
                                    formType: "card",
                                    title: "委托方信息",
                                    customClass: ["mt-3", "mb-5", "mx-1"],
                                    formList: [
                                        { dataIndex: "entrust_unit" },
                                        { dataIndex: "entrust_contact" },
                                        { dataIndex: "entrust_contact_phone" },
                                        { dataIndex: "entrust_email" }
                                    ]
                                }
                            ]
                        },
                        {
                            formList: [
                                {
                                    formType: "card",
                                    title: "研制方信息",
                                    customClass: ["mt-3", "mb-5", "mx-1"],
                                    formList: [
                                        { dataIndex: "dev_unit" },
                                        { dataIndex: "dev_contact" },
                                        { dataIndex: "dev_contact_phone" },
                                        { dataIndex: "dev_email" }
                                    ]
                                }
                            ]
                        },
                        {
                            formList: [
                                {
                                    formType: "card",
                                    title: "测评中心信息",
                                    customClass: ["mt-3", "mb-5", "mx-1"],
                                    formList: [
                                        { dataIndex: "test_unit" },
                                        { dataIndex: "test_contact" },
                                        { dataIndex: "test_contact_phone" },
                                        { dataIndex: "test_email" }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    })

    // CRUD-CLOMNS
    const crudColumns = ref([
        {
            title: "项目标识",
            align: "center",
            width: 80,
            sortable: { sortDirections: ["ascend"] },
            dataIndex: "ident",
            search: true,
            commonRules: [
                { required: true, message: "标识是必填" },
                { validator: validateBlank, message: "标识格式不正确" },
                { validator: validateWindowFileNameInput }
            ],
            validateTrigger: "blur-sm"
        },
        {
            title: "项目名称",
            width: 120,
            align: "center",
            dataIndex: "name",
            search: true,
            commonRules: [{ required: true, message: "名称是必填" }]
        },
        {
            title: "开始日期",
            dataIndex: "beginTime",
            align: "center",
            commonRules: [{ required: true, message: "开始时间必填" }],
            formType: "date",
            width: 110
        },
        {
            title: "结束时间",
            align: "center",
            dataIndex: "endTime",
            formType: "date",
            width: 110,
            extra: "注意：结束时间需要晚于最后一轮结束时间",
            commonRules: [
                {
                    required: true,
                    message: "结束时间必填"
                },
                {
                    validator: (value: any, validationCallbackFunction: any) => {
                        let beginTime = crudRef.value.getFormData().beginTime
                        value < beginTime ? validationCallbackFunction("开始时间必须小于等于结束时间") : null
                    }
                }
            ]
        },
        {
            title: "时间范围",
            hide: true,
            dataIndex: "searchOnlyTimeRange",
            search: true,
            addDisplay: false,
            editDisplay: false,
            infoShow: false,
            formType: "range"
        },
        {
            title: "责任人",
            align: "center",
            width: 50,
            dataIndex: "duty_person",
            search: true,
            commonRules: [{ required: true, message: "责任人必选" }],
            formType: "select",
            dict: { url: "system/user/list", props: { label: "name", value: "name" }, translation: true }
        },
        {
            title: "运行环境",
            dataIndex: "runtime",
            hide: true,
            search: false,
            formType: "select",
            maxTagCount: 4,
            multiple: true,
            allowCreate: true,
            createInfo: {
                title: "运行环境"
            },
            onCreate: async (value: any) => {
                await dictApi.createDictItemFast({ code: "runtime", title: value })
                return "runtime"
            },
            dict: { name: "runtime", props: { label: "title", value: "key" } }
        },
        {
            title: "成员",
            dataIndex: "member",
            hide: true,
            search: true,
            formType: "select",
            // 多选最大标签数量
            maxTagCount: 7,
            multiple: true,
            dict: { url: "system/user/list", props: { label: "name", value: "name" }, translation: true },
            commonRules: [{ required: true, message: "成员至少选择一个" }]
        },
        {
            // 后台默认值1，可不填
            title: "软件类型",
            dataIndex: "soft_type",
            hide: true,
            search: false,
            formType: "select",
            dict: {
                data: [
                    { label: "新研", value: 1 },
                    { label: "改造", value: 2 },
                    { label: "沿用", value: 3 }
                ],
                translation: true
            },
            commonRules: [{ required: true, message: "软件类型必填" }]
        },
        {
            title: "开发环境",
            dataIndex: "devplant",
            hide: true,
            search: false,
            formType: "select",
            multiple:true,
            maxTagCount: 4,
            allowCreate: true,
            createInfo: {
                title: "开发环境"
            },
            onCreate: async (value: any) => {
                await dictApi.createDictItemFast({ code: "devplant", title: value })
                return "devplant"
            },
            dict: { name: "devplant", props: { label: "title", value: "key" } }
        },
        {
            title: "缩略语",
            dataIndex: "abbreviation",
            hide: true,
            // 快速新增缩略语内容
            allowAbbrNew: true,
            abbrNewInfo: {
                title: "新增缩略语"
            },
            search: false,
            formType: "select",
            multiple: true,
            dict: { url: "system/abbreviation/index", props: { label: "title", value: "title" }, translation: true }
        },
        {
            title: "质量保证",
            dataIndex: "quality_person",
            hide: true,
            formType: "select",
            dict: { url: "system/user/list", props: { label: "name", value: "name" }, translation: true },
            commonRules: [{ required: true, message: "至少选择一个质量保证员" }]
        },
        {
            title: "质量监督",
            dataIndex: "vise_person",
            hide: true,
            formType: "select",
            dict: { url: "system/user/list", props: { label: "name", value: "name" }, translation: true },
            commonRules: [{ required: true, message: "至少选择一个质量监督员" }]
        },
        {
            title: "配置管理",
            dataIndex: "config_person",
            hide: true,
            formType: "select",
            dict: { url: "system/user/list", props: { label: "name", value: "name" }, translation: true },
            commonRules: [{ required: true, message: "至少选择一个配置管理员" }]
        },
        {
            title: "关键等级",
            dataIndex: "security_level",
            addDefaultValue: "3",
            hide: true,
            commonRules: [{ required: true, message: "关键等级必填" }],
            search: true,
            formType: "radio",
            dict: { name: "security_level", props: { label: "title", value: "key" } }
        },
        {
            title: "测试级别",
            dataIndex: "test_level",
            commonRules: [{ required: true, message: "请至少选择一个测试级别" }],
            addDefaultValue: ["4"],
            hide: true,
            formType: "checkbox",
            dict: { name: "test_level", props: { label: "title", value: "key" } }
        },
        {
            title: "平台类型",
            dataIndex: "plant_type",
            commonRules: [{ required: true, message: "请至少选择一个平台类型" }],
            addDefaultValue: ["3"],
            hide: true,
            formType: "checkbox",
            dict: { name: "plant_type", props: { label: "title", value: "key" } }
        },
        {
            title: "报告类型",
            dataIndex: "report_type",
            align: "center",
            addDefaultValue: "9",
            search: true,
            width: 70,
            commonRules: [{ required: true, message: "报告类型必填" }],
            // 字典-report_type
            formType: "radio",
            dict: { name: "report_type", translation: true, props: { label: "title", value: "key" } }
        },
        {
            title: "编程语言",
            dataIndex: "language",
            addDefaultValue: ["1"],
            maxTagCount: 4,
            commonRules: [{ required: true, message: "请至少选择一个" }],
            hide: true,
            formType: "select",
            multiple: true,
            dict: { name: "language", props: { label: "title", value: "key" } }
        },
        {
            title: "依据标准",
            dataIndex: "standard",
            addDefaultValue: ["16", "17", "3", "7", "4", "5", "18", "6", "19"],
            maxTagCount: 20,
            commonRules: [{ required: true, message: "请至少选择一个" }],
            hide: true,
            multiple: true,
            formType: "select",
            dict: { name: "standard", props: { label: "title", value: "key" } },
            // 新增select选项
            allowStd: true,
            stdInfo: {
                title: "新增标准"
            }
        },
        {
            title: "单位",
            dataIndex: "entrust_unit",
            hide: true,
            // 快速新增单位内容
            allowNew: true,
            newInfo: {
                title: "新增单位信息"
            },
            commonRules: [{ required: true, message: "单位必选" }],
            formType: "select",
            dict: { url: "system/contact/index", props: { label: "name", value: "name" }, translation: true }
        },
        {
            formType: "input",
            title: "联系人",
            dataIndex: "entrust_contact",
            hide: true,
            commonRules: [{ required: true, message: "联系人必填" }]
        },
        {
            formType: "input",
            title: "联系电话",
            maxLength: 25,
            dataIndex: "entrust_contact_phone",
            hide: true,
            commonRules: [
                { required: true, message: "联系电话必填" },
                {
                    match: /^(1[3-9]\d{9})|(\d{3,4}-\d{7,8}(-\d+)?)$/,
                    message: "电话号码格式错误"
                }
            ]
        },
        {
            formType: "input",
            title: "电子邮箱",
            dataIndex: "entrust_email",
            hide: true
        },
        {
            title: "单位",
            dataIndex: "dev_unit",
            // 快速新增单位内容
            allowNew: true,
            newInfo: {
                title: "新增单位信息"
            },
            hide: true,
            commonRules: [{ required: true, message: "单位必选" }],
            formType: "select",
            dict: { url: "system/contact/index", props: { label: "name", value: "name" }, translation: true }
        },
        {
            formType: "input",
            title: "联系人",
            dataIndex: "dev_contact",
            hide: true,
            commonRules: [{ required: true, message: "联系人必填" }]
        },
        {
            formType: "input",
            title: "联系电话",
            maxLength: 25,
            dataIndex: "dev_contact_phone",
            hide: true,
            commonRules: [
                { required: true, message: "联系电话必填" },
                {
                    match: /^(1[3-9]\d{9})|(\d{3,4}-\d{7,8}(-\d+)?)$/,
                    message: "电话号码格式错误"
                }
            ]
        },
        {
            formType: "input",
            title: "电子邮箱",
            dataIndex: "dev_email",
            hide: true
        },
        {
            title: "单位",
            dataIndex: "test_unit",
            hide: true,
            // 快速新增单位内容
            allowNew: true,
            newInfo: {
                title: "新增单位信息"
            },
            addDefaultValue: textInfo.testUnitAddDefaultText,
            commonRules: [{ required: true, message: "单位必选" }],
            formType: "select",
            dict: { url: "system/contact/index", props: { label: "name", value: "name" }, translation: true }
        },
        {
            formType: "input",
            title: "联系人",
            dataIndex: "test_contact",
            addDefaultValue: textInfo.testUnitContactPersonName,
            hide: true,
            commonRules: [{ required: true, message: "联系人必填" }]
        },
        {
            formType: "input",
            title: "联系电话",
            dataIndex: "test_contact_phone",
            addDefaultValue: textInfo.testUnintContactPhoneNumber,
            hide: true,
            maxLength: 25,
            commonRules: [
                { required: true, message: "联系电话必填" },
                {
                    match: /^(1[3-9]\d{9})|(\d{3,4}-\d{7,8}(-\d+)?)$/,
                    message: "电话号码格式错误"
                }
            ]
        },
        {
            formType: "input",
            title: "电子邮箱",
            dataIndex: "test_email",
            hide: true
        },
        {
            title: "状态",
            align: "center",
            width: 80,
            dataIndex: "step",
            search: true,
            formType: "radio",
            addDefaultValue: "1",
            addDisabled: true,
            dict: {
                name: "step",
                translation: true,
                props: { label: "title", value: "key" },
                tagColors: { 1: "green", 2: "blue", 3: "red", 4: "yellow" }
            }
        },
        {
            title: "密级",
            align: "center",
            dataIndex: "secret",
            search: true,
            hide: true,
            formType: "radio",
            addDefaultValue: "1",
            addDisabled: false,
            dict: {
                name: "secret",
                translation: true,
                props: { label: "title", value: "key" }
            }
        }
    ])

    return { crudRef, crudOptions, crudColumns }
}

export default useCrudInit
