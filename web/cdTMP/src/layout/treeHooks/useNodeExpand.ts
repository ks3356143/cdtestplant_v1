import { ref } from "vue"
import { useTreeDataStore } from "@/store"
export default function useNodeExpand() {
    // global
    const treeDataStore = useTreeDataStore()
    // refs
    const expandedKeys = ref<string[]>([]) // v-model对应a-tree展开的节点
    const allExpandedKeys = ref<string[]>([]) // 全部展开后的节点数组
    /**
     * 事件：用户点击切换展开或收缩
     */
    const toggleExpanded = () => {
        allExpandedKeys.value = treeDataStore.outExpandNode()
        expandedKeys.value = expandedKeys?.value.length ? [] : allExpandedKeys.value
    }
    return {
        expandedKeys,
        toggleExpanded
    }
}
