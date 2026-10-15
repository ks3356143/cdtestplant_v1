<template>
    <a-layout class="layout">
        <div class="navbar layout-navbar">
            <NavBar :title="projectInfo.name" />
        </div>
        <a-layout class="layout layout-demo">
            <a-layout-sider class="layout-sider" :resize-directions="['right']" :width="300">
                <div class="p-2 overflow-auto h-full">
                    <a-input-group class="mb-2 w-full flex items-center" size="mini">
                        <a-input style="height: 32px" v-model="searchKey" allow-clear></a-input>
                        <a-button @click="handleSearchTreeDataClick">搜索</a-button>
                    </a-input-group>
                    <div class="flex justify-between mb-2">
                        <a-button type="primary" @click="toggleExpanded" class="w-5/12">
                            {{ expandedKeys?.length ? "全部收缩" : "全部展开" }}
                        </a-button>
                        <a-popconfirm type="warning" @ok="handleCopyNode" content="是否确定根据选中节点进行创建？">
                            <a-button type="outline" status="warning">
                                <template #icon> <icon-plus /></template>点击复制创建轮次
                            </a-button>
                        </a-popconfirm>
                    </div>
                    <a-tree
                        class="h-10/12 select-none my-arco-wrap-class"
                        :data="treeData"
                        size="mini"
                        showLine
                        checkable
                        block-node
                        draggable
                        animation
                        auto-expand-parent
                        @select="pointNode"
                        @drop="ondrop"
                        :allow-drop="allowdrop"
                        :load-more="loadMore"
                        v-model:expanded-keys="expandedKeys"
                        v-model:selected-keys="selectedKeys"
                        v-model:checked-keys="checkedKeys"
                        ref="treeRef"
                        border
                        @contextmenu="displayRightMenu"
                        :default-selected-keys="[currentNode ? currentNode : route.query.key]"
                    >
                        <!-- 在轮次节点可以新增、编辑、删除、复制 -->
                        <template #extra="nodeData">
                            <template v-if="nodeData.level === '0'">
                                <a-tooltip content="点击新增轮次">
                                    <IconPlus
                                        style="position: absolute; right: 8px; font-size: 12px; top: 8px; color: #3370ff"
                                        @click="() => handleRoundAddClick(nodeData)"
                                    />
                                </a-tooltip>
                                <a-tooltip content="点击删除轮次">
                                    <a-popconfirm content="确定要删除该轮次吗?" position="bottom" @ok="handleRoundDelClick(nodeData)">
                                        <icon-close style="position: absolute; right: 25px; font-size: 12px; top: 8px; color: #3370ff" />
                                    </a-popconfirm>
                                </a-tooltip>
                                <a-tooltip content="点击编辑当前轮次"
                                    ><IconEdit
                                        style="position: absolute; right: 42px; font-size: 12px; top: 8px; color: #3370ff"
                                        @click="() => handleRoundEditClick(nodeData)"
                                /></a-tooltip>
                                <a-tooltip content="综合阅览该轮次下问题单"
                                    ><icon-bug
                                        style="position: absolute; right: 60px; font-size: 12px; top: 8px; color: #3370ff"
                                        @click="handleProblemShowClick"
                                /></a-tooltip>
                                <a-tooltip content="轮次数据管理视图"
                                    ><icon-storage
                                        style="position: absolute; right: 77px; font-size: 12px; top: 8px; color: #3370ff"
                                        :style="{
                                            color: isOpeSetsRoute && nodeData.key === route.query.key ? 'red' : '#3370ff'
                                        }"
                                        @click="
                                            () => {
                                                router.push({
                                                    name: 'opeSets',
                                                    query: {
                                                        ...route.query,
                                                        key: nodeData.key
                                                    }
                                                })
                                            }
                                        "
                                /></a-tooltip>
                                <template v-if="nodeData.key !== '0'">
                                    <Influence :node-data="nodeData"></Influence>
                                </template>
                            </template>
                        </template>
                        <!-- 设计节点的图标 -->
                        <template #switcher-icon="_, { isLeaf }">
                            <div class="font-icon">
                                <IconDownCircle v-if="!isLeaf" />
                                <IconFile v-if="isLeaf" />
                            </div>
                        </template>
                        <!-- 节点图标插槽 -->
                        <template #icon="props">
                            <template v-if="props.node.level === '1'"> <span style="white-space: nowrap">[被测件]</span> </template>
                            <template v-if="props.node.level === '2'"> [设] </template>
                            <template v-if="props.node.level === '3'"> [项] </template>
                            <template v-if="props.node.level === '4'">
                                <template v-if="props.node.isRelatedProblem">
                                    <a-tooltip content="有问题单关联">
                                        <button>[@]</button>
                                    </a-tooltip>
                                </template>
                                <template v-else>
                                    <template v-if="props.node.isNotPassed">
                                        <a-tooltip content="该用例未通过，但是未关联问题单，请关联">
                                            <button :style="{ color: 'red' }">[×]</button>
                                        </a-tooltip>
                                    </template>
                                    <template v-else>
                                        <a-tooltip content="该用例未执行或已通过，未关联问题单">
                                            <button>[>]</button>
                                        </a-tooltip>
                                    </template>
                                </template>
                            </template>
                        </template>
                        <!-- 节点title插槽 -->
                        <template #title="{ level, title }">
                            <template v-if="level === '0' || level === '3'">
                                {{ title }}
                                <span class="small-right-context-tip">
                                    <i>右键</i>
                                </span>
                            </template>
                            <template v-else>{{ title }}</template>
                        </template>
                    </a-tree>
                </div>
            </a-layout-sider>
            <a-layout class="layout-content">
                <!-- 右侧界面是该元素决定滚动条overflow-y:auto -->
                <a-layout-content class="work-area project-layout" id="basic-scroll-container">
                    <PageLayout ref="routeViewRef" />
                </a-layout-content>
            </a-layout>
        </a-layout>
    </a-layout>
    <a-back-top target-container="#basic-scroll-container" :style="{ position: 'absolute' }">
        <a-popover title="回到顶部">
            <a-button type="primary" shape="circle">
                <template #icon>
                    <icon-arrow-rise />
                </template>
            </a-button>
        </a-popover>
    </a-back-top>
    <ma-form-modal ref="maFormModalRef" :title="title" :column="roundColumn" :options="roundOption" :width="800" :submit="handleRoundSubmit"> </ma-form-modal>
    <!-- 如果没有第一轮的SO_dut则弹窗 -->
    <ma-form-modal
        ref="soDutFormRef"
        :title="soDutModalTitle"
        :column="soDutColumn"
        :width="800"
        :submit="handleSoDutSubmit"
        @cancel="handleSoDutCancel"
        cancelText="返回项目页面"
        :cancel-button-props="{ status: 'warning' }"
        :closable="false"
        :mask-closable="false"
    >
        <!-- 添加input前缀 -->
        <template #inputPrepend-version> V </template>
    </ma-form-modal>
    <Progress :visible="visible" :isComplete="isComplete" :text="ptext" @clickConfirm="handleModalConfirmClick"></Progress>
    <!-- 右键菜单 -->
    <a-dropdown v-model:popup-visible="popupVisible" :popup-container="popupContainer" position="bottom" alignPoint :style="{ display: 'block' }">
        <template #content>
            <a-dgroup title="执行操作">
                <a-doption @click="handleDoptionClickGreateCases">
                    <template #icon>
                        <icon-plus-circle />
                    </template>
                    根据测试子项生成所属用例
                </a-doption>
            </a-dgroup>
            <a-dgroup title="复制">
                <a-doption @click="handleDoptionClickCopyDemand">
                    <template #icon>
                        <icon-copy />
                    </template>
                    复制到设计需求下...
                </a-doption>
            </a-dgroup>
        </template>
    </a-dropdown>
    <!-- 复制modal组件 -->
    <!-- 关联的modal组件 -->
    <a-modal v-model:visible="modalVisible" unmount-on-close :width="700" draggable :on-before-ok="handleCopyDemand">
        <template #title>复制到设计需求</template>
        <div class="pb-3">选择复制到的节点（<span class="point">支持搜索</span>）:</div>
        <a-cascader
            :options="options"
            allow-search
            allow-clear
            size="large"
            placeholder="复制到选择的设计需求节点下"
            :loading="cascaderLoading"
            v-model:model-value="relatedCopyData"
        />
        <div class="mt-3"><a-checkbox v-model="checkboxValue">是否复制用例？</a-checkbox></div>
    </a-modal>
    <!-- 拖拽用例气泡提示 -->
    <a-popconfirm
        v-model:popup-visible="paoVisible"
        ok-text="移动"
        cancel-text="复制"
        @ok="paoOk"
        @cancel="paoCancel"
        :popup-container="paoContainer"
        content="选择移动/复制"
    >
    </a-popconfirm>
    <a-popconfirm
        v-model:popup-visible="pao2Visible"
        ok-text="移动"
        cancel-text="复制"
        @ok="paoOk2"
        @cancel="paoCancel2"
        :popup-container="pao2Container"
        content="选择移动/复制"
    >
    </a-popconfirm>
    <!-- w1:外部下拉选项组件 -->
    <roundRight
        :fvisible="roundRightVisible"
        @update:visible="roundRightVisible = false"
        :container="roundRightContainer"
        @click-problem-show="handleProblemShowClick"
        @create-renji="handleCreateRenji"
    ></roundRight>
    <!-- w2:轮次的问题单ma-crud，这里要传参2个，首先是请求另外一个接口，然后取消是否关联字段 -->
    <problem-choose ref="problemRoundRef" hasRelated="roundProblem" :title="problemTitle"></problem-choose>
    <!-- 下面都是对应被测件、设计需求、测试项、测试用例、问题单的SubForm -->
    <DutSubForm ref="dutSubFormRef" />
    <DesignSubForm ref="designSubFormRef" />
    <TestDemandSubForm ref="testDemandSubFormRef" />
    <CaseSubForm ref="caseSubFormRef" />
