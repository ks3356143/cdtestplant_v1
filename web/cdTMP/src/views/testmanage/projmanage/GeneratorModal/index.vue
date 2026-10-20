<template>
    <!-- 该组件是点击生成的弹出框 -->
    <div class="create-modal-container">
        <a-modal v-model:visible="visible" unmount-on-close render-to-body width="50%" hide-cancel :footer="false">
            <template #title> {{ title }}上传下载 </template>
            <a-list class="alist">
                <template #header>上传您的{{ title }}：</template>
                <a-list-item>
                    <!-- 文件上传：回归测试说明、回归测试记录 -->
                    <div v-if="title === '回归测试说明' || title === '回归测试记录'">
                        <HgDocUpload :project-id="projectId" :document-type="title" />
                    </div>
                    <!-- 文件上传：其他文档 -->
                    <div v-else>
                        <a-upload
                            :action="tool.apiUrl(`/api/documentUpload/file?id=${projectId}&documentType=${title}`)"
                            :limit="1"
                            accept=".docx, application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            @error="uploadErrorHandle"
                            @before-upload="confirmUploadHandle"
                        />
                    </div>
                </a-list-item>
            </a-list>
            <!-- 文档片段覆盖选取 -->
            <div v-if="fragmentList.length">
                <a-list :loading="fragmentListPending" hoverable size="small">
                    <template #header>选取需要被覆盖的文档片段：</template>
                    <a-list-item>
                        <div class="buttonAndAlert">
                            <a-alert type="warning">首次生成请全勾选</a-alert>
                            <div class="button-list">
                                <a-button type="primary" status="success" @click="allCheckBtn">全勾选</a-button>
                                <a-button type="primary" status="warning" @click="allUnCheckBtn">全不勾选</a-button>
                            </div>
                        </div>
                    </a-list-item>
                    <a-list-item v-for="(frag, index) in fragmentList" :key="index">
                        <div class="fragment-item">
                            <div class="fragment-name text-center">{{ frag.name }}</div>
                            <a-divider direction="vertical" />
                            <template v-if="frag.isLock">
                                <!-- 表示已经被锁住了 -->
                                <a-popover title="片段被锁定">
                                    <icon-lock style="color: red" size="20" />
                                    <template #content>
                                        <p>文档片段已经被设置为锁定（word中开发工具>属性解锁）</p>
                                        <p style="color: red">注意：被锁定的片段无法被平台数据覆盖!</p>
                                    </template>
                                </a-popover>
                            </template>
                            <template v-else>
                                <icon-unlock style="color: green" size="20" />
                            </template>
                            <a-divider direction="vertical" />
                            <a-switch v-model="frag.isCover"></a-switch>
                        </div>
                    </a-list-item>
                </a-list>
            </div>
            <div v-else>
                <a-list :loading="fragmentListPending" hoverable size="small">
                    <template #header>选取需要被覆盖的文档片段：</template>
                    <a-list-item>
                        <Empty text="未找到文档片段，请先下载" />
                    </a-list-item>
                </a-list>
            </div>
            <div>
                <a-list class="alist">
                    <a-list-item>
                        <div class="button-list">
                            <a-button :loading="isGenerating" type="primary" @click="downloadHandle"> 确认并下载 </a-button>
                        </div>
                    </a-list-item>
                </a-list>
            </div>
        </a-modal>
        <Progress :visible="progressVisible" :isComplete="isComplete" :text="title" @clickConfirm="handleModalConfirmClick"></Progress>
    </div>
</template>

<script setup lang="ts">
import { DocumentType } from "@/utils/types/CommonType" // 产品文档类型
import { ref } from "vue"
import fragmentApi from "@/api/generate/fragment" // 获取某项目某测试文档的片段api
import Empty from "@/components/Empty/index.vue" // 空状态组件
import HgDocUpload from "@/views/testmanage/projmanage/GeneratorModal/HgDocUpload/index.vue"
import Progress from "@/views/testmanage/projmanage/cpns/progress.vue"
import { Message, Modal } from "@arco-design/web-vue"
import tool from "@/utils/tool"
import useGenerateSecond from "../hooks/useGenerateSecond"
import useSeitaiModal from "../hooks/useSeitaiModal"

// 定义覆盖文档片段每项类型
export interface IFragmentItem {
    name: string
    isCover: boolean
    isLock: boolean // 是否锁定
}

// ~~~~1.文档片段展示功能~~~~
const visible = ref(false) // v-model:显式隐藏modal
const title = ref("测评大纲") // modal的标题
const projectId = ref<number | null>(null) // 传入的项目id
const fragmentListPending = ref(false) // 片段列表请求的loading状态
// 定义文档片段储存
const fragmentList = ref<IFragmentItem[]>([])

