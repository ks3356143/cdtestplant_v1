import auth from "./auth/index"
import role from "./role/index"
import copy from "./copy/index"
import loading from "./loading/index"

export default {
    install(Vue) {
        Vue.directive("auth", auth)
        Vue.directive("role", role)
        Vue.directive("copy", copy)
        Vue.directive("loading", loading)
    }
}
