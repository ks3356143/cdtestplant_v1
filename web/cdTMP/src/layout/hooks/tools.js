/**
 * 获取a-tree右键的元素信息
 */
export function getContextNodeInfo(element) {
    const pElement = element.parentElement
    if (pElement.dataset.key) {
        const title = pElement.querySelector("span.arco-tree-node-title-text").innerText
        const isLeaf = pElement.classList.contains("arco-tree-node-is-leaf")
        return {
            nodekey: pElement.dataset.key,
            level: pElement.dataset.level,
            title,
            isLeaf
        }
    } else {
        if (pElement.parentElement) {
            return getContextNodeInfo(pElement) // 易错点，必须返回调用无用
        }
    }
}
