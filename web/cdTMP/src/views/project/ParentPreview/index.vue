<script lang="tsx">
import { defineComponent, Teleport } from "vue"
import { useRoute } from "vue-router"
import { Popover } from "@arco-design/web-vue"
// 请求的API
import dutApi from "@/api/project/dut"
import designApi from "@/api/project/designDemand"
import demandApi from "@/api/project/testDemand"
// hooks
import useHoverText from "./useHoverText"
import useKeyToMaInfo from "./useKeyToMaInfo"

export default defineComponent({
    name: "ParentPreview",
    props: {
        parentKey: { type: String, default: "" } // 在ma-form已经判断所以必然有值，索引上级key
    },
    setup(props) {
        // 1.获取路由上的-项目id
        const route = useRoute()
        const project_id = route.query.id // 项目id
        // 2.获取传入的key信息，给上级节点
        const keyLength = props.parentKey.split("-").length
        // 3.hover变化按钮hook
        const { hoverText, buttonLikeRef, onMouseenter, onMouseleave } = useHoverText()
        // 4.里面处理不同columns，返回的函数可以对ma-info的DOM进行构建
        const { maInfoDom, fetchNodeDataAndSetMaInfo } = useKeyToMaInfo()
        // 5.根据不同长度
        switch (keyLength) {
            case 2:
                // 请求设计需求节点
                fetchNodeDataAndSetMaInfo(dutApi.getDutOne({ project_id, key: props.parentKey }), "dut")
                break
            case 3:
                // 请求测试项节点
                fetchNodeDataAndSetMaInfo(designApi.getDesignDemandOne({ project_id, key: props.parentKey }), "design")
                break
            case 4:
                // 请求用例节点
                fetchNodeDataAndSetMaInfo(demandApi.getTestDemandOne({ project_id, key: props.parentKey }), "demand")
                break
            default:
                break
        }

        return () => (
            <Teleport to="body">
                <Popover trigger="click" position="left">
                    {{
                        default: () => (
                            <div class="preview-container">
                                <div class="button-like" ref={buttonLikeRef} onMouseenter={onMouseenter} onMouseleave={onMouseleave}>
                                    <icon-find-replace />
                                    {hoverText.value && <span class="ml-2">{hoverText.value}</span>}
                                </div>
                            </div>
                        ),
                        content: () => (
                            // 内容插槽
                            <div
                                style={{
                                    width: "600px"
                                }}
                            >
                                {maInfoDom.value}
                            </div>
                        )
                    }}
                </Popover>
            </Teleport>
        )
    }
})
</script>

<style scoped lang="less">
.preview-container {
    position: fixed;
    right: 80px;
    top: 45%;
    z-index: 10000;
}
.button-like {
    width: 40px;
    height: 40px;
    font-size: 16px;
    border-radius: 50%;
    background-color: #fff;
    display: flex;
    justify-content: center;
    align-items: center;
    user-select: none;
    cursor: pointer;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.8);
    transition: all 0.1s;
    overflow: hidden;
    position: relative;
    span {
        white-space: nowrap;
    }
}
.button-like:hover {
    width: 120px;
    border-radius: 22px;
    transition: all 0.1s;
    border: 1px solid rgb(64, 128, 255);
    color: rgb(64, 128, 255);
}
.click-content {
    min-width: 500px;
    min-height: 300px;
    background-color: #fff;
}
</style>
