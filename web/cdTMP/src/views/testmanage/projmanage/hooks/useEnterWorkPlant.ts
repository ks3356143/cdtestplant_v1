import { useRouter } from "vue-router"
/**
 * 整个hook用于点击工作区按钮
 * @returns 返回进入工作区按钮事件处理函数
 */
const useEnterWorkPlant = function () {
    // global
    const router = useRouter()

    // events
    const enterWorkPlant = function (record: any) {
        if (localStorage.getItem("tree_local_data")) {
            localStorage.removeItem("tree_local_data")
        }
        router.push({ name: "project", query: record })
    }
    return {
        enterWorkPlant
    }
}

export default useEnterWorkPlant
