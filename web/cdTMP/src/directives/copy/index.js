// 复制到粘贴板
import useClipboard from "vue-clipboard3"
import { Message } from "@arco-design/web-vue"

const copy = (el, binding) => {
    const { value } = binding
    // 若已绑定过监听，先移除旧的，避免 updated 时重复叠加监听
    if (el._copyHandler) {
        el.removeEventListener("click", el._copyHandler)
    }
    el._copyHandler = async () => {
        if (value && value !== "") {
            try {
                await useClipboard().toClipboard(value)
                Message.success("已成功复制到剪切板")
            } catch (e) {
                Message.error("复制失败")
            }
        } else {
            throw new Error(`need for copy content! Like v-copy="Hello World"`)
        }
    }
    el.addEventListener("click", el._copyHandler)
}

export default {
    mounted(el, binding) {
        copy(el, binding)
    },
    updated(el, binding) {
        copy(el, binding)
    }
}