</template>

<script setup>
import { provide, ref, watch } from "vue"
import NavBar from "@/layout/components/navbar.vue"
import PageLayout from "@/layout/page-layout.vue"
import MaFormModal from "@/components/ma-form-modal/index.vue"
// 影响域分析
import Influence from "@/layout/components/Influence/index.vue"
// 轮次的右键菜单，单独一个组件 -> 在treeComponents里面
import roundRight from "./treeComponents/roundRight.vue"
// 问题单ma-crud
import ProblemChoose from "@/views/project/case/components/ProblemChoose.vue"
import { useRoute, useRouter } from "vue-router"
import { useTreeDataStore } from "@/store"
import { storeToRefs } from "pinia"
import Progress from "@/views/testmanage/projmanage/cpns/progress.vue"
// 导入单独节点类型单独对应的Modal组件
import DutSubForm from "@/views/project/round/DutSubForm"
import DesignSubForm from "@/views/project/dut/DesignSubForm"
import TestDemandSubForm from "@/views/project/design-demand/DemandSubForm"
import CaseSubForm from "@/views/project/testDemand/CaseSubForm"
// hooks模块化
import useTreeDrag from "@/layout/treeHooks/treeDrag.js"
import { useRightClick } from "./treeHooks/rightClick"
import useNodeCopy from "./treeHooks/nodeCopy"
import useSearchNodes from "./treeHooks/searchNodes"
import useMustSoDut from "./treeHooks/mustSoDut"
import useNodeExpand from "./treeHooks/useNodeExpand"
import useNodeClick from "./treeHooks/useNodeClick"
import useLoadTreeNode from "./treeHooks/useLoadTreeNodes"
import useRoundMaForm from "./treeHooks/useRoundMaForm"
// router-view里面组件的ref -> 多个hook使用
const routeViewRef = ref()
provide("rightViewRef", routeViewRef)
const treeDataStore = useTreeDataStore()
const { treeData, currentNode } = storeToRefs(treeDataStore)
const route = useRoute()
const router = useRouter()
const treeRef = ref()
const projectInfo = ref({ ...route.query })
const projectId = ref(route.query.id)

