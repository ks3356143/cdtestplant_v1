<template>
    <div class="w-full mx-auto">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <a-card
                v-for="item in cards"
                :key="item.key"
                :bordered="false"
                class="stat-card"
                :body-style="{ padding: '16px' }"
                hoverable
            >
                <div class="flex items-center gap-3">
                    <div class="stat-icon" :style="{ background: item.bg, color: item.color }">
                        <component :is="item.icon" />
                    </div>
                    <div class="min-w-0">
                        <div class="stat-label">{{ item.label }}</div>
                        <div class="stat-value">{{ statistics[item.key] ?? 0 }}</div>
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

const cards = [
    { key: "ucount", label: "用户统计", icon: "icon-user-group", color: "#0f766e", bg: "#e6f6f3" },
    { key: "ppcount", label: "进行中项目数", icon: "icon-clock-circle", color: "#b45309", bg: "#fdf3e3" },
    { key: "pcount", label: "项目总数", icon: "icon-file", color: "#334155", bg: "#eef1f4" },
    { key: "pdcount", label: "完成的项目数", icon: "icon-check-circle", color: "#047857", bg: "#ecfdf5" }
]

onMounted(async () => {
    try {
        const res = await workplaceApi.getStatistics()
        if (res?.data) statistics.value = res.data
    } catch {
        // 统计失败时保留 0，不影响页面其余内容
    }
})
</script>

<style scoped>
.stat-card {
    border-radius: 0;
    border: 1px solid var(--color-border-2);
    background: var(--color-bg-2);
}

.stat-icon {
    width: 40px;
    height: 40px;
    border-radius: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
}

.stat-label {
    font-size: 13px;
    color: var(--color-text-3);
    line-height: 1.4;
    white-space: nowrap;
}

.stat-value {
    font-size: 26px;
    font-weight: 600;
    line-height: 1.2;
    color: var(--color-text-1);
    font-variant-numeric: tabular-nums;
}
</style>
