import { nextTick, provide, reactive, ref } from "vue"
import MySetting from "../TableCommonComponent/Setting.vue"

export default function useSettings() {
    const settingRef = ref<InstanceType<typeof MySetting> | null>(null)
    // 表格配置
    const options = reactive({
        bordered: {
            wrapper: true,
            cell: true
        },
        size: "small",
        stripe: false
    })
    provide("options", options)
    // 处理函数
    const tableIsShow = ref(true)
    const clickSetting = () => {
        settingRef.value!.open()
    }
    const changeColumn = async () => {
        tableIsShow.value = false
        await nextTick(() => (tableIsShow.value = true))
    }
    return { options, clickSetting, changeColumn, settingRef }
}
