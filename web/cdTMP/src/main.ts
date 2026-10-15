import { createApp } from "vue"
import ArcoVue from "@arco-design/web-vue"
import ArcoVueIcon from "@arco-design/web-vue/es/icon"
import globalComponents from "@/components"
import App from "./App.vue"
import router from "./router"
import pinia from "@/store"

// 导入全局样式
import "@/style/skin.less"
import "@/style/index.css"
import "@/style/global.less"
// 导入vue-data-ui样式
import "vue-data-ui/style.css"

// 读取package.json打印个软件名称和版本
import tool from "@/utils/tool"
import packageJson from "../package.json"

// Before App Started
const app = createApp(App)
app.use(ArcoVue, {})
app.use(ArcoVueIcon)
app.use(router)
app.use(pinia)
app.use(globalComponents)

// 全局loading插件
import loadingPlugin from "./plugins/loading"
app.use(loadingPlugin)

// 使用服务端请求数据管理库
import { VueQueryPlugin } from "@tanstack/vue-query"
app.use(VueQueryPlugin)
import directives from "@/directives"
app.use(directives)

// 注册ma图标
const modules = import.meta.glob("./assets/ma-icons/*.vue", { eager: true })
for (const path in modules) {
    const name = path.match(/([A-Za-z0-9_-]+)/g)![2]
    const componentName = `MaIcon${name}`
    app.component(componentName, (modules[path] as any).default)
}

// 全局注册变量和工具
app.config.globalProperties.$tool = tool
app.config.globalProperties.$title = import.meta.env.VITE_APP_TITLE
app.config.globalProperties.$url = import.meta.env.VITE_APP_BASE
app.config.globalProperties.$version = packageJson.version
app.mount("#app")

// show version tag in console
tool.capsule("TestManagePlant", `v${packageJson.version} debug`)
