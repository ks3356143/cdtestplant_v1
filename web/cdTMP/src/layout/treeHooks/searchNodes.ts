import { ref } from "vue"
import type { Ref } from "vue"
import { useTreeDataStore } from "@/store"
import { storeToRefs } from "pinia"
/**
 * 辅助搜索：递归函数
 */
const loop = (itemdata: any[], searchKey: Ref<string>) => {
    const result: any[] = []
    itemdata.forEach((item) => {
        if (item.title.indexOf(searchKey.value.replace(" ", "")) > -1) {
            result.push({ ...item })
        } else if (item.children) {
            const filterdata = loop(item.children, searchKey)
            if (filterdata.length) {
                result.push({
                    ...item,
                    children: filterdata
                })
            }
        }
    })
    return result
}

/**
 * 搜索v-model/搜索按钮点击
 */
export default function useSearchNodes() {
    // global
    const treeDataStore = useTreeDataStore()
    const { treeData } = storeToRefs(treeDataStore)
    // refs
    const searchKey = ref("")
    // 点击搜索事件
    const handleSearchTreeDataClick = () => {
        // 返回过滤后的treeData
        // treeDataStore.originTreeData
        if (searchKey.value) {
            treeData.value = treeDataStore.originTreeData
            ;(treeData as Ref<any[]>).value = loop(treeDataStore.treeData, searchKey)
        } else {
            treeData.value = treeDataStore.originTreeData
        }
    }
    return {
        searchKey,
        handleSearchTreeDataClick
    }
}
