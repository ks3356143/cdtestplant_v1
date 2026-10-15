<template>
    <div class="project-info-other-container">
        <a-dropdown :popup-max-height="false">
            <a-space>
                <SettingButton label="项目设置">
                    <a-tooltip :content="allStatus ? '您已全部填写' : '还有未填写项目'">
                        <span class="text-green-500" v-if="allStatus">
                            <icon-check-circle-fill size="20px" />
                        </span>
                        <span class="text-red-500" v-else><icon-exclamation-circle-fill size="20px" /></span>
                    </a-tooltip>
                </SettingButton>
            </a-space>
            <template #content>
                <template v-for="item in inputOptions" :key="item.name">
                    <template v-if="!item.status">
                        <a-tooltip :content="`还未录入${item.title}`">
                            <a-doption @click="item.handler">
                                <span class="mr-1">{{ item.title }}</span>
                                <span class="text-red-500"><icon-exclamation-circle-fill /></span>
                            </a-doption>
                        </a-tooltip>
                    </template>
                    <template v-else>
                        <a-doption @click="item.handler">
                            <span class="mr-1">{{ item.title }}</span>
                            <span class="text-green-500"><icon-check-circle-fill /></span>
                        </a-doption>
                    </template>
                </template>
            </template>
        </a-dropdown>
        <!-- 软件概述... -->
        <project-modal ref="projectModalRef" :reset="fetchAllStatus" />
        <!-- 接口图 -->
        <InterfaceImage ref="interfaceImageRef" :reset="fetchAllStatus" />
        <!-- 静态软件项、静态硬件项、动态软件项、动态硬件项 -->
        <StaticDynamicTable ref="staticDynamiRef" :reset="fetchAllStatus" />
        <!-- 环境差异性分析 -->
        <TextAndTable ref="textAndTableRef" :reset="fetchAllStatus" />
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from "vue"
import projectApi from "@/api/project/project"
import { useRoute } from "vue-router"
import { Message } from "@arco-design/web-vue"
import ProjectModal from "./projectModal/index.vue"
import InterfaceImage from "./InterfaceImage.vue"
import StaticDynamicTable from "./StaticDynamicTable.vue"
import TextAndTable from "./TextAndTable.vue"
import SettingButton from "./settingButton/index.vue"

const route = useRoute()

// ref
const projectModalRef = ref<InstanceType<typeof ProjectModal> | null>(null)
const interfaceImageRef = ref<InstanceType<typeof InterfaceImage> | null>(null)
const staticDynamiRef = useTemplateRef("staticDynamiRef")
const textAndTableRef = useTemplateRef("textAndTableRef")

// events
const clickStuctDatas = async (category: string) => {
    projectModalRef.value?.open(category)
}
const clickInterfaceImage = async () => {
    interfaceImageRef.value?.open()
}
const clickStaticDynamic = async (title: string) => {
    staticDynamiRef.value?.open(title)
}
const clickTextAndTable = async (title: string) => {
    textAndTableRef.value?.open(title)
}

// 进入页面时候请求知道各项目样式情况-ref
const fetchAllStatus = async () => {
    try {
        const { data }: { data: Object } = await projectApi.getAllStatus(route.query.id)
        inputOptions.value = inputOptions.value.map((it) => {
            if (data.hasOwnProperty(it.name)) {
                it.status = data[it.name]
            }
            return { ...it }
        })
    } catch (e) {
        Message.error("查询项目级信息是否填写失败，请检查网络")
    }
}

onMounted(async () => {
    await fetchAllStatus()
})

const inputOptions = ref([
    {
        name: "soft_summary",
        title: "软件概述",
        status: false,
        handler: () => clickStuctDatas("软件概述")
    },
    {
        name: "interface_image",
        title: "接口图",
        status: false,
        handler: clickInterfaceImage
    },
    {
        name: "static_soft_item",
        title: "静态软件项表",
        status: false,
        handler: () => clickStaticDynamic("静态软件项")
    },
    {
        name: "static_soft_hardware",
        title: "静态硬件项表",
        status: false,
        handler: () => clickStaticDynamic("静态硬件项")
    },
    {
        name: "dynamic_des",
        title: "动态环境描述",
        status: false,
        handler: () => clickStuctDatas("动态环境描述")
    },
    {
        name: "dynamic_soft_item",
        title: "动态软件项表",
        status: false,
        handler: () => clickStaticDynamic("动态软件项")
    },
    {
        name: "dynamic_soft_hardware",
        title: "动态硬件项表",
        status: false,
        handler: () => clickStaticDynamic("动态硬件项")
    },
    {
        name: "evaluate_data",
        title: "测评数据",
        status: false,
        handler: () => clickStaticDynamic("测评数据")
    },
    {
        name: "env_analysis",
        title: "环境差异性分析",
        status: false,
        handler: () => clickTextAndTable("环境差异性分析")
    }
])
const allStatus = computed(() => inputOptions.value.every((item) => item.status))

defineOptions({
    name: "ProjectInfoOther"
})
</script>

<style scoped lang="less"></style>
