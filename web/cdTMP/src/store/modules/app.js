import { defineStore } from "pinia"
import { Notification } from "@arco-design/web-vue"
import defaultSettings from "@/config/setting.json"

const useAppStore = defineStore("app", {
    state: () => ({
        ...defaultSettings
    }),
    getters: {
        appCurrentSetting(state) {
            return { ...state }
        },
        appDevice(state) {
            return state.device
        },
        appAsyncMenus(state) {
            return state.serverMenu
        }
    },
    actions: {
        // 更新设置
        updateSettings(partial) {
            this.$patch(partial)
        },
        // 改变主题
        toggleTheme() {
            const currentTheme = document.body.getAttribute("arco-theme")
            if (currentTheme === "dark") {
                this.theme = "light"
                document.body.setAttribute("arco-theme", "light")
            } else {
                this.theme = "dark"
                document.body.setAttribute("arco-theme", "dark")
            }
        },
        // 切换用户设备
        toggleDevice(device) {
            this.device = device
        },
        // 切换菜单
        toggleMenu(value) {
            this.hideMenu = value
        },
        async fetchServerMenuConfig() {
            let notifyInstance = null
            try {
                notifyInstance = Notification.info({
                    id: "menuNotice", // Keep the instance id the same
                    content: "loading",
                    closable: true
                })
                const { data } = await getMenuList()
                this.serverMenu = data
                notifyInstance = Notification.success({
                    id: "menuNotice",
                    content: "success",
                    closable: true
                })
            } catch (error) {
                // eslint-disable-next-line @typescript-eslint/no-unused-vars
                notifyInstance = Notification.error({
                    id: "menuNotice",
                    content: "error",
                    closable: true
                })
            }
        },
        clearServerMenu() {
            this.serverMenu = []
        }
    }
})

export default useAppStore
