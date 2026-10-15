import { ref } from "vue"

export default function useHoverText() {
    const hoverText = ref("")
    const buttonLikeRef = ref<HTMLDivElement | null>(null)
    const onMouseenter = () => {
        hoverText.value = "查看上级"
    }
    const onMouseleave = () => {
        hoverText.value = ""
    }
    return { hoverText, buttonLikeRef, onMouseenter, onMouseleave }
}
