/**
 * 生成产品文档按钮
 */
import { ref } from "vue"
import hoosk from "./hooks"
import seitaiGenerateApi from "@/api/generate/seitaiGenerate"
import type { IFragmentItem } from "@/views/testmanage/projmanage/GeneratorModal/index.vue"

const useSeitaiModal = function () {
    // refs
    const visible = ref(false) // Modal显隐
    const isComplete = ref(false) // 是否生成完成
    // events
    const handleModalConfirmClick = () => {
        visible.value = false // 关闭Modal
    }
    // 生成文档
    // ~~~~~~~~测试大纲生成文档~~~~~~~~
    const createSeitaiDagang = async (id: number, ptext: string, fragmentList: IFragmentItem[]) => {
        // 根据一系列文档生成大纲 - 这里有进度条组件、a-modal组件
        hoosk.create_entire_doc(visible, isComplete, seitaiGenerateApi.createDagangSeiTai, id, ptext, fragmentList)
    }
    // ~~~~~~~~测试说明生成文档~~~~~~~~
    const createSeitaiShuoming = async (id: number, ptext: string, fragmentList: IFragmentItem[]) => {
        hoosk.create_entire_doc(visible, isComplete, seitaiGenerateApi.createShuomingSeiTai, id, ptext, fragmentList)
    }
    // ~~~~~~~~记录生成文档~~~~~~~~
    const createSeitaiJilu = async (id: number, ptext: string, fragmentList: IFragmentItem[]) => {
        hoosk.create_entire_doc(visible, isComplete, seitaiGenerateApi.createJiluSeiTai, id, ptext, fragmentList)
    }
    // ~~~~~~~~回归测试说明~~~~~~~~
    const createSeitaiHsm = async (id: number, ptext: string, fragmentList: IFragmentItem[]) => {
        hoosk.create_entire_doc(visible, isComplete, seitaiGenerateApi.createHsmDocument, id, ptext, fragmentList)
    }
    // ~~~~~~~~回归测试记录~~~~~~~~
    const createSeitaiHjl = async (id: number, ptext: string, fragmentList: IFragmentItem[]) => {
        hoosk.create_entire_doc(visible, isComplete, seitaiGenerateApi.createHjlDocument, id, ptext, fragmentList)
    }
    // ~~~~~~~~问题单~~~~~~~~
    const createSeitaiWtd = async (id: number, ptext: string, fragmentList: IFragmentItem[]) => {
        hoosk.create_entire_doc(visible, isComplete, seitaiGenerateApi.createWtdDocument, id, ptext, fragmentList)
    }
    // ~~~~~~~~报告生成文档~~~~~~~~
    const createSeitaiBaogao = async (id: number, ptext: string, fragmentList: IFragmentItem[]) => {
        hoosk.create_entire_doc(visible, isComplete, seitaiGenerateApi.createBgDocument, id, ptext, fragmentList)
    }

    return {
        visible,
        isComplete,
        handleModalConfirmClick,
        createSeitaiDagang,
        createSeitaiShuoming,
        createSeitaiJilu,
        createSeitaiHsm,
        createSeitaiHjl,
        createSeitaiWtd,
        createSeitaiBaogao
    }
}

export default useSeitaiModal
