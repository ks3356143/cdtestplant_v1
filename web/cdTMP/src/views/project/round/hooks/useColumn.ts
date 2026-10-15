import { ref, shallowRef } from "vue"
import { useRoute } from "vue-router"
import beiceType from "@/views/project/round/beiceType"
// 导入自定义组件
import UploadInput from "@/components/UploadInput/index.vue"

export default function (crudOrFormRef: any) {
    // global
    const route = useRoute()
    // 计算注释率计算crud/form的数据，判断
    const calcPercent = () => {
        if (crudOrFormRef) {
            const formData = crudOrFormRef.value.getFormData()
            const { total_lines, comment_lines } = formData
            formData.comment_percent = `${(comment_lines / total_lines).toFixed(2).toString()}%`
        }
        return "无法计算注释率"
    }
    const crudColumns = ref([
        {
            title: "ID",
            width: 50,
            align: "center",
            hide: true,
            dataIndex: "id",
            commonRules: [{ required: true, message: "ID是必填" }],
            validateTrigger: "blur-sm",
            display: false
        },
        {
            title: "测件标识",
            width: 150,
            sortable: { sortDirections: ["ascend"] },
            align: "center",
            dataIndex: "ident",
            search: true,
            // 这里做的标识预填
            addDefaultValue: route.query.ident + "-R" + (parseInt(route.query.key as any) + 1) + "-UT",
            addDisabled: true,
            editDisabled: true,
            validateTrigger: "blur-sm",
            disabled: true,
            placeholder: "被测件标识未空，请检查"
        },
        {
            title: "被测类型",
            align: "center",
            dataIndex: "type",
            search: true,
            width: 200,
            formType: "radio",
            addDefaultValue: "SO",
            dict: {
                data: beiceType,
                translation: true,
                tagColors: { XQ: "blue", SO: "green", SJ: "orangered", XY: "pinkpurple", YZ: "red" }
            },
            onControl: (value: string) => {
                if (value === "SO") {
                    return {
                        total_lines: { display: true },
                        effective_lines: { display: true },
                        comment_lines: { display: true },
                        comment_percent: { display: true },
                        upload: { display: true },
                        release_date: { display: false }
                    }
                } else {
                    // 其他数据清除
                    return {
                        total_lines: { display: false },
                        effective_lines: { display: false },
                        comment_lines: { display: false },
                        comment_percent: { display: false },
                        upload: { display: false },
                        release_date: { display: true }
                    }
                }
            }
        },
        {
            title: "被测件名",
            width: 120,
            align: "center",
            dataIndex: "name",
            search: true,
            commonRules: [{ required: true, message: "被测件名称必填" }],
            validateTrigger: "blur-sm"
        },
        {
            title: "版本",
            align: "center",
            dataIndex: "version",
            search: true,
            commonRules: [{ required: true, message: "版本必填" }],
            validateTrigger: "blur-sm",
            help: "填写不带V字符",
            openPrepend: true
        },
        {
            title: "用户标识",
            align: "center",
            dataIndex: "ref",
            search: true,
            commonRules: [{ required: true, message: "用户标识必填" }],
            validateTrigger: "blur-sm",
            help: "客户使用的标识"
        },
        {
            title: "单位",
            align: "center",
            dataIndex: "release_union",
            search: true,
            commonRules: [{ required: true, message: "单位必选" }],
            formType: "select",
            span: 3,
            dict: { url: "system/contact/index", props: { label: "name", value: "name" }, translation: true }
        },
        {
            title: "发布时间",
            dataIndex: "release_date",
            hide: true,
            commonRules: [{ required: true, message: "时间必填" }],
            formType: "date"
        },
        {
            title: "总行数",
            hide: true,
            align: "center",
            dataIndex: "total_lines",
            formType: "input-number",
            commonRules: [{ required: true, message: "总行数必填" }],
            min: 0,
            onControl: () => {
                calcPercent()
            }
        },
        {
            title: "有效行数",
            hide: true,
            align: "center",
            dataIndex: "effective_lines",
            formType: "input-number",
            commonRules: [{ required: true, message: "有效行数必填" }],
            min: 0,
            onControl: () => {
                calcPercent()
            }
        },
        {
            title: "注释行数",
            hide: true,
            align: "center",
            dataIndex: "comment_lines",
            formType: "input-number",
            commonRules: [{ required: true, message: "注释行数必填" }],
            min: 0,
            onControl: () => {
                calcPercent()
            }
        },
        {
            title: "注释率 %",
            align: "center",
            dataIndex: "comment_percent",
            placeholder: "计算注释率",
            hide: true,
            addDisabled: true,
            editDisabled: true,
            disabled: true
        },
        {
            title: "上传源代码",
            align: "center",
            dataIndex: "upload",
            placeholder: "上传源代码",
            hide: true,
            formType: "component",
            component: shallowRef(UploadInput)
        }
    ])
    return crudColumns
}
