import { ref } from "vue"
import projectApi from "@/api/project/project"
import { useRoute } from "vue-router"
export default function useLoadTreeNode() {
    // global
    const route = useRoute()
    const projectInfo = ref({ ...route.query })
    // Events
    const loadMore = (nodeData) => {
        if (nodeData.level == "0") {
            return new Promise(async (resolve) => {
                const res = await projectApi
                    .getDutInfo(projectInfo.value.id, nodeData.key, nodeData.level)
                    .catch(() => {
                        resolve(undefined) // 捕获错误，让动态加载不再一直转圈
                    })
                nodeData.children = res.data
                resolve(undefined)
            })
        }
        if (nodeData.level == "1") {
            return new Promise(async (resolve) => {
                const res = await projectApi
                    .getDemandInfo(projectInfo.value.id, nodeData.key, nodeData.level)
                    .catch(() => {
                        resolve(undefined)
                    })
                nodeData.children = res.data
                resolve(undefined)
            })
        }
        if (nodeData.level == "2") {
            return new Promise(async (resolve) => {
                const res = await projectApi
                    .getTestInfo(projectInfo.value.id, nodeData.key, nodeData.level)
                    .catch(() => {
                        resolve(undefined)
                    })
                nodeData.children = res.data
                resolve(undefined)
            })
        }
        if (nodeData.level == "3") {
            return new Promise(async (resolve) => {
                const res = await projectApi
                    .getCaseInfo(projectInfo.value.id, nodeData.key, nodeData.level)
                    .catch(() => {
                        resolve(undefined)
                    })
                nodeData.children = res.data
                resolve(undefined)
            })
        }
    }
    return {
        loadMore
    }
}
