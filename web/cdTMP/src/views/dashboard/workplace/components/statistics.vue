<template>
    <st-welcome></st-welcome>
    <st-count />
    <st-project-chart />
    <div class="block lg:flex">
        <st-announced />
        <st-cdtestmanage-info />
    </div>
</template>

<script setup>
import stWelcome from "./cpns/st-welcome.vue"
import stCount from "./cpns/st-count.vue"
import stProjectChart from "./cpns/st-project-chart.vue"
import stAnnounced from "./cpns/st-announced.vue"
import stCdtestmanageInfo from "./cpns/st-cdtestmanage-info.vue"
</script>

<style lang="less" scoped></style>
