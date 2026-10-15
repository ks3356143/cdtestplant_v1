import { ref } from "vue"

export default function (crudOrFormRef?: any) {
    const crudColumns = ref([
        {
            title: "ID",
            align: "center",
            width: 50,
            hide: true,
            dataIndex: "id",
            commonRules: [{ required: true, message: "ID必填" }],
            validateTrigger: "blur-sm",
            display: false
        },
        {
            title: "设需标识",
            align: "center",
            sortable: { sortDirections: ["ascend"] },
            width: 180,
            dataIndex: "ident",
            search: true,
            validateTrigger: "blur-sm",
            placeholder: "请输入文档中设计需求的标识",
            help: '若不知道则填"无"或不填',
            openPrepend: true
        },
        {
            title: "设需名称",
            align: "center",
            width: 200,
            dataIndex: "name",
            search: true,
            commonRules: [{ required: true, message: "设计需求名称是必填" }],
            validateTrigger: "blur-sm"
        },
        {
            title: "章节号",
            align: "center",
            width: 150,
            dataIndex: "chapter",
            search: true,
            help: '若为隐含需求则填"/"'
        },
        {
            title: "需求类型",
            width: 150,
            align: "center",
            dataIndex: "demandType",
            addDefaultValue: "1",
            formType: "radio",
            search: true,
            dict: { name: "demandType", props: { label: "title", value: "key" }, translation: true },
            commonRules: [{ required: true, message: "需求类型是必填" }],
            validateTrigger: "blur-sm",
            // 主要为了添加“接口”的4个字段
            onControl: (value: string, maFormObject: any) => {
                const columnService = maFormObject.getColumnService()
                if (value === "3") {
                    // 表明是接口设计需求
                    columnService.get("forward_source").setAttr("display", true)
                    columnService.get("forward_destination").setAttr("display", true)
                    columnService.get("forward_description").setAttr("display", true)
                    columnService.get("type").setAttr("display", true)
                    columnService.get("is_bidirectional").setAttr("display", true)
                } else {
                    columnService.get("forward_source").setAttr("display", false)
                    columnService.get("forward_destination").setAttr("display", false)
                    columnService.get("forward_description").setAttr("display", false)
                    columnService.get("type").setAttr("display", false)
                    columnService.get("is_bidirectional").setAttr("display", false)
                }
            }
        },
        {
            formType: "grid-tailwind",
            colNumber: 2,
            customClass: ["ml-[5px]"],
            cols: [
                {
                    formList: [
                        {
                            title: "接口类型",
                            dataIndex: "type",
                            hide: true,
                            placeholder: "请填写接口类型或协议，例如：UART"
                        }
                    ]
                },
                {
                    formList: [
                        {
                            // 新增：单项双向接口选择
                            title: "是否双向",
                            dataIndex: "is_bidirectional",
                            formType: "switch",
                            hide: true,
                            onControl: (value: boolean, maFormObject: any) => {
                                const columnService = maFormObject.getColumnService()
                                // 如果is_bidirectional都被隐藏了，那么reverse被隐藏，不要执行后续代码
                                const shuangxiangDisplay = columnService.get("is_bidirectional").getAttr("display")
                                if (!shuangxiangDisplay) {
                                    columnService.get("reverse_source").setAttr("display", false)
                                    columnService.get("reverse_destination").setAttr("display", false)
                                    columnService.get("reverse_description").setAttr("display", false)
                                    return
                                }
                                if (value) {
                                    return {
                                        reverse_source: { display: true },
                                        reverse_destination: { display: true },
                                        reverse_description: { display: true }
                                    }
                                } else {
                                    return {
                                        reverse_source: { display: false },
                                        reverse_destination: { display: false },
                                        reverse_description: { display: false }
                                    }
                                }
                            }
                        }
                    ]
                }
            ]
        },
        {
            formType: "grid-tailwind",
            colNumber: 3,
            customClass: ["ml-3"],
            cols: [
                {
                    formList: [
                        {
                            title: "正向来源",
                            dataIndex: "forward_source",
                            hide: true
                        }
                    ]
                },
                {
                    formList: [
                        {
                            title: "正向去处",
                            dataIndex: "forward_destination",
                            hide: true
                        }
                    ]
                },
                {
                    formList: [
                        {
                            title: "接口描述",
                            dataIndex: "forward_description",
                            hide: true
                        }
                    ]
                }
            ]
        },
        {
            formType: "grid-tailwind",
            colNumber: 3,
            customClass: ["ml-3"],
            cols: [
                {
                    formList: [
                        {
                            title: "反向来源",
                            dataIndex: "reverse_source",
                            hide: true
                        }
                    ]
                },
                {
                    formList: [
                        {
                            title: "反向去处",
                            dataIndex: "reverse_destination",
                            hide: true
                        }
                    ]
                },
                {
                    formList: [
                        {
                            title: "接口描述",
                            dataIndex: "reverse_description",
                            hide: true
                        }
                    ]
                }
            ]
        },
        {
            title: "需求描述",
            dataIndex: "description",
            hide: true,
            width: 300,
            formType: "editor",
            height: 300
        }
    ])
    return crudColumns
}
