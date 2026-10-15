// 用于远程加载数据时候显示加载中
import imgUrl from "@/assets/funcImg/loading.svg"
import styles from "./loading.module.less"

// 创建img元素
function createImg() {
    const imgEle = document.createElement("img")
    // 给个html自定义属性
    imgEle.dataset.role = "loading"
    imgEle.src = imgUrl
    imgEle.classList.add(styles.img)
    imgEle.title = "loading element"
    return imgEle
}

// 通过el找到img元素-在update钩子的时候，在update时已经创建了img元素了
function getImgElement(element) {
    return element.querySelector("img[data-role=loading]")
}

export default function (el, binding) {
    const img = getImgElement(el)
    if (binding.value) {
        // 这里要判断是否有元素，否则在update钩子会创建多个!!!
        if (!img) {
            const img = createImg()
            el.appendChild(img)
        }
    } else {
        if (img) {
            img.remove()
        }
    }
}
