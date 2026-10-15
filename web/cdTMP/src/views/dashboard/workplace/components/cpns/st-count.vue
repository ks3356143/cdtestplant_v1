<template>
    <div class="w-full mx-auto">
        <div class="lg:grid lg:grid-cols-4 lg:gap-1">
            <a-card
                style="height: 65px"
                class="rounded-xs mt-3"
                :body-style="{ padding: 0, height: '65px' }"
                :bordered="false"
                hoverable
            >
                <div class="flex justify-between h-full">
                    <div class="en-title bg-blue-600">NU</div>
                    <div class="w-full ml-3.5 flex justify-between items-center">
                        用户统计
                        <a-space size="large" class="mr-3">
                            <div class="text-right">
                                <div>总数</div>
                                <div>{{ statistics.ucount }}</div>
                            </div>
                        </a-space>
                    </div>
                </div>
            </a-card>
            <a-card
                style="height: 65px"
                class="rounded-xs mt-3 lg:ml-2"
                :body-style="{ padding: 0, height: '65px' }"
                :bordered="false"
                hoverable
            >
                <div class="flex justify-between h-full">
                    <div class="en-title bg-red-600">NA</div>
                    <div class="w-full ml-3.5 flex justify-between items-center">
                        进行中项目数
                        <a-space size="large" class="mr-3">
                            <div class="text-right">
                                <div>总数</div>
                                <div>{{ statistics.ppcount }}</div>
                            </div>
                        </a-space>
                    </div>
                </div>
            </a-card>
            <a-card
                style="height: 65px"
                class="rounded-xs mt-3 lg:ml-2"
                :body-style="{ padding: 0, height: '65px' }"
                :bordered="false"
                hoverable
            >
                <div class="flex justify-between h-full">
                    <div class="en-title bg-pink-600">LC</div>
                    <div class="w-full ml-3.5 flex justify-between items-center">
                        项目总数
                        <a-space size="large" class="mr-3">
                            <div class="text-right">
                                <div>总数</div>
                                <div>{{ statistics.pcount }}</div>
                            </div>
                        </a-space>
                    </div>
                </div>
            </a-card>
            <a-card
                style="height: 65px"
                class="rounded-xs mt-3 lg:ml-2"
                :body-style="{ padding: 0, height: '65px' }"
                :bordered="false"
                hoverable
            >
                <div class="flex justify-between h-full">
                    <div class="en-title bg-green-600">OC</div>
                    <div class="w-full ml-3.5 flex justify-between items-center">
                        完成的项目数
                        <a-space size="large" class="mr-3">
                            <div class="text-right">
                                <div>总数</div>
                                <div>{{ statistics.pdcount }}</div>
                            </div>
                        </a-space>
                    </div>
                </div>
            </a-card>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import workplaceApi from "@/api/system/workplace"
const statistics = ref({
    ucount: 0,
    pcount: 0,
    pdcount: 0,
    ppcount: 0
})
onMounted(async () => {
    const statisticsRes = await workplaceApi.getStatistics()
    statistics.value = statisticsRes.data
})
</script>

<style scoped>
.en-title {
    width: 75px;
    color: #fff;
    text-align: center;
    font-weight: bold;
    font-size: 1.3em;
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