//~~~~~~大模块：选择同一节点新建复制到下一轮~~~~~~
const { checkedKeys, visible, isComplete, ptext, handleCopyNode, handleModalConfirmClick } = useNodeCopy(projectId)

//~~~~~~provide：menu缩小菜单~~~~~~
const drawerVisible = ref(false)
provide("toggleDrawerMenu", () => {
    drawerVisible.value = !drawerVisible.value
})

//~~~~~~小功能：节点搜索功能~~~~~~
const { searchKey, handleSearchTreeDataClick } = useSearchNodes()

//~~~~~~M功能：强制必须有源代码被测件~~~~~~
const { soDutFormRef, soDutModalTitle, handleSoDutExistsForceModal, handleSoDutSubmit, handleSoDutCancel, soDutColumn } = useMustSoDut(projectId)

//~~~~~~小功能：展开和收缩~~~~~~
const { expandedKeys, toggleExpanded } = useNodeExpand()

//~~~~~~大功能：单击/双击节点逻辑~~~~~~
const { selectedKeys, pointNode, dutSubFormRef, designSubFormRef, testDemandSubFormRef, caseSubFormRef } = useNodeClick(expandedKeys)

//~~~~~~小功能：路由中key绑定selectedKeys：好像有点非性能~~~~~~
const isOpeSetsRoute = ref(false)
watch(
    () => route,
    (newRoute) => {
        isOpeSetsRoute.value = newRoute.matched.some((it) => it.name === "opeSets")
        if (isOpeSetsRoute.value) {
            selectedKeys.value = []
        } else {
            selectedKeys.value = [newRoute.query.key]
        }
    },
    { immediate: true, deep: true }
)

