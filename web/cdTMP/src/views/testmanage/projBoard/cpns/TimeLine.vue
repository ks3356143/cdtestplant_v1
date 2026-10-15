<template>
    <div class="time-line-container">
        <div class="ma-content-block rounded-xs flex-column justify-between w-full p-3 bg-color">
            <div class="title">填写的项目时间轴</div>
            <a-timeline direction="horizontal" class="timeline" mode="alternate">
                <a-timeline-item :label="pInfo.time_line.start_time">
                    <a-row :style="{ display: 'inline-flex', alignItems: 'center' }">
                        <div>开始时间</div>
                    </a-row>
                </a-timeline-item>
                <a-timeline-item
                    v-for="(item, index) in pInfo.time_line.round_time"
                    :key="index"
                    :dot-color="isErrorHighlight && index === pInfo.time_line.round_time.length - 1 ? 'red' : undefined"
                >
                    <template #label>
                        <span :class="{ 'text-red-500': isErrorHighlight && index === pInfo.time_line.round_time.length - 1 }">结束时间 : {{ item.end }}</span>
                    </template>
                    <a-col>
                        <div>{{ item.name }}</div>
                        <div class="a-col-title">开始时间 : {{ item.start }}</div>
                    </a-col>
                </a-timeline-item>
                <a-timeline-item :dot-color="isErrorHighlight ? 'red' : undefined">
                    <template #label>
                        <span :class="{ 'text-red-500': isErrorHighlight }">{{ pInfo.time_line.end_time }}</span>
                    </template>
                    <a-row :style="{ display: 'inline-flex', alignItems: 'center' }">
                        <span>结束时间</span>
                    </a-row>
                </a-timeline-item>
                <div class="info">
                    <a-alert>测试人员填写的项目开始时间、结束时间、轮次时间均会影响生成文档的时间!</a-alert>
                    <a-button type="primary" @click="handleModalVisible">展示目前文档生成的日期</a-button>
                </div>
            </a-timeline>
        </div>
        <!-- a-modal组件，展示生成文档的全部信息 -->
        <a-modal v-model:visible="visible" unmount-on-close hide-cancel :closable="false" width="auto">
            <template #title> 生成文档时间一览表 </template>
            <a-card :style="{ width: '600px' }" :title="item.title" hoverable v-for="(item, index) in timeList" :key="item.title">
                <p v-for="(value, key, idx) in item" class="flex">
                    <template v-if="key !== 'title'">
                        <span class="font-bold w-75">{{ key }}</span>
                        <span class="">{{ value }}</span>
                    </template>
                </p>
            </a-card>
        </a-modal>
    </div>
</template>

<script setup>
import { ref } from "vue"
import { useDocTimeShow } from "./useDocTimeShow"
// 1.定义props
const props = defineProps({
    pInfo: {
        type: Object,
        required: true
    },
    projectId: {
        type: String,
        required: true
    }
})

// 在一开始就请求接口
const { visible, handleModalVisible, timeList } = useDocTimeShow(props.projectId, highlightLastItems)

// 控制错误状态
const isErrorHighlight = ref(false)
function highlightLastItems() {
    isErrorHighlight.value = true
}

defineExpose({
    highlightLastItems
})
</script>

<style lang="less" scoped>
.title {
    margin: 10px;
    font-weight: 700;
    font-size: 1rem;
}
.timeline {
    position: relative;
    padding: 50px;
    width: 100%;
    .info {
        width: 180px;
        position: absolute;
        right: 30px;
        top: 1rem;
        button {
            width: 180px;
            border-radius: 0;
        }
    }
}
.a-col-title {
    font-size: 12px;
    margin-bottom: -5px;
    margin-top: 5px;
    color: var(--color-text-3);
}
</style>
