<template>
    <div class="ma-content-block p-3 block lg:border-0 lg:flex justify-between">
        <!-- 注意修复 上面dom删除 -> lg:h-full -->
        <div class="h-full w-full lg:ml-3 lg:mr-2 pt-2">
            <!-- ma-crud组件 -->
            <ma-crud :options="crudOptions" :columns="crudColumns" ref="crudRef">
                <template #operationBeforeExtend="{ record }">
                    <a-popover title="点击配置生成文档" trigger="click">
                        <a-button type="primary" size="mini">
                            <template #icon>
                                <icon-download />
                            </template>
                            文档生成
                        </a-button>
                        <template #content>
                            <a-space direction="vertical" :size="0" align="start">
                                <a-space direction="vertical" :size="0" align="start">
                                    <a-link @click="openCreateModal('测评大纲', record.id)">测评大纲</a-link>
                                    <a-link @click="openCreateModal('测试说明', record.id)">测试说明</a-link>
                                    <a-link @click="openCreateModal('测试记录', record.id)">测试记录</a-link>
                                    <a-link @click="openCreateModal('回归测试说明', record.id)">回归测试说明</a-link>
                                    <a-link @click="openCreateModal('回归测试记录', record.id)">回归测试记录</a-link>
                                    <a-link @click="openCreateModal('问题单', record.id)">问题单</a-link>
                                    <a-link @click="openCreateModal('测评报告', record.id)">测评报告</a-link>
                                </a-space>
                            </a-space>
                        </template>
                    </a-popover>
                    <a-button @click="enterWorkPlant(record)" size="mini" status="warning" type="outline"> 工作区 </a-button>
                    <a-link @click="previewRef.open(record)"><icon-eye />预览</a-link>
                    <a-link @click="handleFragmentClick(record)"><icon-file />片段</a-link>
                    <a-link @click="handleBoardClick(record)"><icon-dashboard />看板</a-link>
                </template>
            </ma-crud>
            <GeneratorModal ref="generatorModalRef" />
        </div>
        <preview ref="previewRef" :columns="crudColumns"></preview>
    </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import preview from "./cpns/preview.vue" // 项目详情预览组件
import useEnterWorkPlant from "./hooks/useEnterWorkPlant" // 进入工作区逻辑
import useCrudInit from "./hooks/useCrudInit"
import GeneratorModal from "./GeneratorModal/index.vue" // 生成文档Modal组件
import type { DocumentType } from "@/utils/types/CommonType" // 产品文档类型

const router = useRouter()
// crud配置和字段信息定义
const { crudRef, crudOptions, crudColumns } = useCrudInit()
// 点击进入工作区函数 - 每次点击后都清除localStorage中树状目录数据
const { enterWorkPlant } = useEnterWorkPlant()

// 其他功能
// 1.跳转到项目看板页面
const handleBoardClick = (record: any) => {
    router.push({
        name: "projBoard",
        params: {
            projectId: record.id
        }
    })
}
// 2.跳转到项目所属文档片段
const handleFragmentClick = (record: any) => {
    router.push({
        name: "projFragment",
        params: {
            projectId: record.id
        }
    })
}
// 3.预览项目信息ref
const previewRef = ref()

// 4.生成文档组件
const generatorModalRef = ref<InstanceType<typeof GeneratorModal> | null>(null) // GeneratorModal组件的ref
const openCreateModal = (documentType: DocumentType, id: number) => {
    generatorModalRef.value!.open(documentType, id) // 打开弹出框
}

defineOptions({
    name: "projmanage"
})
</script>

<style scoped lang="less">
.msg-menu {
    & li {
        border-radius: 1px;
        cursor: pointer;
        margin-bottom: 5px;
        padding: 10px;
        padding-left: 20px;
    }
    & li:hover,
    & li.active {
        background: var(--color-fill-2);
        color: rgb(var(--primary-5));
    }
}
</style>
