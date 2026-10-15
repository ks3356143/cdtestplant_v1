import role from "./role"
// 该文件规定如何role不为对应值则删除dom
// 用法：vue的指令 -> v-role="['admin']"即只允许userStore里面role属性为admin才能看见
const checkRole = (el, binding) => {
    const { value } = binding

    if (Array.isArray(value)) {
        if (value.length > 0) {
            let isHas = false
            value.map((item) => {
                isHas = role(item)
            })

            if (!isHas && el.parentNode) {
                el.parentNode.removeChild(el)
            }
        }
    } else {
        throw new Error(`need role! Like v-role="['seo', 'cfo']"`)
    }
}

export default {
    mounted(el, binding) {
        checkRole(el, binding)
    },
    updated(el, binding) {
        checkRole(el, binding)
    }
}
