import { ref } from "vue"
import projectApi from "@/api/project/project"
import { useRoute } from "vue-router"

export default function useLoadTreeNode() {
    // global
    const route = useRoute()
    const projectInfo = ref({ ...route.query })

    // 各层级对应的懒加载接口
    const levelApiMap = {
        "0": projectApi.getDutInfo,
        "1": projectApi.getDemandInfo,
        "2": projectApi.getTestInfo,
        "3": projectApi.getCaseInfo
    }

    const loadMore = (nodeData) => {
        const fetchChildren = levelApiMap[nodeData.level]
        if (!fetchChildren) return
        return new Promise((resolve) => {
            (async () => {
                try {
                    const res = await fetchChildren(projectInfo.value.id, nodeData.key, nodeData.level)
                    nodeData.children = res?.data ?? []
                } catch {
                    // 请求失败时置为空子节点，避免树一直转圈或二次取值崩溃
                    nodeData.children = []
                } finally {
                    resolve(undefined)
                }
            })()
        })
    }
    return {
        loadMore
    }
}