//~~~~~~大功能：动态加载a-tree节点函数~~~~~~
const { loadMore } = useLoadTreeNode()

//~~~~~~功能：轮次的Ma-Form~~~~~~
const { maFormModalRef, title, roundColumn, roundOption, handleRoundAddClick, handleRoundEditClick, handleRoundDelClick, handleRoundSubmit } = useRoundMaForm(
    projectId,
    handleSoDutExistsForceModal
)

// 大功能：~~~~~~右键菜单实现~~~~~~
const {
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
} = useRightClick(projectId, routeViewRef)

// ~~~~~~~~大功能：拖拽~~~~~~~~
const { paoVisible, paoContainer, pao2Visible, pao2Container, ondrop, allowdrop, paoOk, paoCancel, paoOk2, paoCancel2 } = useTreeDrag(projectId, routeViewRef)
</script>

<style lang="less" scoped>
.tree {
    height: 100%;
}
.layout {
    display: flex;
}
.layout-demo :deep(.arco-layout-sider) {
    min-width: 300px;
    max-width: 800px;
}
.layout {
    width: 100%;
    height: 100%;
}

.layout-navbar {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 100;
    width: 100%;
    height: 60px;
}

.layout-sider {
    will-change: width; // 通知浏览器宽度会变化
    transition: none !important; // 禁止transition防止延迟
    left: 0;
    z-index: 99;
    height: 100%;
    &::after {
        position: absolute;
        top: 0;
        right: -1px;
        display: block;
        width: 1px;
        height: 100%;
        background-color: var(--color-border);
        content: "";
    }

    > :deep(.arco-layout-sider-children) {
        overflow-y: hidden;
    }
}
.layout-demo {
    display: flex; // 确保是 flex 容器（Arco Layout 默认已是 flex）
    height: calc(100vh - 60px);
    margin-top: 60px;
    overflow: hidden; // 防止溢出
}
.layout-content {
    transition: none !important; // 禁止transition防止延迟
    flex: 1;
    min-height: 100vh;
    overflow-y: auto;
    background-color: var(--color-fill-2);
}
.my-arco-wrap-class :deep(.arco-tree-node-title-text) {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
}
.chen-node-title {
    cursor: help;
}
.point {
    color: red;
}
// 自定义选中节点样式
:deep(.arco-tree-node-selected) {
    .arco-tree-node-title {
        color: #f53f3f !important;
    }
}
.font-icon {
    font-size: 20px;
    margin-bottom: -2.8px;
}
.font-icon:hover {
    color: #f53f3fed;
    transition: all 0.3s;
}
// 有右键菜单节点显示图标
.small-right-context-tip {
    align-items: center;
    background: linear-gradient(54.58deg, rgba(74, 228, 255, 0.12) -14.12%, rgba(66, 130, 255, 0.12) 47.61%, rgba(215, 104, 255, 0.12) 105.84%);
    border: 1px solid #d5d7f9;
    border-radius: 10px;
    color: transparent;
    display: inline-flex;
    height: 10px;
    justify-content: center;
    margin-left: 2px;
    padding: 0 2.5px;
    position: absolute;
    top: 7px;
    i {
        -webkit-text-fill-color: transparent !important;
        zoom: 0.7;
        background: linear-gradient(85.2deg, #0062ff -3.15%, #cb50ff 98.89%) !important;
        background-clip: text !important;
        -webkit-background-clip: text !important;
        font-size: 10px;
        font-style: normal;
    }
}
</style>
