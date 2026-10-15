import MaCrud from "./ma-crud/index.vue"
import MaForm from "./ma-form/index.vue"
import MaUpload from "./ma-upload/index.vue"
import MaTreeSlider from "./ma-treeSlider/index.vue"
import MaResource from "./ma-resource/index.vue"
import MaResourceButton from "./ma-resource/button.vue"
import MaUser from "./ma-user/index.vue"
import MaEditor from "./ma-editor/index.vue"
import MaIcon from "./ma-icon/index.vue"
import MaUserInfo from "./ma-userInfo/index.vue"
// 后续增加的全局组件
import Empty from "./Empty/index.vue"

export default {
    install(Vue) {
        Vue.component("MaCrud", MaCrud)
        Vue.component("MaForm", MaForm)
        Vue.component("MaUpload", MaUpload)
        Vue.component("MaTreeSlider", MaTreeSlider)
        Vue.component("MaResource", MaResource)
        Vue.component("MaResourceButton", MaResourceButton)
        Vue.component("MaUser", MaUser)
        Vue.component("MaEditor", MaEditor)
        Vue.component("MaIcon", MaIcon)
        Vue.component("MaUserInfo", MaUserInfo)
        // 后续增加的组件
        Vue.component("Empty", Empty)
    }
}
