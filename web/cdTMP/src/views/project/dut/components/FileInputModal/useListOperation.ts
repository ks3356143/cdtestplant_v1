import { ref } from "vue"

const templateDemandObj = {
    chapter: "",
    title: "",
    ident: "",
    demandType: "",
    content: ""
}

export default function useListOperaton(htmlData: any) {
    // 数据变化spin显示
    const loading = ref(false)
    // 上方按钮：直接在最下新增一条
    const handleCreateAtLatest = () => {
        const newDemand = JSON.parse(JSON.stringify(templateDemandObj))
        htmlData.value.push(newDemand)
    }
    // 上方按钮：重置数据，点击页面不卡段
    const handleResetData = () => {
        htmlData.value = []
    }
    // 点击单条右侧按钮：下方新增 - 深拷贝,并插入到下方
    const handledownCreate = (index: number) => {
        const newDemand = JSON.parse(JSON.stringify(templateDemandObj))
        htmlData.value.splice(index + 1, 0, newDemand)
    }
    // 因为a-list限制必须知道当前页码和页容量
    const currentPage = ref(1)
    const handlePageChange = (page) => {
        currentPage.value = page
    }
    // 点击单条右侧按钮：删除 - 需要根据currentPage动态觉得因为a-list每页都是这样计算的
    const handleDelete = (index: number) => {
        const currentIndex = index + (currentPage.value - 1) * 15
        htmlData.value.splice(currentIndex, 1)
    }
    return { loading, handleCreateAtLatest, handleResetData, handledownCreate, handlePageChange, handleDelete }
}