// out：暴露出去的函数
const open = async (documentType: DocumentType, id: number) => {
    projectId.value = id // 传入的项目id
    title.value = documentType
    visible.value = true
    // 打开时清空fragmentList数据
    fragmentList.value = []
    // 打开时请求数据
    fragmentListPending.value = true // 设置loading状态
    // 请求片段列表数据
    try {
        const { data } = await fragmentApi.getFragmentByDocumentType({
            id: projectId.value,
            documentType
        })
        // 填充到fragmentList
        fragmentList.value = data.map((it: { frag_name: string; isLock: boolean }) => ({
            name: it.frag_name,
            isCover: false,
            isLock: it.isLock // 是否锁定
        }))
        fragmentListPending.value = false
    } catch (err) {
        fragmentListPending.value = false // 请求失败，关闭loading状态
    }
}

// 全勾选/全不勾选按钮
const allCheckBtn = () => {
    fragmentList.value.forEach((item) => {
        item.isCover = true // 全部勾选
    })
}
const allUnCheckBtn = () => {
    fragmentList.value.forEach((item) => {
        item.isCover = false // 全部不勾选
    })
}

// ~~~~2.文件上传功能~~~~
// 上传失败的事件 - 报错内容由后端定义（message字段）
const uploadErrorHandle = (fielItem: any) => {
    const res = JSON.parse(fielItem.response)
    if (res.message) {
        Message.error(res.message)
    }
}
// 上传弹窗事件
const confirmUploadHandle = (file: any) => {
    return new Promise<boolean>((resolve, reject) => {
        Modal.confirm({
            title: "请确认您上传的文件是带有文档片段的docx文档",
            content: `${file.name}`,
            onOk: () => resolve(true),
            onCancel: () => reject("cancel")
        })
    })
}

// ~~~~3.产品文档下载功能~~~~
// 注意二段文档生成成功后，需要刷新片段列表数据（待完成）
const downloadHandle = async () => {
    // 判断产品文档类型
    const documentType = title.value
    try {
        // 二段文档异步请求
        switch (documentType) {
            case "测评大纲":
                await createDgItem(projectId.value!)
                break
            case "测试说明":
                await createSmItem(projectId.value!)
                break
            case "测试记录":
                await createJLItem(projectId.value!)
                break
            case "回归测试说明":
                await createHsmItem(projectId.value!)
                break
            case "回归测试记录":
                await createHjlItem(projectId.value!)
                break
            case "问题单":
                await createWtdItem(projectId.value!)
                break
            case "测评报告":
                await createBgItem(projectId.value!)
                break
            default:
                break
        }
        // 生成最终产品文档请求 -> 添加当前用户取消选择的片段
        switch (documentType) {
            case "测评大纲":
                await createSeitaiDagang(projectId.value!, documentType, fragmentList.value)
                break
            case "测试说明":
                await createSeitaiShuoming(projectId.value!, documentType, fragmentList.value)
                break
            case "测试记录":
                await createSeitaiJilu(projectId.value!, documentType, fragmentList.value)
                break
            case "回归测试说明":
                await createSeitaiHsm(projectId.value!, documentType, fragmentList.value)
                break
            case "回归测试记录":
                await createSeitaiHjl(projectId.value!, documentType, fragmentList.value)
                break
            case "问题单":
                await createSeitaiWtd(projectId.value!, documentType, fragmentList.value)
                break
            case "测评报告":
                await createSeitaiBaogao(projectId.value!, documentType, fragmentList.value)
                break
            default:
                break
        }
        // 为了方便直接关闭弹窗，这样用户可以使用open函数初始化
        visible.value = false
    } catch (err) {
        // 总体出错处理，关闭弹窗
        visible.value = false
    }
}

// hook-二段文档函数
const { isGenerating, createDgItem, createSmItem, createJLItem, createHsmItem, createHjlItem, createWtdItem, createBgItem } = useGenerateSecond()

// hook-生成产品文档
const {
    visible: progressVisible,
    isComplete,
    handleModalConfirmClick,
    createSeitaiDagang,
    createSeitaiShuoming,
    createSeitaiJilu,
    createSeitaiHsm,
    createSeitaiHjl,
    createSeitaiWtd,
    createSeitaiBaogao
} = useSeitaiModal()

defineExpose({ open })

defineOptions({
    name: "GeneratorModal"
})
</script>

<style lang="less" scoped>
.fragment-item {
    display: flex;
    align-items: center;
    justify-content: space-around;
    .fragment-name {
        width: 40%;
    }
}

.button-list {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-left: 20px;
}

.alist {
    margin: 10px 0;
}
.buttonAndAlert {
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
