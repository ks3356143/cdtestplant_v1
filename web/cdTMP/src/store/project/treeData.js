import { defineStore } from "pinia"
import projectApi from "@/api/project/project"

// beforeunload 监听只注册一次：initTreeData 每次进入工作区都会调用，
// 原先每次追加一个匿名监听器，长期使用会不断累积
let unloadListenerBound = false

const useTreeDataStore = defineStore("treeDataStore", {    state: () => {
        return {
            treeData: [],
            originTreeData: [],
            currentNode: undefined,
            isInit: false
        }
    },
    /**
     * 注意action不能使用箭头函数，不能绑定this
     */
    actions: {
        async initTreeData(projectId) {
            // 判断是否有项目树缓存：pid 为项目后端 id
            const pid = localStorage.getItem("pid")
            const sameProject = pid !== null && String(pid) === String(projectId)
            // tree_local_data 兼容旧格式（纯数组）与新格式（{ pid, data }）
            let cachedData = null
            try {
                const raw = localStorage.getItem("tree_local_data")
                const parsed = raw ? JSON.parse(raw) : null
                cachedData = Array.isArray(parsed) ? parsed : parsed?.data ?? null
                // 旧格式没有 pid，只有在 pid 与当前项目一致时才认为可用
                if (!Array.isArray(parsed) && parsed?.pid !== undefined && String(parsed.pid) !== String(projectId)) {
                    cachedData = null
                }
            } catch {
                cachedData = null
            }
            // 只有同一项目且缓存有数据时才复用缓存，避免 A 项目的树渲染到 B 项目下
            if (sameProject && Array.isArray(cachedData) && cachedData.length > 0) {
                this.treeData = cachedData
                this.originTreeData = cachedData
            } else {
                // 切换项目或缓存无效：清掉旧缓存并重新请求
                localStorage.removeItem("tree_local_data")
                const roundData = await projectApi.getRoundInfo(projectId)
                this.treeData = roundData.data
                this.originTreeData = roundData.data
            }
            // 每次进入工作区存一个localStorage项目ID
            localStorage.setItem("pid", projectId)
            // 将用户关闭页面数据储存于localStorage中
            // 注意：监听只注册一次；保存时以当前的 pid 为准，避免闭包持有首次进入的项目 id
            if (!unloadListenerBound) {
                unloadListenerBound = true
                window.addEventListener("beforeunload", () => {
                    try {
                        localStorage.setItem(
                            "tree_local_data",
                            JSON.stringify({ pid: localStorage.getItem("pid"), data: this.treeData })
                        )
                    } catch {
                        // 树数据过大或浏览器禁用存储时忽略，不影响正常使用
                    }
                })
            }
        },
        // 用于新增轮次后显示
        async resetTreeData(projectId) {
            const roundData = await projectApi.getRoundInfo(projectId)
            this.treeData = roundData.data
            this.originTreeData = roundData.data
        },
        // 新增删除dut后更新树状显示-注意传的key是dut下面的design的key
        async updateDutTreeData(data, projrctId) {
            if (!data?.key) return
            let temp = data.key.split("-")
            temp.pop(-1)
            let roundKey = temp[0]
            const roundNode = this.treeData?.[roundKey]
            // 直达链接或树未展开时层级可能不存在，回退为整树刷新，避免 undefined.xxx 报错
            // 树未加载到该层级时无需更新，展开时会懒加载最新数据
            if (!roundNode) return
            const res = await projectApi.getDutInfo(projrctId, temp.join("-"), "0") // nodeKey:'0'
            roundNode.children = res?.data ?? []
        },
        // 新增删除designDemand后tree显示-注意传的是测试项的key
        async updateDesignDemandTreeData(data, projrctId) {
            if (!data?.key) return
            let temp = data.key.split("-")
            temp.pop(-1)
            let roundKey = temp[0]
            let dutKey = temp[1]
            const dutNode = this.treeData?.[roundKey]?.children?.[dutKey]
            // 树未加载到该层级时无需更新，展开时会懒加载最新数据
            if (!dutNode) return
            const res = await projectApi.getDemandInfo(projrctId, temp.join("-"), "1")
            dutNode.children = res?.data ?? []
        },
        // 新增删除testDemand后tree显示
        async updateTestDemandTreeData(data, projrctId) {
            if (!data?.key) return
            let temp = data.key.split("-")
            temp.pop(-1)
            let roundKey = temp[0]
            let dutKey = temp[1]
            let designKey = temp[2]
            const designNode = this.treeData?.[roundKey]?.children?.[dutKey]?.children?.[designKey]
            // 树未加载到该层级时无需更新，展开时会懒加载最新数据
            if (!designNode) return
            const res = await projectApi.getTestInfo(projrctId, temp.join("-"), "2")
            designNode.children = res?.data ?? []
        },
        // 新增删除case后tree显示
        /**
         * 第一个参数格式：data.key，data为用例数据，里面必须有key属性
         */
        async updateCaseTreeData(data, projrctId) {
            if (!data?.key) return
            let temp = data.key.split("-")
            temp.pop(-1)
            let roundKey = temp[0]
            let dutKey = temp[1]
            let designKey = temp[2]
            let testKey = temp[3]
            const testNode = this.treeData?.[roundKey]?.children?.[dutKey]?.children?.[designKey]?.children?.[testKey]
            // 树未加载到该层级时无需更新，展开时会懒加载最新数据
            if (!testNode) return
            const res = await projectApi.getCaseInfo(projrctId, temp.join("-"), "3")
            testNode.children = res?.data ?? []
        },
        setCurrentNode(nodeKey) {
            this.currentNode = nodeKey
        },
        // 获取轮次信息中差中间的是哪几个轮次
        getRoundMiddleInfo() {
            // 树为空（切项目首次进入、接口失败或缓存被清）时直接返回 0，
            // 避免 this.treeData[length - 1].key 抛 undefined 取值错误
            const list = Array.isArray(this.treeData) ? this.treeData : []
            if (list.length === 0) return 0
            const roundLength = list.length
            // 取出最后一个key的值
            const lastKey = parseInt(list[list.length - 1]?.key ?? "0", 10) + 1
            if (!Number.isFinite(lastKey)) return roundLength
            if (roundLength !== lastKey) {
                let cha = lastKey - roundLength
                return lastKey - cha - 1
            } else {
                return roundLength
            }
        },
        // 输出当前树状结构可展开的节点
        outExpandNode() {
            // 定义递归函数
            const res = []
            function digui(data) {
                if (Object.prototype.toString.call(data) === "[object Array]") {
                    for (let i = 0; i < data.length; i++) {
                        if (data[i].children) {
                            res.push(data[i].key)
                            digui(data[i].children)
                        }
                    }
                }
            }
            this.treeData.forEach((item) => {
                if (item.children) {
                    res.push(item.key)
                    digui(item.children)
                }
            })
            return res
        }
    }
})

export default useTreeDataStore
