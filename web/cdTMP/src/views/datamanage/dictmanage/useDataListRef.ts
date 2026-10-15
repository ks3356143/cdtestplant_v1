import { ref } from "vue"
/**
 * 该hook仅定义dataList的ref以及调用open函数
 */
export default function useDataListRef() {
    const datalistRef = ref()
    // 打开datalist页面
    const openDictList = async (row: object) => {
        datalistRef.value.open(row)
    }
    return {
        datalistRef,
        openDictList
    }
}
