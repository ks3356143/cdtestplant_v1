import { TableColumnData } from "@arco-design/web-vue"
import { ref, reactive } from "vue"
// 粘贴图片组件
import ImageInput from "../ImageInput/index.vue"
// wordlike组件
import WordLikeTable from "../wordLikeTable/index.vue"

export default function useTable(reset: Function) {
    const columns = reactive<TableColumnData[]>([
        {
            title: "类型",
            width: 50,
            align: "center",
            dataIndex: "type",
            render: ({ record }) => {
                let item: string = "文"
                let color: string = "red"
                switch (record.type) {
                    case "text":
                        item = "文"
                        color = "blue"
                        break
                    case "image":
                        item = "图"
                        color = "red"
                        break
                    case "table":
                        item = "表"
                        color = "orangered"
                        break
                }
                return <a-tag color={color}>{item}</a-tag>
            }
        },
        {
            title: "内容",
            dataIndex: "content",
            slotName: "content",
            render({ record, rowIndex }) {
                const { type } = record
                switch (type) {
                    case "text":
                        return <a-textarea v-model={data.value[rowIndex].content} placeholder="请输入段落" allow-clear />
                    case "image":
                        return <ImageInput v-model={data.value[rowIndex].content} v-model:fontnote={data.value[rowIndex].fontnote}></ImageInput>
                    case "table":
                        return <WordLikeTable v-model={data.value[rowIndex].content} v-model:fontnote={data.value[rowIndex].fontnote}></WordLikeTable>
                }
            }
        },
        {
            title: "操作",
            align: "center",
            width: 80,
            render: ({ rowIndex }) => {
                return (
                    <a-space>
                        <a-tooltip content="注意：删除后数据丢失">
                            <a-button type="primary" status="danger" onClick={() => deleteRow(rowIndex)}>
                                {{ icon: () => <icon-delete /> }}
                            </a-button>
                        </a-tooltip>
                    </a-space>
                )
            }
        }
    ])

    // 卸载时清空数据
    const handleOnClose = () => {
        data.value = [{ ...initalRowData }]
        // 更新展示状态
        reset()
    }

    // 数据定义 - 测试
    const data = ref<
        {
            type: string
            content: string | string[][]
            fontnote: string
        }[]
    >([])

    // 单行初始内容-并设置数据类型
    const initalRowData = {
        type: "text",
        content: "",
        fontnote: ""
    }

    // 删除该行
    const deleteRow = async (rowIndex: number) => {
        data.value.splice(rowIndex, 1)
    }

    // 拖拽
    const handleChange = (_data: typeof data.value) => {
        data.value = _data
    }

    // 新增文
    const addTextRow = () => {
        data.value.push({ ...initalRowData })
    }

    // 新增图片
    const addPicRow = () => {
        data.value.push({ type: "image", content: "", fontnote: "" })
    }

    // 新增表格
    const addTableRow = () => {
        data.value.push({
            type: "table",
            content: [
                ["", "", ""],
                ["", "", ""],
                ["", "", ""]
            ],
            fontnote: ""
        })
    }

    return { columns, data, handleChange, addTextRow, addPicRow, addTableRow, handleOnClose }
}
