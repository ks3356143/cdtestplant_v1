import { ref } from "vue"
import type { Ref } from "vue"
import { Message, Notification } from "@arco-design/web-vue"
import copyApi from "@/api/treeOperation/copy"
import { useRouter } from "vue-router"
import { useRoute } from "vue-router"
import { useTreeDataStore } from "@/store"
export default function useNodeCopy(projectId: Ref<string>) {
    // global
    const router = useRouter()
    const route = useRoute()
    const treeDataStore = useTreeDataStore()
    // refs
    const checkedKeys = ref<string[]>([]) // v-model勾选的节点
    const visible = ref<boolean>(false) // 进度条专用modal
    const isComplete = ref<boolean>(false)
    const ptext = ref("轮次数据")
    // 事件处理
    /**
     * 处理弹窗点击确定事件
     */
    const handleCopyNode = async () => {
        // 0.先判断是否是同一个轮次的节点，如果不是则不处理
        let firstNodeRoundKey: string = ""
        let isFirst: boolean = true
        checkedKeys.value.forEach((item) => {
            if (isFirst) {
                firstNodeRoundKey = item.split("-")[0]
                isFirst = false
            } else {
                if (item.split("-")[0] !== firstNodeRoundKey) {
                    Message.error("请选择同一轮次的节点进行复制")
                    return
                }
            }
        })
        // 1.先判断是否选中了节点
        if (checkedKeys.value.length < 1) {
            Message.error("您未选择节点，请选择后再试...")
            return
        }
        visible.value = true // 显示气泡弹窗
        isComplete.value = false
        const st = await copyApi
            .copyCheckedNode({ checkedNodes: checkedKeys.value, project_id: projectId.value })
            .catch(() => {
                // 如果接口出错则关闭进度显示
                isComplete.value = true
                visible.value = false
            })
        isComplete.value = true
        Message.success(st.message)
        Notification.warning("请注意自动生成的设计需求、测试项、用例信息重复，需要修改")
        // 清空checkedKeys
        checkedKeys.value = []
        // 处理完后需要更新树结构
        treeDataStore.resetTreeData(projectId.value)
        // 清除右侧路由的组件显示，不然会因为数据而出错，当然直接复制query可能是错误信息
        router.replace({ name: "project", query: route.query })
    }
    const handleModalConfirmClick = () => {
        visible.value = false
    }
    return {
        checkedKeys,
        visible,
        isComplete,
        ptext,
        handleCopyNode,
        handleModalConfirmClick
    }
}
