import NProgress from "nprogress" // progress bar
import "nprogress/nprogress.css"
import { useUserStore } from "@/store"
// userInfo守卫
export default function setupUserLoginInfoGuard(router) {
    router.beforeEach(async (to, from) => {
        NProgress.start()
        const userStore = useUserStore()
        // 如果用户已经登录
        if (userStore.isLogin()) {
            if (userStore.role) {
                return
            } else {
                try {
                    await userStore.info()
                    return
                } catch (error) {
                    await userStore.logout()
                    return {
                        name: "login",
                        query: {
                            redirect: to.name,
                            ...to.query
                        }
                    }
                }
            }
        } else {
            if (to.name === "login") {
                return
            }
            return {
                name: "login",
                query: {
                    redirect: to.name,
                    ...to.query
                }
            }
        }
    })
}
