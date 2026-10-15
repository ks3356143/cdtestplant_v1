import { ref } from "vue"
import { getContextNodeInfo } from "@/layout/hooks/tools"
import { Message, Notification } from "@arco-design/web-vue"
import caseApi from "@/api/project/case"
import designApi from "@/api/project/designDemand"
import demandApi from "@/api/project/testDemand"
import { useTreeDataStore } from "@/store"

/**
 * 右键测试项节点与轮次的hook
 */
export function useRightClick(projectId, routeViewRef) {
    // global
    const treeDataStore = useTreeDataStore()
    // refs
    const popupVisible = ref(false) // 右键弹出菜单显影
    const popupContainer = ref() // 右键挂载容器
    const roundRightVisible = ref(false) // 轮次右键dropdown显示变量
    const roundRightContainer = ref(null) // 轮次右键dropdown的容器
    const problemRoundRef = ref(null) // problemchoose组件的ref
    // 复制refs
    const options = ref([])
    const modalVisible = ref(false)
    const relatedCopyData = ref(0)
    const cascaderLoading = ref(false)
    // 闭包变量s
    let rightClickNode = { level: 3, isLeaf: false, nodekey: "", title: "" } // 右键节点储存的信息
    const problemTitle = ref("第1轮问题单") // 弹出问题列表标题
    // 事件
    /**
     * 右键点击节点，判断节点级别来处理
     */
    const displayRightMenu = (e) => {
        if (e.target) {
            const context = getContextNodeInfo(e.target)
            if (!context) {
                return
            }
            const { nodekey = undefined, level, title, isLeaf } = context
            // 如果是测试项则弹出【1.根据测试项步骤生成当前测试项用例 2.复制测试项到设计需求】
            if (+level === 3) {
                e.preventDefault()
                // 首先将被右键点击的node储存到组件全局
                rightClickNode.level = level
                rightClickNode.isLeaf = isLeaf
                rightClickNode.nodekey = nodekey
                rightClickNode.title = title
                // 将popup组件绑定到被右键点击的元素 -> !注意!：现在固定为当前节点的父行div上，注意后续修改
                popupContainer.value = e.target.parentElement.parentElement
                popupVisible.value = true
            }
            if (+level === 0) {
                // 测试显示下拉框
                e.preventDefault()
                rightClickNode.level = level
                rightClickNode.isLeaf = isLeaf
                rightClickNode.nodekey = nodekey
                rightClickNode.title = title
                problemTitle.value = `第${+rightClickNode.nodekey + 1}轮问题单`
                roundRightContainer.value = e.target.parentElement
                roundRightVisible.value = true
            }
        }
    }
    /**
     * 打开问题单事件
     */
    const handleProblemShowClick = () => {
        // 这里要显示轮次的问题单
        problemRoundRef.value.open(rightClickNode.nodekey)
    }
    /**
     * 右键测试项->自动根据子项生成用例
     */
    const handleDoptionClickGreateCases = async () => {
        rightClickNode.project_id = projectId.value // 在rightClickNode对象加入project_id属性
        await caseApi.createByDemand(rightClickNode)
        routeViewRef.value.refresh()
    }

    /**
     * 右键弹出popup后复制
     */
    const handleDoptionClickCopyDemand = async () => {
        // 首先是要获取选项数据
        cascaderLoading.value = true
        modalVisible.value = true
        // 请求后端给级联选择器数据
        const res = await designApi.getRelatedCasDesign({ id: projectId.value }).catch((err) => {
            Message.error("请求后端数据发生错误，请重试")
            cascaderLoading.value = false
        })
        options.value = res.data
        // 先获取当前右击的需求的key -> 然后找到所属design的nodekey
        const currentDemandKey = rightClickNode.nodekey
        const belongDesignKey = currentDemandKey.substring(0, currentDemandKey.lastIndexOf("-"))
        // 默认赋值给demand的当前design，直接点击确定可以复制到当前
        options.value.forEach((item) => {
            item.children.forEach((tem) => {
                tem.children.forEach((design_obj) => {
                    if (belongDesignKey === design_obj.key) {
                        relatedCopyData.value = design_obj.value
                    }
                })
            })
        })
        cascaderLoading.value = false
        // 将checkbox-depth参数设置为非勾选
        checkboxValue.value = false
    }
    /// refs
    const checkboxValue = ref(false)
    /**
     * 确认复制
     */
    const handleCopyDemand = async () => {
        // 获取选择的design的id
        const design_id = relatedCopyData.value
        // 没有选取则直接返回false
        if (!design_id) {
            return false
        }
        // 这里进行复制的数据处理
        const res = await demandApi.copyToDesign({
            project_id: projectId.value,
            design_id: design_id,
            demand_key: rightClickNode.nodekey,
            depth: checkboxValue.value
        })
        if ((res.code = 200)) {
            // 注意必须传projectId，否则返回空
            treeDataStore.updateTestDemandTreeData(res.data, projectId.value)
            Notification.success("复制成功,为避免重复,设置了(复制)字样,请手动修改...")
            return true
        } else {
            Message.error("复制失败，服务器错误")
        }
    }

    // 新增点击增加人机交互界面测试
    const handleCreateRenji = async () => {
        const res = await designApi.create_rj({
            round_id: rightClickNode.nodekey,
            project_id: projectId.value
        })
        // 更新树状目录
        if (res.code === 200 && res.data) {
            treeDataStore.updateDesignDemandTreeData({ key: res.data + "-0" }, projectId.value)
        }
    }

    return {
        popupVisible,
        popupContainer,
        roundRightVisible,
        roundRightContainer,
        problemRoundRef,
        options,
        modalVisible,
        relatedCopyData,
        cascaderLoading,
        problemTitle,
        checkboxValue,
        displayRightMenu,
        handleProblemShowClick,
        handleDoptionClickGreateCases,
        handleDoptionClickCopyDemand,
        handleCopyDemand,
        handleCreateRenji
    }
}
