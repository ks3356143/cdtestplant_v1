import { useRoute } from "vue-router"
import { useUserStore } from "@/store"

export default function () {
    const route = useRoute()
    const userStore = useUserStore()
    const columns = [
        {
            title: "id",
            dataIndex: "id",
            display: false
        },
        {
            formType: "grid",
            customClass: ["mt-0"],
            cols: [
                {
                    span: 12,
                    formList: [
                        {
                            title: "名称",
                            align: "left",
                            search: true,
                            dataIndex: "name",
                            rules: [{ required: true, message: "名称是必填" }],
                            validateTrigger: "blur-sm"
                        }
                    ]
                },
                {
                    span: 12,
                    formList: [
                        {
                            title: "问题标识",
                            align: "center",
                            width: 140,
                            search: true,
                            disabled: true,
                            dataIndex: "ident",
                            validateTrigger: "blur-sm"
                        }
                    ]
                }
            ]
        },
        {
            formType: "grid",
            customClass: ["ml-4"],
            cols: [
                {
                    span: 12,
                    formList: [
                        {
                            title: "缺陷状态",
                            align: "center",
                            width: 80,
                            search: true,
                            dataIndex: "status",
                            formType: "radio",
                            rules: [{ required: true, message: "缺陷状态是必填" }],
                            dict: {
                                name: "problemStatu",
                                translation: true,
                                props: { label: "title", value: "key" },
                                tagColors: { 1: "green", 2: "blue", 3: "#FF7D00", 4: "red" }
                            }
                        }
                    ]
                },
                {
                    span: 12,
                    formList: [
                        {
                            title: "闭环方式",
                            align: "center",
                            width: 200,
                            dataIndex: "closeMethod",
                            search: true,
                            formType: "checkbox",
                            dict: {
                                name: "closeMethod",
                                translation: true,
                                props: { label: "title", value: "key" }
                            }
                        }
                    ]
                }
            ]
        },
        {
            formType: "grid",
            customClass: ["ml-4"],
            cols: [
                {
                    span: 12,
                    formList: [
                        {
                            title: "缺陷等级",
                            align: "center",
                            width: 80,
                            dataIndex: "grade",
                            search: true,
                            formType: "radio",
                            rules: [{ required: true, message: "缺陷等级必填" }],
                            dict: {
                                name: "problemGrade",
                                translation: true,
                                props: { label: "title", value: "key" }
                            }
                        }
                    ]
                },
                {
                    span: 12,
                    formList: [
                        {
                            title: "缺陷类型",
                            align: "center",
                            width: 80,
                            dataIndex: "type",
                            search: true,
                            formType: "radio",
                            rules: [{ required: true, message: "缺陷类型必选" }],
                            dict: {
                                name: "problemType",
                                translation: true,
                                props: { label: "title", value: "key" }
                            }
                        }
                    ]
                }
            ]
        },
        {
            formType: "divider"
        },
        {
            formType: "grid",
            cols: [
                {
                    span: 24,
                    formList: [
                        {
                            title: "问题描述",
                            hide: true,
                            search: true,
                            align: "center",
                            dataIndex: "operation",
                            formType: "editor"
                        }
                    ]
                }
            ]
        },
        {
            formType: "grid",
            cols: [
                {
                    span: 24,
                    formList: [
                        {
                            title: "问题影响",
                            hide: true,
                            align: "center",
                            dataIndex: "result",
                            formType: "textarea"
                        }
                    ]
                }
            ]
        },
        {
            formType: "divider"
        },
        {
            formType: "grid",
            cols: [
                {
                    span: 24,
                    formList: [
                        {
                            title: "原因分析",
                            hide: true,
                            align: "center",
                            dataIndex: "analysis",
                            formType: "textarea"
                        }
                    ]
                }
            ]
        },
        {
            formType: "grid",
            cols: [
                {
                    span: 24,
                    formList: [
                        {
                            title: "影响域分析",
                            hide: true,
                            align: "center",
                            dataIndex: "effect_scope",
                            formType: "textarea"
                        }
                    ]
                }
            ]
        },
        {
            formType: "grid",
            cols: [
                {
                    span: 24,
                    formList: [
                        {
                            title: "改正措施",
                            hide: true,
                            align: "center",
                            dataIndex: "solve",
                            formType: "textarea"
                        }
                    ]
                }
            ]
        },
        {
            formType: "divider"
        },
        {
            formType: "grid",
            cols: [
                {
                    span: 24,
                    formList: [
                        {
                            title: "回归结果",
                            hide: true,
                            align: "center",
                            dataIndex: "verify_result",
                            formType: "editor"
                        }
                    ]
                }
            ]
        },
        {
            formType: "divider",
            title: "人员信息"
        },
        {
            formType: "grid",
            cols: [
                {
                    span: 12,
                    formList: [
                        {
                            title: "测试人员",
                            dataIndex: "postPerson",
                            search: true,
                            align: "center",
                            formType: "select",
                            rules: [{ required: true, message: "测试人员必填" }],
                            dict: {
                                url: "system/user/list",
                                params: { project_id: route.query.id },
                                translation: true,
                                props: { label: "name", value: "name" }
                            }
                        }
                    ]
                },
                {
                    span: 12,
                    formList: [
                        {
                            title: "测试日期",
                            hide: true,
                            dataIndex: "postDate",
                            formType: "date"
                        }
                    ]
                }
            ]
        },
        {
            formType: "grid",
            cols: [
                {
                    span: 12,
                    formList: [
                        {
                            title: "开发人员",
                            hide: true,
                            dataIndex: "designerPerson",
                            formType: "input"
                        }
                    ]
                },
                {
                    span: 12,
                    formList: [
                        {
                            title: "开发方日期",
                            hide: true,
                            dataIndex: "designDate",
                            formType: "date"
                        }
                    ]
                }
            ]
        },
        {
            formType: "grid",
            cols: [
                {
                    span: 12,
                    formList: [
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
                        }
                    ]
                },
                {
                    span: 12,
                    formList: [
                        {
                            title: "回归日期",
                            hide: true,
                            dataIndex: "verifyDate",
                            formType: "date"
                        }
                    ]
                }
            ]
        }
    ]
    return { columns }
}
