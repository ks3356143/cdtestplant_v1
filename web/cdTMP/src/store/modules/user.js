import { defineStore } from "pinia"
import tool from "@/utils/tool"
import { removeRouteListener } from "@/utils/route-listener"
import loginAPI from "@/api/login"
import { useAppStore } from "@/store"

const useUserStore = defineStore("user", {
    state: () => ({
        username: undefined,
        name: undefined,
        avatar: undefined,
        job: undefined,
        organization: undefined,
        location: undefined,
        introduction: undefined,
        personalWebsite: undefined,
        jobName: undefined,
        organizationName: undefined,
        locationName: undefined,
        phone: undefined,
        registrationDate: undefined,
        accountId: undefined,
        certification: undefined,
        role: ""
    }),

    getters: {
        setUserInfo(state) {
            return { ...state }
        }
    },

    actions: {
        // 切换角色函数
        switchRoles() {
            return new Promise((resolve) => {
                this.role = this.role === "user" ? "admin" : "user"
                resolve(this.role)
            })
        },
        // token相关操作
        isLogin() {
            return !!localStorage.getItem(import.meta.env.VITE_APP_TOKEN_PREFIX)
        },
        setToken(token) {
            tool.local.set(import.meta.env.VITE_APP_TOKEN_PREFIX, token)
        },
        getToken() {
            return tool.local.get(import.meta.env.VITE_APP_TOKEN_PREFIX)
        },
        clearToken() {
            tool.local.remove(import.meta.env.VITE_APP_TOKEN_PREFIX)
        },
        // 全局更新userInfo信息
        setInfo(data) {
            this.$patch(data)
        },
        // 请求用户信息
        async info() {
            const res = await loginAPI.getInfo()
            this.setInfo(res.data)
        },
        resetUserInfo() {
            this.$reset()
        },

        // login函数，传一个form信息
        login(form) {
            const form_data = { username: form.username, password: form.password }
            return loginAPI
                .login(form_data)
                .then((res) => {
                    if (res.success === true) {
                        this.setToken(res.data.token)
                        // this.setToken(res.data.token)
                        return true
                    } else {
                        return false
                    }
                })
                .catch((e) => {
                    return false
                })
        },
        logoutCallBack() {
            const appStore = useAppStore()
            this.resetUserInfo()
            this.clearToken()
            removeRouteListener()
            appStore.clearServerMenu()
        },
        async logout() {
            try {
                await loginAPI.logout()
            } finally {
                this.logoutCallBack()
            }
        }
    }
})

export default useUserStore
