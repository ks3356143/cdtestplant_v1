<template>
    <div class="proj-fragment-container">
        <div class="ma-content-block lg:flex justify-between p-4">
            <div class="lg:w-full w-full lg:ml-4 mt-5 lg:mt-0" v-loading="isDataLoading">
                <page-header :data="headerData">
                    <a-popover position="right">
                        <icon-exclamation-circle-fill size="26" style="color: #ff9800" />
                        <template #content>
                            <a-typography-title :heading="6">注意：</a-typography-title>
                            <a-typography-paragraph>
                                <p>
                                    自定义片段的名称必须是<span class="text-red-500">平台所支持的片段名称</span
                                    >，否则无效!
                                </p>
                                <p>
                                    测试人员新增文档片段，可录入<span class="text-red-500">文字（含缩进）</span>、<span
                                        class="text-red-500"
                                        >图片（居中）</span
                                    >、<span class="text-red-500">表格</span>等内容
                                </p>
                            </a-typography-paragraph>
                            <a-typography-title :heading="6">目前已支持片段名称：</a-typography-title>
                            <a-typography-paragraph>
                                <ul>
                                    <li>测评对象</li>
                                    <li>静态测试环境说明</li>
                                    <li>静态软件项</li>
                                    <li>静态硬件和固件项</li>
                                    <li>动态测试环境说明</li>
                                    <li>动态软件项</li>
                                    <li>动态硬件和固件项</li>
                                    <li>测评数据</li>
                                    <li>环境差异性分析</li>
                                    <li>测试级别和测试类型</li>
                                    <li>测试策略</li>
                                </ul>
                            </a-typography-paragraph>
                        </template>
                    </a-popover>
                </page-header>
                <hr />
                <ma-crud class="mt-3" :options="crudOptions" :columns="crudColumns" ref="crudRef">
                    <!-- 切换is_main -->
                    <template #is_main="{ record }">
                        <a-switch
                            v-model:model-value="record.is_main"
                            :before-change="beforeSwitchChange(record)"
                        ></a-switch>
                    </template>
                    <!-- 选择预制文档片段模版 -->
                    <template #tableAfterButtons>
                        选择新增时预制数据：
                        <a-select
                            v-model="selectedValue"
                            :style="{ width: '230px' }"
                            placeholder="请选择新增时文档片段模版"
                        >
                            <a-option v-for="(value, key) in fragmentName" :key="key">{{ value }}</a-option>
                        </a-select>
                    </template>
                </ma-crud>
            </div>
        </div>
    </div>
</template>

<script setup lang="tsx">
import { computed, ComputedRef } from "vue"
import PageHeader from "@/views/testmanage/components/PageHeader/index.vue"
// apis - import
import { FragApi } from "@/api/system/fragment"
import projectApi from "@/api/testmanage/project"
// types - import
import type { IPageHeaderProps } from "../components/PageHeader/types"
import { Message } from "@arco-design/web-vue"
// 导入文档片段的配置
import { fragmentName } from "@/views/testmanage/projFragment/constants"
// hooks-import
import useFetchData from "@/hooks/fetchData"
import useCrudOption from "./hooks/crudOption"
// 1.hook-crudOptions
const { crudRef, crudOptions, crudColumns, route, selectedValue } = useCrudOption()
// 2.hook-获取单个项目信息
const fetchData = async () => {
    return projectApi.getProjectById(route.params.projectId)
}
const { loadingData, isDataLoading } = useFetchData({}, fetchData)
// 3.给头部组件的计算属性
const headerData: ComputedRef<IPageHeaderProps> = computed(() => {
    return {
        title: loadingData.value.ident as string,
        name: loadingData.value.name as string
    }
})
// 4.noQuery - 请求头部数据
const beforeSwitchChange = (record: any) => {
    return async function (newVal: boolean) {
        await FragApi.update(record.id, {
            is_main: newVal,
            projectId: route.params.projectId as string
        })
        Message.success("设置成功")
    }
}

defineOptions({
    name: "projFragment"
})
</script>

<style scoped></style>
