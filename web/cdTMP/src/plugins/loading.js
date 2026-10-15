import { createVNode, render } from "vue"
import LoadingComponent from "@/components/GlobalLoading/index.vue"

export default {
    install(app) {
        // 创建虚拟节点并渲染
        const vnode = createVNode(LoadingComponent)
        render(vnode, document.body)

        // 挂载到全局属性
        app.config.globalProperties.$loading = {
            show: (text) => vnode.component?.exposed?.show(text),
            hide: () => vnode.component?.exposed?.hide()
        }
    }
}
