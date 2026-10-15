import { ref } from "vue"
import { storeToRefs } from "pinia"
import { Message, Notification } from "@arco-design/web-vue"
import caseApi from "@/api/project/case"
import { useTreeDataStore } from "@/store"
import designApi from "@/api/project/designDemand"
import { useRoute } from "vue-router"

export default function useTreeDrag(projectId, routeViewRef) {
    // global
    const route = useRoute()
    const treeDataStore = useTreeDataStore()
    const { treeData } = storeToRefs(treeDataStore)
    // 闭包储存变量
    let dragNodeGlobal = null
    let dropNodeGlobal = null
    let dragDropPosition = 0
    // ref对象
    const paoVisible = ref(false)
    const paoContainer = ref(null)
    const pao2Visible = ref(false)
    const pao2Container = ref(null)
    // a-tree -> 节点在可释放目标释放的操作 - drapNode是被拖拽的节点，
    // dropNone是释放在哪个节点下，dropPosition是释放的位置-1,0...
    const ondrop = async ({ e, dragNode, dropNode, dropPosition }) => {
        const data = treeData.value // 这是整体的树数据
        // 提示用户只能拖拽用例节点、设计需求节点
        if (!["2", "4"].includes(dragNode.level)) {
            Message.warning("只能拖拽用例节点、设计需求节点")
            return
        }
        // 拖拽逻辑：
        // 1.用例节点拖拽
        if (dragNode.level === "4") {
            // 2.1.如果是拖拽到测试项节点下
            if (dropNode.level === "3") {
                // 2.1.1.如果位置为0，则放在了测试项里面,为1，-1在测试上下都不处理
                if (dropPosition === 0) {
                    // 判断用例是否已经测试项节点里面了
                    if (!dropNode.children || !dropNode.children.includes(dragNode)) {
                        // 不在测试项里面，则弹出提示是复制还是移动
                        dragNodeGlobal = dragNode
                        dropNodeGlobal = dropNode
                        paoContainer.value = e.target.parentElement
                        paoVisible.value = true
                    } else if (dropNode.children.includes(dragNode)) {
                        // 这里就用例拖拽到当前的测试项节点，则可弹出复制弹窗
                        dragNodeGlobal = dragNode
                        dropNodeGlobal = dropNode
                        paoContainer.value = e.target.parentElement
                        paoVisible.value = true
                    }
                }
            } else if (dropNode.level === "4") {
                // 2.2.如果拖拽到测试用例节点，注意拖动到自己上下方不触发
                // 2.2.1先要判断用例是否是同一个demand，则是改变顺序
                dragNodeGlobal = dragNode
                dropNodeGlobal = dropNode
                pao2Container.value = e.target.parentElement
                pao2Visible.value = true
                dragDropPosition = dropPosition
            }
        }
        // 2.设计需求节点拖拽-改变sort字段
        if (dragNode.level === "2") {
            // 如果位置为0，即放在节点上不处理
            if (dropPosition === 0) return
            // 如果不为0，则发出请求，传key后端处理即可
            const res = await designApi.switch_position(dragNode.key, dropNode.key, dropPosition, route.query.id)
            // 最后更新树状目录
            treeDataStore.updateDesignDemandTreeData({ key: res.data }, route.query.id)
        }
    }
    // a-tree拖拽时是否允许在某级别节点上释放：目前支持在测试项节点、测试用例节点释放
    const allowdrop = (options) => {
        if (["4", "3", "2"].includes(options.dropNode.level)) {
            return true
        }
        return false
    }
    // 拖拽后弹出气泡-移动
    const paoOk = async () => {
        const res = await caseApi.copyOrMoveCaseToDemand({
            project_id: projectId.value,
            case_key: dragNodeGlobal.key,
            demand_key: dropNodeGlobal.key,
            move: true
        })
        await treeDataStore.updateCaseTreeData(res.data.oldCaseKey, projectId.value)
        await treeDataStore.updateCaseTreeData(res.data.newCaseKey, projectId.value)
        routeViewRef.value.refresh()
        Notification.success("移动用例成功")
    }
    /// 拖拽后弹出气泡-复制
    const paoCancel = async () => {
        const res = await caseApi.copyOrMoveCaseToDemand({
            project_id: projectId.value,
            case_key: dragNodeGlobal.key,
            demand_key: dropNodeGlobal.key,
            move: false
        })
        await treeDataStore.updateCaseTreeData(res.data.oldCaseKey, projectId.value)
        await treeDataStore.updateCaseTreeData(res.data.newCaseKey, projectId.value)
        routeViewRef.value.refresh()
        Notification.success("复制用例成功")
    }
    /// 同级分2个气泡ok是移动，cancel是复制
    const paoOk2 = async () => {
        const res = await caseApi.copyOrMoveCaseByCase({
            project_id: projectId.value,
            drag_key: dragNodeGlobal.key,
            drop_key: dropNodeGlobal.key,
            position: dragDropPosition,
            move: true
        })
        await treeDataStore.updateCaseTreeData(res.data.old, projectId.value)
        await treeDataStore.updateCaseTreeData(res.data.new, projectId.value)
        routeViewRef.value.refresh()
        Notification.success("移动用例成功")
    }
    const paoCancel2 = async () => {
        const res = await caseApi.copyOrMoveCaseByCase({
            project_id: projectId.value,
            drag_key: dragNodeGlobal.key,
            drop_key: dropNodeGlobal.key,
            position: dragDropPosition,
            move: false
        })
        await treeDataStore.updateCaseTreeData(res.data.old, projectId.value)
        await treeDataStore.updateCaseTreeData(res.data.new, projectId.value)
        routeViewRef.value.refresh()
        Notification.success("复制用例成功")
    }
    return {
        paoVisible,
        paoContainer,
        pao2Visible,
        pao2Container,
        ondrop,
        allowdrop,
        paoOk,
        paoCancel,
        paoOk2,
        paoCancel2
    }
}
