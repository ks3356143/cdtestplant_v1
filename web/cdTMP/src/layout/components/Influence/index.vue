<template>
    <div class="influence-container">
        <a-tooltip content="影响域分析">
            <icon-fire
                style="position: absolute; right: 95px; font-size: 12px; top: 8px"
                :style="{ color: isInfluence ? '#00b42a' : '#ff7d00' }"
                @click="handleInfluence"
            />
        </a-tooltip>
        <EffectModal ref="effectRef" :reset="fetchInfluenceExist" />
    </div>
</template>

<script setup lang="ts">
import { useTemplateRef, provide, onMounted, ref } from "vue"
import type { NodeDataInterface } from "./types"
import EffectModal from "./EffectModal/index.vue"
import roundApi from "@/api/project/round"
import { useRoute } from "vue-router"

// globals
const route = useRoute()

// 树状传递的轮次节点数据
const { nodeData } = defineProps<{ nodeData: NodeDataInterface }>()
provide("nodeData", nodeData)

const effectRef = useTemplateRef("effectRef")

const handleInfluence = () => {
    effectRef.value?.open()
}

// 在挂载时查询影响域分析
const isInfluence = ref(false)
const fetchInfluenceExist = async () => {
    try {
        const res = await roundApi.getInfluenceStatus(route.query.id, nodeData.key)
        isInfluence.value = res.data
    } catch {}
}
onMounted(async () => {
    await fetchInfluenceExist()
})

defineOptions({
    name: "Influence"
})
</script>

<style scoped></style>
